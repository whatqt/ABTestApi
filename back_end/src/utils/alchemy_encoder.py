from utils.logger import logger
from sqlalchemy.ext.declarative import DeclarativeMeta
import json



class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        fields = {}
        for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and x != "registry"]:
            data = obj.__getattribute__(field)
            try:
                fields[field] = data
            except TypeError:
                logger.debug(f"Ошибка у поля {field}")
                fields[field] = None
        return fields

