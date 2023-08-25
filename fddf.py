from fast_bitrix24 import Bitrix

from authentication import authentication


b = Bitrix(authentication('Bitrix'))


a = b.get_all('crm.activity.get', {'id': '652423', 'select': ['*', 'UF_*']})
print(a)
b = b.get_all('crm.timeline.note.get', {
    'ownerTypeId': '4',
    'ownerId': '11045',
    'itemType': '2',
    'itemId': '652423'
})
print(b)