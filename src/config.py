import numpy as np
import random


#### ORDER ###########################################################
# ORDER_QUANTITY: order quantity
# CUST_ORDER_CYCLE: Customer ordering cycle [days]

#### JOB #####################################################################
# JOB_QUANTITY : Job QUNANTITY / number of patients
# JOB_SIZE : Number of items in a job

#### Job의 속성 정의 ##########################################################
# JOB_TYPES: Job의 속성 정의 사전, 기본 Job 유형의 다양한 속성 범위를 포함함
# - VOLUME_RANGE: Job 볼륨의 최소/최대 범위 (예: 1에서 45)
# - BUILD_TIME_RANGE: Job 제작 시간 범위 (예: 1에서 5일)
# - POST_PROCESSING_TIME_RANGE: 후처리 시간 범위
# - PACKAGING_TIME_RANGE: 포장 시간 범위

#### 후처리 작업자 설정 ########################################################
# POST_PROCESSING_WORKER: 작업자 정보 설정, 각 작업자의 ID를 포함
# 작업자가 동시에 처리할 수 있는 Job은 1개로 제한됨

#### 3D 프린터 정보 설정 #######################################################
# PRINTERS: 각 프린터의 정보 설정 (ID와 최대 처리 용량)
# PRINTERS_INVEN: 각 프린터별 Job 대기열을 저장하는 리스트

# 시뮬레이션 설정
SIM_TIME = 1  # 시뮬레이션 기간 (일 단위)

# Job 생성 파라미터 설정
JOB_CREATION_INTERVAL = 3  # 평균 1시간 간격으로 Job 생성


# Job의 속성 정의
JOB_TYPES = {
    "DEFAULT": {
        "WIDTH_RANGE": (10, 20), # 단위: mm
        "HEIGHT_RANGE": (10, 20), # 단위: mm
        "DEPTH_RANGE": (10, 20), # 단위: mm
        "FILAMENT_DIAMETER": 1.75,
        "BUILD_SPEED": 3600,
        "WASHING_RANGE": (10, 20)
    }
}


CUSTOMER = {
    "JOB_LIST_SIZE": 2,
     "ITEM_SIZE": 2
     }

# 3D 프린터 정보 설정, VOL: WIDTH * HEIGHT * DEPTH / 단위: mm
PRINTERS = {
    0: {"ID": 0}, 
    1: {"ID": 1},
    2: {"ID": 2},
    3: {"ID": 3},
    4: {"ID": 4}
}

# unit: mm
PRINTERS_SIZE = {"VOL": 669130000, "WIDTH": 1540, "HEIGHT": 790, "DEPTH": 550, "SET_UP": 10, "CLOSING": 30}

WASHING_MACHINE = {
    0: {"ID": 0, "WASHING_SIZE": 2},
    1: {"ID": 1, "WASHING_SIZE": 2}
}

DRY_MACHINE = {
    0: {"ID": 0, "DRYING_SIZE": 3},
    1: {"ID": 1, "DRYING_SIZE": 3}
}

POST_PROCESSING_WORKER = {
    0: {"ID": 0},
    1: {"ID": 1},
    2: {"ID": 2},
    3: {"ID": 3},
    4: {"ID": 4},
    5: {"ID": 5}
}

PACKAGING_MACHINE = {
    0: {"ID": 0},
    1: {"ID": 1},
    2: {"ID": 2}
}


PRINT_SATISFICATION = True
VISUALIZATION = True
PRINT_SIM_EVENTS = True
PRINT_SIM_COST = True  # True로 설정하면 비용이 출력됨, False로 설정하면 출력되지 않음