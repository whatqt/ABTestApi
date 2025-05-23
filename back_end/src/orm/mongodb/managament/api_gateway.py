import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from mongodb.settings import client
from pymongo.errors import DuplicateKeyError
from src.utils.logger import logger


class ManageAPIGateway:
    def __init__(self, id_user: str):
        self.db = client["abtestapi"]
        self.id_user = id_user
        self.collection = self.db[self.id_user]

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
    
    async def increase_logins(
            self, 
            main_api: str,
            _type: str,
            
        ) -> None:
        '''
        сделать документацию
        '''
        if _type not in ("successful_logins", "unsuccessful_logins"):
            raise ValueError("_type должен быть successful_logins или unsuccessful_logins")
        data = await self.collection.find_one(
            {"_id": main_api}
        )
        old_value = data[_type]
        if old_value is None:
            old_value = 0

        new_value = old_value + 1
        result = await self.collection.update_one(
            {"_id": main_api},
            {"$set": {_type: new_value}}
        )
        logger.debug(result)
        return result