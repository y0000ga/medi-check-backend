from enum import StrEnum


class DosageForm(StrEnum):
    tablet = "tablet"                         # 錠劑
    capsule = "capsule"                       # 膠囊
    softgel = "softgel"                       # 軟膠囊
    pill = "pill"                             # 藥丸，泛稱

    liquid = "liquid"                         # 液體
    syrup = "syrup"                           # 糖漿
    suspension = "suspension"                 # 懸浮液
    drops = "drops"                           # 滴劑

    powder = "powder"                         # 粉末
    granule = "granule"                       # 顆粒
    sachet = "sachet"                         # 藥包 / 小包裝粉劑

    injection = "injection"                   # 注射劑
    vial = "vial"                             # 小瓶針劑
    ampoule = "ampoule"                       # 安瓿

    inhaler = "inhaler"                       # 吸入劑
    spray = "spray"                           # 噴劑
    nebulizer_solution = "nebulizer_solution" # 霧化液

    cream = "cream"                           # 乳膏
    ointment = "ointment"                     # 軟膏
    gel = "gel"                               # 凝膠
    lotion = "lotion"                         # 乳液

    patch = "patch"                           # 貼片
    suppository = "suppository"               # 栓劑
    eye_drops = "eye_drops"                   # 眼藥水
    ear_drops = "ear_drops"                   # 耳滴劑
    nasal_spray = "nasal_spray"               # 鼻噴劑

    other = "other"                           # 其他
