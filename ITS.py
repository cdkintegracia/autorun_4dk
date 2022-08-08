"""
Tips:
1. Значения полей элементов универсального списка из Битрикса возвращаются в виде словаря (ключ -
хз что значит, значение словаря - значение поля.

Надо сюда написать справочник по полям в списке
"""
from time import time
from time import asctime
from time import sleep
from fast_bitrix24 import Bitrix
import requests

"""
Спас меня этот сайт
https://reqbin.com/req/o3vugw0p/post-json-string-with-basic-authentication
"""

# Вебхук для доступа к Bitrix24
webhook = "https://vc4dk.bitrix24.ru/rest/311/r1oftpfibric5qym/"
b = Bitrix(webhook)

'''
def get_user_codes(sheet):
    """
    :param sheet: Номер страницы с записями
    :return: Получение кодов пользователей
    """
    headers = {
        'accept': 'application/json;charset=UTF-8',
        'Content-Type': 'application/json;charset=UTF-8',
        'Authorization': 'Basic YXBpLWxvZ2luLTQzODI6MGY4M2VmYWQwODEzNGM='   # Логин:пароль в base64("Basic" - зачем? хз)
    }

    json_data = {
        'page': sheet,  # Каждую страницу с данными необходимо запрашивать отдельно (передается в параметре)
        'size': 300,    # Максимум 300 записей на одном листе
    }

    response = requests.post('https://partner-api.1c.ru/api/rest/public/subscriber', headers=headers, json=json_data)
    return response.json()['subscribers']   # Возврат списка пользователей
'''


def get_report_number(type_report):
    """
    Запрос на создание отчета и получение номера отчета

    :param type_report:
    CLOUD_BACKUP – сервис 1С:Облачный архив
    COUNTERAGENT – сервис 1С:Контрагент
    LINK – сервис 1С:Линк
    NOMENCLATURE – сервис 1С:Номенклатура
    REPORTING – сервис 1С-Отчетность
    SIGN – сервис 1С:Подись
    SPARK_RISKS – сервис 1СПАРК Риски
    ESS – сервис 1С:Кабинет сотрудника
    MAG1C – сервис mag1c
    DOCUMENT_RECOGNITION – сервис 1С:Распознавание первичных документов

    :return: ID отчета
    """
    headers = {
        'accept': 'application/json;charset=UTF-8',
        'Authorization': 'Basic YXBpLWxvZ2luLTQzODI6MGY4M2VmYWQwODEzNGM='  # Логин:пароль в base64
    }

    json_data = {

        "type": type_report
    }

    response = requests.post(
        'https://partner-api.1c.ru/api/rest/public/option/billing-report',
        headers=headers, json=json_data)

    report_number = response.json()['reportUeid']   # ID запрошенного отчета
    print(f'Запрос на формирование отчета "{type_report}" отправлен. Номер отчета: {report_number}')
    return report_number


def get_report(report_number):
    """
    Получение отчета по его номеру

    :param report_number: Номер отчета
    :return: Данные отчета
    """
    headers = {

        'accept': 'application/json;charset=UTF-8',
        'Authorization': 'Basic YXBpLWxvZ2luLTQzODI6MGY4M2VmYWQwODEzNGM='  # логин:пароль в base64
    }

    response = requests.get(
        'https://partner-api.1c.ru/api/rest/public/option/billing-report/' + report_number,
        headers=headers)
    report = response.json()

    while report['state'] == 'PROCESSING':  # Ожидание готовности отчета

        print(f'Отчет формируется {asctime()}')
        sleep(10)
        report = get_report(report_number)  # Обновление статуса отчета

    if report['state'] == 'OK':     # Отчет готов
        print('Отчет получен, начинается обработка данных')
        return report
    else:
        print('Не удалось сформировать отчет', asctime())


# Получение списка с кодами всех пользователей

'''
user_codes = []
# Получение страниц с кодами пользователей
for i in range(0, 100):
    user_list = get_user_codes(i)
    if user_list == []:
        print('Все листы с данными получены')
        break
    for user in user_list:
        user_codes.append(user['code'])
    print(f'Лист {i} обработан')
'''

# Получение отчета по типу, и загрузка данных в список Битрикса "Отчет по сервисам"


def update_bitrix_list(report_type):
    """
    :param report_type: см. описание функции 'get_report_number'
    :return: Получение отчета по типу, и загрузка данных в список Битрикса "Отчет по сервисам"
    """
    report_number = get_report_number(report_type)  # Запрос отчета и получение номера запроса
    report = get_report(report_number)  # Получение отчета
    name_element_type = report_types[report_type][0]     # Название типа для элемента списка
    deal_type = report_types[report_type][1]    # Тип сделки для получения массива сделок
    name_report_type = report_types[report_type][2]     # Название услуги для фильтрации в отчете

    # Получение массива сделок по фильтру

    deals = b.get_all('crm.deal.list',
                      {
                          'select': ['COMPANY_ID'],
                          'filter': {'TYPE_ID': deal_type}
                      }
                      )

    # Элементы списка "Отчет по сервисам" из Битрикса

    bitrix_elements = b.get_all('lists.element.get',
                                {
                                    'IBLOCK_TYPE_ID': 'lists',
                                    'IBLOCK_ID': '169'}
                                )

    for element in report['report']['entries']:

        for tariff in element['tariffs']:
            flag = False    # Флаг определяющий создание нового элемента списка или обновление существующего

            if 'userOrganizationInn' in tariff:     # Если есть ИНН в элементе отчета, если нет - компания неопознана

                if name_report_type in tariff['name']:  # Если в отчете найдена нужная услуга

                    startDate = tariff['startDate']     # Дата начала из отчета
                    inn = tariff['userOrganizationInn']     # ИНН компании из отчета

                    # Поиск компании в Битриксе по ИНН из отчета

                    companies = b.get_all('crm.company.list',
                                              {
                                                  'select': ['*', 'UF_*'],
                                                  'filter': {'UF_CRM_1656070716': inn}
                                              }
                                              )

                    # Перебор компаний, сделок, элементов списки

                    for option in tariff['options']:

                        # Если не найдена нужная услуга в отчете

                        if option['name'] not in report_types[report_type][3]:
                            continue

                        # Услуга имеет счетчик количества использований

                        if 'maxVolume' in option and 'usedVolume' in option:

                            maxVolume = option['maxVolume']     # Доступное значение для сервиса
                            usedVolume = option['usedVolume']   # Использованное значение сервиса

                            if report_type in ['COUNTERAGENT']:     # Услуги, у которых есть несколько опций
                                name_element_type = option['name']

                        for company in companies:

                            for deal in deals:

                                if company['ID'] == deal['COMPANY_ID']:     # Найдена сделка, принадлежащая компании

                                    for bitrix_element in bitrix_elements:

                                        # Поля элемента списка в переменные

                                        for field_value in bitrix_element['PROPERTY_1283']:

                                            # ID компании, привязанной к элементу списка

                                            element_company_id = bitrix_element['PROPERTY_1283'][field_value]

                                        for field_value in bitrix_element['PROPERTY_1285']:

                                            # Дата начала сервиса из элемента списка

                                            element_startDate = bitrix_element['PROPERTY_1285'][field_value]

                                        # Обновление элемента списка если найден соответствующий для компании

                                        if element_company_id == company['ID'] and\
                                                element_startDate == startDate and\
                                                 bitrix_element['NAME'] == name_element_type:

                                            element_id = bitrix_element['ID']   # ID элемента списка

                                            b.call('lists.element.update',
                                                   {
                                                       'IBLOCK_TYPE_ID': 'lists',
                                                       'IBLOCK_ID': '169',
                                                       'ELEMENT_ID': element_id,
                                                       'fields':
                                                           {
                                                               'PROPERTY_1277': maxVolume,
                                                               'PROPERTY_1279': usedVolume,
                                                               'NAME': name_element_type,
                                                               'PROPERTY_1283': company['ID'],
                                                               'PROPERTY_1285': startDate
                                                           }
                                                   }
                                                   )

                                            # print(f'Обновлен элемент списка {name_element_type} {bitrix_element}')
                                            flag = True     # Найден элемент для обновления, новый создавать не нужно

                                    if flag is False:   # Если не был найден элемент для обновления

                                        # Создание элемента списка

                                        b.call('lists.element.add',
                                               {
                                                   'IBLOCK_TYPE_ID': 'lists',
                                                   'IBLOCK_ID': '169',
                                                   'ELEMENT_CODE': time(),
                                                   'fields':
                                                       {
                                                           'PROPERTY_1277': maxVolume,
                                                           'PROPERTY_1279': usedVolume,
                                                           'NAME': name_element_type,
                                                           'PROPERTY_1283': company['ID'],
                                                           'PROPERTY_1285': startDate}})

                                        # print(f"Создан {name_element_type} {company['TITLE']} {startDate}")

                                    # Защита от дублирования в том случае, если сделок по фильтру больше одной

                                    break


"""
Значения элементов словаря:
0: Тип отчета
1: Тип сделки
2: Название услуги для фильтрации в отчете
3: Список названия услуг, которые необходмо вывести в список
"""

report_types = {
    'COUNTERAGENT': [
        'Контрагент',
        'UC_A7G0AM',
        'Контрагент',
        [
            'Автозаполнение реквизитов контрагентов ',
            'Досье контрагента',
        ]
    ],
    'DOCUMENT_RECOGNITION': [
        'РПД',
        'UC_GZFC63',
        'Распознавание первичных документов',
        [
            'Число страниц',
        ]
    ],
    'ESS': [
        'Кабинет сотрудника',
        'UC_D1DN7U',
        'Кабинет сотрудника',
        [
            'Число кабинетов сотрудников',
        ]
    ],
}

def main():
    for report_type in report_types:
        update_bitrix_list(report_type)
