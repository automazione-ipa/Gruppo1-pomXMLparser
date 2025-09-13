# logger.py
import logging
import json
from .pydantic_utils import to_serializable_v2

def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    def safe_info(obj, **kwargs):
        """Serializza Pydantic e dict per logging leggibile."""
        try:
            msg = json.dumps(to_serializable_v2(obj), ensure_ascii=False, **kwargs)
        except Exception:
            msg = str(obj)
        logger.info(msg)

    logger.safe_info = safe_info
    return logger
