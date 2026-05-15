from datetime import datetime
import base64
from fast_bitrix24 import Bitrix
from authentication import authentication

b = Bitrix(authentication('Bitrix'))

def clear_city_phone_contact():


    # Получаем только контакты без компании И с заполненными телефонами
    contacts = b.get_all(
        'crm.contact.list',
        {
            'filter': {
                'COMPANY_ID': False,
                '!PHONE': False
            },
            'select': [
                'ID',
                'PHONE',
            ]
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
            '''

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
                'Контакт был отвязан от компании. Из карточки удалены городские номера: '
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
            '''


            #users_id = ['1391', '1']
            users_id = ['1391']
            for user_id in users_id:
                b.call('im.notify.system.add', {
                    'USER_ID': user_id,
                    'MESSAGE': f'В контакте https://vc4dk.bitrix24.ru/crm/contact/details/{contact_id}/ удалены номера {city_phones}'
                    })

        except Exception as e:


            users_id = ['1391']
            for user_id in users_id:
                b.call('im.notify.system.add', {
                    'USER_ID': user_id,
                    'MESSAGE': f'[ERROR] Контакт {contact_id}: {e}'
                    })

        
if __name__ == '__main__':
    clear_city_phone_contact()