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


class Customer:
    """
    고객 클래스:
      - 각 고객은 고유한 customer_id와 
      - JOB_SIZE 개의 랜덤 아이템(8~12 사이 정수)으로 구성된 job 리스트를 가집니다.
    """
    def __init__(self, customer_id):
        self.customer_id = customer_id
        # 각 고객마다 JOB_SIZE 개의 랜덤 아이템 생성 (8~12 사이 정수)
        self.job_list = [random.randint(8, 12) for _ in range(JOB['JOB_SIZE'])]
        
    def __str__(self):
        return f"Customer {self.customer_id}: {self.job_list}"
    
    def create_customers(self, num_customers=JOB['JOB_QUANTITY']):
        """
        인스턴스 메서드로, 주어진 고객 수(num_customers) 만큼 Customer 인스턴스를 생성하여 리스트로 반환합니다.
        이 메서드는 인스턴스에 종속적이므로, 먼저 인스턴스를 생성한 후에 호출해야 합니다.
        """
        # self.num_customers 대신 num_customers 매개변수를 사용합니다.
        return [Customer(customer_id=i + 1) for i in range(num_customers)]

# 사용 예시:
# dummy 인스턴스를 생성한 후, 이를 통해 고객 리스트를 생성합니다.
dummy_customer = Customer(0)  # customer_id는 dummy용으로 0을 사용
customers = dummy_customer.create_customers()  # JOB_QUANTITY 값(5)을 기본값으로 사용

print("생성된 고객 목록:")
for customer in customers:
    print(customer)
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
