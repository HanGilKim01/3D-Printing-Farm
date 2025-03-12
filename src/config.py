import numpy as np
import random


#### Job ##########################################################
# Volume_range : item의 각 volume 범위

#### Customer ##########################################################
# JOB_LIST_SIZE : job 갯수
# ITEM_SIZE : item 갯수
# INTERVAL : job 생성 간격

#### Post_Processor ########################################################
# POST_PROCESSING_WORKER: 작업자 정보 설정, 각 작업자의 ID를 포함
# 작업자가 동시에 처리할 수 있는 Job은 1개로 제한됨

#### Print #######################################################
# PRINTERS: 각 프린터의 정보


# 시뮬레이션 설정
SIM_TIME = 1  # 시뮬레이션 기간 (일 단위)

# Job의 속성 정의
JOB_TYPES = {
    "DEFAULT": {
        "Volume_range": (10, 20), # 단위: mm     
    }
}


CUSTOMER = {"JOB_LIST_SIZE": 2, "ITEM_SIZE": 2, "INTERVAL": 5}

# 3D 프린터 정보 설정, VOL: WIDTH * HEIGHT * DEPTH / 단위: mm
PRINTERS = {0: {"ID": 0}, 1: {"ID": 1}}

# unit: mm
PRINTERS_SIZE = {"Volume_range": 100, "SET_UP": 10, "CLOSING": 30}



PRINT_SATISFICATION = True
VISUALIZATION = True
PRINT_SIM_EVENTS = True
PRINT_SIM_COST = True  # True로 설정하면 비용이 출력됨, False로 설정하면 출력되지 않음