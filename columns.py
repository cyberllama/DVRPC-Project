from enum import Enum

class OutputColumns(Enum):
    COUNTY = 0
    MCD_NAME = 1
    MCD_ID = 2
    YEAR = 3
    POPULATION_ESTIMATE = 4
    TOTAL_KSI_RATE = 5
    PEDESTRIAN_KSI_RATE = 6
    BICYCLIST_KSI_RATE = 7
    TOTAL_KSI_RATE_5YR = 8
    PEDESTRIAN_KSI_RATE_5YR = 9
    BICYCLIST_KSI_RATE_5YR = 10

class MCDCrashColumns(Enum):
    COUNTY = 0
    MCD_NAME = 1
    MCD_ID = 2
    YEAR = 3
    TOTAL_KSI = 4
    PEDESTRIAN_KSI = 5
    BICYCLIST_KSI = 6


class MCDPopColumns(Enum):
    MCD_ID = 0
    POP_2015 = 1
    POP_2019 = 2
    POP_2020 = 3
    POP_2025 = 4
