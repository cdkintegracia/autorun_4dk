from fast_bitrix24 import Bitrix

from authentication import authentication


def clear_bp():
    b = Bitrix(authentication('Bitrix'))
    elements = b.get_all('lists.element.get', {
        'IBLOCK_TYPE_ID': 'lists',
        'IBLOCK_ID': '105',
        'filter': {
            '>PROPERTY_479': '16.06.2023',
            '<PROPERTY_479': '18.07.2023',
        }
    })
    bp = b.get_all('bizproc.workflow.instance.list', {'select': ['DOCUMENT_ID', 'ID'], 'filter': {'TEMPLATE_ID': '593', 'DOCUMENT_ID': list(map(lambda x: x['ID'], elements))}})
    for i in bp:
        b.call('bizproc.workflow.terminate', {'ID': i['ID']})


if __name__ == '__main__':
    clear_bp()