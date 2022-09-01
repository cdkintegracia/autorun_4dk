from fast_bitrix24 import Bitrix
import requests
from time import time
#from authentication import authentication


# Токен доступа 1С
token_1c = 'Bearer ' \
           'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MzgyIiwiaWF0IjoxNjU5MDk0MDYwfQ.USrZrC_uQqxZDhmMJJAMPKBt4cCWlMFVc4nzAJqMrM8'



# Считывание файла authentication.txt

#webhook = authentication('Bitrix')
webhook = 'https://vc4dk.bitrix24.ru/rest/311/r1oftpfibric5qym/'
b = Bitrix(webhook)

def get_id(_inn):

    """
    :param _inn: ИНН компании
    :return: Код пользователя из 1С
    """

    headers = {
        'accept': '*/*',
        'Authorization': token_1c,
    }

    params = {
        'inn': _inn,
    }

    response = requests.get('https://service-api.1capp.com/partner-api/v2/customers/findByInn', params=params,
                            headers=headers)

    # Возврат ID 1С из json-ответа если для него найдена конфигурация

    if 'id' in response.json():
        return response.json()['id']


lst_configs = []    # Список всех найденных конфигураций, для сравнения с Битриксом


def get_config(_id):

    """
    :param _id: ID пользователя 1С из поля сделки 	id ГРМ ('UF_CRM_1659520257149')
    :return: Информация о конфигурации ГРМ
    """

    headers = {
        'accept': '*/*',
        'Authorization': token_1c,
    }

    response = requests.get(f'https://service-api.1capp.com/partner-api/v2/customers/{_id}/applications',
                            headers=headers)

    lst_configs.append(response.json())     # Список всех полученных ГРМ для сравнения с Битриксом
    return response.json()


def main():

    # Список ID 1C компаний, которые нужно игнорировать при создании задачи

    ignore_companies = [
        'ef26acee-0553-43fd-ab6d-e34841486d46',     # ООО "АУРИГА"
        '400762b4-fb29-4ff6-a566-62c843202dd4',     # ООО "ЛЕНИНГРАДСКИЙ ЗАВОД МЕТАЛЛОКОНСТРУКЦИЙ МЕТАЛЛГАРАНТ"
        '0e09e942-3536-4ef8-bf99-c4e3738895d9',     # ИП Дурускар Марина Викторовна
        '0e36df54-c04d-4d52-914d-896a06ab4939',     # ЧДК
    ]

    # Сделки с типами ГРМ, ГРМ Спец, ГРМ Бизнес

    deals = b.get_all(
        'crm.deal.list',
        {
            'select': ['COMPANY_ID'],
            'filter': {'TYPE_ID': [
                'GOODS',         # ГРМ
                'UC_D7TC4I',         # ГРМ
                'UC_K9QJDV'     # ГРМ Бизнес
            ]
            }
        }
    )

    # Поиск компаний, у которых есть ИНН, но нет id ГРМ

    companies = []      # Список компаний для последующих итераций

    for deal in deals:
        lst_companies = b.get_all('crm.company.list', {
            'select': [
                'UF_CRM_1659520257149',     # id ГРМ
                'UF_CRM_1656070716',      # СлужИНН
            ],
            'filter': {
                'ID': deal['COMPANY_ID'],
                '!UF_CRM_1656070716': None,   # СлужИНН != None
                'UF_CRM_1659520257149': None  # id ГРМ == None
            }
        }
                              )

        # Наполнение списка компаний для итерации

        for company in lst_companies:
            companies.append(company)

    # Заполнение поля id ГРМ в компаниях

    for company in companies:
        if company['UF_CRM_1659520257149'] is None:

            inn = company['UF_CRM_1656070716']      # ИНН компании, полученный из Битрикса
            id_1c = get_id(inn)     # ID 1С, полученный через GET запрос

            if id_1c is not None:
                b.call('crm.company.update', {
                    'ID': company['ID'],
                    'fields': {
                        'UF_CRM_1659520257149': id_1c
                    }
                }
                       )

    companies = []  # Очищение списка компаний

    # Обновление списка компаний после заполнения id ГРМ

    for deal in deals:
        lst_companies = b.get_all('crm.company.list', {
            'select': [
                'UF_CRM_1659520257149',     # id ГРМ
                'UF_CRM_1656070716',      # СлужИНН
                'TITLE',
            ],
            'filter': {
                'ID': deal['COMPANY_ID'],
                '!UF_CRM_1656070716': None,   # СлужИНН != None
                '!UF_CRM_1659520257149': None,
            }
        }
                              )

        # Наполнение списка компаний для итерации

        for company in lst_companies:
            if company not in companies:
                companies.append(company)

    # Получение всех элементов списка "Конфигурации ГРМ"

    elements = b.get_all('lists.element.get', {
        'IBLOCK_TYPE_ID': 'lists',
        'IBLOCK_ID': '167',
        'select': ['*', 'UF_*']
    }
                         )

    # Поиск расхождений (сравниваются конфигурации 1С с Битриксом)

    task_text = ''      # Текст для задачи

    for company in companies:   # Итерация списка компаний
        configs = get_config(company['UF_CRM_1659520257149'])    # Получение конфигураций компании из 1С

        for config in configs:  # Итерация списка конфигураций компании

            if 'id' not in config:
                continue

            flag = False

            for element in elements:    # Итерация списка

                for key in element['PROPERTY_1243']:    # Значения поля в элементе списка зачем-то сделано словарем

                    if config['id'] == element['PROPERTY_1243'][key]:

                        # Если конфигурация уже естn - обновляются значения полей элемента

                        b.call('lists.element.update',
                               {'IBLOCK_TYPE_ID': 'lists', 'IBLOCK_ID': '167', 'ELEMENT_ID': element['ID'],
                                'fields':
                                    {
                                        'NAME': company['TITLE'],
                                        'PROPERTY_1243': config['id'],
                                        'PROPERTY_1245': config['configurationId'],
                                        'PROPERTY_1247': config['configurationName'],
                                        'PROPERTY_1249': config['configurationVersionId'],
                                        'PROPERTY_1251': config['initialVersion'],
                                        'PROPERTY_1253': config['version'],
                                        'PROPERTY_1255': ['platformVersionId'],
                                        'PROPERTY_1257': config['platformVersion'],
                                        'PROPERTY_1259': config['name'],
                                        'PROPERTY_1261': config['status'],
                                        'PROPERTY_1263': config['url'],
                                        'PROPERTY_1265': config['licenseCount'],
                                        'PROPERTY_1267': config['scheduledDeleteDate'],
                                        'PROPERTY_1269': config['deleted'],
                                        'PROPERTY_1271': config['customerId'],
                                        'PROPERTY_1273': company['ID'],
                                        'PROPERTY_1313': '2201',
                                        # Расхождение - найдена в 1С, нет в Битриксе
                                        'PROPERTY_1275': '',
                                    }
                                }
                               )

                        flag = True

            if flag is False:

                # Если конфигурация не найдена - создается новая

                b.call('lists.element.add', {'IBLOCK_TYPE_ID': 'lists', 'IBLOCK_ID': '167', 'ELEMENT_CODE': time(),
                                             'fields':
                                                 {
                                                     'NAME': company['TITLE'],
                                                     'PROPERTY_1243': config['id'],
                                                     'PROPERTY_1245': config['configurationId'],
                                                     'PROPERTY_1247': config['configurationName'],
                                                     'PROPERTY_1249': config['configurationVersionId'],
                                                     'PROPERTY_1251': config['initialVersion'],
                                                     'PROPERTY_1253': config['version'],
                                                     'PROPERTY_1255': ['platformVersionId'],
                                                     'PROPERTY_1257': config['platformVersion'],
                                                     'PROPERTY_1259': config['name'],
                                                     'PROPERTY_1261': config['status'],
                                                     'PROPERTY_1263': config['url'],
                                                     'PROPERTY_1265': config['licenseCount'],
                                                     'PROPERTY_1267': config['scheduledDeleteDate'],
                                                     'PROPERTY_1269': config['deleted'],
                                                     'PROPERTY_1271': config['customerId'],
                                                     'PROPERTY_1273': company['ID'],
                                                     'PROPERTY_1313': '2201',
                                                     # Расхождение - найдена в 1С, нет в Битриксе
                                                     'PROPERTY_1275': '2183',
                                                 }
                                             }
                       )

                # Формирование текста конфигурации для задачи

                for i in element["PROPERTY_1259"]:
                    config_name = element["PROPERTY_1259"][i]

                for i in element["PROPERTY_1243"]:
                    config_id = element["PROPERTY_1243"][i]

                # Создание задачи на нахождение расхождения

                task_text += f'Компания: {company["TITLE"]}\n' \
                             f'Конфигурация: {config_name}\n' \
                             f'ID: {config_id}\n'\
                             f'Название услуги: {element["NAME"]}'\
                             f'---------------------------------------------------------\n'

    if task_text != '':
        b.call('tasks.task.add', {
                        'fields': {
                            'TITLE': f'Обнаружены новые конфигурации ГРМ в 1С',
                            'DESCRIPTION': task_text,
                            'CREATED_BY': '173',
                            'GROUP_ID': '13',
                            'RESPONSIBLE_ID': '311',
                            'ACCOMPLICES': '1',
                            'UF_CRM_TASK': f'C_{element["PROPERTY_1273"]}'
                        }
        }
               )

    # Поиск расхождений (сравниваются конфигурации Битрикс и 1С)

    task_text = ''      # Текст для задачи

    for element in elements:    # Итерация списка

        for key in element['PROPERTY_1243']:    # Опять словарь в значении
            flag = False

            for configs in lst_configs:

                for config in configs:

                    if 'id' not in config:
                        continue

                    if element['PROPERTY_1243'][key] == config['id']:
                        flag = True

            if flag is False:

                for id_company in element['PROPERTY_1273']:

                    # Получение названия компании для задачи

                    company_name = b.get_all(
                        'crm.company.get',
                        {
                            'ID': element['PROPERTY_1273'][id_company]
                        }
                    )

                    # Формирование текста конфигурации для задачи

                    for i in element["PROPERTY_1259"]:
                        config_name = element["PROPERTY_1259"][i]

                    for i in element["PROPERTY_1243"]:
                        config_id = element["PROPERTY_1243"][i]

                    for i in element['PROPERTY_1313']:
                        element_status = element['PROPERTY_1313'][i]

                    if element_status != '2199':

                        task_text += f'{company_name["TITLE"]}\n' \
                                     f'Конфигурация: {config_name}\n' \
                                     f'ID: {config_id}\n' \
                                     f'-----------------------------------\n'

    # Постановление задачи, если были найдены рассхождения

    if task_text != '':
        b.call('tasks.task.add', {
            'fields':
                {
                    'TITLE': f'Конфигурации ГРМ - не найдены в 1С',
                    'DESCRIPTION': task_text,
                    'CREATED_BY': '173',
                    'GROUP_ID': '13',
                    'RESPONSIBLE_ID': '311',
                    'ACCOMPLICES': '1',
                    'UF_CRM_TASK': f'C_{element["PROPERTY_1273"]}'
                }
        }
               )

    # Сравнение массива клиентов Битрикса и 1С

    companies = b.get_all('crm.company.list', {'select': ['*', 'UF_*']})   # Перебор всех клиентов, стоит заменить с фильтром

    headers = {
            'accept': '*/*',
            'Authorization': token_1c,
        }

    response = requests.get(f'https://service-api.1capp.com/partner-api/v2/customers', headers=headers)
    task_text = ''     # Текст для задачи с клиентами, которые есть в 1С и нет в Битриксе

    for client in response.json():      # Итерация списка клиентов в 1С
        flag = False

        for company in companies:       # Итерация списка компаний из Битрикса

            # Если клиент есть в обеих базах

            if client['id'] == company['UF_CRM_1659520257149']:
                flag = True

        # Если клиент из 1С не найден в Битриксе и компанию не нужно игнорировать

        if flag is False and str(client['id']) not in ignore_companies:
            task_text += f'ID 1C: {client["id"]}\n' \
                         f'email: {client["email"]}\n' \
                         f'Логин: {client["login"]}\n' \
                         f'ИНН: {client["inn"]}\n' \
                         f'КПП: {client["kpp"]}\n' \
                         f'Название: {client["name"]}\n' \
                         f'Контакт: {client["responsible"]}\n' \
                         f'Телефон: {client["phone"]}\n' \
                         f'----------------------------------------------\n'

    # Постановление задачи, если были найдены рассхождения

    if task_text != '':
        b.call('tasks.task.add', {
            'fields':
                {
                    'TITLE': f'Найдены новые клиенты в 1С',
                    'DESCRIPTION': f'Данные клиентов, которые есть в 1С и нет в Битриксе:\n'
                                   f'\n'
                                   f'{task_text}',
                    'CREATED_BY': '173',
                    'GROUP_ID': '13',
                    'RESPONSIBLE_ID': '311',
                    'ACCOMPLICES': '1',
                    'UF_CRM_TASK': f'C_{element["PROPERTY_1273"]}'
                }
        }
               )


if __name__ == '__main__':
    main()
