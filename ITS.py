"""
Tips:
1. Значения полей элементов универсального списка из Битрикса возвращаются в виде словаря (ключ -
хз что значит, значение словаря - значение поля.

Надо сюда написать справочник по полям в списке
"""
from time import time
from time import asctime
from time import sleep
import dateutil.parser
from datetime import datetime
from datetime import timedelta

from fast_bitrix24 import Bitrix
import requests

from authentication import authentication

"""
Спас меня этот сайт
https://reqbin.com/req/o3vugw0p/post-json-string-with-basic-authentication
"""

# Считывание файла authentication.txt

b = Bitrix(authentication('Bitrix'))

# Получение массива сделок по фильтру

deals = b.get_all('crm.deal.list',
                  {
                      'select': ['COMPANY_ID'],
                  }
                  )
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

    print(response)
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
    element_type_fields = {
        'Кабинет сотрудника': '2187',
        'Автозаполнение реквизитов контрагентов ': '2191',
        'Досье контрагента': '2193',
        'РПД': '2189',
    }

    # Элементы списка "Отчет по сервисам" из Битрикса

    bitrix_elements = b.get_all('lists.element.get',
                                {
                                    'IBLOCK_TYPE_ID': 'lists',
                                    'IBLOCK_ID': '169'}
                                )

    current_date = datetime.now()

    for element in report['report']['entries']:

        for tariff in element['tariffs']:
            flag = False    # Флаг определяющий создание нового элемента списка или обновление существующего

            inn = ''
            if 'userOrganizationInn' in tariff:     # Если есть ИНН в элементе отчета, если нет - компания неопознана
                    inn = tariff['userOrganizationInn']     # ИНН компании из отчета
            else:
                else_flag = False
                # Поиск компании в элементах списка
                for elem in bitrix_elements:
                    if else_flag is True:
                        break
                    for value in elem['PROPERTY_1289'].values():
                        subscriber_code = value
                    if element['subscriberCode'] == subscriber_code:
                        for value in elem['PROPERTY_1283'].values():
                            company_id = value
                        inn = b.get_all('crm.company.list', {'select': ['UF_CRM_1656070716'], 'filter': {'ID': company_id}})[0]['UF_CRM_1656070716']
                        else_flag = True
                        break

            startDate = tariff['startDate']  # Дата начала из отчета
            startDate_formated = dateutil.parser.isoparse(startDate).strftime('%Y-%m-%d %H:%M:%S')

            # Поиск компании в Битриксе по ИНН из отчета
            if not inn:
                continue
            companies = b.get_all('crm.company.list',
                                      {
                                          'select': ['*', 'UF_*'],
                                          'filter': {'UF_CRM_1656070716': inn}
                                      }
                                  )

            # Перебор компаний, сделок, элементов списки

            for option in tariff['options']:

                test_option = '2245'
                test_option_str = 'Нет'
                if 'тестовый' in tariff['name']:
                    test_option_str = 'Да'
                    test_option = '2243'

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

                    element_responsible = company['ASSIGNED_BY_ID']

                    for deal in deals:

                        if company['ID'] == deal['COMPANY_ID']:     # Найдена сделка, принадлежащая компании

                            for bitrix_element in bitrix_elements:

                                for field_value in bitrix_element['PROPERTY_1287']:
                                    update_date = datetime.strptime(bitrix_element['PROPERTY_1287'][field_value], '%d.%m.%Y %H:%M:%S')
                                    if (current_date - update_date).days > 5:
                                        try:
                                            b.call('lists.element.delete', {
                                        'IBLOCK_TYPE_ID': 'lists',
                                        'IBLOCK_ID': '169',
                                        'ELEMENT_ID': bitrix_element['ID']
                                            }
                                    )
                                        except:
                                            pass


                                # Поля элемента списка в переменные

                                for field_value in bitrix_element['PROPERTY_1283']:

                                    # ID компании, привязанной к элементу списка

                                    element_company_id = bitrix_element['PROPERTY_1283'][field_value]

                                for field_value in bitrix_element['PROPERTY_1285']:

                                    # Дата начала сервиса из элемента списка

                                    element_startDate = bitrix_element['PROPERTY_1285'][field_value]

                                for field_value in bitrix_element['PROPERTY_1277']:

                                    # Максимальное значение из элемента списка

                                    element_maxVolume = bitrix_element['PROPERTY_1277'][field_value]

                                    # Код подписчика из элемента списка

                                for field_value in bitrix_element['PROPERTY_1289']:

                                    element_subscriberCode = bitrix_element['PROPERTY_1289'][field_value]

                                try:
                                    for field_value in bitrix_element['PROPERTY_1331']:

                                        # 95% задача

                                        task_95 = bitrix_element['PROPERTY_1331'][field_value]
                                except:
                                    task_95 = '2213'

                                subscriberCode = element['subscriberCode']

                                # Обновление элемента списка если найден соответствующий для компании

                                if element_company_id == company['ID'] and\
                                        element_startDate == startDate and\
                                         bitrix_element['NAME'] == name_element_type and\
                                        str(maxVolume) == str(element_maxVolume) and\
                                        subscriberCode == element_subscriberCode:


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
                                                       'PROPERTY_1285': startDate,
                                                       'PROPERTY_1289': subscriberCode,
                                                       'PROPERTY_1293': element_type_fields[name_element_type],
                                                       'PROPERTY_1331': task_95,
                                                       'PROPERTY_1347': startDate_formated,
                                                       'PROPERTY_1349': maxVolume,
                                                       'PROPERTY_1351': usedVolume,
                                                       'PROPERTY_1353': element_responsible,
                                                       'PROPERTY_1357': test_option,
                                                       'PROPERTY_1373': test_option
                                                   }
                                           }
                                           )

                                    # print(f'Обновлен элемент списка {name_element_type} {bitrix_element}')
                                    flag = True     # Найден элемент для обновления, новый создавать не нужно

                            if flag is False:   # Если не был найден элемент для обновления

                                # Создание элемента списка
                                new_element = b.call('lists.element.add',
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
                                                   'PROPERTY_1285': startDate,
                                                   'PROPERTY_1289': subscriberCode,
                                                   'PROPERTY_1293': element_type_fields[name_element_type],
                                                   'PROPERTY_1331': '2213',
                                                   'PROPERTY_1347': startDate_formated,
                                                   'PROPERTY_1349': maxVolume,
                                                   'PROPERTY_1351': usedVolume,
                                                   'PROPERTY_1353': element_responsible,
                                                   'PROPERTY_1357': test_option,
                                                   'PROPERTY_1373': '1'
                                               }
                                       }
                                       )
                                element_id = str(new_element)

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
    'DOCUMENT_RECOGNITION': [
            'РПД',
            'UC_GZFC63',
            'Распознавание первичных документов',
            [
                'Число страниц',
            ]
        ],
    'COUNTERAGENT': [
        'Контрагент', [
            'UC_A7G0AM',    # '1С Контрагент'
            'UC_HT9G9H',    # 'ПРОФ Земля'
            'UC_XIYCTV',    # 'ПРОФ Земля+Помощник'
            'UC_5T4MAW',    # 'ПРОФ Земля+Облако+Помощник'
            'UC_N113M9',    # 'ПРОФ Земля+Облако'
            'UC_ZKPT1B',    # 'ПРОФ Облако'
            'UC_2SJOEJ',    # 'ПРОФ Облако+Помощник'
            'UC_AVBW73',    # 'Базовый Земля'
            'UC_GPT391',    # 'Базовый Облако'
            'UC_81T8ZR',    # 'АОВ'
            'UC_SV60SP',    # 'АОВ+Облако'
            'UC_92H9MN',    # 'Индивидуальный'
            'UC_7V8HWF',    # 'Индивидуальный+Облако'
            'UC_1UPOTU',    # 'ИТС Бесплатный'
        ],
        'Контрагент',
        [
            'Автозаполнение реквизитов контрагентов ',
            'Досье контрагента',
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


if __name__ == '__main__':
    main()
