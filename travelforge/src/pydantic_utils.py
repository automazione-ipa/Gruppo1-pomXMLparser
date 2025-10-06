# pydantic_utils.py
import json
from typing import Any, Type
from pydantic import ValidationError

def to_serializable_v2(obj: Any) -> Any:
    """Converte oggetti Pydantic v2 (o altri) in strutture serializzabili da json.dumps."""
    if obj is None:
        return None

    if isinstance(obj, (dict, list, str, int, float, bool)):
        if isinstance(obj, str):
            try:
                return json.loads(obj)
            except Exception:
                return obj
        return obj

    # Pydantic v2
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()
        except Exception:
            pass

    if hasattr(obj, "model_dump_json"):
        try:
            return json.loads(obj.model_dump_json())
        except Exception:
            pass

    if hasattr(obj, "__dict__"):
        try:
            return obj.__dict__
        except Exception:
            pass

    return str(obj)


def to_pydantic_v2(cls: Type, data: Any):
    """
    Converte `data` in un'istanza Pydantic v2 di tipo `cls` usando model_validate.
    Solleva ValidationError in caso di problemi.
    """
    if data is None:
        return None

    # se è già istanza
    try:
        if isinstance(data, cls):
            return data
    except Exception:
        pass

    # se è stringa JSON, proviamo a decodificarla
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            pass

    # model_validate è la API v2
    try:
        return cls.model_validate(data)
    except ValidationError:
        raise
    except Exception as e:
        # incapsula in ValidationError-like per uniformità
        raise ValidationError(e)
