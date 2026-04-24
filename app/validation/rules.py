PASSWORD_RULE = {
    "type": "string",
    "required": True,
    "min_length": 6,
    "max_length": 18,
    "allow_whitespace": False,
    "allowed_chars_pattern": r"^[A-Za-z0-9!@#$%^&*]+$",
    "rules": [
        {
            "name": "hasUppercase",
            "pattern": r"[A-Z]",
            "error_key": "auth.password.requireUppercase",
        },
        {
            "name": "hasSpecialChar",
            "pattern": r"[!@#$%^&*]",
            "error_key": "auth.password.requireSpecialChar",
        },
    ],
}

NAME_RULE = {
    "type": "string",
    "required": True,
    "min_length": 1,
    "max_length": 100,
    "trim": True,
    "public": True,
}

EMAIL_RULE = {
    "type": "string",
    "required": True,
    "max_length": 255,
    "format": "email",
    "trim": True,
    "public": True,
}

AVATAR_URL_RULE = {
    "type": "string",
    "required": False,
    "min_length": 1,
    "max_length": 500,
    "format": "url",
    "trim": True,
    "public": True,
}

PASSWORD_HASH_RULE = {
    "type": "string",
    "required": True,
    "max_length": 255,
    "public": False,
}

REFRESH_TOKEN_HASH_RULE = {
    "type": "string",
    "required": True,
    "max_length": 255,
    "public": False,
}

MEDICATION_NAME_RULE = {
    "type": "string",
    "required": True,
    "min_length": 1,
    "max_length": 100,
    "trim": True,
    "public": True,
}

MEMO_RULE = {
    "type": "string",
    "required": False,
    "min_length": 0,
    "max_length": 500,
    "trim": True,
    "public": True,
}

IP_ADDRESS_RULE = {
    "type": "string",
    "required": False,
    "max_length": 45,
    "public": False,
}

USER_AGENT_RULE = {
    "type": "string",
    "required": False,
    "max_length": 255,
    "public": False,
}
