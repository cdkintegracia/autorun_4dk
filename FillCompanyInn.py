from fast_bitrix24 import Bitrix

from authentication import authentication


b = Bitrix(authentication('Bitrix'))


def fill_company_inn():
    companies = b.get_all('crm.company.list', {
        'filter': {
            'UF_CRM_1656070716': None,
            'COMPANY_TYPE': 'CUSTOMER'
        }
    })

    for company in companies:
        title = company['TITLE'].split()
        if title[-1].isdigit() and len(title[-1]) in [10, 12]:
            b.call('crm.company.update', {
                'ID': company['ID'],
                'fields': {
                    'UF_CRM_1656070716': title[-1],
                }
            })


if __name__ == '__main__':
    fill_company_inn()