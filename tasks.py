from fast_bitrix24 import Bitrix



# Считывание файла authentication.txt

with open('authentication.txt') as file:
    lines = file.readlines()
    authentication = {}
    for line in lines:
        lst = line.split(': ')
        authentication.setdefault(lst[0], lst[1].strip())


# Вебхук для доступа к Bitrix24
webhook = authentication['Bitrix']
b = Bitrix(webhook)

