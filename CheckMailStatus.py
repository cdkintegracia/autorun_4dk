import datetime

from fast_bitrix24 import Bitrix

from authentication import authentication

b = Bitrix(authentication('Bitrix'))


def main():
    crm_dct = {
        '1': ['Лид:', 'lead'],
        '2': ['Сделка:', 'deal'],
        '3': ['Контакт:', 'contact'],
        '4': ['Компания', 'company']
    }
    current_date = datetime.datetime.utcnow().strftime('%Y %m %d')
    current_date = datetime.datetime.strptime(current_date, '%Y %m %d')
    date_filter = current_date - datetime.timedelta(days=1)
    date_filter = date_filter.strftime('%Y-%m-%d')

    mails = b.get_all('crm.activity.list', {'filter': {'OWNER_TYPE_ID': '4', 'PROVIDER_TYPE_ID': 'EMAIL', '>CREATED': date_filter}})

    current_date = datetime.datetime.utcnow().strftime('%Y %m %d')
    current_date = datetime.datetime.strptime(current_date, '%Y %m %d')

    for mail in mails:
        created = mail['CREATED'].split('-')
        created[2] = created[2][:2]
        date_created = datetime.datetime.strptime('-'.join(created), '%Y-%m-%d')
        different = current_date - date_created
        if different.days > 0:
            if 'READ_CONFIRMED' not in mail['SETTINGS']:
                b.call('im.notify.system.add',
                       {'USER_ID': '311',
                        'MESSAGE': f'Письмо не прочитано в течении суток или было не доставлено:'
                        f'{crm_dct[mail["OWNER_TYPE_ID"]][0]} https://vc4dk.bitrix24.ru/crm/{crm_dct[mail["OWNER_TYPE_ID"]][1]}/details/{mail["OWNER_ID"]}/'})

if __name__ == '__main__':
    main()