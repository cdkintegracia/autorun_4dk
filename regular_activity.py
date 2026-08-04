#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Контроль активности сотрудников Битрикс24 за последние несколько часов."""

import argparse
import logging
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional, Set, Tuple

from fast_bitrix24 import Bitrix
from authentication import authentication


# -----------------------------------------------------------------------------
# НАСТРОЙКИ
# -----------------------------------------------------------------------------

DATA_AUTH = "Bitrix"
NOTIFY_AUTH = "Bitrix"
EXPECTED_NOTIFY_SENDER_ID = 1
NOTIFY_USER_ID = 1

WINDOW_HOURS = 3
MSK = timezone(timedelta(hours=3), name="MSK")

EMPLOYEE_IDS = [
    355,
    131,
    355,
    185,
    1435,
    291,
    6605,
    153,
    181,
    177,
    1203,
    135,
    175,
    161,
    169,
    129,
    179,
    471,
    187
]

MANUAL_EXCLUDE_IDS = {
    # 789,
}


# -----------------------------------------------------------------------------
# REST И ОБЩИЕ ФУНКЦИИ
# -----------------------------------------------------------------------------


def raw_call(bitrix: Bitrix, method: str, params: dict):
    response = bitrix.call(method, params, raw=True)
    if not isinstance(response, dict):
        raise RuntimeError(f"{method}: неожиданный ответ {type(response).__name__}")
    if response.get("error"):
        raise RuntimeError(
            f"{method}: {response['error']} — "
            f"{response.get('error_description', 'без описания')}"
        )
    return response.get("result")


def as_ids(values: Iterable) -> Set[int]:
    result: Set[int] = set()
    for value in values:
        try:
            result.add(int(value))
        except (TypeError, ValueError):
            pass
    return result


def field_id(item: dict, *names: str) -> Optional[int]:
    for name in names:
        if name in item and item[name] not in (None, ""):
            try:
                return int(item[name])
            except (TypeError, ValueError):
                continue
    return None


def webhook_owner_id(url: str) -> Optional[int]:
    match = re.search(r"/rest/(\d+)/", url)
    return int(match.group(1)) if match else None


def resolve_webhook(value: str) -> str:
    value = value.strip()
    if value.startswith(("https://", "http://")):
        return value.rstrip("/") + "/"
    return authentication(value)


def b24_datetime(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def send_notification(bitrix: Bitrix, text: str) -> None:
    notification_id = raw_call(
        bitrix,
        "im.notify.personal.add",
        {
            "USER_ID": int(NOTIFY_USER_ID),
            "MESSAGE": text,
            "MESSAGE_OUT": text,
        },
    )

    if notification_id in (None, False):
        raise RuntimeError("Битрикс24 не создал уведомление")


def get_names(bitrix: Bitrix, employee_ids: Set[int]) -> Dict[int, str]:
    users = bitrix.get_all("user.get", {"filter": {"ID": sorted(employee_ids)}})
    names: Dict[int, str] = {}
    for user in users:
        user_id = int(user["ID"])
        name = " ".join(
            part for part in [user.get("NAME", ""), user.get("LAST_NAME", "")] if part
        ).strip()
        names[user_id] = name or user.get("EMAIL") or f"ID {user_id}"

    for user_id in employee_ids:
        names.setdefault(user_id, f"ID {user_id}")
    return names


# -----------------------------------------------------------------------------
# ОТСУТСТВИЯ
# -----------------------------------------------------------------------------


def event_interval_utc(event: dict) -> Optional[Tuple[datetime, datetime]]:
    try:
        start = datetime.fromtimestamp(
            int(float(event["DATE_FROM_TS_UTC"])), tz=timezone.utc
        )
        end = datetime.fromtimestamp(
            int(float(event["DATE_TO_TS_UTC"])), tz=timezone.utc
        )
        return start, end
    except (KeyError, TypeError, ValueError, OSError):
        pass

    try:
        start = datetime.fromisoformat(str(event["DATE_FROM"]).replace("Z", "+00:00"))
        end = datetime.fromisoformat(str(event["DATE_TO"]).replace("Z", "+00:00"))
        if start.tzinfo is None:
            start = start.replace(tzinfo=MSK)
        if end.tzinfo is None:
            end = end.replace(tzinfo=MSK)
        return start.astimezone(timezone.utc), end.astimezone(timezone.utc)
    except (KeyError, TypeError, ValueError):
        return None


def get_absent_ids(
    bitrix: Bitrix,
    employee_ids: Set[int],
    period_start: datetime,
    period_end: datetime,
) -> Set[int]:
    result = raw_call(
        bitrix,
        "calendar.accessibility.get",
        {
            "users": sorted(employee_ids),
            "from": period_start.date().isoformat(),
            "to": (period_end.date() + timedelta(days=1)).isoformat(),
        },
    )
    if not isinstance(result, dict):
        raise RuntimeError("calendar.accessibility.get вернул неожиданный результат")

    start_utc = period_start.astimezone(timezone.utc)
    end_utc = period_end.astimezone(timezone.utc)
    absent_ids: Set[int] = set()

    for raw_user_id, events in result.items():
        user_id = int(raw_user_id)
        if user_id not in employee_ids or not isinstance(events, list):
            continue

        for event in events:
            if str(event.get("ACCESSIBILITY", "")).lower() != "absent":
                continue

            interval = event_interval_utc(event)
            if interval is None:
                absent_ids.add(user_id)
                break

            event_start, event_end = interval
            if event_start < end_utc and event_end > start_utc:
                absent_ids.add(user_id)
                break

    return absent_ids


# -----------------------------------------------------------------------------
# АКТИВНОСТЬ
# -----------------------------------------------------------------------------


def monitored_actor(activity: dict, employee_ids: Set[int]) -> Optional[int]:
    """Определяет сотрудника CRM-дела.

    Для звонков и писем главным полем является RESPONSIBLE_ID. AUTHOR_ID и
    EDITOR_ID используются только как запасные варианты, если ответственный не
    входит в контролируемый список.
    """
    for names in (
        ("RESPONSIBLE_ID", "responsibleId"),
        ("AUTHOR_ID", "authorId"),
        ("EDITOR_ID", "editorId"),
    ):
        user_id = field_id(activity, *names)
        if user_id in employee_ids:
            return user_id
    return None


def get_crm_activities(
    bitrix: Bitrix,
    base_filter: dict,
    time_fields: Iterable[str],
    start: str,
    end: str,
) -> List[dict]:
    """Получает CRM-дела по нескольким временным полям и убирает дубли по ID."""
    by_id: Dict[str, dict] = {}
    select = [
        "ID",
        "TYPE_ID",
        "PROVIDER_ID",
        "PROVIDER_TYPE_ID",
        "SUBJECT",
        "CREATED",
        "LAST_UPDATED",
        "START_TIME",
        "END_TIME",
        "COMPLETED",
        "DIRECTION",
        "RESPONSIBLE_ID",
        "AUTHOR_ID",
        "EDITOR_ID",
        "ASSOCIATED_ENTITY_ID",
    ]

    for time_field in time_fields:
        current_filter = dict(base_filter)
        current_filter[f">={time_field}"] = start
        current_filter[f"<{time_field}"] = end
        rows = bitrix.get_all(
            "crm.activity.list",
            {"filter": current_filter, "select": select},
        )
        for row in rows:
            activity_id = str(row.get("ID", ""))
            if activity_id:
                by_id[activity_id] = row

    return list(by_id.values())


def collect_activity(
    bitrix: Bitrix,
    employee_ids: Set[int],
    period_start: datetime,
    period_end: datetime,
    debug: bool = False,
) -> Dict[int, Counter]:
    start = b24_datetime(period_start)
    end = b24_datetime(period_end)

    # Наборы нужны, чтобы одно и то же событие, найденное разными методами или
    # по разным временным полям, не посчиталось дважды.
    events: Dict[int, Dict[str, Set[str]]] = {
        user_id: defaultdict(set) for user_id in employee_ids
    }

    # 1. Поставленные задачи: постановщик + CREATED_DATE.
    created_tasks = bitrix.get_all(
        "tasks.task.list",
        {
            "filter": {">=CREATED_DATE": start, "<CREATED_DATE": end},
            "select": ["ID", "TITLE", "CREATED_BY", "CREATED_DATE"],
        },
    )
    for task in created_tasks:
        user_id = field_id(task, "createdBy", "CREATED_BY")
        if user_id in employee_ids:
            events[user_id]["created_tasks"].add(str(task.get("id") or task.get("ID")))
            if debug:
                logging.info("DEBUG создана задача: user=%s task=%s", user_id, task)

    # 2. Закрытые задачи из модуля задач.
    closed_tasks = bitrix.get_all(
        "tasks.task.list",
        {
            "filter": {">=CLOSED_DATE": start, "<CLOSED_DATE": end},
            "select": [
                "ID",
                "TITLE",
                "RESPONSIBLE_ID",
                "CLOSED_DATE",
                "STATUS",
            ],
        },
    )
    for task in closed_tasks:
        user_id = field_id(task, "responsibleId", "RESPONSIBLE_ID")
        if user_id in employee_ids:
            task_id = str(task.get("id") or task.get("ID"))
            events[user_id]["closed_tasks"].add(f"task:{task_id}")
            if debug:
                logging.info("DEBUG закрыта задача: user=%s task=%s", user_id, task)

    # 3. CRM-задачи. Это страхует случай, когда действие видно в истории CRM,
    # но не попало в выборку tasks.task.list.
    crm_tasks = get_crm_activities(
        bitrix,
        {"TYPE_ID": 3, "COMPLETED": "Y"},
        ("LAST_UPDATED",),
        start,
        end,
    )
    for activity_item in crm_tasks:
        user_id = monitored_actor(activity_item, employee_ids)
        if user_id is None:
            continue
        associated_id = field_id(activity_item, "ASSOCIATED_ENTITY_ID")
        if associated_id:
            event_key = f"task:{associated_id}"
        else:
            event_key = f"crm-task:{activity_item['ID']}"
        events[user_id]["closed_tasks"].add(event_key)
        if debug:
            logging.info(
                "DEBUG завершена CRM-задача: user=%s activity=%s",
                user_id,
                activity_item,
            )

    # 4. Звонки из статистики телефонии.
    calls = bitrix.get_all(
        "voximplant.statistic.get",
        {
            "FILTER": {
                ">=CALL_START_DATE": start,
                "<CALL_START_DATE": end,
                "CALL_TYPE": 1,
            }
        },
    )
    for call in calls:
        user_id = field_id(call, "PORTAL_USER_ID")
        if user_id not in employee_ids:
            continue
        crm_activity_id = field_id(call, "CRM_ACTIVITY_ID")
        event_key = (
            f"crm-call:{crm_activity_id}"
            if crm_activity_id
            else f"vox-call:{call.get('ID')}"
        )
        events[user_id]["outgoing_calls"].add(event_key)
        if debug:
            logging.info("DEBUG звонок телефонии: user=%s call=%s", user_id, call)

    # 5. Исходящие звонки как CRM-дела. Это покрывает ручные звонки и внешнюю
    # телефонию, которые могут быть видны в истории CRM, но отсутствовать в
    # voximplant.statistic.get.
    crm_calls = get_crm_activities(
        bitrix,
        {"TYPE_ID": 2, "DIRECTION": 2},
        ("CREATED", "START_TIME"),
        start,
        end,
    )
    for activity_item in crm_calls:
        user_id = monitored_actor(activity_item, employee_ids)
        if user_id is None:
            continue
        events[user_id]["outgoing_calls"].add(f"crm-call:{activity_item['ID']}")
        if debug:
            logging.info(
                "DEBUG исходящий CRM-звонок: user=%s activity=%s",
                user_id,
                activity_item,
            )

    # 6. Исходящие письма. Для сотрудника сначала используем RESPONSIBLE_ID:
    # AUTHOR_ID у почтового дела нередко является системным пользователем или
    # владельцем интеграции.
    emails = get_crm_activities(
        bitrix,
        {"TYPE_ID": 4, "DIRECTION": 2},
        ("CREATED", "START_TIME"),
        start,
        end,
    )
    for email in emails:
        user_id = monitored_actor(email, employee_ids)
        if user_id is None:
            continue
        events[user_id]["outgoing_emails"].add(f"crm-email:{email['ID']}")
        if debug:
            logging.info("DEBUG исходящее письмо: user=%s email=%s", user_id, email)

    result: Dict[int, Counter] = {}
    for user_id in employee_ids:
        result[user_id] = Counter(
            {
                "created_tasks": len(events[user_id]["created_tasks"]),
                "closed_tasks": len(events[user_id]["closed_tasks"]),
                "outgoing_calls": len(events[user_id]["outgoing_calls"]),
                "outgoing_emails": len(events[user_id]["outgoing_emails"]),
            }
        )
    return result


# -----------------------------------------------------------------------------
# ЗАПУСК
# -----------------------------------------------------------------------------


def run(dry_run: bool = False, debug: bool = False) -> int:
    now = datetime.now(MSK)
    if now.isoweekday() in (6, 7):
        logging.info("Выходной день — проверка пропущена")
        return 0

    employee_ids = as_ids(EMPLOYEE_IDS) - as_ids(MANUAL_EXCLUDE_IDS)
    if not employee_ids:
        logging.warning("Заполните EMPLOYEE_IDS")
        return 0

    data_webhook = resolve_webhook(DATA_AUTH)
    notify_webhook = resolve_webhook(NOTIFY_AUTH)
    data_b24 = Bitrix(data_webhook, verbose=False)
    notify_b24 = Bitrix(notify_webhook, verbose=False)

    sender_id = webhook_owner_id(notify_webhook)
    if sender_id is not None and sender_id != EXPECTED_NOTIFY_SENDER_ID:
        raise RuntimeError(
            f"Вебхук уведомлений принадлежит пользователю {sender_id}, "
            f"а должен принадлежать {EXPECTED_NOTIFY_SENDER_ID}"
        )

    period_end = now
    period_start = now - timedelta(hours=WINDOW_HOURS)
    logging.info(
        "Проверяем интервал %s — %s",
        period_start.isoformat(timespec="seconds"),
        period_end.isoformat(timespec="seconds"),
    )

    names = get_names(data_b24, employee_ids)
    absent_ids = get_absent_ids(data_b24, employee_ids, period_start, period_end)
    checked_ids = employee_ids - absent_ids

    for user_id in sorted(absent_ids, key=lambda uid: names[uid]):
        logging.info("Пропущен отсутствующий сотрудник: %s", names[user_id])

    if not checked_ids:
        logging.info("Все контролируемые сотрудники отсутствуют")
        return 0

    activity = collect_activity(
        data_b24,
        checked_ids,
        period_start,
        period_end,
        debug=debug,
    )
    inactive_ids: List[int] = []

    for user_id in sorted(checked_ids, key=lambda uid: names[uid]):
        counts = activity[user_id]
        total = sum(counts.values())
        logging.info(
            "%s: поставлено=%d, закрыто=%d, звонков=%d, писем=%d, всего=%d",
            names[user_id],
            counts["created_tasks"],
            counts["closed_tasks"],
            counts["outgoing_calls"],
            counts["outgoing_emails"],
            total,
        )
        if total == 0:
            inactive_ids.append(user_id)

    if not inactive_ids:
        logging.info("Нулевой активности ни у кого нет")
        return 0

    inactive_names = ", ".join(names[user_id] for user_id in inactive_ids)
    message = (
        f"Сотрудники {inactive_names} не активны за последние {WINDOW_HOURS} часа "
        f"({period_start:%H:%M}–{period_end:%H:%M})."
    )

    if dry_run:
        logging.info("DRY RUN: %s", message)
    else:
        send_notification(notify_b24, message)
        logging.info("Уведомление отправлено пользователю ID %s", NOTIFY_USER_ID)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    try:
        return run(dry_run=args.dry_run, debug=False)

    except Exception as error:
        logging.exception("Проверка не выполнена")

        try:
            notify_b24 = Bitrix(resolve_webhook(NOTIFY_AUTH), verbose=False)
            text = f"Скрипт контроля активности сотрудников не выполнен: {error}"

            if args.dry_run:
                logging.error("DRY RUN: %s", text)
            else:
                send_notification(notify_b24, text)

        except Exception:
            logging.exception("Не удалось отправить уведомление об ошибке")

        return 1


if __name__ == "__main__":
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
