from enum import StrEnum


class DosageUnit(StrEnum):
    Mg = "mg"
    Ml = "ml"
    Tablet = "tablet"
    Capsule = "capsule"
    Package = "package"
    Drop = "drop"


class FrequencyUnit(StrEnum):
    day = "day"
    week = "week"
    month = "month"
    year = "year"


class EndType(StrEnum):
    never = "never"
    until = "until"
    counts = "counts"
