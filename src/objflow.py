import bpy
import os
from . import addon
from . import byaml

_objflow = None
_id_dict = {}
_label_dict = {}
_label_items = []


def get_label_items(self, context):
    # Returns the list of all textual labels, in a tuple to be used by a Blender search operator.
    _ensure_loaded()
    return _label_items


def get_obj_by_label(label):
    # Returns the Obj definition for the given unique textual label, case-insensitive.
    _ensure_loaded()
    return _label_dict.get(label.lower())


def get_obj_by_id(obj_id):
    # Returns the Obj definition for the given Obj ID.
    _ensure_loaded()
    return _id_dict.get(obj_id)


def get_res_names_by_id(obj_id):
    # Returns the ResName's which need to be loaded by the game to use this object.
    _ensure_loaded()
    objflow_entry = _id_dict.get(obj_id)
    return objflow_entry["ResName"] if objflow_entry else []


_param_names = {  # Tuples must have a length of 8: Either document an object fully or let it.
    1003: (None, None, None, None, None, None, None, None),  # Choropoo
    1004: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # Frogoon
    1005: (None, None, None, None, None, None, None, None),  # PylonB
    1006: ("Initial Delay", "Life Time", "Delay", "Unknown 4", None, None, None, None),  # PackunMusic
    1007: ("Unknown 1", None, None, None, None, None, None, None),  # KuriboBoard
    1008: (None, None, None, None, None, None, None, None),  # DKBarrel
    1009: (None, None, None, None, None, None, None, None),  # PylonY
    1010: (None, None, None, None, None, None, None, None),  # DdQuicksand
    1011: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # Kuribo
    1012: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # Sanbo
    1013: (None, None, None, None, None, None, None, None),  # ItemBox
    1014: ("Initial Delay", "Slam Delay", "Unknown 3", None, None, None, None, None),  # Dossun
    1015: (None, None, None, None, None, None, None, None),  # Crab
    1016: (None, None, None, None, None, None, None, None),  # SnowRock
    1017: (None, None, None, None, None, None, None, None),  # BushBoard
    1018: ("Unknown 1", None, None, "Unknown 4", None, None, None, None),  # Coin
    1019: (None, None, None, None, None, None, None, None),  # Dokan1
    1021: ("Unknown 1", "Unknown 2", "# Bats", "Unknown 4", "Unknown 5", None, None, None),  # Basabasa
    1022: (None, None, None, None, None, None, None, None),  # Barrel
    1023: (None, None, None, None, None, None, None, None),  # CrashBox
    1024: (None, None, None, None, None, None, None, None),  # PylonR
    1025: ("Unknown 1", "Unknown 2", "Unknown 3", None, "Unknown 5", None, None, None),  # Pukupuku
    1026: (None, None, None, None, None, None, None, None),  # TikiTak
    1027: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # PackunFlower
    1028: (None, None, None, None, None, None, None, None),  # PuchiPackun
    1029: (None, None, None, None, None, None, None, None),  # SkateHeyhoR
    1030: (None, None, None, None, None, None, None, None),  # Note
    1031: (None, None, "# Shy Guys", "Unknown 4", "Unknown 5", None, None, None),  # SkateHeyhoB
    1032: (None, None, None, None, None, None, None, None),  # SnowMan
    1033: (None, "Unknown 2", None, None, None, None, None, None),  # MovingCoin
    1034: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # MovingItemBox
    1035: (None, None, None, None, None, None, None, None),  # Oil
    1036: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # PcBalloon
    1037: (None, None, None, None, None, None, None, None),  # N64YoshiEgg
    1039: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # Bird
    1040: ("# Goombas (max 100?)", "Unknown 2", None, None, None, None, None, None),  # TowerKuribo
    1041: ("? (3/4 seen)", None, None, None, None, None, None, None),  # Cow
    1042: (None, None, "Unknown 3", "Unknown 4", "Unknown 5", None, None, None),  # FishBone
    1043: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # Teresa
    1044: ("Unknown 1", None, None, None, None, None, None, None),  # CmnToad
    1055: ("Unknown 1", None, None, None, None, None, None, None),  # RelayCar
    1056: (None, None, None, None, None, None, None, None),  # Seagull
    1057: (None, None, None, None, None, None, None, None),  # ExTram
    1058: (None, None, None, None, None, None, None, None),  # GingerBread
    1059: (None, None, None, None, None, None, None, None),  # CakePylonB
    1060: (None, None, None, None, None, None, None, None),  # CakePylonA
    1063: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # ShyguyWatchman
    1064: ("Unknown 1", None, None, None, None, None, None, None),  # ShyguyPickax
    1066: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # PackunFlower2
    1067: ("Initial Delay", None, None, None, None, None, None, None),  # HhStatue
    1068: (None, None, None, None, None, None, None, None),  # CakeBalloon
    1070: (None, None, None, None, None, None, None, None),  # Karon
    1071: (None, None, None, None, None, None, None, None),  # PylonTechno
    1072: (None, None, None, None, None, None, None, None),  # DokanTechno
    1073: (None, None, None, None, None, None, None, None),  # PackunCake
    1074: (None, "Unknown 2", None, None, None, None, None, None),  # APMoveCBox
    1075: (None, None, None, None, None, None, None, None),  # Moray
    1076: (None, None, None, None, None, None, None, None),  # DokanCake
    1077: ("Unknown 1", None, None, None, None, None, None, None),  # MareM
    1078: (None, None, None, None, None, None, None, None),  # BarrelFlower
    1079: (None, None, None, None, None, None, None, None),  # Helicopter
    1081: ("Unknown 1", "Unknown 2", "Unknown 3", None, "Unknown 5", None, None, None),  # SnowBoardHeyho
    1083: (None, None, None, None, None, None, None, None),  # CmnHeyho
    1084: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # FireSnake
    1085: (None, None, None, None, None, None, None, None),  # CmnBirdNest
    1086: ("Unknown 1", None, None, None, None, None, None, None),  # MonteM
    1087: (None, None, None, None, None, None, None, None),  # CmnYoshi
    1088: (None, None, None, None, None, None, None, None),  # OcManta
    1090: (None, None, None, None, None, None, None, None),  # OcLifton
    1091: (None, None, None, None, None, None, None, None),  # SnorkelToad
    1092: (None, None, None, None, None, None, None, None),  # OcLightJellyfish
    1093: (None, None, None, None, None, None, None, None),  # CmnHawk
    1094: (None, None, None, None, None, None, None, None),  # FcClown
    1095: (None, None, "Unknown 3", None, "Unknown 5", None, None, None),  # PukupukuMecha
    1097: (None, None, None, None, None, None, None, None),  # CmnPatapataUD
    1098: (None, None, None, None, None, None, None, None),  # CmnPatapataLR
    1099: ("Unknown 1", None, None, None, None, None, None, None),  # CmnGroupToad
    1100: ("Unknown 1", None, None, None, None, None, None, None),  # NoteChild
    1101: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # PackunHone
    1103: (None, None, None, None, None, None, None, None),  # KoopaClaw
    1104: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # PackunTechno
    1105: (None, None, None, None, None, None, None, None),  # DokanHone
    1106: ("Unknown 1", None, None, None, None, None, None, None),  # PitToadB
    1107: ("Unknown 1", None, None, None, None, None, None, None),  # PitToadY
    1108: ("Unknown 1", None, None, None, None, None, None, None),  # PitToadG
    1109: ("Unknown 1", None, None, None, None, None, None, None),  # PitToadP
    1110: ("Unknown 1", None, None, None, None, None, None, None),  # PitToadR
    1111: ("Unknown 1", None, None, None, None, None, None, None),  # PitToadW
    1112: (None, None, None, None, None, None, None, None),  # DKBanana
    1114: (None, None, None, None, None, None, None, None),  # JungleBird
    1115: ("Unknown 1", None, None, None, None, None, None, None),  # PitToadWro
    1117: (None, None, None, None, None, None, None, None),  # ShyguyRope
    1118: ("Unknown 1", None, None, None, None, None, None, None),  # CmnNokonoko
    1119: ("Road Index (0/1)", "Initial Delay", "Slam Delay", None, None, None, None, None),  # CrWanwanB
    1120: (None, None, None, None, None, None, None, None),  # CmnBros
    1123: ("Unknown 1", None, None, None, None, None, None, None),  # TcHeyho
    1124: (None, None, None, None, None, None, None, None),  # SmToad
    1125: (None, None, None, None, None, None, None, None),  # SmHeyho
    1126: (None, None, None, None, None, None, None, None),  # SmYoshi
    1127: ("Unknown 1", None, "Unknown 3", None, "Unknown 5", None, None, None),  # JumpPukupuku
    1130: (None, None, None, None, None, None, None, None),  # CmnCow
    1131: (None, "Unknown 2", None, None, None, None, None, None),  # SpaceToad
    1132: (None, None, None, "Unknown 4", None, None, None, None),  # PackunTechno_NoAt
    1134: (None, None, None, None, None, None, None, None),  # CmnKaron
    1135: (None, "Unknown 2", "Unknown 3", None, "Unknown 5", None, None, None),  # JumpPukuClip
    1136: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_StarDossun
    1137: ("Unknown 1", None, None, None, None, None, None, None),  # DL_CmnAnimalA
    1138: ("Unknown 1", None, None, None, None, None, None, None),  # DL_CmnAnimalB
    1139: ("Unknown 1", None, None, None, None, None, None, None),  # DL_CmnAnimalC
    1140: ("Unknown 1", None, None, None, None, None, None, None),  # DL_CmnAnimalD
    1144: (None, None, None, None, None, None, None, None),  # DL_CmnSoldier
    1145: (None, None, None, None, None, None, None, None),  # DL_IceToad
    1147: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", "Unknown 5", None, None, None),  # DL_Keith
    1148: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # DL_Dekubaba
    1149: (None, None, None, None, None, None, None, None),  # DL_MCAirship
    1150: (None, None, None, None, None, None, None, None),  # DL_ShyguyPickaxR
    1151: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # DL_YcHelicopter
    1152: (None, None, None, None, None, None, None, None),  # DL_IceHelicopter
    1153: (None, None, None, None, None, None, None, None),  # DL_WoPulleyShyguy
    1154: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # DL_Reset
    1156: (None, None, None, None, None, None, None, None),  # DL_NkClown
    1157: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # DL_NkClownW
    1158: (None, None, None, None, None, None, None, None),  # DL_AnimalTotakeke
    1159: (None, None, None, None, None, None, None, None),  # DL_AnimalRisa
    1160: (None, None, None, None, None, None, None, None),  # DL_AnimalFuta
    1161: (None, None, None, None, None, None, None, None),  # DL_AnimalAsami
    1162: (None, None, None, None, None, None, None, None),  # DL_AnimalKinuyo
    1163: (None, None, None, None, None, None, None, None),  # DL_AnimalTanukichi
    1164: (None, "Unknown 2", None, None, None, None, None, None),  # DL_MovingItemBoxDLC
    1165: (None, None, None, None, None, None, None, None),  # DL_MechaKoopa
    1166: ("Unknown 1", None, None, None, None, None, None, None),  # DL_Wanwan
    1167: (None, "Unknown 2", None, None, None, None, None, None),  # DL_WdMovingCoin
    1168: (None, None, None, None, None, None, None, None),  # DL_AnimalKaizo
    1169: (None, None, None, None, None, None, None, None),  # DL_AnimalSnowman
    1170: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # DL_WdBird
    1171: ("Unknown 1", None, None, None, None, None, None, None),  # DL_SurpriseBox
    1172: (None, None, None, None, None, None, None, None),  # DL_RibbonToad
    1173: (None, None, None, None, None, None, None, None),  # DL_ItemBoxMetro
    1174: (None, None, None, None, None, None, None, None),  # DL_WdBarrel
    1175: (None, None, None, None, None, None, None, None),  # DL_WdBarrelR
    2004: (None, None, None, None, None, None, None, None),  # ChimneySmoke
    2006: (None, None, None, None, None, None, None, None),  # Fountain
    2007: ("Initial Delay", "Life Time", "Unknown 3", None, None, None, None, None),  # VolFlame
    2009: ("Initial Delay", "Life Time", None, None, None, None, None, None),  # VolBomb
    2010: (None, None, None, None, None, None, None, None),  # Flyingbug
    2011: (None, None, None, None, None, None, None, None),  # ButterflyB
    2012: (None, None, None, None, None, None, None, None),  # ButterflyA
    2013: (None, None, None, None, None, None, None, None),  # ButterflySp
    2014: (None, None, None, None, None, None, None, None),  # WPFountain
    2015: ("Unknown 1", None, None, None, None, None, None, None),  # WsFirebar
    2016: ("Unknown 1", None, None, None, None, None, None, None),  # WsFirering
    2017: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", "Unknown 5", None, None, None),  # CmnWaterCurrent
    2018: (None, None, None, None, None, None, None, None),  # Balloon
    2021: (None, None, None, None, None, None, None, None),  # CmnCloud
    2022: (None, None, None, None, None, None, None, None),  # Candle
    2023: ("Unknown 1", "Unknown 2", None, None, None, None, None, "Model Index (Boost plate)"),  # ClThunder
    2024: (None, None, None, None, None, None, None, None),  # DiTorchInside
    2025: (None, None, None, None, None, None, None, None),  # BDTorch
    2026: (None, None, None, None, None, None, None, None),  # VolTorch
    2027: (None, None, None, None, None, None, None, None),  # DiTorchOutside
    2028: (None, None, None, "Unknown 4", None, None, None, None),  # SandFallSmoke
    2030: (None, None, None, None, None, None, None, None),  # TCSearchLight
    2031: (None, None, None, None, None, None, None, None),  # SeaLight
    2032: (None, None, None, None, None, None, None, None),  # PsSplashA
    2033: (None, None, None, None, None, None, None, None),  # CakeSplash
    2034: (None, None, None, None, None, None, None, None),  # CakeFountain
    2035: (None, None, None, None, None, None, None, None),  # SunLight
    2036: (None, None, None, None, None, None, None, None),  # PowderSugar
    2037: (None, None, None, None, None, None, None, None),  # CakeBubble
    2039: (None, None, None, None, None, None, None, None),  # FcSearchLight
    2040: (None, None, None, None, None, None, None, None),  # OcManyFish
    2041: (None, None, None, None, None, None, None, None),  # CakeSplashB
    2042: (None, None, None, None, None, None, None, None),  # CakeFountainB
    2043: (None, None, None, None, None, None, None, None),  # CakeBottleBubble
    2045: (None, None, None, None, None, None, None, None),  # TCFountain
    2046: (None, None, None, None, None, None, None, None),  # DiFluff
    2047: (None, None, None, None, None, None, None, None),  # DiWaterfall
    2048: (None, None, None, None, None, None, None, None),  # DdWaterCurent
    2050: (None, None, None, None, None, None, None, None),  # BDSunLight
    2051: (None, None, None, None, None, None, None, None),  # VolTorchL
    2052: (None, None, None, None, None, None, None, None),  # TCSplashSet1
    2053: (None, None, None, None, None, None, None, None),  # TCSplashSet2
    2054: (None, None, None, None, None, None, None, None),  # TCFireworks
    2055: (None, None, None, None, None, None, None, None),  # TTCSunLight
    2056: (None, None, None, None, None, None, None, None),  # DkTorch
    2057: ("Initial Delay", "Unknown 2", "Unknown 3", None, None, None, None, None),  # LaserBeam
    2059: (None, None, None, None, None, None, None, None),  # BCTorch1
    2060: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # BCExplosion
    2061: (None, None, None, None, None, None, None, None),  # BCSearchLight
    2062: (None, None, None, None, None, None, None, None),  # FireworksFc
    2063: (None, None, None, None, None, None, None, None),  # FireworksSl
    2064: ("Unknown 1", None, None, None, None, None, None, None),  # FireworksN64R
    2065: (None, None, None, None, None, None, None, None),  # TTCSunLightS
    2066: (None, None, None, None, None, None, None, None),  # McSplash
    2067: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # OcWaterCurrent
    2068: (None, None, None, None, None, None, None, None),  # VolSmoke
    2069: (None, None, None, None, None, None, None, None),  # FireworksN64Rs
    2070: (None, None, None, None, None, None, None, None),  # DdQuickSandSplash
    2071: (None, None, None, None, None, None, None, None),  # EntranceSunLight
    2072: (None, None, None, None, None, None, None, None),  # LibrarySunLight
    2073: (None, None, None, None, None, None, None, None),  # CorridorSunLight
    2074: (None, None, None, None, None, None, None, None),  # AnnexeSunLight
    2077: (None, None, None, None, None, None, None, None),  # DpManyFish
    2078: (None, None, None, None, None, None, None, None),  # SlAurora
    2079: (None, None, None, None, None, None, None, None),  # FcSearchLightClip
    2081: (None, None, None, None, None, None, None, None),  # FcSearchLightOutside
    2082: (None, None, None, None, None, None, None, None),  # BCTorch2
    2083: (None, None, None, None, None, None, None, None),  # DkSunLight
    2084: (None, None, None, None, None, None, None, None),  # DL_Triforce
    2085: (None, None, None, None, None, None, None, None),  # DL_HySmoke
    2086: (None, None, None, None, None, None, None, None),  # DL_RainbowMountainA
    2087: (None, None, None, None, None, None, None, None),  # DL_RainbowMountainB
    2088: (None, None, None, None, None, None, None, None),  # DL_HyTorch
    2089: (None, None, None, None, None, None, None, None),  # DL_McStartLogo
    2090: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # DL_YoshiWaterCurrent
    2091: (None, None, None, None, None, None, None, None),  # DL_DrTorch
    2092: ("Unknown 1", None, None, None, None, None, None, None),  # DL_HySalute
    2093: (None, None, None, None, None, None, None, None),  # DL_HyHouseSmoke
    2094: (None, None, None, None, None, None, None, None),  # DL_WdChimneySmoke
    2096: (None, None, None, None, None, None, None, None),  # DL_NkThunder
    2097: (None, None, None, None, None, None, None, None),  # DL_BbStartLogoA
    2098: (None, None, None, None, None, None, None, None),  # DL_BbStartLogoB
    2099: (None, None, None, None, None, None, None, None),  # DL_AnimalFountain
    2100: (None, None, None, None, None, None, None, None),  # DL_AnimalSmoke
    3002: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # Rock1
    3004: ("Unknown 1", None, None, None, None, None, None, None),  # CarA
    3006: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # TruckA
    3007: (None, None, None, None, None, None, None, None),  # DkAirship
    3008: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # Bus
    3009: (None, None, None, None, None, None, None, None),  # Trolley
    3011: ("Unknown 1", None, None, None, None, None, None, None),  # CarrierCar
    3012: ("Unknown 1", None, None, None, None, None, None, None),  # BDSandShip
    3013: (None, None, None, None, None, None, None, None),  # Submarine
    3014: (None, None, None, None, None, None, None, None),  # TrolleyNoMove
    3015: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # APJetFly
    3016: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # DiWheel
    3018: ("Unknown 1", None, "Unknown 3", None, None, None, None, None),  # Chairlift
    3020: ("Unknown 1", None, None, None, None, None, None, None),  # CarSurf
    3021: (None, None, None, None, None, None, None, None),  # N64RTrain
    3022: (None, None, None, None, None, None, None, None),  # BDSandShipNoMove
    3023: (None, None, None, None, None, None, None, None),  # GessoShuttle
    3024: ("Unknown 1", None, None, None, None, None, None, None),  # DL_WarioTram
    3025: (None, None, None, None, None, None, None, None),  # DL_WarioTramB
    3026: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", "Unknown 5", "Unknown 6", "Unknown 7", "Unknown 8"),  # DL_Metro
    3027: (None, None, None, None, None, None, None, None),  # DL_AnimalTrain
    4004: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # ClockGearY
    4005: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # ClockHandL
    4006: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # ClockGearZ
    4007: ("Unknown 1", None, None, None, None, None, None, None),  # Furiko
    4036: (None, None, None, None, None, None, None, None),  # CityBoat
    4038: (None, None, None, None, None, None, None, None),  # HorrorRoad
    4039: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # ClockHandS
    4040: ("Unknown 1", None, None, None, None, None, None, None),  # ClockGearPole
    4042: ("Fall Delay", None, None, None, None, None, None, None),  # KaraPillar
    4043: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # MpBoard
    4044: (None, None, None, None, None, None, None, None),  # ExDash
    4048: ("Unknown 1", "Unknown 2", "Delay between rise", "Unknown 4", None, None, None, None),  # BDSandGeyser
    4050: ("Unknown 1", "Unknown 2", "Shake speed", "Unknown 4", "Unknown 5", "Unknown 6", None, None),  # VolMovRoadPlus
    4051: (None, None, "Shake speed", "Unknown 4", "Unknown 5", "Unknown 6", None, None),  # VolMovRoad
    4052: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, "Model Index"),  # VolcanoPiece
    4055: (None, None, None, None, None, None, None, None),  # DiDomino
    4060: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", "Unknown 5", None, None, None),  # DkScreamPillar
    4061: (None, None, None, None, None, None, None, None),  # SmDash
    4065: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # ClockHandL2
    4066: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # ClockHandS2
    4068: (None, None, None, None, None, None, None, None),  # KoopaRoadR
    4069: (None, None, None, None, None, None, None, None),  # KoopaRoadL
    4070: (None, None, None, None, None, None, None, None),  # RRroadout
    4071: (None, None, None, None, None, None, None, None),  # RRroadin
    4072: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # TtcBoard
    4074: (None, None, None, None, None, None, None, None),  # SpikeBall
    4075: ("Unknown 1", None, None, None, None, None, None, None),  # ClockGearArrow
    4077: (None, None, None, None, None, None, None, None),  # N64RRoad1
    4078: ("Unknown 1", None, None, None, None, None, None, None),  # N64RRoad2
    4081: (None, None, None, None, None, None, None, None),  # DonutsRoadA
    4082: (None, None, None, None, None, None, None, None),  # DonutsRoadB
    4084: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # BCCannon
    4085: ("Unknown 1", None, None, None, None, None, None, None),  # RRdash
    4086: (None, None, None, None, None, None, None, "ID"),  # DL_EbField
    4087: ("Pattern #", None, None, None, None, None, None, None),  # DL_EbDirt
    4088: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # DL_LotusLeaf
    4089: ("Unknown 1", None, None, None, None, None, None, None),  # DL_AnimalBalloon
    4090: (None, None, None, None, None, None, None, None),  # DL_EbDirtBig
    4091: (None, None, None, None, None, None, None, None),  # DL_HySwitch
    4092: (None, None, None, None, None, None, None, None),  # DL_HyJump
    4095: ("Unknown 1", "Unknown 2", "Unknown 3", None, None, None, None, None),  # DL_Iceberg
    4096: ("Unknown 1", None, None, None, None, None, None, None),  # DL_RainbowArrow
    4097: (None, None, None, None, None, None, None, None),  # DL_MasterSword
    4098: (None, None, None, None, None, None, None, None),  # DL_MCGoalLine
    4099: (None, None, None, None, None, None, None, None),  # DL_SfcRRoad1
    4100: (None, None, None, None, None, None, None, None),  # DL_SfcRRoad2
    4101: (None, None, None, None, None, None, None, None),  # DL_SfcRRoad3
    4102: (None, None, None, None, None, None, None, None),  # DL_SfcRRoad4
    4103: (None, None, None, None, None, None, None, None),  # DL_MCDashSet
    4104: (None, None, None, None, None, None, None, None),  # DL_RibbonRoad1
    4106: ("Unknown 1", None, None, None, None, None, None, None),  # DL_TicketGate
    4107: (None, None, None, None, None, None, None, None),  # DL_MetroTollBar
    4108: (None, None, None, None, None, None, None, None),  # DL_MetroDash
    4109: (None, None, None, None, None, None, None, None),  # DL_BbDash
    4110: (None, None, None, None, None, None, None, None),  # DL_FallenLeaf
    4111: (None, None, None, None, None, None, None, None),  # DL_AnimalShell
    4112: ("Unknown 1", None, None, None, None, None, None, None),  # DL_RibbonBox
    4113: (None, None, None, None, None, None, None, None),  # DL_RibbonRoad2
    4114: (None, None, None, None, None, None, None, None),  # DL_AnimalApple
    4115: (None, None, None, None, None, None, None, None),  # DL_AnimalOrange
    4116: (None, None, None, None, None, None, None, None),  # DL_AnimalLemon
    5002: (None, None, None, None, None, None, None, None),  # BumpingFlower
    5005: (None, None, None, None, None, None, None, None),  # WindMill
    5014: (None, None, None, None, None, None, None, None),  # TreeAgb
    5015: (None, None, None, None, None, None, None, None),  # TreeSnow
    5016: (None, None, None, None, None, None, None, None),  # TreeSph
    5017: (None, None, None, None, None, None, None, None),  # Tree64A
    5019: (None, None, None, None, None, None, None, None),  # TreeTri
    5020: (None, None, None, None, None, None, None, None),  # Tree64Deep
    5021: (None, None, None, None, None, None, None, None),  # WaterSurface
    5022: (None, None, None, None, None, None, None, None),  # WaterBox
    5023: (None, None, None, None, None, None, None, None),  # FlagStartDossun
    5024: (None, None, None, None, None, None, None, None),  # FlagStartMario
    5025: (None, None, None, None, None, None, None, None),  # FlagStartMooMoo
    5026: (None, None, None, None, None, None, None, None),  # FlagStartAGB
    5027: (None, None, None, None, None, None, None, None),  # YachtG
    5028: (None, None, None, None, None, None, None, None),  # YachtP
    5029: (None, None, None, None, None, None, None, None),  # YachtR
    5030: (None, None, None, None, None, None, None, None),  # YachtY
    5031: (None, None, None, None, None, None, None, None),  # HhDoor
    5033: (None, None, None, None, None, None, None, None),  # HhChandelier
    5034: (None, None, None, None, None, None, None, None),  # HhMovingWall
    5041: (None, None, None, None, None, None, None, None),  # RotaryBoard
    5042: (None, None, None, None, None, None, None, None),  # FlagRope1
    5044: (None, None, None, None, None, None, None, None),  # FlagTriangle1
    5047: (None, None, None, None, None, None, None, None),  # TreeCakeB
    5049: (None, None, None, None, None, None, None, None),  # WindMillCake
    5051: (None, None, None, None, None, None, None, None),  # MpTrumpet
    5052: (None, None, None, None, None, None, None, None),  # MpTambourin
    5053: (None, None, None, None, None, None, None, None),  # MpSax
    5054: (None, None, None, None, None, None, None, None),  # MpSpeaker
    5056: (None, None, None, None, None, None, None, None),  # MpCymbal
    5057: ("Unknown 1", None, None, None, None, None, None, None),  # MpPiston
    5058: (None, None, None, None, None, None, None, None),  # SearchLight
    5059: (None, None, None, None, None, None, None, None),  # TollBar
    5060: (None, None, None, None, None, None, None, None),  # TreeCakeD
    5062: (None, None, None, None, None, None, None, None),  # HhFan
    5063: (None, None, None, None, None, None, None, None),  # FlagTriangle2
    5064: (None, None, None, None, None, None, None, None),  # ExExcavator
    5070: (None, None, None, None, None, None, None, None),  # ClGun
    5071: (None, None, None, None, None, None, None, None),  # ClBattleShip
    5072: (None, None, None, None, None, None, None, None),  # Tree64Yoshi
    5075: (None, None, None, None, None, None, None, None),  # BDSearchLight
    5076: (None, None, None, None, None, None, None, None),  # BDFlagSquare1
    5077: (None, None, None, None, None, None, None, None),  # BDWindmill
    5078: (None, None, None, None, None, None, None, None),  # FlagTapestryDossun
    5079: (None, None, None, None, None, None, None, None),  # FlagTapestryPeach
    5080: (None, None, None, None, None, None, None, None),  # FlagTapestryMusic
    5081: (None, None, None, None, None, None, None, None),  # FlagTriangle3
    5082: ("Unknown 1", None, None, None, None, None, None, None),  # TcMirrorBall
    5083: (None, None, None, None, None, None, None, None),  # Kanransya
    5084: ("# Cups in Circle", None, None, None, None, None, None, None),  # CoffeeCup
    5085: (None, None, None, None, None, None, None, None),  # TreeSph_AddCol
    5088: (None, None, None, None, None, None, None, None),  # TreeTriB
    5089: (None, None, None, None, None, None, None, None),  # TreeBush
    5090: (None, None, None, None, None, None, None, None),  # TreeCityA
    5091: (None, None, None, None, None, None, None, None),  # APGuide
    5093: (None, None, None, None, None, None, None, None),  # TreeCakeBB
    5094: (None, None, None, None, None, None, None, None),  # TreeCakeBY
    5095: (None, None, None, None, None, None, None, None),  # APCBelt
    5096: (None, None, None, None, None, None, None, None),  # APSBelt
    5097: (None, None, None, None, None, None, None, None),  # APTollBar
    5098: (None, None, None, None, None, None, None, None),  # FlagTriangle4
    5103: (None, None, None, None, None, None, None, None),  # WPTollBar
    5104: (None, None, None, None, None, None, None, None),  # McGate
    5106: (None, None, None, None, None, None, None, None),  # DrumInside
    5107: (None, None, None, None, None, None, None, None),  # FlagStadiumA
    5108: (None, None, None, None, None, None, None, None),  # FlagStadiumB
    5109: (None, None, None, None, None, None, None, None),  # FlagStadiumC
    5110: (None, None, None, None, None, None, None, None),  # ClTrampoline
    5111: (None, None, None, None, None, None, None, None),  # SmHelicopter
    5112: (None, None, None, None, None, None, None, "Unknown 8"),  # FcGallery
    5114: ("Unknown 1", None, None, None, None, None, None, None),  # AccelRing
    5115: (None, None, None, None, None, None, None, None),  # RacingPole
    5116: (None, None, None, None, None, None, None, "Unknown 8"),  # TechnoStepGreen
    5117: (None, None, None, None, None, None, None, "Unknown 8"),  # TechnoStepRed
    5118: (None, None, None, None, None, None, None, None),  # BarrelCannon
    5119: (None, None, None, None, None, None, None, None),  # OcRing
    5120: (None, None, None, None, None, None, None, None),  # APPropeller
    5121: (None, None, None, None, None, None, None, None),  # FlagSquareAP
    5122: (None, None, None, None, None, None, None, None),  # FlagTriangle5
    5124: (None, None, None, None, None, None, None, None),  # ClBattleShipS
    5125: (None, None, None, None, None, None, None, None),  # FlagTapestryFc
    5130: (None, None, None, None, None, None, None, None),  # CakeCannon
    5131: (None, None, None, None, None, None, None, None),  # FlagTapestryWp
    5132: (None, None, None, None, None, None, None, None),  # GuardrailRSpot
    5133: (None, None, None, None, None, None, None, None),  # ExExcavatorBig
    5134: (None, None, None, None, None, None, None, None),  # ClPropeller
    5136: (None, None, None, None, None, None, None, None),  # BDRope
    5137: (None, None, None, None, None, None, None, None),  # BDCloth
    5138: (None, None, None, None, None, None, None, None),  # GearDecoA
    5139: (None, None, None, None, None, None, None, None),  # GearDecoB
    5140: (None, None, None, None, None, None, None, None),  # GearDecoC
    5141: ("Unknown 1", None, None, None, None, None, None, None),  # TcStarSpeaker
    5142: (None, None, None, None, None, None, None, None),  # TcSpeaker
    5145: (None, None, None, None, None, None, None, None),  # GearDecoD
    5146: (None, None, None, None, None, None, None, None),  # GearDecoE
    5147: (None, None, None, None, None, None, None, None),  # TcDisplay
    5155: (None, None, None, None, None, None, None, None),  # GearDecoF
    5156: (None, None, None, None, None, None, None, None),  # GearDecoG
    5157: (None, None, None, None, None, None, None, None),  # ClockSpring
    5161: (None, None, None, None, None, None, None, None),  # TcDisplayR
    5162: ("Unknown 1", None, None, None, None, None, None, None),  # TcSoundRoadG
    5163: ("Unknown 1", None, None, None, None, None, None, None),  # TcSoundRoadR
    5165: (None, None, None, None, None, None, None, None),  # TreeSnow_AddCol
    5166: (None, None, None, None, None, None, None, None),  # TreeCityACol
    5167: (None, None, None, None, None, None, None, None),  # FlagStadiumWarioC
    5168: (None, None, None, None, None, None, None, None),  # FlagStadiumWarioA
    5169: (None, None, None, None, None, None, None, None),  # FlagStadiumWarioB
    5170: (None, None, None, None, None, None, None, None),  # FlagTapestryWs
    5171: (None, None, None, None, None, None, None, None),  # SlRopeL
    5172: (None, None, None, None, None, None, None, None),  # SlRopeM
    5173: (None, None, None, None, None, None, None, None),  # FlagTapestrySl
    5174: (None, None, None, None, None, None, None, None),  # GravityBox
    5175: (None, None, None, None, None, None, None, None),  # FlagStartSnow
    5176: ("Unknown 1", None, None, None, None, None, None, None),  # N64RAccelRing
    5177: (None, None, None, None, None, None, None, None),  # N64RCheck
    5178: (None, None, None, None, None, None, None, None),  # N64RStart
    5179: (None, None, None, None, None, None, None, None),  # SwanBoatR
    5180: (None, None, None, None, None, None, None, "# Stacked Tires"),  # Tire
    5181: (None, None, None, None, None, None, None, None),  # SwanBoatB
    5182: (None, None, None, None, None, None, None, None),  # WaterPlantA
    5183: (None, None, None, None, None, None, None, None),  # WaterPlantB
    5184: (None, None, None, None, None, None, None, None),  # FlagTapestryPs
    5185: (None, None, None, None, None, None, None, None),  # WPBoatA
    5186: (None, None, None, None, None, None, None, None),  # WPBoatB
    5187: (None, None, None, None, None, None, None, None),  # WPBoatC
    5188: ("Unknown 1", None, None, None, None, None, None, None),  # N64RAccelRingAir
    5189: (None, None, None, None, None, None, None, None),  # N64RStageSet
    5190: (None, None, None, None, None, None, None, None),  # UltraArm
    5192: (None, None, None, None, None, None, None, None),  # ClockBell
    5193: (None, None, None, None, None, None, None, None),  # Tree64Middle
    5194: (None, None, None, None, None, None, None, None),  # Tree64Light
    5195: (None, None, None, None, None, None, None, None),  # FlagPeachCircuit
    5196: (None, None, None, None, None, None, None, None),  # MilkTank
    5198: (None, None, None, None, None, None, None, None),  # StrawRoll
    5200: (None, None, None, None, None, None, None, None),  # ClockArm
    5201: (None, None, None, None, None, None, None, None),  # ClockCylinder
    5202: (None, None, None, None, None, None, None, None),  # BCGate
    5203: (None, None, None, None, None, None, None, None),  # BCElevator
    5204: (None, None, None, None, None, None, None, None),  # BCEngine
    5205: (None, None, None, None, None, None, None, None),  # BCFlag
    5207: (None, None, None, None, None, None, None, None),  # BCChain
    5210: (None, None, None, None, None, None, None, None),  # TreeDD
    5217: (None, None, None, None, None, None, None, None),  # TreeDonuts
    5218: (None, None, None, None, None, None, None, None),  # Tree64DeepCol
    5219: (None, None, None, None, None, None, None, None),  # Tree64MiddleCol
    5220: (None, None, None, None, None, None, None, None),  # Tree64LightCol
    5221: (None, None, None, None, None, None, None, None),  # TreePukupuku
    5222: (None, None, None, None, None, None, None, None),  # ConnectBoard
    5223: (None, None, None, None, None, None, None, None),  # SlRedSpot
    5224: (None, None, None, None, None, None, None, None),  # BDFlagSquare2
    5225: (None, None, None, None, None, None, None, None),  # FlagStartPukupuku
    5227: (None, None, None, None, None, None, None, None),  # SpinTurboBar_BD
    5228: (None, None, None, None, None, None, None, None),  # FlagSquare1
    5229: (None, None, None, None, None, None, None, None),  # WsGate
    5230: (None, None, None, None, None, None, None, None),  # PeachBell
    5231: (None, None, None, None, None, None, None, None),  # SpinTurboBar_TC
    5232: (None, None, None, None, None, None, None, None),  # SpinTurboBar_AP
    5234: (None, None, None, None, None, None, None, None),  # OceanWaterPlantA
    5235: (None, None, None, None, None, None, None, None),  # OceanWaterPlantB
    5236: (None, None, None, None, None, None, None, None),  # RRstationA
    5237: (None, None, None, None, None, None, None, None),  # RRstationB
    5238: (None, None, None, None, None, None, None, None),  # RRstationC
    5239: (None, None, None, None, None, None, None, None),  # RRguide
    5240: (None, None, None, None, None, None, None, None),  # RRring
    5241: (None, None, None, None, None, None, None, None),  # RRseat
    5242: (None, None, None, None, None, None, None, None),  # WindMillSmall
    5244: (None, None, None, None, None, None, None, "# Stacked Tires"),  # TireR
    5245: (None, None, None, None, None, None, None, "# Stacked Tires"),  # TireW
    5246: (None, None, None, None, None, None, None, None),  # PsFan
    5247: (None, None, None, None, None, None, None, None),  # TcMoveLight
    5248: (None, None, None, None, None, None, None, None),  # Weathercock
    5249: (None, None, None, None, None, None, None, None),  # RRstartring
    5250: (None, None, None, None, None, None, None, None),  # TcChandelier
    5251: (None, None, None, None, None, None, None, None),  # FlagMusicSwing
    5252: (None, None, None, None, None, None, None, None),  # SherbetPlantA
    5253: (None, None, None, None, None, None, None, None),  # SherbetPlantB
    5254: (None, None, None, None, None, None, None, None),  # FlagTriangle3Y
    5255: (None, None, None, None, None, None, None, None),  # N64RStageSet2
    5256: (None, None, None, None, None, None, None, None),  # N64RStar
    5257: (None, None, None, None, None, None, None, None),  # TcChandelierS
    5258: (None, None, None, None, None, None, None, None),  # TcChandelierM
    5259: (None, None, None, None, None, None, None, None),  # WindMillB
    5261: (None, None, None, None, None, None, None, None),  # SpinTurboBar_RR
    5262: (None, None, None, None, None, None, None, None),  # CmnDashBoard
    5263: (None, None, None, None, None, None, None, None),  # McJump
    5265: (None, None, None, None, None, None, None, None),  # MmJump
    5266: (None, None, None, None, None, None, None, None),  # KhJump
    5267: (None, None, None, None, None, None, None, None),  # SmFan
    5268: (None, None, None, None, None, None, None, None),  # BCParts
    5269: (None, None, None, None, None, None, None, None),  # ClGuide
    5270: (None, None, None, None, None, None, None, None),  # BCPiston
    5271: (None, None, None, None, None, None, None, None),  # BCBattleShipS
    5272: (None, None, None, None, None, None, None, None),  # SearchLightNoClip
    5273: (None, None, None, None, None, None, None, None),  # RRbox
    5274: (None, None, None, None, None, None, None, None),  # McKart
    5275: (None, None, None, None, None, None, None, None),  # TreeSphB
    5276: (None, None, None, None, None, None, None, None),  # CiJump
    5277: (None, None, None, None, None, None, None, None),  # TreeSphB_AddCol
    5278: (None, None, None, None, None, None, None, None),  # Holography
    5279: ("Unknown 1", None, "Unknown 3", None, None, None, None, None),  # ChairliftNoMove
    5280: (None, None, None, None, None, None, None, None),  # DL_TreeTri
    5281: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_TreeApple
    5282: (None, None, None, None, None, None, None, None),  # DL_SpinTurboBar_DR
    5283: (None, None, None, None, None, None, None, None),  # DL_SpinTurboBar_MC
    5284: (None, None, None, None, None, None, None, None),  # DL_WgExcavator
    5285: (None, None, None, None, None, None, None, None),  # DL_WgGear
    5286: (None, None, None, None, None, None, None, None),  # DL_WgGearBig
    5287: (None, None, None, None, None, None, None, None),  # DL_FlagStartIce
    5289: (None, None, None, None, None, None, None, None),  # DL_EbGridGate
    5290: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_TreeOrange
    5291: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_TreeLemon
    5292: (None, None, None, None, None, None, None, None),  # DL_TreeSphYoshi
    5293: (None, None, None, None, None, None, None, None),  # DL_FlagTriangle6
    5294: (None, None, None, None, None, None, None, None),  # DL_WgFlagSquare
    5295: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_TreeAnimal
    5296: (None, None, None, None, None, None, None, None),  # DL_FlagStadiumEB
    5297: (None, None, None, None, None, None, None, None),  # DL_TreePineA
    5298: (None, None, None, None, None, None, None, None),  # DL_TreePineB
    5299: (None, None, None, None, None, None, None, None),  # DL_FlagDragon
    5300: (None, None, None, None, None, None, None, None),  # DL_MCRotaryBoardA
    5301: (None, None, None, None, None, None, None, None),  # DL_MCBldgParts
    5302: (None, None, None, None, None, None, None, None),  # DL_MCCars
    5303: (None, None, None, None, None, None, None, None),  # DL_MCTriangleBoard
    5304: (None, None, None, None, None, None, None, None),  # DL_MCPipeRing
    5305: (None, None, None, None, None, None, None, None),  # DL_MCJets
    5306: (None, None, None, None, None, None, None, None),  # DL_HyFlagSquare
    5307: (None, None, None, None, None, None, None, None),  # DL_IceFlagSquare
    5308: (None, None, None, None, None, None, None, None),  # DL_YcYacht
    5309: (None, None, None, None, None, None, None, None),  # DL_SpinTurboBar_IP
    5310: (None, None, None, None, None, None, None, None),  # DL_WeathercockYoshi
    5311: (None, None, None, None, None, None, None, None),  # DL_FlagStartYoshi
    5312: (None, None, None, None, None, None, None, None),  # DL_FlagRopeYoshi
    5313: (None, None, None, None, None, None, None, None),  # DL_MasterSwordBase
    5314: (None, None, None, None, None, None, None, None),  # DL_MCRotaryBoardB
    5315: (None, None, None, None, None, None, None, None),  # DL_MCRotaryBoardC
    5316: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", "Unknown 5", "Unknown 6", None, None),  # DL_WoElevator
    5317: (None, None, None, None, None, None, None, None),  # DL_WoWaterWheel
    5318: (None, None, None, None, None, None, None, None),  # DL_BbAirship
    5319: (None, None, None, None, None, None, None, None),  # DL_BbCars
    5320: (None, None, None, None, None, None, None, None),  # DL_BbJets
    5321: (None, None, None, None, None, None, None, None),  # DL_BpSwingride
    5322: (None, None, None, None, None, None, None, None),  # DL_BpPirate
    5323: (None, None, None, None, None, None, None, None),  # DL_BpParatroopa
    5324: (None, None, None, None, None, None, None, None),  # DL_BpWingA
    5325: (None, None, None, None, None, None, None, None),  # DL_BpWingB
    5326: (None, None, None, None, None, None, None, None),  # DL_BpGear
    5327: ("Unknown 1", None, None, None, None, None, None, None),  # DL_CheeseBox
    5328: (None, None, None, None, None, None, None, None),  # DL_TreePalm
    5329: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_CoinStone
    5330: (None, None, None, None, None, None, None, None),  # DL_BpKanransya
    5331: (None, None, None, None, None, None, None, None),  # DL_BpCoaster
    5332: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_TreeAutumnApple
    5333: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_TreeAutumnLemon
    5334: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_TreeAutumnOrange
    5335: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_TreeWinter
    5336: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_TreeWinterApple
    5337: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_TreeWinterLemon
    5338: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_TreeWinterOrange
    5339: (None, None, None, None, None, None, None, None),  # DL_TreeSakura
    5340: (None, None, None, None, None, None, None, None),  # DL_TreeBushAutumn
    5341: (None, None, None, None, None, None, None, None),  # DL_TreeBushWinter
    5342: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_TreeAutumn
    5343: (None, None, None, None, None, None, None, None),  # DL_NkSearchLight
    5344: (None, None, None, None, None, None, None, None),  # DL_StationAlarm
    5345: (None, None, None, None, None, None, None, None),  # DL_FlagStartWoods
    5346: (None, None, None, None, None, None, None, None),  # DL_TreeSakura2
    5347: (None, None, None, None, None, None, None, None),  # DL_TreeSakura3
    5348: (None, None, None, None, None, None, None, None),  # DL_AnimalJump
    5349: (None, None, None, None, None, None, None, None),  # DL_NkGate
    5350: (None, None, None, None, None, None, None, None),  # DL_NkArrowArea_A
    5351: (None, None, None, None, None, None, None, None),  # DL_NkArrowArea_B
    5352: (None, None, None, None, None, None, None, None),  # DL_NkArrowArea_C
    5353: (None, None, None, None, None, None, None, None),  # DL_SpinTurboBar_Bb
    5354: (None, None, None, None, None, None, None, None),  # DL_Bbguide
    5355: (None, None, None, None, None, None, None, None),  # DL_BbAccelRing
    5356: (None, None, None, None, None, None, None, None),  # DL_BbCannon
    5357: (None, None, None, None, None, None, None, None),  # DL_BbBuildA
    5358: (None, None, None, None, None, None, None, None),  # DL_BbCarsB
    5359: (None, None, None, None, None, None, None, None),  # DL_AnimalFlag
    5360: (None, None, None, None, None, None, None, None),  # DL_FlagTriangle7
    5361: (None, None, None, None, None, None, None, None),  # DL_NkElevator
    5362: (None, None, None, None, None, None, None, None),  # DL_NkRotaryBoard_A
    5363: (None, None, None, None, None, None, None, None),  # DL_NkCars_A
    5372: (None, None, None, None, None, None, None, None),  # DL_BpStartGate
    5373: (None, None, None, None, None, None, None, None),  # DL_SpinTurboBar_Nk
    5376: (None, None, None, None, None, None, None, None),  # DL_SpinTurboBar_Cl
    5377: (None, None, None, None, None, None, None, None),  # DL_BbPipeRing
    5378: (None, None, None, None, None, None, None, None),  # DL_BbRotaryBoardA
    5379: (None, None, None, None, None, None, None, None),  # DL_BbBoardPart
    5381: (None, None, None, None, None, None, None, None),  # DL_NkArrowArea_D
    5382: (None, None, None, None, None, None, None, None),  # DL_NkArrowArea_E
    5383: ("Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4", None, None, None, None),  # DL_CoinStoneSnow
    6002: (None, None, None, None, None, None, None, "Unknown 8"),  # TestStart
    6003: (None, None, None, None, None, None, None, "Unknown 8"),  # Start
    6004: (None, None, None, None, None, None, None, None),  # Sun
    6005: (None, None, None, None, None, None, None, None),  # Moon
    6006: (None, None, None, None, None, None, None, None),  # Sunset
    6008: (None, None, None, None, None, None, None, None),  # SunInf
    6009: (None, None, None, None, None, None, None, None),  # SunInfY
    6010: (None, None, None, None, None, None, None, None),  # MoonInf
    6011: (None, None, None, None, None, None, None, None),  # MoonInfY
    6012: (None, None, None, None, None, None, None, None),  # SunsetInf
    6013: (None, None, None, None, None, None, None, None),  # SunsetInfY
    6014: (None, None, None, None, None, None, None, None),  # Moon2Inf
    6015: (None, None, None, None, None, None, None, None),  # Moon2InfY
    6016: (None, None, None, None, None, None, None, None),  # DL_RainbowLightA
    6017: (None, None, None, None, None, None, None, None),  # DL_RainbowLightB
    7005: (None, None, None, None, None, None, None, None),  # VR64Highway
    7006: (None, None, None, None, None, None, None, None),  # VRfair
    7008: (None, None, None, None, None, None, None, None),  # VRagbMario
    7009: (None, None, None, None, None, None, None, None),  # VR64Peach
    7010: (None, None, None, None, None, None, None, None),  # VRHorror
    7011: (None, None, None, None, None, None, None, None),  # VRCake
    7012: (None, None, None, None, None, None, None, None),  # VRcloudSea
    7013: (None, None, None, None, None, None, None, None),  # VRWaterPark
    7014: (None, None, None, None, None, None, None, None),  # VRFirst
    7015: (None, None, None, None, None, None, None, None),  # VRAirport
    7016: (None, None, None, None, None, None, None, None),  # VRTechno
    7017: (None, None, None, None, None, None, None, None),  # VRSnowMt
    7018: (None, None, None, None, None, None, None, None),  # VRCloud
    7019: (None, None, None, None, None, None, None, None),  # VRDesert
    7020: (None, None, None, None, None, None, None, None),  # VRExpert
    7021: (None, None, None, None, None, None, None, None),  # VRCity
    7022: (None, None, None, None, None, None, None, None),  # VRDossun
    7023: (None, None, None, None, None, None, None, None),  # VRMario
    7024: (None, None, None, None, None, None, None, None),  # VR64Yoshi
    7025: (None, None, None, None, None, None, None, None),  # VRMenu
    7026: (None, None, None, None, None, None, None, None),  # VRStorm
    7027: (None, None, None, None, None, None, None, None),  # VRGcDesert
    7028: (None, None, None, None, None, None, None, None),  # VRWiiMoo
    7029: (None, None, None, None, None, None, None, None),  # VRCosmos
    7030: (None, None, None, None, None, None, None, None),  # VRCustomizer
    7031: (None, None, None, None, None, None, None, None),  # VRWarioStadium
    7032: (None, None, None, None, None, None, None, None),  # VRG64Rainbow
    7033: (None, None, None, None, None, None, None, None),  # VRRainbowRoad
    7034: (None, None, None, None, None, None, None, None),  # VRClock
    7035: (None, None, None, None, None, None, None, None),  # VROcean
    7036: (None, None, None, None, None, None, None, None),  # VRSherbet
    7037: (None, None, None, None, None, None, None, None),  # VRDonuts
    7038: (None, None, None, None, None, None, None, None),  # VRPackunS
    7039: (None, None, None, None, None, None, None, None),  # VRPukuB
    7040: (None, None, None, None, None, None, None, None),  # VRBowser
    7041: (None, None, None, None, None, None, None, None),  # DL_VRSfcRainbow
    7042: (None, None, None, None, None, None, None, None),  # DL_VRMuteCity
    7043: (None, None, None, None, None, None, None, None),  # DL_VRDragon
    7044: (None, None, None, None, None, None, None, None),  # DL_VRExciteBike
    7045: (None, None, None, None, None, None, None, None),  # DL_VRHyrule
    7046: (None, None, None, None, None, None, None, None),  # DL_VRIcePark
    7047: (None, None, None, None, None, None, None, None),  # DL_VRBabyPark
    7048: (None, None, None, None, None, None, None, None),  # DL_VRYoshiCircuit
    7049: (None, None, None, None, None, None, None, None),  # DL_VRWoods
    7050: (None, None, None, None, None, None, None, None),  # DL_VRNeoBowserCity
    7051: (None, None, None, None, None, None, None, None),  # DL_VRRibbon
    7052: (None, None, None, None, None, None, None, None),  # DL_VRAnimalSpring
    7053: (None, None, None, None, None, None, None, None),  # DL_VRAnimalSummer
    7054: (None, None, None, None, None, None, None, None),  # DL_VRAnimalAutumn
    7055: (None, None, None, None, None, None, None, None),  # DL_VRAnimalWinter
    7056: (None, None, None, None, None, None, None, None),  # DL_VRCheeseLand
    7057: (None, None, None, None, None, None, None, None),  # DL_VRBigBlue
    8001: (None, None, None, None, None, None, None, None),  # ColCylinder
    8008: ("Unknown 1", None, None, None, None, None, None, None),  # StartEx
    8009: (None, None, None, None, None, None, None, None),  # ColCylinderStone
    8010: (None, None, None, None, None, None, None, None),  # ColCylinderWood
    8011: (None, None, None, None, None, None, None, None),  # ColCylinderMetal
    8014: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # CmnWaterCurrent_NoMdl
    8015: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # CmnWaterCurrent_NoEff
    8016: (None, None, None, None, None, None, None, None),  # ColSpinDash
    8017: (None, None, None, None, None, None, None, None),  # ColCylinderGum
    8021: (None, None, None, None, None, None, None, None),  # RRsat
    8022: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # N64RCoin
    8024: (None, None, None, None, None, None, None, None),  # ColLeafBox
    8025: ("Unknown 1", None, None, None, None, None, None, None),  # NoteArea
    8026: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # ShortCutBox
    8027: (None, None, None, None, None, None, None, None),  # DL_EbCheerCol
    8028: ("Unknown 1", None, None, None, None, None, None, None),  # DL_EbApproachCol
    8029: ("Unknown 1", "Unknown 2", None, None, None, None, None, None),  # Adjuster200cc
    8030: (None, None, None, None, None, None, None, None),  # DL_WanwanSearchArea
    8031: (None, None, None, None, None, None, None, None),  # DL_WanwanAttackPoint
    8032: ("Unknown 1", None, None, None, None, None, None, None),  # DL_AnimalVoiceAutumn
    8033: (None, None, None, None, None, None, None, None),  # DL_AnimalVoiceSummer
    9006: (None, None, None, None, None, None, None, None),  # KaraPillarBase
    9007: (None, None, None, None, None, None, None, None)  # ItemBoxFont
}


def get_param_names(obj_id, index):
    names = _param_names.get(obj_id)
    if names:
        param_name = names[index - 1]
        # Return "Unused X" when such parameters should be shown.
        if not param_name and bpy.context.user_preferences.addons[__package__].preferences.show_unused_obj_params:
            param_name = "Unused {}".format(index)
    else:
        param_name = "Unknown {}".format(index)
    return param_name


def _ensure_loaded():
    global _objflow
    if not _objflow:
        # Load the objflow as it has not been loaded yet.
        addon.log(0, "Loading objflow...")
        addon_prefs = bpy.context.user_preferences.addons[__package__].preferences
        objflow_path = os.path.join(addon_prefs.game_path, "content", "data", "objflow.byaml")
        if not os.path.isfile(objflow_path):
            raise AssertionError("objflow.byaml does not exist as '{}'. Correct your game directory.".format(objflow_path))
        _objflow = byaml.File()
        _objflow.load_raw(open(objflow_path, "rb"))
        # Create lookup dictionaries and arrays for quick access.
        for obj in _objflow.root:
            obj_id = obj["ObjId"]
            label = obj["Label"]
            _id_dict[obj_id] = obj
            _label_dict[label.lower()] = obj
            _label_items.append((str(obj_id), label, ""))
        _label_items.sort(key=lambda item: item[1].lower())
