stage_ids = {
    'C1:NEW': 'Услуга активна',
    'C1:UC_0KJKTY': 'Счет сформирован',
    'C1:UC_3J0IH6': 'Счет отправлен клиенту',
    'C1:UC_KZSOR2':  'Нет оплаты',
    'C1:UC_VQ5HJD':  'Ждём решения клиента',
    'C1:WON':  'Услуга завершена',
    'C1:LOSE': 'Отказ от сопровождения',
    'C9:NEW': 'Новые заявки',
    'C9:UC_ZZKRJ6': 'Требования определены',
    'C9:UC_4FV40W': 'КП выставлено',
    'C9:UC_O6PQB3': 'Защита КП',
    'C9:PREPARATION': 'Выставлен счет',
    'C9:FINAL_INVOICE': 'Оплата получена',
    'C9:WON': 'Сделка закрыта',
    'C9:LOSE': 'Отказ',
    'DT133_3:NEW': 'Продажа состоялась',
    'DT133_3:PREPARATION': 'Отправлено сотруднику',
    'DT133_3:SUCCESS': 'Успех',
    'DT133_3:FAIL': 'Провал',
    'DT186_9:NEW': 'Досье сформировано',
    'DT186_9:UC_0H816O': 'Проведено первое знакомство',
    'DT186_9:PREPARATION': 'Онбординг',
    'DT186_9:CLIENT': 'Согласование',
    'DT186_9:SUCCESS': 'Договор продлен на платный',
    'DT186_9:FAIL': 'Отказ от сопровождения',
    'DT186_21:NEW': 'Досье сформировано',
    'DT186_21:SUCCESS': 'Успех',
    'DT186_21:FAIL': 'Провал',
}

category_types = {
    'UC_HT9G9H': 'ПРОФ Земля',
    'UC_XIYCTV': 'ПРОФ Земля+Помощник',
    'UC_N113M9': 'ПРОФ Земля+Облако',
    'UC_5T4MAW': 'ПРОФ Земля+Облако+Помощник',
    'UC_ZKPT1B': 'ПРОФ Облако',
    'UC_2SJOEJ': 'ПРОФ Облако+Помощник',
    'UC_81T8ZR': 'АОВ',
    'UC_SV60SP': 'АОВ+Облако',
    'UC_92H9MN': 'Индивидуальный',
    'UC_7V8HWF': 'Индивидуальный+Облако',
    'UC_34QFP9': 'Уникс',
    'UC_AVBW73': 'Базовый Земля',
    'UC_GPT391': 'Базовый Облако',
    'UC_1UPOTU': 'ИТС Бесплатный',
    'UC_K9QJDV': 'ГРМ Бизнес',
    'GOODS': 'ГРМ',
    'UC_J426ZW': 'Садовод',
    'UC_DBLSP5': 'Садовод+Помощник',
    'UC_IUJR81': 'Допы Облако',
    'UC_USDKKM': 'Медицина',
    'UC_BZYY0D': 'ИТС Отраслевой',
    'UC_2R01AE': 'Услуги (без нашего ИТС)',
    'UC_IV3HX1': 'Тестовый',
    'UC_YIAJC8': 'Лицензия с купоном ИТС',
    'UC_QQPYF0': 'Лицензия',
    'UC_O99QUW': 'Отчетность',
    'UC_OV4T7K': 'Отчетность (в рамках ИТС)',
    'UC_2B0CK2': '1Спарк в договоре',
    'UC_86JXH1': '1Спарк 3000',
    'UC_WUGAZ7': '1СпаркПЛЮС 22500',
    'UC_A7G0AM': 'Контрагент',
    'UC_GZFC63': 'РПД',
    'UC_8Z4N1O': 'Подпись',
    'UC_FOKY52': 'Подпись 1000',
    'UC_D1DN7U': 'Кабинет сотрудника',
    'UC_H8S037': 'ЭДО',
    'UC_66Z1ZF': 'ОФД',
    'UC_40Q6MC': 'СтартЭДО',
    'UC_8LW09Y': 'МДЛП',
    'UC_3SKJ5M': '1С Касса',
    'UC_4B5UQD': 'ЭТП',
    'UC_H7HOD0': 'Коннект',
    'UC_XJFZN4': 'Кабинет садовода',
    'UC_74DPBQ': 'БИТРИКС24',
    'UC_6TCS2E': 'Линк',
    '1': 'Не указан',
    'UC_D7TC4I': 'ГРМ Спец',
    'UC_GP5FR3': 'ДУО',
    '': '',
    '2': 'Контрагент (в договоре)',
    'UC_5EMX7G': 'Заявка на продажу',
    'UC_4N16O3': 'Работа с РПД',
    'CLIENT': 'Клиенты',
    None: '',
    'UC_FPWC96': 'Потенциальный',
    'PARTNER': 'Партнеры',
    'OTHER': 'Другое',
    'UC_45UGHN': 'НЕ ПРИВЯЗАН К КОМПАНИЯМ',
    'SUPPLIER': 'Поставщики',
    'CUSTOMER': 'Клиент',
    'UC_RTNQP4': 'Потенциальный',
    'UC_E99TUC': 'ЗАКОНЧИЛСЯ ИТС!',
    'UC_5SE8LU': 'Не наш по ИТС, работаем',
    'UC_8TI0LB': 'Ликвидированы',
    'COMPETITOR': 'Конкурент',
    'UC_74XO1E': 'ТОКСИЧНЫЙ',
    'UC_R1P5S5': 'Передали ИТС',
    'UC_LAMPV8': 'Автосервис',
    'UC_AD0LKE': 'Автошкола',
    'UC_5S2HWI': 'Архитектура, ремонт, проектирование',
    'BANKING': 'Банковские услуги',
    'UC_Y3YXRX': 'Деятельность больничных организаций',
    'DELIVERY': 'Доставка',
    'IT': 'Информационные технологии',
    'UC_0KN4CO': 'Клининговые услуги',
    'UC_CQUTRO': 'Коммунальное хозяйство',
    'CONSULTING': 'Консалтинг',
    'UC_EBNP1F': 'Медицинские услуги',
    'NOTPROFIT': 'Не для получения прибыли / Некоммерческая',
    'UC_73VO74': 'Образование',
    'UC_3IZ9UL': 'Оптовая торговля',
    'UC_MU2KNL': 'Охранное предприятие',
    'UC_P75AJE': 'Пекарня по франшизе',
    'UC_F3W4NO': 'Перевозка пассажиров',
    'UC_9L5V4I': 'Полиграфия',
    'GOVERNMENT': 'Правительство',
    'MANUFACTURING': 'Производство',
    'ENTERTAINMENT': 'Развлечения',
    'UC_18OE00': 'Рекламная деятельность',
    'UC_5WL2K7': 'Розничная торговля',
    'UC_R281QA': 'Сбор отходов',
    'UC_QPG2P1': 'Сдача недвижимости в аренду',
    'UC_ZS5TWZ': 'Складская логистика',
    'UC_FDCQBQ': 'Страхование',
    'UC_N5REPZ': 'Строительство канализационных сетей',
    'TELECOM': 'Телекоммуникации и связь',
    'UC_9PE24R': 'Транспортная логистика',
    'UC_IJWNV6': 'Услуги',
    'FINANCE': 'Финансы',
    'UC_7X31NV': 'Деятельность гостиниц и прочих мест для временного проживания',
    'UC_9ILKE9': 'Строительно-монтажные работы и строительство',
    'UC_H7N068': 'Сельское хозяйство',
    'UC_VN6ZAQ': 'Аренда',
    'UC_A44OO9': 'НИОКР',
    'UC_Q79LN1': 'Бухгалтерский учет и аудит',
    'UC_38DI8T': 'Общепит, рестораны, кафе',
    'UC_RDLPYP': 'Спортивные организации',
    'EMPLOYEES_1': '1-5',
    'EMPLOYEES_2': '6-20',
    'EMPLOYEES_3': '21-50',
    'EMPLOYEES_4': '51-100',
    'UC_RLD5AE': '101-300',
    'UC_XDBM0O': '301-1000',
    'UC_Q73AXJ': 'свыше 1000',
    '3': 'mag1c',
    '4': '1С-Администратор'
}


UF_CRM_1657878818384_values = {
    '859': 'ИТС',
    '903': 'Товар',
    '905': 'Отчетность',
    '907': 'Сервисы ИТС',
    None: '',
}

departments_id_name = {
    '29': 'ГО4',
    '27': 'ГО3',
    '5': 'ЦС',
    '1': '4DK',
    '231': 'ЛК',
    '235': 'Битрикс',
    '237': 'Интеграторы',
    '233': 'Служебные',
    '361': 'ОВ (РСС)',
    '225': 'ОВ',
    '363': 'Отдел развития',
}

month_int_names = {
        1: 'Январь',
        2: 'Февраль',
        3: 'Март',
        4: 'Апрель',
        5: 'Май',
        6: 'Июнь',
        7: 'Июль',
        8: 'Август',
        9: 'Сентябрь',
        10: 'Октябрь',
        11: 'Ноябрь',
        12: 'Декабрь',
    }