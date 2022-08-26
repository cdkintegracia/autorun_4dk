from fast_bitrix24 import Bitrix

from authentication import authentication

webhook = authentication('Bitrix')
#webhook = 'https://vc4dk.bitrix24.ru/rest/311/r1oftpfibric5qym/'
b = Bitrix(webhook)


def main():
    elements = b.get_all('lists.element.get', {'IBLOCK_TYPE_ID': 'lists', 'IBLOCK_ID': '109'})
    for element in elements:
        for value in element['PROPERTY_519']:
            deal_id = element['PROPERTY_519'][value]
        deal = b.get_all('crm.deal.list', {'select': ['STAGE_ID'], 'filter': {'ID': deal_id}})
        try:
            if deal[0]['STAGE_ID'] != 'C1:LOSE':
                b.call('lists.element.delete', {'IBLOCK_TYPE_ID': 'lists', 'IBLOCK_ID': '109', 'ELEMENT_ID': element['ID']})
        except:
            print(element)
            print(deal)


if __name__ == '__main__':
    main()
