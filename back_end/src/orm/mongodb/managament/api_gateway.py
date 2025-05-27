import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from mongodb.settings import client
from pymongo.errors import DuplicateKeyError
from src.utils.logger import logger



class Settings:
    def __init__(self, id_user: str):
        self.db = client["abtestapi"]
        self.id_user = id_user
        self.collection = self.db[self.id_user]

class ManageAPIGateway(Settings):
    def __init__(self, id_user: str):
        super().__init__(id_user)
        
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
                "memory": None,
                "i/o": None,
            }
            result = await self.collection.insert_one(
                {
                    "_id": data["main_api"],
                    "main_api": data["main_api"],
                    "first_api_percent": data["first_api_percent"],
                    "first_api_response": data["first_api_response"],
                    "second_api_percent": data["second_api_percent"],
                    "second_api_response": data["second_api_response"],
                    "successful_logins": None,
                    "unsuccessful_logins": None,
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

    async def get(self, main_api: str) -> dict:
        result = await self.collection.find_one(
            {"_id": main_api}
        )
        return result
    
class SaveCollections(Settings):
    def __init__(self, id_user: str):
        super().__init__(id_user)

    async def save_time_request(
        self, 
        main_api: str, 
        time_: str,
        response_url: str
    ):
        filter_ = {"_id": main_api}
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
        statistics["latency"] = time_
        new_data = data.copy()
        new_data[name_statistics] = statistics
        await self.collection.update_one(
            filter_,
            {"$set": new_data}
        )
        return True
