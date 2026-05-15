from datetime import datetime
import base64
from fast_bitrix24 import Bitrix
from authentication import authentication

b = Bitrix(authentication('Bitrix'))


def clear_city_phone_contact():

    changed_contacts = []

    # Получаем только контакты без компании с заполненными телефонами
    contacts = b.get_all(
        'crm.contact.list',
        {
            'filter': {
                'COMPANY_ID': False,
                '!PHONE': False
            },
            'select': ['ID', 'PHONE']
        }
    )

    for contact in contacts:

        contact_id = contact.get('ID')
        phones = contact.get('PHONE', [])

        if not phones:
            continue

        city_phones = []
        remaining_phones = []

        for phone in phones:

            value = phone.get('VALUE', '')

            # Нормализуем номер
            normalized = (
                value.replace(' ', '')
                     .replace('-', '')
                     .replace('(', '')
                     .replace(')', '')
                     .replace('+', '')
            )

            # Проверяем городской номер СПб
            if normalized.startswith(('812', '7812')):
                city_phones.append(value)
            else:
                remaining_phones.append(phone)

        # Если городских номеров нет — пропускаем
        if not city_phones:
            continue

        try:

            # Обновляем телефоны контакта
            b.call(
                'crm.contact.update',
                {
                    'id': contact_id,
                    'fields': {
                        'PHONE': remaining_phones
                    }
                }
            )

            # Добавляем комментарий в таймлайн
            comment_text = (
                'Контакт был отвязан от компании. '
                'Из карточки удалены городские номера: '
                + ', '.join(city_phones)
            )

            b.call(
                'crm.timeline.comment.add',
                {
                    'fields': {
                        'ENTITY_ID': contact_id,
                        'ENTITY_TYPE': 'contact',
                        'COMMENT': comment_text
                    }
                }
            )

            # Добавляем в список уведомления
            changed_contacts.append({
                'id': contact_id,
                'phones': city_phones
            })

            print(
                f'[OK] Контакт {contact_id}: '
                f'удалены номера {city_phones}'
            )

        except Exception as e:
            print(f'[ERROR] Контакт {contact_id}: {e}')

    # Формируем сообщение
    if changed_contacts:

        message_lines = ['В следующих контактах удалены городские номера:\n']

        for item in changed_contacts:

            contact_link = (f'https://vc4dk.bitrix24.ru/crm/contact/details/{item["id"]}/')
            phones = ', '.join(item['phones'])
            message_lines.append(f'{contact_link} - {phones}')

        message = '\n'.join(message_lines)

    else:
        message = ('Контактов без компании с городскими номерами найдено не было.')

    # Отправляем уведомления
    #users_id = ['1391', '1']
    users_id = ['1391']
    for user_id in users_id:
        b.call(
            'im.notify.system.add',
            {
                'USER_ID': user_id,
                'MESSAGE': message
            }
        )

if __name__ == '__main__':
    clear_city_phone_contact()