import simpy
import functools
import numpy as np
from config import *  # Assuming this imports necessary configurations
from log import *  # Assuming this imports necessary logging functionalities
from visualization import *
import random

""" csv 파일 로드하는 형식
class Print:
    def __init__(self, env, name, process_id, production_rate, output, output_inventory, model_file):
        # Initialize production process
        self.env = env
        self.name = name
        self.process_id = process_id
        self.production_rate = production_rate[0]
        self.output = output
        self.output_inventory = output_inventory
        self.processing_time = 24 / self.production_rate
        self.batch_size = 50  # 50개 단위 출력
        self.num_printers = MACHINE[self.process_id]["NUM_PRINTERS"]
        self.total_produced = 0
        self.order_quantity = ORDER['ORDER_QUANTITY']*ORDER['JOB_SIZE']
        self.model_file = model_file


        # 프린터 개수만큼 simpy 자원 생성
        self.machines = [simpy.Resource(env, capacity=1) for _ in range(self.num_printers)]

        # 🔹 CSV에서 모델 데이터 불러오기
        self.model_data = self.load_model_data(model_file)

    def load_model_data(self, model_file):
       
        try:
            df = pd.read_csv(model_file)  # CSV 파일 읽기
            return df.to_dict(orient="records")  # 리스트 딕셔너리 형태로 변환
        except FileNotFoundError:
            print(f"Error: {model_file} 파일을 찾을 수 없습니다.")
            return []

    def process_for_machine(self, machine_id, daily_events):
       
        printer_name = f"PRINTER-{machine_id + 1}"  # "PRINTER-1", "PRINTER-2" 형식
        while self.total_produced < self.order_quantity:
            with self.machines[machine_id].request() as request:
                yield request

                # 생산 시작
                daily_events.append("===============Build Phase===============")
                daily_events.append(f"{present_daytime(self.env.now)}: {self.name} ({printer_name}) begins producing {self.batch_size} units.")

                yield self.env.timeout((self.processing_time - TIME_CORRECTION) * self.batch_size)

                # 🔹 50개 생산할 때마다 모델 ID 부여
                produced_items = []
                for _ in range(self.batch_size):
                    model = random.choice(self.model_data)  # 랜덤 모델 선택
                    produced_items.append(model["MODEL_ID"])  # 생산된 모델 ID 저장

                self.output_inventory.update_inven_level(self.batch_size, "ON_HAND", daily_events)
                self.total_produced += self.batch_size

                daily_events.append("===============Build Result Phase===============")
                daily_events.append(f"{present_daytime(self.env.now)}: {self.output['NAME']} has been produced: {self.batch_size} units by {printer_name}")
                daily_events.append(f"Produced Models: {produced_items}")  # 🔹 어떤 모델이 생산되었는지 기록

                if self.total_produced >= self.order_quantity:  # 🔹 주문량만큼 생산되면 종료
                    daily_events.append(f"{present_daytime(self.env.now)}: Order completed! {self.order_quantity} units produced. Stopping production.")
                    break

                yield self.env.timeout(TIME_CORRECTION)  # Time correction

    def start_production(self, daily_events):
       
        for machine_id in range(self.num_printers):
            self.env.process(self.process_for_machine(machine_id, daily_events))
"""



class Print:
    
    def __init__(self, env, name, process_id, production_rate, output, output_inventory):
        self.env = env
        self.name = name
        self.process_id = process_id
        self.production_rate = production_rate[0]
        self.output = output
        self.output_inventory = output_inventory
        self.processing_time = 24 / self.production_rate
        self.batch_size = ORDER['JOB_SIZE']  # 50개 단위 출력
        self.num_printers = MACHINE[self.process_id]["NUM_PRINTERS"]
        self.total_produced = 0
        self.order_quantity = ORDER['ORDER_QUANTITY']*ORDER['JOB_SIZE']
        self.model_list = model_list  # 50개의 모델 리스트

        self.batch_numbers = [1, 2] 

        self.machines = [simpy.Resource(env, capacity=1) for _ in range(self.num_printers)]
        self.gantt_data = gantt_data

    

    def process_for_machine(self, machine_id, daily_events):
        
        printer_name = {i: f"PRINTER-{i+1}" for i in range(MACHINE[0]["NUM_PRINTERS"])}[machine_id]
        

        while self.total_produced < self.order_quantity:
            with self.machines[machine_id].request() as request:
                yield request

                if self.output_inventory.on_hand_inventory + self.batch_size > self.output_inventory.capacity_limit:
                    daily_events.append(f"{present_daytime(self.env.now)}: Stop {self.name} ({printer_name}) due to full inventory.")
                    break

                daily_events.append("===============Print Phase===============")
                daily_events.append(f"{present_daytime(self.env.now)}: {self.name} ({printer_name}) begins producing batch {self.batch_numbers[machine_id]},{self.batch_size} units.")
                start_time = self.env.now
                yield self.env.timeout((self.processing_time - TIME_CORRECTION) * self.batch_size)
                end_time = self.env.now

                # 50개 제품 각각 모델 부여
                produced_items = []
                for i in range(self.batch_size):
                    model = self.model_list[i % len(self.model_list)]  # 순차적 할당
                    produced_items.append({"ID": self.batch_numbers[machine_id] , "Model": model})
                    

                self.output_inventory.update_inven_level(self.batch_size, "ON_HAND", daily_events)
                self.total_produced += self.batch_size
                daily_events.append("===============Print Result Phase===============")
                daily_events.append(f"{present_daytime(self.env.now)}: {self.output['NAME']} has been produced: {produced_items}")

            
                self.gantt_data.append({
                    'Machine': f'Printer {machine_id + 1}',
                    'Batch ID': self.batch_numbers[machine_id] - 2,
                    'Start Time': start_time,
                    'End Time': end_time,
                    'Model':f"Print Batch {self.batch_numbers[machine_id] }",  # 첫 모델만 기록 (배치 이름 사용)
                    'Produced Units': self.batch_size  # 생산된 유닛 수 추가
                })

                if self.total_produced >= self.order_quantity:
                    daily_events.append(f"{present_daytime(self.env.now)}: Order completed! {self.batch_numbers[machine_id]} batches produced.")
                    break

                
                self.batch_numbers[machine_id] += 2




                daily_events.append(f"{present_daytime(self.env.now)}: {self.name} ({printer_name}) completes batch {self.batch_numbers[machine_id] - 2}.")
                yield self.env.timeout(TIME_CORRECTION)

    def start_production(self, daily_events):
        for machine_id in range(self.num_printers):
            self.env.process(functools.partial(self.process_for_machine, machine_id, daily_events))

# 모델 리스트 정의
model_list = [f"Aligner_Model_{i+1}" for i in range(50)]
gantt_data = []

#모델에 따른 잡 몇개 함수
#잡에 따른 클래스 or 함수
#def or class > random?? > 


class PostProcess:
    
    def __init__(self, env, name, process_id, production_rate, output, input_inventories, qnty_for_input_item, output_inventory, ):
        # Initialize production process
        self.env = env
        self.name = name
        self.process_id = process_id
        self.production_rate = production_rate
        self.output = output
        self.input_inventories = input_inventories
        self.qnty_for_input_item = qnty_for_input_item
        self.output_inventory = output_inventory
        self.processing_time = 24 / self.production_rate
        self.print_stop = True
        self.print_limit = True
        self.batch_size = ORDER['JOB_SIZE']
        self.num_printers = MACHINE[self.process_id]["NUM_POST_PROCESSORS"]
        self.processing_time = (24 / self.production_rate) / self.num_printers
        self.total_produced = 0
        self.order_quantity = ORDER['ORDER_QUANTITY']*ORDER['JOB_SIZE']

        # 후처리 기계 4대 운영
        self.machines = [simpy.Resource(env, capacity=1) for _ in range(self.num_printers)]
        self.batch_number = 1
        self.gantt_data = gantt_data
        


    def process_for_machine(self, machine_id, daily_events):
        """
        각 기계가 독립적으로 생산을 수행하지만, 생산량을 함께 집계하여 50개 단위로 결과 출력
        """
        
        while True:
            with self.machines[machine_id].request() as request:
                yield request
   

                # 입력 재고 확인 (필요한 재고가 없으면 대기)
                shortage_check = any(inven.on_hand_inventory < input_qnty
                                     for inven, input_qnty in zip(self.input_inventories, self.qnty_for_input_item))

                if shortage_check:
                    if self.print_stop:
                        daily_events.append(f"{present_daytime(self.env.now)}: Stop {self.name} due to input shortage")
                    self.print_stop = False
                    yield self.env.timeout(1)  # 1시간 대기 후 재확인
                    continue

                # 출력 재고 확인 (최대 용량 초과 시 대기)
                if self.output_inventory.on_hand_inventory >= self.output_inventory.capacity_limit:
                    if self.print_limit:
                        daily_events.append(f"{present_daytime(self.env.now)}: Stop {self.name} due to full inventory")
                    self.print_limit = False
                    yield self.env.timeout(1)  # 1시간 대기 후 재확인
                    continue

                
                
                
                #yield self.env.timeout(self.processing_time - TIME_CORRECTION)  # 병렬 생산 반영
                
                if self.total_produced == 0:
                    start_time = self.env.now
                    
                    daily_events.append("===============PostProcess Phase================")
                    daily_events.append(f"{present_daytime(start_time)}: Batch {self.batch_number} Post-processing started!")
                # 입력 재고 감소
                for inven, input_qnty in zip(self.input_inventories, self.qnty_for_input_item):
                    inven.update_inven_level(-input_qnty, "ON_HAND", daily_events)

                yield self.env.timeout(self.processing_time - TIME_CORRECTION)  # 병렬 생산 반영

                # 출력 재고 증가
                self.output_inventory.update_inven_level(1, "ON_HAND", daily_events)

                # 🔹 총 생산량 업데이트
                self.total_produced += 1

                # 🔹 50개 단위로 결과 출력
                if self.total_produced >= self.batch_size:
                    daily_events.append("===============PostProcessResult Phase================")
                    daily_events.append(f"{present_daytime(self.env.now)}: {self.output['NAME']} has been produced: Batch {self.batch_number}")

                    end_time = self.env.now
                    
                    self.gantt_data.append({
                        'Machine': f'PostProcess',
                        'Batch ID': self.batch_number,
                        'Start Time': start_time,
                        'End Time': end_time,
                        'Model': f"PostProcess Batch {self.batch_number}",
                        'Produced Units': self.batch_size
                        })

                
                    
                    self.batch_number += 1
                    self.total_produced = 0  # 생산량 초기화
                    
                    
                    
                
                if self.total_produced >= self.order_quantity:  # 🔹 주문량만큼 생산되면 종료
                    daily_events.append(f"{present_daytime(self.env.now)}: Order completed! {self.order_quantity} units produced. Stopping production.")
                    break

                yield self.env.timeout(TIME_CORRECTION)  # 시간 보정

    def start_production(self, daily_events):
        """
        각 기계를 독립적으로 실행
        """
        for machine_id in range(self.num_printers):
            self.env.process(self.process_for_machine(machine_id, daily_events))



class Customer:
    def __init__(self, env, name, item_id,):
        # Initialize customer object
        self.env = env
       
        self.current_job_id = 0  # Job ID 초기값
        self.last_assigned_printer = -1 # 마지막으로 할당된 프린터 ID
        self.name = name
        self.item_id = item_id
        
        self.temp_order_list = []       # 누적된 주문(Order)들을 임시로 저장

    def order_product(self, product_inventory, daily_events, scenario):
        #제품 주문 생성, 주문량 판매 프로세스로 전달(,Sales객체-주문처리, 재고객체, 이벤트로그리스트, 주문량 생성 시나리오(분포유형))
        """
        Place orders for products to the sales process.
        """
        while True:
            # Generate a random demand quantity
            ORDER["ORDER_QUANTITY"] = ORDER_QTY_FUNC(scenario)
            #scenario기반으로 무작위 수요량 생성하고 결과를 ORDER["ORDER_QUANTITY"]에 저장
            # Receive demands and initiate delivery process
            
            yield self.env.timeout(ORDER["CUST_ORDER_CYCLE"] * 24)
            #고객 주문 주기(custordercycle)에 따라 다음 주문 생성까지 대기


class Job:
    def __init__(self, env, job_id, config):
        self.env = env  # SimPy 환경 객체
        self.job_id = job_id  # Job ID
        self.size = np.random.randint(*config["SIZE_RANGE"])
        
class Order:
    def __init__(self, order_id, jobs):
        self.order_id = order_id
        self.jobs = jobs  # 이 주문에 포함된 Job 리스트
        
        
        


class Inventory:
    def __init__(self, env, item_id,):
        # Initialize inventory object
        self.env = env
        self.item_id = item_id  # 0: product; others: WIP or material
        # Initial inventory level
        self.on_hand_inventory = ITEM[self.item_id]['INIT_LEVEL']
        # Inventory in transition (e.g., being delivered)
        self.capacity_limit = INVEN_LEVEL_MAX  # Maximum capacity of the inventory
        #재고 용량 제한. 최대값은 INVEN_LEVEL_MAX로 설정
        self.daily_inven_report = [f"Day {self.env.now // 24+1}", ITEM[self.item_id]['NAME'],
                                   ITEM[self.item_id]['TYPE'], self.on_hand_inventory, 0, 0, 0, 0]
        #하루동안의 재고 상태 기록 템플릿


    #고객 수요량 업데이트, 해당 이벤트 기록 매서드
    def update_demand_quantity(self, daily_events):
        """
        Update the demand quantity and log the event.
        """
        #현재 발생 고객 주문 이벤트를 문자열로 생성하여 daily_events리스트에 추가
        daily_events.append(
            f"{present_daytime(self.env.now)}: Customer order of {ITEM[0]['NAME']}                                 : {ORDER['ORDER_QUANTITY']} order ")
        daily_events.append(
            f"{present_daytime(self.env.now)}: Total amount of {ITEM[0]['NAME']} to be produced                    : {ORDER['ORDER_QUANTITY']*ORDER['JOB_SIZE']} units ")

    #재고 수준 업데이트. 재고 변경량 적용, 이벤트 기록.
    def update_inven_level(self, quantity_of_change, inven_type, daily_events):
        if inven_type == "ON_HAND":
            # Update on-hand inventory
            
            self.on_hand_inventory += quantity_of_change
            #보유 재고에 변화 반영

            # Check if inventory exceeds capacity limit
            if self.on_hand_inventory > self.capacity_limit:
                #보유 재고에 변화 반영했는데, 만약 최대 용량을 초과한 경우
                daily_events.append(
                    f"{present_daytime(self.env.now)}: Due to the upper limit of the inventory, {ITEM[self.item_id]['NAME']} is wasted: {self.on_hand_inventory - self.capacity_limit}")
                self.on_hand_inventory = self.capacity_limit
                #초과 재고는 낭비로 간주하여 기록하고, 버림
                #보유 재고를 용량 한도로 제한
            


        self._update_report(quantity_of_change, inven_type)
        #재고 변화 관련 보고서 업데이트. quantity of change와 inventype기반으로 재고 상태 기록

    #보유/운송 중 재고 변화량을 보고서에 반영
    #quantityofchange 양:입고 음:출고 / inventype on-hand or in-transit
    def _update_report(self, quantity_of_change, inven_type):
        """
        Update the daily inventory report based on the quantity of change.
        """
        if inven_type == "ON_HAND":
            if quantity_of_change > 0:
                # Income Inventory
                self.daily_inven_report[4] += quantity_of_change

            else:
                # Outgoing Invnetory
                self.daily_inven_report[5] -= quantity_of_change



def create_env(ITEM, MACHINE, daily_events):
    # Function to create the simulation environment and necessary objects
    simpy_env = simpy.Environment()  # Create a SimPy environment

    # Create an inventory for each item
    inventoryList = []
    for i in ITEM.keys():
        inventoryList.append(Inventory(simpy_env, i ))



    # Create stakeholders (Customer) 고객 객체 생성
    customer = Customer(simpy_env, "CUSTOMER", ITEM[0]["ID"])

    BuildList = []

    BuildList.append(Print(simpy_env, "3D-Printing" , MACHINE[0]["ID"],
                                   [MACHINE[machine_id]["PRODUCTION_RATE"] for machine_id in MACHINE],
                                   MACHINE[0]["OUTPUT"], 
                                   inventoryList[MACHINE[0]["OUTPUT"]["ID"]]))
    
    postprocessList = []
    postprocessList.append(PostProcess(simpy_env, "Post-process", MACHINE[1]["ID"],
                                   MACHINE[1]["PRODUCTION_RATE"], MACHINE[1]["OUTPUT"], 
                                   [inventoryList[j["ID"]] for j in MACHINE[1]["INPUT_TYPE_LIST"]], 
                                   MACHINE[1]["QNTY_FOR_INPUT_ITEM"], 
                                   inventoryList[MACHINE[1]["OUTPUT"]["ID"]]))

    
    return simpy_env, inventoryList, BuildList, postprocessList, customer, daily_events
    

# Event processes for SimPy simulation
#이벤트 정의. 고객 주문, 제조공정, 후작업, 재고기록 같은 작업 처리
def simpy_event_processes(simpy_env, inventoryList, BuildList, postprocessList, customer, daily_events, ITEM, scenario):
    #주요 이벤트 프로세스 설정(환경, 재고객체리스트, 제조 공정 객체 리스트, 후작업 리스트, 판매 객체, 고객 객체,  이벤트 로그 기록 리스트, I재고 정보 사전, 시나리오)

    simpy_env.process(customer.order_product(
         inventoryList[ITEM[0]["ID"]], daily_events, scenario["DEMAND"]))
    #고객 객체(customer)가 제품을 주문하는 프로세스를 Simpy환경에서 실행.
    #order_product 메서드 호출 > 특정 제품 주문(sales-판매객체,주문대상 재고 객체, 이벤트 로그 리스트, 시나리오)
    
    for production in BuildList:
        for machine_id in range(production.num_printers): 
            simpy_env.process(production.process_for_machine(machine_id, daily_events)) 

    #for production in BuildList:
        #simpy_env.process(production.process_for_machine(daily_events))
    #제조 공정 실행. 모든 제조 공정 객체(productionlist)에 대해 processitems메서드 실행
    #process_itmes 제조 공정 입력 재료 소비하고 산출물 생성
    
    for postprocess in postprocessList:
        simpy_env.process(postprocess.process_for_machine(machine_id, daily_events))
    

    
    #재고 상태 기록



def present_daytime(env_now):
    days = int(env_now // 24)
    hours = int(env_now % 24)
    minutes = int((env_now % 1) * 60)  # 소수점을 분으로 변환
    
    return f"[{days:02}:{hours:02}:{minutes:02}]"
