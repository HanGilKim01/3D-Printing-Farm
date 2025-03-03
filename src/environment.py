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
        self.model_list = customer_model_list  # 50개의 모델 리스트

        self.batch_counter = 1 # 전역적으로 batch 번호 관리
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

                if self.batch_counter > self.total_batches:
                    daily_events.append(f"{present_daytime(self.env.now)}: Production completed! Total {self.total_batches} Orders-WIP produced.")
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

                
                customer_model_list_for_batch = [item for item in self.model_list if item["Customer ID"] == current_batch_number]
                for customer_model in customer_model_list_for_batch:
                     produced_items.append({"Customer ID": customer_model["Customer ID"], "Model": customer_model["Model"]})
                    #produced_items.append({"Customer ID": current_batch_number, "Model": customer_model["Model"]})

                #print(produced_items)


                
                
                self.total_produced += len(produced_items) #self.batch_size
                daily_events.append("===============Print Result Phase===============")
                daily_events.append(f"{present_daytime(self.env.now)}: {self.output['NAME']} has been produced: {produced_items}")

                
                if isinstance(self.postprocess, list):
                    for produced_item in produced_items:
                        self.postprocess[0].queue.put(produced_item) 
                else:
                    for produced_item in produced_items:
            # produced_item에서 "Customer ID"와 "Model"을 따로 넣기
                        self.postprocess.queue.put(produced_item)


                



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
                

                # 현재 작업이 완료되었음을 로그에 추가
                daily_events.append(f"{present_daytime(self.env.now)}: {self.name} ({printer_name}) completes Order {current_batch_number}.")
                yield self.env.timeout(TIME_CORRECTION)

    def start_production(self, daily_events):
        for machine_id in range(self.num_printers):
            if not self.is_busy(machine_id):
                self.env.process(self.process_for_machine(machine_id, daily_events))



class PostProcess:
    
    def __init__(self, env, name, process_id, production_rate, output, queue):
        self.env = env
        self.name = name
        self.process_id = process_id
        self.production_rate = production_rate[1]
        self.output = output

        self.batch_size = ORDER['JOB_SIZE']
        self.num_machines = MACHINE[self.process_id]["NUM_POST_PROCESSORS"]  # 🔹 기계 2대 사용
        self.processing_time = 24 / self.production_rate # 🔹 병렬 생산 고려
        self.total_produced = 0
        self.total_quantity = ORDER['ORDER_QUANTITY'] * self.batch_size


        self.busy_machines = [False] * self.num_machines

        # 🔹 PostProcess 기계 & queue 추가
        self.machines = [simpy.Resource(env) for _ in range(self.num_machines)]
        self.queue = queue  # 🔹 batch를 받을 queue 생성
        self.gantt_data = gantt_data
        self.global_unit_counter = 0
        self.completed_orders = []

    def is_busy(self, machine_id):
        
        return self.busy_machines[machine_id]

    def next_available_machine(self):
        
        for i in range(self.num_machines):
            if not self.is_busy(i):
                return i
        return None  # 모든 프린터가 바쁠 경우 None 반환
    

    def process_order(self, order, daily_events):
        order = yield self.queue.get()
        #print(f"Received order data: {order}")
        order_id = order["Customer ID"]
        products = order["Model"]
        units_to_process = len(products)  # 현재 Order의 유닛 개수


        units_processed = 0 
        tasks = []
        
        while units_processed < units_to_process:
            for machine_id in range(self.num_machines):
                if units_processed < units_to_process:  # 남은 유닛이 있을 경우에만 실행
                    
                    product_data = products[units_processed]
                    task = self.env.process(self.process_unit(order_id, machine_id, product_data, daily_events))
                    tasks.append(task)
                    units_processed += 1  # 하나의 기계가 한 유닛을 처리할 예정

        # 🔹 모든 유닛이 처리될 때까지 대기
            yield simpy.AllOf(self.env, tasks)

        daily_events.append("===============Order Complete===============")
        daily_events.append(f"{present_daytime(self.env.now)}: Order {order_id} post-processing completed!")
        
        self.completed_orders.append(order)

        
    def process_unit(self, order_id, machine_id, product_data, daily_events):
        
        machine_name = f"Machine {machine_id + 1}"

        self.global_unit_counter += 1
        current_unit_id = self.global_unit_counter
        product_name = product_data['Product']
        

        
        with self.machines[machine_id].request() as request:
            yield request  # 기계 사용 요청

            self.busy_machines[machine_id] = True

            daily_events.append("===============PostProcess Start===============")
            daily_events.append(f"{present_daytime(self.env.now)}: {machine_name} starts processing Product {product_name} of Order {order_id}.")

            start_time = self.env.now
            yield self.env.timeout(self.processing_time - TIME_CORRECTION)  # 1개 처리 시간
            end_time = self.env.now


            self.gantt_data.append({
                    'Machine': f'PostProcess {machine_id + 1}',
                    'Start Time': start_time,
                    'End Time': end_time,
                    'Model': f"Product {product_name} of Order {order_id}",
                    'Produced Units': self.batch_size
                        })


            self.total_produced += 1
            self.busy_machines[machine_id] = False

            daily_events.append("===============PostProcess Result===============")
            daily_events.append(f"{present_daytime(self.env.now)}: {machine_name} finished Product {product_name} of Order {order_id}!")

                #if self.total_produced >= self.total_quantity:
                 #   daily_events.append(f"{present_daytime(self.env.now)}: All Orders completed! Total {self.total_quantity} units processed.")
                  #  return  # 전체 생산 완료 시 종료
    def start_processing(self, daily_events):
        
        all_orders = []
        while len(self.queue.items) > 0 :
            order = yield self.queue.get()
            all_orders.append(order) 
        for order in all_orders : 
            yield self.env.process(self.process_order(order, daily_events)) 

        while len(self.completed_orders) < ORDER['ORDER_QUANTITY']:
            yield self.env.timeout(1)
    


class Customer:
    def __init__(self, env, name, item_id,):
        # Initialize customer object
        self.env = env
       
        self.current_job_id = 0  # Job ID 초기값
        self.last_assigned_printer = -1 # 마지막으로 할당된 프린터 ID
        self.name = name
        self.item_id = item_id
        
  
    def order_product(self, daily_events, scenario):
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

    

class Job :
    def __init__(self):
        pass



class Item :
    def __init__(self):
        pass



#환경 생성 함수
def create_env(ITEM, MACHINE, daily_events):
    # Function to create the simulation environment and necessary objects
    simpy_env = simpy.Environment()  # Create a SimPy environment

    # Create an inventory for each item
    
    # Create stakeholders (Customer) 고객 객체 생성
    customer = Customer(simpy_env, "CUSTOMER", ITEM[0]["ID"])

    postprocessor = [PostProcess(simpy_env, "Post-process", MACHINE[1]["ID"],
                                   [MACHINE[machine_id]["PRODUCTION_RATE"] for machine_id in MACHINE], MACHINE[1]["OUTPUT"], simpy.Store(simpy_env),  
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
            simpy_env.process(postprocess.process_order(machine_id, daily_events))
    

    
    #재고 상태 기록



def present_daytime(env_now):
    days = int(env_now // 24)
    hours = int(env_now % 24)
    minutes = int((env_now % 1) * 60)  # 소수점을 분으로 변환
    
    return f"[{days:02}:{hours:02}:{minutes:02}]"

