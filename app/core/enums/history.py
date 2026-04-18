from enum import StrEnum


class HistoryStatus(StrEnum):
    pending = "pending"
    taken = "taken"
    missed = "missed"


class HistorySource(StrEnum):
    manual = "manual"
    quickCheck = "quickCheck"
    system = "system"
