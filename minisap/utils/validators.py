def required(value, field_name: str):
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} es obligatorio")


def non_negative(value, field_name: str):
    try:
        num = float(value)
    except Exception as exc:
        raise ValueError(f"{field_name} debe ser numérico") from exc
    if num < 0:
        raise ValueError(f"{field_name} no puede ser negativo")
    return num


def parse_int(value, field_name: str):
    try:
        return int(value)
    except Exception as exc:
        raise ValueError(f"{field_name} debe ser entero") from exc
