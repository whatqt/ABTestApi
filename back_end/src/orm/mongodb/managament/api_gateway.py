import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from mongodb.settings import client
from pymongo.errors import DuplicateKeyError
from pymongo.results import (
    BulkWriteResult,
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult,
)
from src.utils.logger import logger
from typing import Union



class Settings:
    '''Настройка колекции MongoDB. Класс ТОЛЬКО для наследования'''
    def __init__(self, id_user: str, main_api: str):
        '''
        Подключение к базе данных и создание
        коллекции.

        Params:
            id_user: id пользователя.
            main_api: url из которого будут приходить запросы на наши обработчики.
        '''
        self.db = client["abtestapi"]
        self.id_user = id_user
        self.collection = self.db[self.id_user]
        self.main_api = main_api
class ManageAPIGateway(Settings):
    '''CRUD операции над документами'''
    def __init__(self, id_user: str, main_api: str):
        super().__init__(
            id_user,
            main_api
        )
        
    async def create_data(
        self, 
        data: dict, 
    ) -> Union[InsertOneResult, None]:
        '''
        Создаёт документ.

        :param data: в data находится следующие ключи:
            main_api,
            first_api_percent,
            first_api_response,
            second_api_percent,
            second_api_response.
        :return InsertOneResult | None: если документ был успешно создан, 
        то результат будет InsertOneResult, иначе None.
        '''
        try:
            statistics = {
                #web
                "latency": None,
                #server
                "busyness_cpu": None,
                "memory_byte": None,
            }
            result = await self.collection.insert_one(
                {
                    "_id": data["main_api"],      # исправить и понять, 
                    "main_api": self.main_api,    # что лучше
                    "first_api_percent": data["first_api_percent"],
                    "first_api_response": data["first_api_response"],
                    "second_api_percent": data["second_api_percent"],
                    "second_api_response": data["second_api_response"],
                    "statistics_first_api": statistics,
                    "statistics_second_api": statistics
                }
            )
        except DuplicateKeyError:
            return None
        return result
    
    async def get_all_main_api(self) -> list[str]:
        '''
        Возвращает список со всеми main_api, которые есть в колекции пользователя.
        
        :return list[str]: список со всеми api
        '''
        results = self.collection.find()
        main_api_list = []
        async for result in results:
            main_api = result["_id"]
            main_api_list.append(main_api)
        return main_api_list

    async def get(self) -> dict:
        '''
        Получение одного документа по main_api.

        :return dict: документ
        '''
        result = await self.collection.find_one(
            {"_id": self.main_api}
        )
        return result
    
    async def delete(self) -> int:
        '''
        Удаление документа по main_api.

        :return int: сколько было удалено документов
        '''
        result = await self.collection.delete_one(
            {"_id": self.main_api},
        )
        return result.deleted_count 
        
    async def update(self, new_data: dict) -> Union[UpdateResult, None]:
        '''
        Обновление документа.
        
        :param new_data: словарь, с новымми данными.
            В нём обязательно должен быть ключ main_api, а остальные - нет.
            Пример ключей:
                first_api_percent,
                first_api_response,
                second_api_percent,
                second_api_response.
        :return UpdateResult | None: если были найдены старые данные, 
        то отдаёт UpdateResult, иначе None
        '''
        data_for_replace = await self.get()
        if not data_for_replace:
            return None
        for key in new_data.keys():
            data_for_replace[key] = new_data[key]

        result = await self.collection.update_one(
            {"_id": self.main_api},
            {"$set": data_for_replace}
        )
        return result
    
class SaveStatistics(Settings):
    '''Сохранение статистики в документы'''
    def __init__(self, id_user: str, main_api: str):
        super().__init__(
            id_user,
            main_api
        )

    async def __abstract_save_statistic(
        self, 
        response_url: str,
        value: Union[None,int], 
        type_stat: str
    ) -> bool:
        '''
        Абстрактный метод сохранения. 
        Предназначен ТОЛЬКО использование в самом классе.
        
        Сохраняет статистику в документ, в нужный объект (словарь), 
        который определяется при помощи response_url 
        (statistics_first_reponse или statistics_second_response.). 
        
        Params:
            response_url: Url, на который пришёл ответ.
            value: Значение которое будет сохранено.
            type_stat: Тип статистики. Определяет, 
                в какой ключ будет сохранено значение.
        
        :return bool: Возвращает True, 
        если статистика была сохранена, иначе False.
        
        '''
        filter_ = {"_id": self.main_api}
        data: dict = await self.collection.find_one(
            filter_
        )
        first_api_response = data["first_api_response"]
        name_statistics = None
        if first_api_response == response_url:
            statistics: dict = data["statistics_first_api"]
            name_statistics = "statistics_first_api"
        else:
            statistics: dict = data["statistics_second_api"]
            name_statistics = "statistics_second_api"

        statistics[type_stat] = value
        new_data = data.copy()
        new_data[name_statistics] = statistics
        result = await self.collection.update_one(
            filter_,
            {"$set": new_data}
        )
        # изменить на результат result.modified_count и так же
        # изменить результат функции в документации
        return True  
    
    async def save_time_request(
        self, 
        time_: str,
        response_url: str,
        _type_stat: str = "latency"
    ) -> bool:  
        '''
        Сохраняет время запроса.
        
        Params:
            time_: Время запроса.
            response_url: Какой url обработал.
            _type_stat: атрибут,который НЕ ДОЛЖЕН изменяться.
                определяет тип статистики в колекции. 
                По умолчанию - latency.

        :return bool: Возвращает True, 
        если статистика была сохранена, иначе False.
        '''
        result = await self.__abstract_save_statistic(
            response_url,
            time_,
            _type_stat
        )
        return result

    async def save_memory(
        self,
        value,
        response_url,
        _type_stat: str = "memory_byte"
    ):
        '''
        Сохраняет память в байтах, затраченного во время запроса.
        
        Params:
            value: Память.
            response_url: Какой url обработал.
            _type_stat: атрибут,который НЕ ДОЛЖЕН изменяться.
                определяет тип статистики в колекции. 
                По умолчанию - memory_byte.

        :return bool: Возвращает True, 
        если статистика была сохранена, иначе False.
        '''
        result = await self.__abstract_save_statistic(
            response_url,
            value,
            _type_stat
        )
        return result
    
    async def save_busyness_cpu(
        self,
        value,
        response_url,
        _type_stat: str = "busyness_cpu"
    ):
        '''
        Сохраняет значение процесса во время запроса.
        
        Params:
            value: Значение процесса.
            response_url: Какой url обработал.
            _type_stat: атрибут,который НЕ ДОЛЖЕН изменяться.
                определяет тип статистики в колекции. 
                По умолчанию - busyness_cpu.

        :return bool: Возвращает True, 
        если статистика была сохранена, иначе False.
        '''
        result = await self.__abstract_save_statistic(
            response_url,
            value,
            _type_stat
        )
        return result
