from enum import StrEnum


class DosageUnit(StrEnum):
    # Mass
    mcg = "mcg"                         # 微克
    mg = "mg"                           # 毫克
    g = "g"                             # 公克

    # Volume
    ml = "ml"                           # 毫升
    l = "l"                             # 公升
    drop = "drop"                       # 滴

    # Count / solid dosage
    tablet = "tablet"                   # 錠
    capsule = "capsule"                 # 顆膠囊
    pill = "pill"                       # 顆
    packet = "packet"                   # 包
    sachet = "sachet"                   # 小包
    piece = "piece"                     # 個 / 片 / 泛用計數

    # Application
    spray = "spray"                     # 噴
    puff = "puff"                       # 吸 / puff
    patch = "patch"                     # 片貼片
    application = "application"         # 次塗抹
    suppository = "suppository"         # 顆栓劑

    # Liquid household / medicine cup
    tsp = "tsp"                         # 茶匙
    tbsp = "tbsp"                       # 湯匙
    cup = "cup"                         # 杯

    # Medical / concentration-related
    unit = "unit"                       # 單位，例如 insulin unit
    iu = "iu"                           # International Unit
    meq = "meq"                         # 毫當量
    percent = "percent"                 # 百分比濃度

    other = "other"


class FrequencyUnit(StrEnum):
    day = "day"
    week = "week"
    month = "month"
    year = "year"


class EndType(StrEnum):
    never = "never"
    until = "until"
    counts = "counts"
