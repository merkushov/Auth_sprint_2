import orjson as orjson
from pydantic import BaseModel
from pydantic.main import Any, validate_model


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class BaseServiceModel(BaseModel):
    """Базовая модель для всех API моделей."""

    def __init__(__pydantic_self__, **data: Any) -> None:
        # Перехватываю исключения pydantic, чтобы подсунуть свои,
        # в случае необходимости
        if hasattr(__pydantic_self__.Config, "custom_exception"):
            values, fields_set, validation_error = validate_model(
                __pydantic_self__.__class__, data
            )

            custom_errors = list()
            if validation_error:
                errors = validation_error.errors()
                for error in errors:
                    custom_errors.append(
                        "'{field}' - {message}".format(
                            field=error.get("loc")[0], message=error.get("msg")
                        )
                    )
                raise __pydantic_self__.Config.custom_exception(
                    detail="; ".join(custom_errors)
                )

        super().__init__(**data)

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
