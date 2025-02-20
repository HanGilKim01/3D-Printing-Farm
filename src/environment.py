import simpy
import numpy as np
from config import *  # Assuming this imports necessary configurations
from log import *  # Assuming this imports necessary logging functionalities
from visualization import *
import random

class Print:
    
    def __init__(self, env, name, process_id, production_rate, output, postprocess):
        self.env = env
        self.name = name
        self.process_id = process_id
        self.production_rate = production_rate[0]
        self.output = output
        self.postprocess = postprocess

        self.processing_time = 24 / self.production_rate
        self.batch_size = ORDER['JOB_SIZE']  # 50개 단위 출력
        self.num_printers = MACHINE[self.process_id]["NUM_PRINTERS"]
        self.total_produced = 0
        self.total_batches = ORDER['ORDER_QUANTITY']  # 🔹 목표 batch 개수 설정 (5개)
        self.model_list = model_list  # 50개의 모델 리스트

        self.batch_counter = 1  # 전역적으로 batch 번호 관리
        self.busy_machines = [False] * self.num_printers  # 프린터 상태 (False: 쉬고 있음, True: 작업 중)

        self.machines = [simpy.Resource(env, capacity=1) for _ in range(self.num_printers)]
        self.gantt_data = gantt_data

    def is_busy(self, machine_id):
        """ 현재 기계가 사용 중인지 확인 """
        return self.busy_machines[machine_id]

    def next_available_machine(self):
        """ 쉬고 있는 프린터 중 가장 먼저 찾은 기계의 ID 반환 """
        for i in range(self.num_printers):
            if not self.is_busy(i):
                return i
        return None  # 모든 프린터가 바쁠 경우 None 반환

    def process_for_machine(self, machine_id, daily_events):
        """ 특정 프린터가 작업을 수행하는 프로세스 """
        printer_name = f"PRINTER-{machine_id + 1}"

        while self.total_produced < self.total_batches * self.batch_size:
            with self.machines[machine_id].request() as request:
                yield request

                # 🔹 목표 batch 개수를 초과하면 즉시 종료
                if self.batch_counter > self.total_batches:
                    break

                # 현재 프린터를 사용 중으로 설정
                self.busy_machines[machine_id] = True  

                # 현재 배치 번호 할당 후 증가
                current_batch_number = self.batch_counter
                self.batch_counter += 1  # 전역 batch 번호 증가

                daily_events.append("===============Print Phase===============")
                daily_events.append(f"{present_daytime(self.env.now)}: {self.name} ({printer_name}) begins producing Order {current_batch_number}, {self.batch_size} units.")

                
                
                start_time = self.env.now
                yield self.env.timeout((self.processing_time - TIME_CORRECTION) * self.batch_size)
                end_time = self.env.now

                # 50개 제품 각각 모델 부여
                produced_items = []
                for i in range(self.batch_size):
                    model = self.model_list[i % len(self.model_list)]  # 순차적 할당
                    produced_items.append({"Customer ID": current_batch_number, "Model": model})

                
                self.total_produced += self.batch_size
                daily_events.append("===============Print Result Phase===============")
                daily_events.append(f"{present_daytime(self.env.now)}: {self.output['NAME']} has been produced: {produced_items}")

                
                if isinstance(self.postprocess, list):  
                    self.postprocess[0].queue.put({"ID": current_batch_number, "Products": produced_items}) 
                else:
                    self.postprocess.queue.put({"ID": current_batch_number, "Products": produced_items})
                
                


                
                # 간트차트 데이터 저장
                self.gantt_data.append({
                    'Machine': f'Printer {machine_id + 1}',
                    'Batch ID': current_batch_number,
                    'Start Time': start_time,
                    'End Time': end_time,
                    'Model': f"Print Order {current_batch_number}", 
                    'Produced Units': self.batch_size  
                })

                # 작업 완료 후 프린터 상태 업데이트
                self.busy_machines[machine_id] = False  

                # 🔹 목표 batch 개수 도달 시 종료
                if self.batch_counter > self.total_batches:
                    daily_events.append(f"{present_daytime(self.env.now)}: Production completed! Total {self.total_batches} Orders-WIP produced.")
                    break

                # 현재 작업이 완료되었음을 로그에 추가
                daily_events.append(f"{present_daytime(self.env.now)}: {self.name} ({printer_name}) completes Order {current_batch_number}.")
                yield self.env.timeout(TIME_CORRECTION)

    def start_production(self, daily_events):
        for machine_id in range(self.num_printers):
            if not self.is_busy(machine_id):
                self.env.process(self.process_for_machine(machine_id, daily_events))

class PostProcess:
    
    def __init__(self, env, name, process_id, production_rate, output):
        self.env = env
        self.name = name
        self.process_id = process_id
        self.production_rate = 24
        self.output = output
        self.batch_size = ORDER['JOB_SIZE']
        self.num_machines = MACHINE[self.process_id]["NUM_POST_PROCESSORS"]  # 🔹 기계 2대 사용
        self.processing_time = (24 / self.production_rate) # 🔹 병렬 생산 고려
        self.total_produced = 0
        self.order_quantity = ORDER['ORDER_QUANTITY'] * self.batch_size


        self.busy_machines = [False] * self.num_machines

        # 🔹 PostProcess 기계 & queue 추가
        self.machines = [simpy.Resource(env, capacity=1) for _ in range(self.num_machines)]
        self.queue = simpy.Store(env)  # 🔹 batch를 받을 queue 생성
        self.gantt_data = gantt_data
        self.global_unit_counter = 0

    def is_busy(self, machine_id):
        """ 현재 기계가 사용 중인지 확인 """
        return self.busy_machines[machine_id]

    def next_available_machine(self):
        """ 쉬고 있는 프린터 중 가장 먼저 찾은 기계의 ID 반환 """
        for i in range(self.num_machines):
            if not self.is_busy(i):
                return i
        return None  # 모든 프린터가 바쁠 경우 None 반환
    
    def process_for_machine(self, machine_id, daily_events):
        """ 특정 기계가 queue에서 batch를 받아와 병렬적으로 후처리를 수행 """
        machine_name = f"Machine {machine_id + 1}"
        current_order = 1  # 첫 번째 Order부터 시작

        while self.total_produced < self.order_quantity:  # 전체 생산량 목표가 다 차기 전까지 반복
            batch = yield self.queue.get()  # queue에서 batch 꺼내기
            batch_id = batch['ID']
            products = batch['Products']

            # 각 unit을 개별적으로 처리
            for unit_id in enumerate(products):
                if self.total_produced >= self.order_quantity:
                    break  # 목표 생산량 달성 시 종료

                with self.machines[machine_id].request() as request:
                    yield request  # 기계 사용 요청

                    self.busy_machines[machine_id] = True  # 기계 사용 중 상태로 변경
                    self.global_unit_counter += 1  # unit 번호 증가
                    current_unit_id = self.global_unit_counter  # 현재 처리할 unit의 고유 ID

                    start_time = self.env.now
                    daily_events.append(f"{present_daytime(start_time)}: Order {current_order} - Unit {current_unit_id} started on {machine_name}!")

                    # 후처리 진행 (기계가 처리하는 시간)
                    yield self.env.timeout(self.processing_time - TIME_CORRECTION)

                    # 작업 완료 후 결과 출력
                    daily_events.append(f"{present_daytime(self.env.now)}: {machine_name} finished processing Unit {current_unit_id} of Order {current_order}!")

                    self.total_produced += 1  # 생산량 증가
                    self.busy_machines[machine_id] = False  # 기계 상태를 유휴로 변경

                    # 🔹 batch_size만큼 처리하면 결과 출력
                    if self.total_produced % self.batch_size == 0:
                        daily_events.append("===============PostProcessResult Phase================")
                        daily_events.append(f"{present_daytime(self.env.now)}: {self.output['NAME']} has been produced: Order {current_order}")
                        current_order += 1
                        self.global_unit_counter = 0

                    yield self.env.timeout(TIME_CORRECTION)  # 시간 보정

            # 한 Order가 끝났을 때, 다음 Order로 넘어감
            

        # 전체 생산량 목표를 달성했으면 종료
        daily_events.append(f"{present_daytime(self.env.now)}: Post-processing completed for all orders!")

    def start_processing(self, daily_events):
        """ 각 기계가 queue에서 batch를 꺼내 처리하도록 설정 """
        for machine_id in range(self.num_machines):
            if not self.is_busy(machine_id):
                self.env.process(self.process_for_machine(machine_id, daily_events))


"""
class PostProcess:
    
    def __init__(self, env, name, process_id, production_rate, output):
        # Initialize PostProcess
        self.env = env
        self.name = name
        self.process_id = process_id
        self.production_rate = production_rate[1]
        self.output = output

        self.batch_size = ORDER['JOB_SIZE']
        self.num_machines = MACHINE[self.process_id]["NUM_POST_PROCESSORS"]
        self.processing_time = 24 / self.production_rate
        self.total_produced = 0
        self.batch_number = 1
        self.order_quantity = ORDER['ORDER_QUANTITY'] * self.batch_size

        # PostProcess 기계 & queue 추가
        self.machines = [simpy.Resource(env, capacity=1) for _ in range(self.num_machines)]
        self.queue = simpy.Store(env)  # 🔹 batch를 받을 queue 생성
        self.gantt_data = gantt_data
    
    def process_for_machine(self, machine_id, daily_events):

        machine_name = f"PostProcess-{machine_id + 1}"


        while self.total_produced < self.order_quantity:

            batch = yield self.queue.get()
            

            with self.machines[machine_id].request() as request:
                yield request  # 기계 사용 요청 (빈자리 있을 때만 실행됨)
                
                start_time = self.env.now
                
                daily_events.append("===============PostProcess Phase================")
                daily_events.append(f"{present_daytime(start_time)}: Order {batch['ID']} Post-processing started on Machine {machine_name}!")
                
                
            # 후처리 진행
                yield self.env.timeout(self.processing_time - TIME_CORRECTION)  
                end_time = self.env.now
            # 🔹 총 생산량 업데이트
                self.total_produced += self.batch_size

            # 🔹 batch 단위로 결과 출력
                if self.total_produced >= self.batch_size:
                    daily_events.append("===============PostProcessResult Phase================")
                    daily_events.append(f"{present_daytime(self.env.now)}: {self.output['NAME']} has been produced: Order {batch['ID']}")
                    

                    
                    
                    self.gantt_data.append({
                    'Machine': f'PostProcess {machine_id + 1}',
                    'Batch ID': batch['ID'],
                    'Start Time': start_time,
                    'End Time': end_time,
                    'Model': f"PostProcess Batch {batch['ID']}",
                    'Produced Units': self.batch_size
                        })

                self.batch_number += 1
                    

            # 🔹 주문량만큼 생산되면 종료
                if self.total_produced >= self.order_quantity:
                    daily_events.append(f"{present_daytime(self.env.now)}: Order completed! {self.order_quantity} units produced. Stopping production.")
                    break

                yield self.env.timeout(TIME_CORRECTION)  # 시간 보정
    
    
    
    def start_processing(self, daily_events):
       
        for machine_id in range(self.num_machines):
            self.env.process(self.process_for_machine(machine_id, daily_events))
"""


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




class Order:
    def __init__(self, order_id, jobs):
        self.order_id = order_id
        self.jobs = jobs  # 이 주문에 포함된 Job 리스트

    




#환경 생성 함수
def create_env(ITEM, MACHINE, daily_events):
    # Function to create the simulation environment and necessary objects
    simpy_env = simpy.Environment()  # Create a SimPy environment

    # Create an inventory for each item
    
    # Create stakeholders (Customer) 고객 객체 생성
    customer = Customer(simpy_env, "CUSTOMER", ITEM[0]["ID"])

    postprocessor = [PostProcess(simpy_env, "Post-process", MACHINE[1]["ID"],
                                   [MACHINE[machine_id]["PRODUCTION_RATE"] for machine_id in MACHINE], MACHINE[1]["OUTPUT"],  
                                   )]

    printer = [Print(simpy_env, "3D-Printing" , MACHINE[0]["ID"],
                                   [MACHINE[machine_id]["PRODUCTION_RATE"] for machine_id in MACHINE],
                                   MACHINE[0]["OUTPUT"], 
                                   postprocessor)]
    
    

    
    return simpy_env, printer, postprocessor, customer, daily_events
    


#이벤트 정의. 고객 주문, 제조공정, 후작업, 재고기록 같은 작업 처리
def simpy_event_processes(simpy_env, printer, postprocessor, customer, daily_events, ITEM, scenario):
    #주요 이벤트 프로세스 설정(환경, 재고객체리스트, 제조 공정 객체 리스트, 후작업 리스트, 판매 객체, 고객 객체,  이벤트 로그 기록 리스트, I재고 정보 사전, 시나리오)



    for production in printer:
        for machine_id in range(production.num_printers): 
            simpy_env.process(production.process_for_machine(machine_id, daily_events)) 

    #for production in PrintList:
        #simpy_env.process(production.process_for_machine(daily_events))
    #제조 공정 실행. 모든 제조 공정 객체(productionlist)에 대해 processitems메서드 실행
    #process_itmes 제조 공정 입력 재료 소비하고 산출물 생성
    
    for postprocess in postprocessor:
        for machine_id in range(postprocess.num_machines) :
            simpy_env.process(postprocess.process_for_machine(machine_id, daily_events))
    

    
    #재고 상태 기록



def present_daytime(env_now):
    days = int(env_now // 24)
    hours = int(env_now % 24)
    minutes = int((env_now % 1) * 60)  # 소수점을 분으로 변환
    
    return f"[{days:02}:{hours:02}:{minutes:02}]"



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