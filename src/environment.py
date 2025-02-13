import simpy
import functools
import numpy as np
from config import *  # Assuming this imports necessary configurations
from log import *  # Assuming this imports necessary logging functionalities
from visualization import *



class Inventory:
    def __init__(self, env, item_id,):
        # Initialize inventory object
        self.env = env
        self.item_id = item_id  # 0: product; others: WIP or material
        # Initial inventory level
        self.on_hand_inventory = I[self.item_id]['INIT_LEVEL']
        # Inventory in transition (e.g., being delivered)
        self.capacity_limit = INVEN_LEVEL_MAX  # Maximum capacity of the inventory
        #재고 용량 제한. 최대값은 INVEN_LEVEL_MAX로 설정
        # Daily inventory report template:
        '''
        Day / Inventory_Name / Inventory_Type / Inventory at the start of the day / Income_Inventory(Onhand) / Outgoing_inventory(Onhand) / Inventory at the end of the day
        '''
        self.daily_inven_report = [f"Day {self.env.now // 24+1}", I[self.item_id]['NAME'],
                                   I[self.item_id]['TYPE'], self.on_hand_inventory, 0, 0, 0, 0]
        #하루동안의 재고 상태 기록 템플릿
       

    #고객 수요량 업데이트, 해당 이벤트 기록 매서드
    def update_demand_quantity(self, daily_events):
        """
        Update the demand quantity and log the event.
        """
        #현재 발생 고객 주문 이벤트를 문자열로 생성하여 daily_events리스트에 추가
        daily_events.append(
            f"{present_daytime(self.env.now)}: Customer order of {I[0]['NAME']}                                 : {I[0]['DEMAND_QUANTITY']} order ")
        daily_events.append(
            f"{present_daytime(self.env.now)}: Total amount of {I[0]['NAME']} to be produced                    : {I[0]['DEMAND_QUANTITY']*50} units ")

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
                    f"{present_daytime(self.env.now)}: Due to the upper limit of the inventory, {I[self.item_id]['NAME']} is wasted: {self.on_hand_inventory - self.capacity_limit}")
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

        


class Production:
    def __init__(self, env, name, process_id, production_rate, output, output_inventory):
        # Initialize production process
        self.env = env
        self.name = name
        self.process_id = process_id
        self.production_rate = production_rate[0]
        self.output = output
        self.output_inventory = output_inventory
        self.processing_time = 24 / self.production_rate
        self.print_stop = True
        self.print_limit = True
        self.batch_size = 50 #50개 단위 출력
        self.num_printers = P[self.process_id]["NUM_PRINTERS"]
        self.total_produced = 0
        self.order_quantity = I[0]['DEMAND_QUANTITY']*50


        self.machines = [simpy.Resource(env, capacity=1) for _ in range(self.num_printers)]

    

    def process_for_machine(self, machine_id, daily_events):
        """
        각 프린터가 독립적으로 50개씩 생산하는 함수
        """
        printer_name = M1[machine_id]["NAME"]
        while self.total_produced < self.order_quantity:
            with self.machines[machine_id].request() as request:
                yield request

                inven_upper_limit_check = (
                    self.output_inventory.on_hand_inventory + self.batch_size > self.output_inventory.capacity_limit)

                if inven_upper_limit_check:
                    daily_events.append("===============Stop Process Phase===============")
                    daily_events.append(f"{present_daytime(self.env.now)}: Stop {self.name} ({printer_name}) due to full inventory.")
                    break
                    #yield self.env.timeout(1)  # Check upper limit every hour


                else:
                    daily_events.append("===============Build Phase===============")
                    daily_events.append(f"{present_daytime(self.env.now)}: {self.name} ({printer_name}) begins producing {self.batch_size} units.")
                    yield self.env.timeout((self.processing_time - TIME_CORRECTION) * self.batch_size)

                    self.output_inventory.update_inven_level(self.batch_size, "ON_HAND", daily_events)
                    self.total_produced += self.batch_size 


                    daily_events.append("===============Build Result Phase===============")
                    daily_events.append(f"{present_daytime(self.env.now)}: {self.output['NAME']} has been produced: {self.batch_size} units by Machine {machine_id}")

                    if self.total_produced >= self.order_quantity:  # 🔹 주문량만큼 생산되면 종료
                        daily_events.append(f"{present_daytime(self.env.now)}: Order completed! {self.order_quantity} units produced. Stopping production.")
                        break

                    yield self.env.timeout(TIME_CORRECTION)  # Time correction

    def start_production(self, daily_events):
        """
        각 프린터에 대해 생산 프로세스를 개별적으로 시작
        """
        for machine_id in range(self.num_printers):
            self.env.process(functools.partial(self.process_for_machine, machine_id, daily_events))

    """
    def process_items(self, daily_events):
        
        
        while True:
            
            # Check if there's a shortage of input materials or WIPs
            with self.machine.request() as request :
                yield request


                # 🔹 50개 생산 후 output inventory가 넘치지 않는지 확인
                inven_upper_limit_check = (
                    self.output_inventory.on_hand_inventory + self.batch_size > self.output_inventory.capacity_limit )

                
             
                if inven_upper_limit_check:
                    if self.print_limit:
                        daily_events.append(
                            "===============Process Phase===============")
                        daily_events.append(
                         f"{present_daytime(self.env.now)}: Stop {self.name} due to the upper limit of the inventory. The output inventory is full")
                    self.print_limit = False
                    yield self.env.timeout(1)  # Check upper limit every hour

                else:
                    
                    daily_events.append("===============Process Phase===============")
                    daily_events.append(f"{present_daytime(self.env.now)}: Process {self.process_id} begins producing {self.batch_size} units")

                    

                    # **생산 시간 진행 (출력 없음)**
                    yield self.env.timeout((self.processing_time - TIME_CORRECTION) * self.batch_size)

                    # **50개 완성 후 한 번에 output 추가**
                    self.output_inventory.update_inven_level(self.batch_size, "ON_HAND", daily_events)

                    
                    
                    daily_events.append("===============Result Phase================")
                    daily_events.append(f"{present_daytime(self.env.now)}: {self.output['NAME']} has been produced                         : {self.batch_size} units")

                    self.print_limit = True
                    self.print_stop = True
                    yield self.env.timeout(TIME_CORRECTION)  # Time correction

             """       
    


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
        self.batch_size = 50
        self.num_printers = P[self.process_id]["NUM_POST_PROCESSORS"]
        self.processing_time = (24 / self.production_rate) / self.num_printers
        self.total_produced = 0
        self.order_quantity = I[0]['DEMAND_QUANTITY']*50

        # 후처리 기계 4대 운영
        self.machines = [simpy.Resource(env, capacity=1) for _ in range(self.num_printers)]
        #self.machine = simpy.Resource(env, capacity=P[self.process_id]["NUM_POST_PROCESSORS"] ) #P[self.process_id]["NUM_POST_PROCESSORS"]  

#self.num_printers = P[self.process_id]["NUM_PRINTERS"]
#self.machines = [simpy.Resource(env, capacity=1) for _ in range(self.num_printers)]
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

                # 생산 시작
                
                yield self.env.timeout(self.processing_time - TIME_CORRECTION)  # 병렬 생산 반영

                # 입력 재고 감소
                for inven, input_qnty in zip(self.input_inventories, self.qnty_for_input_item):
                    inven.update_inven_level(-input_qnty, "ON_HAND", daily_events)

                # 출력 재고 증가
                self.output_inventory.update_inven_level(1, "ON_HAND", daily_events)

                # 🔹 총 생산량 업데이트
                self.total_produced += 1

                # 🔹 50개 단위로 결과 출력
                if self.total_produced >= self.batch_size:
                    daily_events.append("===============PostProcessResult Phase================")
                    daily_events.append(f"{present_daytime(self.env.now)}: {self.output['NAME']} has been produced: {self.total_produced} units (Accumulated)")
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

"""
    def process_for_machine(self, daily_events):
               
        while True:
            # Check if there's a shortage of input materials or WIPs
            shortage_check = False
            #일단 기본값으로 재고 부족량을 false로 설정 > 현재는 재고 부족이 없다
            for inven, input_qnty in zip(self.input_inventories, self.qnty_for_input_item):
                #zip : 재고 객체와 필요 수량을 한쌍으로 묶음.
                if inven.on_hand_inventory < input_qnty:
                    #현재보유량이 필요수량보다 적은지 확인
                    shortage_check = True
                    #부족하다면, True로 하여, 나머지 재고를 확인하지않고 루프를 종료
                    # early stop
                    break

            # Check if the output inventory is full
            inven_upper_limit_check = False
            if self.output_inventory.on_hand_inventory >= self.output_inventory.capacity_limit:
                inven_upper_limit_check = True
            #출력재고가 최대용량을 초과했는지 확인

            #입력 재고 부족 여부 확인
            #True가 되면 입력 재고 부족한 것, False이면 충분해서 공정 진행
            if shortage_check:
                if self.print_stop:
                    #초기값은 True. 그러니까, shortae_check가 true일때만 출력, 이후에는 출력x
                    daily_events.append(
                        "===============PostProcess Phase===============")
                    #구분선 메시지 추가

                    daily_events.append(
                        f"{present_daytime(self.env.now)}: Stop {self.name} due to a shortage of input WIPs")
                    #이벤트 로그에 기록
                self.print_stop = False
                #메시지 출력이후 False로 하여 재출력 방지

                yield self.env.timeout(1)  # Check shortage every hour 1시간 대기 후 재확인
            #shortagecheck와 같은 구조
            elif inven_upper_limit_check:
                if self.print_limit:
                    daily_events.append(
                        "===============PostProcess Phase===============")
                    daily_events.append(
                        f"{present_daytime(self.env.now)}: Stop {self.name} due to the upper limit of the inventory. The output inventory is full")
                self.print_limit = False
                yield self.env.timeout(1)  # Check upper limit every hour
            
            #생산 공정 시작, 생산 시작 메시지 기록
            #입력 재고가 충분하고, 출력 재고가 초과 되지 않은 경우 생산 작업을 수행하는 로직
            #입력재고를 소비하고 산출물 생성, 생산관련 이벤트 기록 / 생산 소요시간 비용 계산, 시간 보정 처리
            else:
                
                
                daily_events.append("===============PostProcess Phase===============")
                #생산 공정이 시작되었음을 이벤트 로그에 기록
                daily_events.append(f"{present_daytime(self.env.now)}: Process {self.process_id} begins")
                

                #입력 재고(input_inventories)에서 필요한 수량(qntyforinputitem)만큼 감소(update_inven_level 호출)
                # Consume input materials or WIPs
                for inven, input_qnty in zip(self.input_inventories, self.qnty_for_input_item):
                    inven.update_inven_level(-input_qnty,"ON_HAND", daily_events)
                    #재고감소량 / 보유 재고 / 이벤트 로그 리스트
                # Process items (consume time)
                
                #생산 비용 계산, 기록

                # Time correction 생산시간소요
                yield self.env.timeout(self.processing_time-TIME_CORRECTION)

                # 🔹 1개 생산 완료 (출력 재고 증가)
                self.output_inventory.update_inven_level(1, "ON_HAND", daily_events)
                # Update the inventory level for the output item
                #출력 재고를 1단위 증가하여 update

                # 🔹 작업 개수 카운트 증가
                self.batch_counter += 1
                if self.batch_counter % self.batch_size == 0:
                        daily_events.append("===============PostProcessResult Phase================")
                        daily_events.append(f"{present_daytime(self.env.now)}: {self.output['NAME']} has been produced                     : {self.batch_size} units")


                self.print_limit = True
                self.print_stop = True
                yield self.env.timeout(TIME_CORRECTION)  # Time correction
"""                



class Sales:
    def __init__(self, env, item_id, due_date):
        # Initialize sales process
        self.env = env
        self.item_id = item_id
        self.due_date = due_date
        self.delivery_item = 0

    def _deliver_to_cust(self, demand_size, product_inventory, daily_events):
        """
        Deliver products to customers and handle shortages if any.
        """
        yield self.env.timeout(I[self.item_id]["DUE_DATE"] * 24-TIME_CORRECTION/2)  # Time Correction
        
        
        daily_events.append(
            f"DEMAND: {demand_size}, DELIVERY:{self.delivery_item}")
        # If there are some products available, deliver them first
        if self.delivery_item > 0:
            daily_events.append(
                f"{self.env.now+TIME_CORRECTION/2}: PRODUCT have been delivered to the customer       : {self.delivery_item} units ")
            # Update inventory
            product_inventory.update_inven_level(
                -self.delivery_item, 'ON_HAND', daily_events)
            

        yield self.env.timeout(TIME_CORRECTION/2)  # Time Correction


    def receive_demands(self, demand_qty, product_inventory, daily_events):
        """
        Receive demands from customers and initiate the delivery process.
        """
        # Update demand quantity in inventory
        product_inventory.update_demand_quantity(daily_events)
        # Initiate delivery process
        self.env.process(self._deliver_to_cust(
            demand_qty, product_inventory, daily_events))


#고객 제품 주문 생성, 판매sales 프로세스를 통해 처리
#일정 주기로 주문량 생성, 주문 처리
class Customer:
    def __init__(self, env, name, item_id):
        # Initialize customer object
        self.env = env
        self.name = name
        self.item_id = item_id

    def order_product(self, sales, product_inventory, daily_events, scenario):
        #제품 주문 생성, 주문량 판매 프로세스로 전달(,Sales객체-주문처리, 재고객체, 이벤트로그리스트, 주문량 생성 시나리오(분포유형))
        """
        Place orders for products to the sales process.
        """
        while True:
            # Generate a random demand quantity
            I[0]["DEMAND_QUANTITY"] = DEMAND_QTY_FUNC(scenario)
            #scenario기반으로 무작위 수요량 생성하고 결과를 I[0]["DEMAND_QUANTITY"]에 저장
            # Receive demands and initiate delivery process
            sales.receive_demands(
                I[0]["DEMAND_QUANTITY"], product_inventory, daily_events)
            #생성된 주문량(I[0]["DEMAND_QUANTITY"])을 판매 프로세스 Sales의 receive_demands에 전달
            # Wait for the next order cycle
            yield self.env.timeout(I[0]["CUST_ORDER_CYCLE"] * 24)
            #고객 주문 주기(custordercycle)에 따라 다음 주문 생성까지 대기



def record_inventory(env, inventoryList):
    #함수 정의 record_inventory : 재고 데이터를 추적, 기록 (환경,기록할 재고 객체 리스트)
    """
    Record inventory at every hour
    """
    record_graph(I)
    #초기 재고 데이터를 그래프로 기록하는 함수 호출
    while (True):
        for inven in inventoryList:
            GRAPH_LOG[I[inven.item_id]['NAME']].append(inven.on_hand_inventory)
            #각 재고 객체의 현재 보유 재고량(onhandinventory)을 그래프 로그에 추가
            #I[][] : 해당 재고의 이름
            # >> 해당 재고 이름에 해당하는 로그 리스트에 데이터 추가

        yield env.timeout(1)



#필요한 객체(재고,고객,공급자,제조공정)를 생성하여 simpy환경에서 사용
def create_env(I, P, daily_events):
    # Function to create the simulation environment and necessary objects
    simpy_env = simpy.Environment()  # Create a SimPy environment

    # Create an inventory for each item
    inventoryList = []
    for i in I.keys():
        inventoryList.append(Inventory(simpy_env, i ))



    # Create stakeholders (Customer, Suppliers) 고객 객체 생성
    customer = Customer(simpy_env, "CUSTOMER", I[0]["ID"])

    
    #판매 관리자 객체 생성
    # Create managers for manufacturing process, procurement process, and delivery process
    sales = Sales(simpy_env, customer.item_id, I[0]["DUE_DATE"])
    #sales 객체 초기화(환경,id,납품 기한)

    productionList = []


    """
    for machine_id in M1:
        productionList.append(Production(simpy_env,"PROCESS_" + str(0), 
                P[0]["ID"],  # P에서 ID 가져오기
                M1[machine_id]["PRODUCTION_RATE"],  # M에서 PRODUCTION_RATE 가져오기
                P[0]["OUTPUT"], 
                inventoryList[P[1]["OUTPUT"]["ID"]]))
    
    """
    productionList.append(Production(simpy_env, "PROCESS_" + str(0), P[0]["ID"],
                                   [M1[machine_id]["PRODUCTION_RATE"] for machine_id in M1],
                                   P[0]["OUTPUT"], 
                                   inventoryList[P[0]["OUTPUT"]["ID"]]))
    
   

    postprocessList = []
    postprocessList.append(PostProcess(simpy_env, "PROCESS_" + str(1), P[1]["ID"],
                                   P[1]["PRODUCTION_RATE"], P[1]["OUTPUT"], 
                                   [inventoryList[j["ID"]] for j in P[1]["INPUT_TYPE_LIST"]], 
                                   P[1]["QNTY_FOR_INPUT_ITEM"], 
                                   inventoryList[P[1]["OUTPUT"]["ID"]]))

    
    return simpy_env, inventoryList, productionList, postprocessList, sales, customer, daily_events
    

# Event processes for SimPy simulation
#이벤트 정의. 고객 주문, 제조공정, 후작업, 재고기록 같은 작업 처리
def simpy_event_processes(simpy_env, inventoryList, productionList, postprocessList, sales, customer, daily_events, I, scenario):
    #주요 이벤트 프로세스 설정(환경, 재고객체리스트, 제조 공정 객체 리스트, 후작업 리스트, 판매 객체, 고객 객체,  이벤트 로그 기록 리스트, I재고 정보 사전, 시나리오)

    simpy_env.process(customer.order_product(
        sales, inventoryList[I[0]["ID"]], daily_events, scenario["DEMAND"]))
    #고객 객체(customer)가 제품을 주문하는 프로세스를 Simpy환경에서 실행.
    #order_product 메서드 호출 > 특정 제품 주문(sales-판매객체,주문대상 재고 객체, 이벤트 로그 리스트, 시나리오)
    
    for production in productionList:
        for machine_id in range(production.num_printers): 
            simpy_env.process(production.process_for_machine(machine_id, daily_events)) 

    #for production in productionList:
        #simpy_env.process(production.process_for_machine(daily_events))
    #제조 공정 실행. 모든 제조 공정 객체(productionlist)에 대해 processitems메서드 실행
    #process_itmes 제조 공정 입력 재료 소비하고 산출물 생성
    
    for postprocess in postprocessList:
        simpy_env.process(postprocess.process_for_machine(machine_id, daily_events))
    

    simpy_env.process(record_inventory(simpy_env, inventoryList))
    #재고 상태 기록


#매일 재고 상태 업데이트, 로그에 기록하는 작업 수행
def update_daily_report(inventoryList):
    # Update daily reports for inventory
    #일일 보고서와 상태 사전에 기록
    day_list = [] #일일보고서 리스트
    day_dict = {} #상태 사전(키-값)
    for inven in inventoryList:
        inven.daily_inven_report[-1] = inven.on_hand_inventory
        day_list = day_list+(inven.daily_inven_report)
        #현재 보유 재고(onhandinventory)로 보고서 마지막 항목 업데이트
        #현재 재고 객체 일일 보고서를 day list에 추가


        #상태 사전 업데이트
        day_dict[f"On_Hand_{I[inven.item_id]['NAME']}"] = inven.on_hand_inventory
        
    LOG_DAILY_REPORTS.append(day_list)
    LOG_STATE_DICT.append(day_dict)
    #보고서, 사전에 기록
    # Reset report
    for inven in inventoryList:
        inven.daily_inven_report = [f"Day {inven.env.now//24+1}", I[inven.item_id]['NAME'], I[inven.item_id]['TYPE'],
                                    inven.on_hand_inventory, 0, 0, 0]  # inventory report
        #모든 재고 객체 일일 보고서 초기화
        #[날짜, 재고이름, 재고 유형, 보유 재고, 운송 중 재고, 초기값0]


def present_daytime(env_now):
    days = int(env_now // 24)
    hours = int(env_now % 24)
    minutes = int((env_now % 1) * 60)  # 소수점을 분으로 변환
    
    return f"[{days:02}:{hours:02}:{minutes:02}]"
