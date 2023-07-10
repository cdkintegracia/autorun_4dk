from fast_bitrix24 import Bitrix

from authentication import authentication


b = Bitrix(authentication('Bitrix'))


d = b.get_all('crm.deal.fields')

print(d)