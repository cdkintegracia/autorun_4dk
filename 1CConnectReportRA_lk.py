#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
1C-Connect → Bitrix24 SPA (entityTypeId=1090) для МНОЖЕСТВА специалистов.

- Для каждого SpecialistID из SPECIALIST_IDS берём сеансы за TARGET_DATE и создаём СП.
- ClientRead грузится один раз → карта ClientID → ИНН.
- Привязка компании по UF компании с ИНН (COMPANY_INN_UF_CODE = UF_CRM_1656070716).
- Заполняем: Сотрудник, Начало подключения, Продолжительность, Компания.
- Ответственный = 1, Категория = 111, stageId задай ниже.
"""

import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, date
import time
from authentication import authentication
from SendNotification import send_notification

from tools import send_bitrix_request  # твоя обёртка над REST Bitrix24

# ====== НАСТРОЙКИ ======
CONNECT_LOGIN = "bitrix"
CONNECT_PASSWORD = authentication('Connect')

SPA_ENTITY_TYPE_ID       = 1090
SPA_CATEGORY_ID          = 111
SPA_STAGE_ID             = "DT1090_111:NEW"
ASSIGNED_BY_ID_DEFAULT   = 1
B24_EMPLOYEE_ID_DEFAULT  = 1

# UF компании (crm.company), где хранится ИНН
COMPANY_INN_UF_CODE      = "UF_CRM_1656070716"

# Дата выборки
TARGET_DATE = date.today()

# Дедуп (Начало + Длительность + Сотрудник)
DEDUP = False

# ====== СПИСОК СПЕЦИАЛИСТОВ И ИХ МАППИНГ В Б24 (взято из твоего Excel) ======

SPECIALIST_TO_B24 = {
    # ЛК
    'feba0696-7606-4793-8212-9861989abe75': 119,  # Боцула
    '2b35669f-fa13-11e4-80d2-0025904f970d': 125,  # Корсунова
    'edf1d230-db47-4a0d-a4a1-cd40b92ef78a': 137,  # Коршакова
    '88210ff5-6f17-4194-bf2e-e81a3abf0024': 121,  # Рачеева
    'b2ad7a01-3578-4936-a15b-a78445c12325': 123,  # Умалатова
    '11f68b39-79be-448f-a015-9fcdb698b41a': 4247,  # Захарчук
    '6efa0ce0-fa13-11e4-80d2-0025904f970d': 127, #Плотникова
}


SPECIALIST_IDS = [
    *SPECIALIST_TO_B24.keys()
]

# ====== regex/вспомогательные ======
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
INN_RE  = re.compile(r"^\d{10}(\d{2})?$")

def normalize_inn(x: str | None) -> str | None:
    if not x: return None
    digits = re.sub(r"\D+", "", str(x))
    return digits if INN_RE.match(digits) else None

# ====== SOAP helpers ======
NS_SOAP = "{http://www.w3.org/2003/05/soap-envelope}"
NS_CORE = "{http://v8.1c.ru/8.1/data/core}"

def soap_envelope(inner_xml: str) -> str:
    return f"""<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
                              xmlns:par="http://buhphone.com/PartnerWebAPI2"
                              xmlns:core="http://v8.1c.ru/8.1/data/core"
                              xmlns:xs="http://www.w3.org/2001/XMLSchema"
                              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <soap:Header/>
  <soap:Body>{inner_xml}</soap:Body>
</soap:Envelope>"""

def core_prop(name: str, xs_type: str, value: str) -> str:
    esc = (str(value).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))
    return f'<core:Property name="{name}"><core:Value xsi:type="xs:{xs_type}">{esc}</core:Value></core:Property>'

def pick_endpoint(session: requests.Session) -> str:
    HOSTS = [
        "https://cus.1c-connect.com",
        "https://eu-cus.1c-connect.com",
        "https://cus2.1c-connect.com",
        "https://cus3.1c-connect.com",
    ]
    for base in HOSTS:
        try:
            r = session.post(base + "/cus/ws/PartnerWebAPI2", data=b"", timeout=10,
                             auth=(CONNECT_LOGIN, CONNECT_PASSWORD))
            if r.status_code != 401:
                return base + "/cus/ws/PartnerWebAPI2"
        except requests.RequestException:
            continue
    return HOSTS[0] + "/cus/ws/PartnerWebAPI2"

def _local(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag

def find_first_by_localname(elem: ET.Element, local: str):
    for e in elem.iter():
        if _local(e.tag) == local:
            return e
    return None

def safe_parse_xml(text: str):
    if not text or not text.strip():
        return None
    try:
        return ET.fromstring(text)
    except ET.ParseError:
        return None

def soap_call(session: requests.Session, endpoint: str, method: str, props_xml: str):
    body = f'<par:{method}><par:Params>{props_xml}</par:Params></par:{method}>'
    env  = soap_envelope(body)
    try:
        r = session.post(
            endpoint,
            data=env.encode("utf-8"),
            headers={"Content-Type":"application/soap+xml; charset=utf-8",
                     "User-Agent":"b24-connect-uploader/1.0"},
            auth=(CONNECT_LOGIN, CONNECT_PASSWORD),
            timeout=60
        )
        r.raise_for_status()
    except requests.RequestException as e:
        return "HTTP_ERROR", {"rows": [], "error": str(e)}

    root = safe_parse_xml(r.text)
    if root is None:
        return "PARSE_ERROR", {"rows": [], "raw": (r.text or "")[:400]}

    body_el = find_first_by_localname(root, "Body")
    if body_el is None:
        return "PARSE_ERROR", {"rows": [], "raw": (r.text or "")[:400]}

    fault_el = find_first_by_localname(body_el, "Fault")
    if fault_el is not None:
        return "SOAP_FAULT", {"rows": [], "fault": ET.tostring(fault_el, encoding="unicode")}

    ret_el = find_first_by_localname(body_el, "return")
    if ret_el is None:
        return "NO_RETURN", {"rows": [], "raw": (r.text or "")[:400]}

    def get_prop(name: str):
        for prop in ret_el.findall(f".//{NS_CORE}Property"):
            if prop.get("name") == name:
                return prop
        return None

    p_data = get_prop("ResultData")
    rows = []
    if p_data is not None:
        v = p_data.find(f".//{NS_CORE}Value")
        if v is not None:
            rows = parse_value_table(v)

    return "SUCCESS", {"rows": rows}

def parse_value_table(value_el: ET.Element):
    rows = []
    for row_el in value_el.findall(f"./{NS_CORE}row"):
        cells = [text_to_python(cell.text) for cell in row_el.findall(f"./{NS_CORE}Value")]
        rows.append({f"col_{i+1}": c for i, c in enumerate(cells)})
    return rows

def text_to_python(s: str):
    if s is None: return None
    t = s.strip()
    if t.lower() in ("true","false"): return t.lower() == "true"
    if re.fullmatch(r"-?\d+", t): return int(t)
    if re.fullmatch(r"-?\d+\.\d+", t): return float(t)
    return t

# ====== Время/форматы ======
def parse_duration_to_seconds(x) -> int | None:
    if x is None: return None
    try: return int(float(x))
    except: return None

def parse_start_local_string(st_raw: str) -> str:
    s = str(st_raw or "")
    if s.endswith("Z"): s = s[:-1]
    s = s.replace("T"," ")
    return s[:19]

# ====== Поля СП (ufCrm.. auto-resolve) ======
HUMAN_FIELD_NAMES = {
    "EMPLOYEE": "Сотрудник",
    "START":    "Начало подключения",
    "END":      "Конец подключения",
    "DURATION": "Продолжительность",
    "COMPANY":  "Компания",
}
FALLBACK_UI_CODES = {
    "EMPLOYEE": "UF_CRM_81_1760192006",
    "START":    "UF_CRM_81_1760192180",
    "END":      "UF_CRM_81_1760192205",
    "DURATION": "UF_CRM_81_1760192221",
    "COMPANY":  "UF_CRM_81_1760192128",
}

def _title_text(meta) -> str:
    if not isinstance(meta, dict): return ""
    t = meta.get("title")
    if isinstance(t, str): return t
    if isinstance(t, dict):
        return t.get("ru") or t.get("ru_RU") or t.get("ru-ru") or t.get("en") or next(iter(t.values()), "")
    return ""

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()

def _ui_suffix(ui_code: str) -> str | None:
    m = re.search(r'UF_CRM_\d+_(\d+)$', ui_code or '')
    return m.group(1) if m else None

def resolve_field_codes(entity_type_id: int):
    fields = send_bitrix_request('crm.item.fields', {'entityTypeId': entity_type_id}) or {}

    index_by_title = {}
    for code, meta in fields.items():
        title_txt = _title_text(meta)
        if title_txt:
            index_by_title[_norm(title_txt)] = code

    def by_title(human: str):
        return index_by_title.get(_norm(human))

    def by_suffix(ui_code: str):
        suf = _ui_suffix(ui_code)
        if not suf: return None
        suf = "_" + suf.lower()
        for code in fields.keys():
            if code.lower().endswith(suf):
                return code
        return None

    code_map = {}
    for key in ("EMPLOYEE", "START", "END", "DURATION", "COMPANY"):
        human = HUMAN_FIELD_NAMES.get(key)
        ui    = FALLBACK_UI_CODES.get(key)
        code  = by_title(human) or by_suffix(ui) or (ui and ui.replace('UF_CRM_', 'ufCrm').lower().replace('ufcrm', 'ufCrm'))
        code_map[key] = code

    print("Определённые коды полей (из crm.item.fields):")
    for key in ("EMPLOYEE", "START", "DURATION", "END", "COMPANY"):
        code = code_map.get(key); meta = fields.get(code) if code else None
        print(f"  {key:9s}: {code}  (title={_title_text(meta)!r}, type={(meta or {}).get('type')!r})")
    return code_map, fields

# ====== Поиск компании по ИНН ======
def find_company_id_by_company_uf_inn(inn: str) -> int | None:
    inn = normalize_inn(inn)
    if not inn: return None
    rows = send_bitrix_request('crm.company.list', {
        'filter': { COMPANY_INN_UF_CODE: inn },
        'select': ['ID', 'TITLE', COMPANY_INN_UF_CODE],
        'order': {'ID': 'ASC'},
        'start': -1
    }) or []
    if not rows:
        return None
    try:
        return int(rows[0]['ID'])
    except Exception:
        return None

# ====== ClientRead: ClientID → ИНН ======
def detect_client_id_in_row(row: dict) -> str | None:
    for v in row.values():
        s = str(v or "").strip()
        if UUID_RE.match(s):
            return s
    return None

def detect_inn_in_row(row: dict) -> str | None:
    for v in row.values():
        inn = normalize_inn(v)
        if inn:
            return inn
    return None

def load_clients_map(session: requests.Session, endpoint: str, changed_from_iso: str = "2000-01-01T00:00:00"):
    props = core_prop("ChangedFrom", "dateTime", changed_from_iso)
    code, data = soap_call(session, endpoint, "ClientRead", props)
    if code != "SUCCESS":
        print(f"⚠ ClientRead вернул {code}")
        return {}
    rows = data.get("rows") or []
    m = {}; bad = 0
    for r in rows:
        cid = r.get("ClientID") or r.get("clientid") or detect_client_id_in_row(r)
        inn = r.get("TaxPayerIdentificator") or r.get("taxpayeridentificator") or detect_inn_in_row(r)
        inn = normalize_inn(inn)
        if cid and inn:
            m[str(cid)] = inn
        else:
            bad += 1
    print(f"Загружено клиентов из ClientRead: {len(m)} шт. (пропущено {bad})")
    return m

# ====== Создание СП ======
def create_sp_item(row: dict, code_map: dict, fields_meta: dict, clients_map: dict, specialist_id: str) -> int | None:
    code_employee = code_map['EMPLOYEE']
    code_start    = code_map['START']
    code_dur      = code_map['DURATION']
    code_company  = code_map.get('COMPANY')
    meta_company  = fields_meta.get(code_company) if code_company else None

    # колонки из GetHistoryOfServiceRASessions
    start_raw = row.get("col_12")  # StartTime
    dur_raw   = row.get("col_13")  # Duration (секунды)
    spec      = row.get("col_6")   # SpecialistID/AgentAsAdmin
    client    = row.get("col_8") or ""           # в заголовок
    client_id = (row.get("ClientID") or row.get("clientid") or row.get("col_2") or "").strip()

    # фильтруем по текущему specialist_id прохода
    if spec and spec.strip() and spec.lower() != specialist_id.lower():
        return None

    dur = parse_duration_to_seconds(dur_raw)
    if not start_raw or not dur or dur <= 0:
        return None

    start_local = parse_start_local_string(start_raw)
    try:
        datetime.fromisoformat(start_local)
    except ValueError:
        return None

    employee_user_id = int(SPECIALIST_TO_B24.get(spec) or B24_EMPLOYEE_ID_DEFAULT)

    # --- Компания по ИНН из карты ClientRead ---
    company_binding = None
    if client_id and code_company:
        inn = clients_map.get(str(client_id))
        if inn:
            comp_id = find_company_id_by_company_uf_inn(inn)
            if comp_id:
                company_binding = {'entityTypeId': 4, 'id': int(comp_id)}  # COMPANY

    title = f"RA сеанс {client} — {start_local}"

    fields = {
        "title": title,
        "categoryId": SPA_CATEGORY_ID,
        "stageId": SPA_STAGE_ID,
        "assignedById": ASSIGNED_BY_ID_DEFAULT,   # Ответственный = 1
        code_employee: int(employee_user_id),     # Сотрудник
        code_start:    start_local,               # Начало
        code_dur:      int(dur),                  # Продолжительность
    }

    if code_company and company_binding:
        if isinstance(meta_company, dict) and meta_company.get('type') == 'crm':
            fields[code_company] = [company_binding]  # привязка в виде массива
        else:
            fields[code_company] = int(company_binding['id'])

    res = send_bitrix_request('crm.item.add', {
        'entityTypeId': SPA_ENTITY_TYPE_ID,
        'fields': fields
    })
    if isinstance(res, dict):
        item_id = (res.get('item') or {}).get('id')
        if item_id:
            print(f"✔ СП создан: id={item_id} (spec={specialist_id}, start={start_local})")
            return int(item_id)
    print(f"✖ Неожиданный ответ crm.item.add: {res}")
    time.sleep(2)
    return None

# ====== Загрузка сессий по специалисту ======
def fetch_sessions_for_day(d: date, specialist_id: str):
    session = requests.Session()
    endpoint = pick_endpoint(session)

    start_iso = f"{d.isoformat()}T00:00:00"
    end_iso   = f"{(d + timedelta(days=1)).isoformat()}T00:00:00"
    print(f"SOAP GetHistoryOfServiceRASessions: PeriodFrom={start_iso}, PeriodTo={end_iso}, SpecialistID={specialist_id}")

    props = core_prop("PeriodFrom", "dateTime", start_iso) + core_prop("PeriodTo", "dateTime", end_iso)
    if specialist_id:
        props += core_prop("SpecialistID", "string", specialist_id)

    code, data = soap_call(session, endpoint, "GetHistoryOfServiceRASessions", props)
    print(f"SOAP Code={code}")

    rows = data.get("rows", []) or []
    print(f"Всего строк из Коннекта (spec={specialist_id[:8]}…): {len(rows)}")
    if rows[:1]:
        print("Колонки примера:", ", ".join(rows[0].keys()))
    return rows, session, endpoint

# ====== MAIN ======
def main():
    code_map, fields_meta = resolve_field_codes(SPA_ENTITY_TYPE_ID)

    clients_map_cache = None
    total_created = total_skipped = total_errors = 0

    for specialist_id in SPECIALIST_IDS:
        if not specialist_id or not UUID_RE.match(specialist_id):
            print(f"⚠ Пропуск некорректного SpecialistID: {specialist_id!r}")
            continue

        rows_all, session, endpoint = fetch_sessions_for_day(TARGET_DATE, specialist_id)

        # Инициализируем карту клиентов один раз
        if clients_map_cache is None:
            clients_map_cache = load_clients_map(session, endpoint, "2000-01-01T00:00:00")

        if not rows_all:
            print(f"— Пусто по специалисту {specialist_id}")
            continue

        created = skipped = errors = 0
        for row in rows_all:
            try:
                res_id = create_sp_item(row, code_map, fields_meta, clients_map_cache, specialist_id)
                if res_id: created += 1
                else: skipped += 1
            except Exception as e:
                errors += 1
                print(f"✖ Ошибка создания: {e}")

        total_created += created
        total_skipped += skipped
        total_errors  += errors
        print(f"[{specialist_id}] Создано: {created}, пропущено: {skipped}, ошибок: {errors}")

    print(f"ИТОГО. Создано: {total_created}, пропущено: {total_skipped}, ошибок: {total_errors}")
    notification_text = f"Загрузка данных по RA 1С-Коннект. Создано: {total_created}, пропущено: {total_skipped}, ошибок: {total_errors}"
    send_notification(['1', '1391'], notification_text)

if __name__ == "__main__":
    main()
