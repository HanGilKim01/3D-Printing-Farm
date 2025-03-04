import simpy
import numpy as np
from config import *  # Assuming this imports necessary configurations
from log import *  # Assuming this imports necessary logging functionalities
from visualization import *
import environment as env
import random



class Item :
    """
    config에서 생성된 item_list의 item들을 id로 배정하는 클래스
    """
    def __init__(self, item_id, value):
        self.id = item_id
        self.value = value

    def transform_list(item_list):
        """랜덤 리스트를 Item 객체 리스트로 변환하고, ID 리스트 반환"""
        return [[i + 1 for i in range(len(item_list))] for item_list in item_list]

class Job:
    """
    Job 리스트를 생성하는 클래스
    """
    def __init__(self, job_quantity, item_list):
        self.job_quantity = job_quantity
        self.item_list = item_list
        self.job_list = self.create_job_list()

    def create_job_list(self):
        """Item 클래스를 활용해 변환된 리스트를 받아 Job 리스트 생성"""
        transformed_item_list = Item.transform_list(self.item_list)
        return [{"Job_id": job_id + 1, "Item_id": item_list} for job_id, item_list in enumerate(transformed_item_list)]

    def get_jobs(self):
        """생성된 Job 리스트 반환"""
        return self.job_list
    
class Order:
    """Job 리스트를 받아 주문을 생성하는 클래스"""
    def __init__(self, job_list):
        self.orders = job_list  # job_list를 그대로 할당

    def get_orders(self):
        """생성된 주문 리스트 반환"""
        return self.orders

class Customer:
    """ 고객이 주문을 생성하고 ProductionPlanning으로 전달하는 클래스 """
    def __init__(self, order):
        self.order = order

    def place_order(self, production_planning):
        """주문을 생산 계획 시스템으로 전달"""
        production_planning.receive_order(self.order.get_orders())

class Production_Planning:
    """ 생산 계획을 관리하는 클래스 (Job 단위로 나누어 대기열 관리) """
    def __init__(self):
        self.job_queue = []

    def receive_order(self, job_list):
        """주문을 받아 Job 단위로 대기열에 추가"""
        for job in job_list:
            self.job_queue.append(job)
        print("Production queue updated:", self.job_queue)

    def process_jobs(self, proc_build):
        """대기열에 있는 Job을 ProcBuild로 전달하여 처리"""
        while self.job_queue:
            job = self.job_queue.pop(0)
            proc_build.execute_job(job)

class ProcBuild:
    """ 개별 Job을 처리하는 클래스 (생산) """
    def __init__(self, proc_wash):
        self.proc_wash = proc_wash  # ProcWash 객체 참조

    def execute_job(self, job):
        """Job을 실행하는 메서드 (생산 후 세척 공정으로 전달)"""
        print(f"Processing Job {job['Job_id']} with items {job['Item_id']}")
        self.proc_wash.receive_job(job)  # 생산 완료 후 ProcWash로 전달

class Proc_Wash:
    """ 세척 공정을 담당하는 클래스 """
    def __init__(self):
        self.wash_queue = []

    def receive_job(self, job):
        """ProcBuild에서 완료된 Job을 받아 세척 대기열에 추가"""
        self.wash_queue.append(job)
        print(f"Job {job['Job_id']} moved to washing queue.")

    def process_washing(self):
        """세척 공정 실행"""
        while self.wash_queue:
            job = self.wash_queue.pop(0)
            print(f"Washing Job {job['Job_id']} with items {job['Item_id']}")

# 객체 생성 및 실행
job = Job(JOB['JOB_QUANTITY'], item_list)  # Job 생성
order = Order(job.get_jobs())  # Order 생성
customer = Customer(order)  # Customer 생성

production_planning = Production_Planning()  # 생산 계획 객체 생성
  # 생산 처리 객체 생성
proc_wash = Proc_Wash()
proc_build = ProcBuild(proc_wash)

customer.place_order(production_planning)  # 고객이 주문을 제출
production_planning.process_jobs(proc_build)  # 생산 계획이 Job을 처리
    
"""
class Production_Planning :
    def __init__(self):
        pass

class Proc_Build:
    def __init__(self):
        pass

class Proc_Wash:
    def __init__(self):
        pass

class Proc_Dry:
    def __init__(self):
        pass

class Proc_Inspect:
    def __init__(self):
        pass
"""
         



def create_env(JOB, daily_events):
    # Function to create the simulation environment and necessary objects
    simpy_env = simpy.Environment()  # Create a SimPy environment


    job = Job(JOB['JOB_QUANTITY'], item_list)
    
    order = Order(job.get_jobs())   
    
    return simpy_env, job, daily_events
    


#이벤트 정의. 고객 주문, 제조공정, 후작업, 재고기록 같은 작업 처리
#def simpy_event_processes(simpy_env, job, daily_events):
    #주요 이벤트 프로세스 설정(환경, 재고객체리스트, 제조 공정 객체 리스트, 후작업 리스트, 판매 객체, 고객 객체,  이벤트 로그 기록 리스트, I재고 정보 사전, 시나리오)



    

    

"""
def present_daytime(env_now):
    days = int(env_now // 24)
    hours = int(env_now % 24)
    minutes = int((env_now % 1) * 60)  # 소수점을 분으로 변환
    
    return f"[{days:02}:{hours:02}:{minutes:02}]"


simpy_env, job, daily_events = env.create_env(JOB, LOG_DAILY_EVENTS)

env.simpy_event_processes(simpy_env, job, daily_events)
"""