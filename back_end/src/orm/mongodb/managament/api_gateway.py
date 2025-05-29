import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from mongodb.settings import client
from pymongo.errors import DuplicateKeyError
from src.utils.logger import logger
from typing import Union


class Settings:
    '''Настройка колекции mongoDB. Класс ТОЛЬКО для наследования'''
    def __init__(self, id_user: str, main_api: str):
        self.db = client["abtestapi"]
        self.id_user = id_user
        self.collection = self.db[self.id_user]
        self.main_api = main_api

class ManageAPIGateway(Settings):
    '''
    Управляет базой данных для Mon
    '''
    def __init__(self, id_user: str, main_api: str):
        super().__init__(
            id_user,
            main_api
        )
        
    async def create_data(
        self, 
        data: dict, 
    ):
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
    
    async def get_all_main_api(self):
        results = self.collection.find()
        main_api_list = []
        async for result in results:
            main_api = result["_id"]
            main_api_list.append(main_api)
        return main_api_list

    async def get(self) -> dict:
        result = await self.collection.find_one(
            {"_id": self.main_api}
        )
        return result
    
    async def delete(self) -> int:
        result = await self.collection.delete_one(
            {"_id": self.main_api},
        )
        return result.deleted_count 
        
    async def update(self, new_data: dict) -> Union[dict, None]:
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
    def __init__(self, id_user: str, main_api: str):
        super().__init__(
            id_user,
            main_api
        )


    async def __abstract_save_statistic(
        self, response_url: str,
        value, type_stat
    ):
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
        await self.collection.update_one(
            filter_,
            {"$set": new_data}
        )
        return True
    
    async def save_time_request(
        self, 
        time_: str,
        response_url: str,
        _type_stat: str = "latency"
    ):  
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
        _type_stat: str = "memory"
    ):
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
        result = await self.__abstract_save_statistic(
            response_url,
            value,
            _type_stat
        )
        return result