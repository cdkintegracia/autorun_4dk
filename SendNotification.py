from fast_bitrix24 import Bitrix

from authentication import authentication

b = Bitrix(authentication('Bitrix'))


def send_motification(users_id:list, message:str):
    for user_id in users_id:
        b.call('im.notify.system.add', {
            'USER_ID': user_id,
            'MESSAGE': message})