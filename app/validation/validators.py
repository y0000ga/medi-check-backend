import re

def validate_by_rule(value: str, rule: dict) -> str:
    if rule.get("required") and not value:
        raise ValueError("required")

    min_length = rule.get("min_length")
    if min_length and len(value) < min_length:
        raise ValueError("minLength")

    max_length = rule.get("max_length")
    if max_length and len(value) > max_length:
        raise ValueError("maxLength")

    if rule.get("allow_whitespace") is False and re.search(r"\s", value):
        raise ValueError("noWhitespace")

    allowed_chars_pattern = rule.get("allowed_chars_pattern")
    if allowed_chars_pattern and not re.match(allowed_chars_pattern, value):
        raise ValueError("invalidCharacter")

    for item in rule.get("rules", []):
        if not re.search(item["pattern"], value):
            raise ValueError(item["error_key"])

    return value
