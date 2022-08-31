from fast_bitrix24 import Bitrix

webhook = 'https://vc4dk.bitrix24.ru/rest/311/r1oftpfibric5qym/'
b = Bitrix(webhook)

companies = b.get_all('crm.company.list', {'select': ['*', 'UF_*'], 'filter': {'ID': '2461'}})

print(companies[0]['UF_CRM_1656070716'])