from enum import StrEnum


class HistoryStatus(StrEnum):
    pending = "pending"
    taken = "taken"
    missed = "missed"


class HistorySource(StrEnum):
    manual = "manual" # 手動補登的可能性
    quickCheck = "quickCheck" #使用者自己點的
    system = "system" # 通常是系統自動判定沒吃，因為使用者沒點
