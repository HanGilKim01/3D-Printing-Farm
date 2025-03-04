import random  # For random number generation
import numpy as np


#### ORDER #####################################################################
# ORDER_QUANTITY: order quantity
# CUST_ORDER_CYCLE: Customer ordering cycle [days]

#### JOB #####################################################################
# JOB_QUANTITY : Job QUNANTITY / number of patients
# JOB_SIZE : Number of items in a job

#### MACHINE #####################################################################
# ID: Index of the element in the dictionary
# NAME: machine's name or model;
# PRODUCTION_RATE [units/day] 
# NUM_MACHINES : number of machines


# Simulation 기간
SIM_TIME = 3  # [days] per episode

ORDER = {"ORDER_QUANTITY": 1, "CUST_ORDER_CYCLE": 28}

JOB = {"JOB_QUANTITY": 5, "JOB_SIZE": 10}


MACHINE = {
            0: {"ID": 0, "NAME": "PRINTER",
               "NUM_MACHINES" : 2, "PRODUCTION_RATE": 24,
               },

            1: {"ID": 1, "NAME": "WASHING_MACHINE",
                "NUM_MACHINES" : 2, "PRODUCTION_RATE": 24},
            
            2: {"ID": 2, "NAME": "DRY_MACHINE",
                "NUM_MACHINES" : 2, "PRODUCTION_RATE": 24},
            
            3: {"ID": 3, "NAME": "INSPECT_MACHINE",
                "NUM_MACHINES" : 2, "PRODUCTION_RATE": 24}
            }





item_list = [[random.randint(8, 12) for _ in range(JOB['JOB_SIZE'])] for _ in range(JOB['JOB_QUANTITY'])]
#시뮬레이션 속성으로, 보통통

        

"""
item 리스트를 먼저 만들어!! 원래 시뮬레이션 성격상 리스트에 교정기 모델을 넣을거 아녀.
order = Order()
    for j in Jobs:
        job = Job(JOB['JOB_QUANTITY'], item_list)

        for i in items:
            job.append(Item())

그러면, 여기서 item리스트에 랜덤으로 사이즈를 지정해서 item 리스트를 job갯수만큼 생성
ex.itme_list = (10, 9 ,8, 11, 10, 12, 7, 9, 10...)(랜덤 사이즈), (11,8,9,10,...) (...) ... (N개)
config에선 우선 이렇게만 지정해.


그리고 env에서 class item에서, 해당 리스트를 숫자,id로 메겨. item_id_list = (1,2,3,4,5,6,7,8,9,10) (1,2,3,4...,10), ... , (N개)


그리고 class job에서 job list를 다시 만들어.
{'Job_id': 1, 'Item_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]} , ... , N개
그리고 모든 job은 order1에게 지정한다.

시뮬레이션 작동 흐름
order를 생성하였다면, customer는 해당 order를 주문하게 된다. >> production planning으로 order를 넘김

production planning은 그러면 해당 order를 job으로 세분화해서 대기열에 세운다.

job 단위로 proc_build에게 넘긴다.

proc_build,wash,dry는 job 단위로 생산을 시작하고, 생산이 끝나면, 후처리 기계들로 넘긴다.

후처리 기계들(postprocess,inspect)는 item 단위로 생산을 한다. so, job으로 받은 것들을 item단위로 쪼개고, job안의 item 갯수만큼 생산이 마치게 되면 job단위로 또 후처리를 넘기는 방식으로 반복

후처리 기계들이 job단위로 생산을 마칠때마다 최종 결과물 리스트 안에 저장해놓기.
"""
gantt_data = []



PRINT_GRAPH_RECORD = True
PRINT_SIM_EVENTS = True
PRINT_SIM_REPORT = True
VISUALIZATION = True
TIME_CORRECTION = 0
