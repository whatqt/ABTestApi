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


    async def insert_data(self, data: dict):
        try:
            result = await self.collection.insert_one(
                {
                    "_id": data["main_api"],
                    "data": {
                        "first_api": data["first_api"],
                        "second_api": data["second_api"],
                        "first_api_percent": data["first_api_percent"],
                        "second_api_percent": data["second_api_percent"],
                    }
                }
            )
        except DuplicateKeyError:
            return None
        return result
    
    async def get(self, main_api: str = None):
        if not main_api:
            results = self.collection.find()
            objects = []
            async for result in results:
                objects.append(result)
            return objects
        result = await self.collection.find_one(
            {"_id": main_api}
        )
        return result