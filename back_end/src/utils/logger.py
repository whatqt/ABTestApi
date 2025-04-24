import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import logging
from logging.handlers import RotatingFileHandler



# def setup_logger(name: str = 'back_end') -> logging.Logger:
#     """
#     Настройка логгера с ротацией файлов.
    
#     :param name: имя логгера
#     :return: Настроенный экземпляр логгера
#     """

#     log_dir = Path('logs')
#     log_dir.mkdir(exist_ok=True)
    
#     # logger = logging.getLogger(name)
#     logger = logging.getLogger(name)
#     logger.setLevel(logging.DEBUG)
    
#     formatter = logging.Formatter(
#         '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         datefmt='%Y-%m-%d %H:%M:%S'
#     )
    
#     file_handler = RotatingFileHandler(
#         filename=log_dir / f'{name}.log',
#         maxBytes=300 * 1024 * 1024,  # 300 МБ
#         backupCount=2,
#         encoding='utf-8'
#     )
#     file_handler.setFormatter(formatter)
#     file_handler.setLevel(logging.INFO)
    
#     console_handler = logging.StreamHandler()
#     console_handler.setFormatter(formatter)
#     console_handler.setLevel(logging.DEBUG)
    
#     logger.addHandler(file_handler)
#     logger.addHandler(console_handler)
    
#     return logger

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("uvicorn.error")  # Используем Uvicorn-логгер
    logger.setLevel(logging.DEBUG)
    
    # файловый логгер
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler = RotatingFileHandler(
        filename=log_dir / f'back_end.log',
        maxBytes=300 * 1024 * 1024,  # 300 МБ
        backupCount=2,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)    
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()