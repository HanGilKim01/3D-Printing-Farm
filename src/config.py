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




import random

class Customer:
    def __init__(self):
        self.job_list = []
        self.create_jobs()

    def create_jobs(self):
        # job_list를 JOB_QUANTITY 만큼의 job으로 구성
        self.job_list = []  # 기존 리스트 초기화
        for _ in range(JOB['JOB_QUANTITY']):
            job = [random.randint(8, 12) for _ in range(JOB['JOB_SIZE'])]
            self.job_list.append(job)



class Order:
    # 생성된 order를 카운트하는 클래스 변수
    

    def __init__(self, job_list):
        self.order_number = 0
        self.job_list = job_list

    def order_count(self):
        self.order_number += 1
        return f"Order{self.order_number}: {self.job_list}"


customer = Customer()
order = Order()
print(order)



gantt_data = []



PRINT_GRAPH_RECORD = True
PRINT_SIM_EVENTS = True
PRINT_SIM_REPORT = True
VISUALIZATION = True
TIME_CORRECTION = 0
