from fast_bitrix24 import Bitrix

b = Bitrix('https://vc4dk.bitrix24.ru/rest/311/wkq0a0mvsvfmoseo/')

elements = b.get_all('lists.element.get', {'IBLOCK_TYPE_ID': 'lists', 'IBLOCK_ID': '185', 'filter': {'PROPERTY_1343' : 'None'}})

for element in elements:
    mail = b.get_all('crm.activity.list',
                                  {'filter': {'PROVIDER_TYPE_ID': 'EMAIL', 'ID': element['NAME']}})
    print(mail)
    exit()

