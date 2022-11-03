from fast_bitrix24 import Bitrix
import requests

from authentication import authentication



webhook = authentication('Bitrix')
b = Bitrix(webhook)


def update_deal_1c_code():

    deals = b.get_all('crm.deal.list', {
        'select': [
            'ID',
            ''
        ], 'filter': {
            'STAGE_ID': [
                'C1:NEW',
                'C1:UC_0KJKTY',
                'C1:UC_3J0IH6',
                'C1:UC_KZSOR2',
                'C1:UC_VQ5HJD'

            ],
            'CATEGORY_ID': '1',
            'TYPE_ID': [
                'UC_5T4MAW',
                'UC_N113M9',
                'UC_ZKPT1B',
                'UC_2SJOEJ',
                'UC_AVBW73',
                'UC_GPT391',
                'UC_92H9MN',
                'UC_7V8HWF',
                'UC_IUJR81',
                'UC_IV3HX1',
                'UC_1UPOTU',
                'UC_81T8ZR',
                'UC_SV60SP',
                'UC_2B0CK2',
                'UC_86JXH1',
                'UC_WUGAZ7'
            ]
        }})
    error_text = ''
    for deal in deals:
        try:
            deal_id = deal['ID']

            # Получение информации о продукте сделки

            deal_product = requests.get(url=webhook + 'crm.deal.productrows.get.json?id=' + deal_id)

            # ID продукта сделки

            id_deal_product = str(deal_product.json()['result'][0]['PRODUCT_ID'])


            # Получение полей продукта

            product_fields = requests.get(url=webhook + 'crm.product.get.json?id=' + id_deal_product)

            # Получение кода 1С

            if product_fields.json()['result']['PROPERTY_139'] is None:
                return "NO CODE"
            code_1c = product_fields.json()['result']['PROPERTY_139']['value']

            # Сверка кода 1С продукта и кода в сделке

            deal_1c_code = requests.get(url=f"{webhook}crm.deal.get?id={deal_id}").json()['result']['UF_CRM_1655972832']

            if deal_1c_code != code_1c:

                # Запись кода в сделку

                requests.post(url=f"{webhook}crm.deal.update?id={deal_id}&fields[UF_CRM_1655972832]={code_1c}")
        except:
            error_text += f"{deal_id}\n"
    if error_text:
        data = {
            'fields': {
                'GROUP_ID': '13',
                'DESCRIPTION': error_text,
                'TITLE': 'Ошибка обновления поля в сделках "СлужКод1С',
                'RESPONSIBLE_ID': '173',
                'CREATED_BY': '173',
            }
        }
        new_task = requests.post(f"{webhook}tasks.task.add", json=data)
