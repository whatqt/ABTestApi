import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from mongodb.settings import client
from pymongo.errors import DuplicateKeyError



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
                "rps": None,
                "latency": None,
                #server
                "busyness_cpu": None,
                "memory": None,
                "i/o": None,
                #security
                "vulnerabilities": None,
                "successful_logins": None,
                "unsuccessful_logins": None
            }
            result = await self.collection.insert_one(
                {
                    "_id": data["main_api"],
                    "main_api": data["main_api"],
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

    async def get(self, main_api: str) -> dict:
        result = await self.collection.find_one(
            {"_id": main_api}
        )
        return result