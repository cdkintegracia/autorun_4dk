from fast_bitrix24 import Bitrix
from datetime import datetime
from datetime import timedelta

b = Bitrix('https://vc4dk.bitrix24.ru/rest/311/wkq0a0mvsvfmoseo/')

bitrix_elements = b.get_all('lists.element.get',
                                {
                                    'IBLOCK_TYPE_ID': 'lists',
                                    'IBLOCK_ID': '169',
                                    'ELEMENT_ID': '136571'
                                    }
                                )

print(bitrix_elements)