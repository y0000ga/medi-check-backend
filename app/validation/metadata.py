from app.validation.rules import (
    AVATAR_URL_RULE,
    MEDICATION_NAME_RULE,
    MEMO_RULE,
    NAME_RULE,
    PASSWORD_RULE,
)


KEY_MAPPING = {
    "min_length": "minLength",
    "max_length": "maxLength",
    "allow_whitespace": "allowWhitespace",
    "error_key": "errorKey",
}


def to_public_rule(rule: dict) -> dict:
    result = {}

    for key, value in rule.items():
        if key == "public":
            continue

        new_key = KEY_MAPPING.get(key, key)

        if isinstance(value, list):
            result[new_key] = [
                {
                    KEY_MAPPING.get(item_key, item_key): item_value
                    for item_key, item_value in item.items()
                }
                for item in value
            ]
        else:
            result[new_key] = value

    return result


def get_validation_metadata():
    return {
        "version": "2026-04-24",
        "rules": {
            "name": to_public_rule(NAME_RULE),
            "password": to_public_rule(PASSWORD_RULE),
            "avatar_url": to_public_rule(AVATAR_URL_RULE),
            "medication_name": to_public_rule(MEDICATION_NAME_RULE),
            "note": to_public_rule(MEMO_RULE),
        },
    }
