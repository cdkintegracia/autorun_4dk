from fast_bitrix24 import Bitrix

from authentication import authentication


def clear_bp():
    b = Bitrix(authentication('Bitrix'))

    elements = {}
    bp = b.get_all('bizproc.workflow.instance.list', {'select': ['DOCUMENT_ID', 'ID'], 'filter': {'TEMPLATE_ID': '593'}})
    for i in bp:
        if i['DOCUMENT_ID'] not in elements:
            elements.setdefault(i['DOCUMENT_ID'], [i['ID']])
        else:
            elements[i['DOCUMENT_ID']].append(i['ID'])

    for element in elements:
        if len(elements[element]) > 1:
            #for bizproc in elements[element]:
                #b.call('bizproc.workflow.terminate', {'ID': bizproc})
            #b.call('bizproc.workflow.start', {'TEMPLATE_ID': '593', 'DOCUMENT_ID': ['lists', 'Bitrix\Lists\BizprocDocumentLists', element]})
            b.call('tasks.task.add', {
                'fields': {
                    'TITLE': f'В элементе списка ОтправкаПисемПлан запущено несколько БП',
                    'DESCRIPTION': f'ID элемента: {element}',
                    'CREATED_BY': '1',
                    'GROUP_ID': '13',
                    'RESPONSIBLE_ID': '1',
                }
            }
                   )

if __name__ == '__main__':
    clear_bp()