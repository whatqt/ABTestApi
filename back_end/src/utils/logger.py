import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import logging
from logging.handlers import RotatingFileHandler



def setup_logger() -> logging.Logger:
    '''
    Перехватывает логер uvicorn и изменяем настройки, а именно:
    добавление уровня DEBUG в консоль,
    записывание логов от уровня INFO в файл

    :return: logger
    '''
    
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