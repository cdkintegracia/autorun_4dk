from fast_bitrix24 import Bitrix

from authentication import authentication


b = Bitrix(authentication('Bitrix'))


def delete_dismissed_user_vacation():
    users = b.get_all('user.get', {
        'filter': {
            'ACTIVE': 'true'
        }})

    elements = b.get_all('lists.element.get', {
        'IBLOCK_TYPE_ID': 'lists',
        'IBLOCK_ID': '159',
        'filter': {
            '!PROPERTY_1235': list(map(lambda x: x['ID'], users))
        }
    })

    for element in elements:
        b.call('lists.element.delete', {
            'IBLOCK_TYPE_ID': 'lists',
            'IBLOCK_ID': '159',
            'ELEMENT_ID': element['ID'],
        })