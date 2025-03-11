import simpy
import numpy as np
from config import *  # 설정 파일 (JOB_TYPES, PRINTERS, PRINTERS_INVEN 등)
from log import *  # 로그 파일 (DAILY_EVENTS 등)
import time



# Job 클래스: 전문 job(작업)의 속성을 정의
class Job:
    """
    job 속성 정의 클래스
    각 Job은 Item을 포함
    """
    def __init__(self, job_id, items, create_time):
        """
        self.job_id: Job ID
        self.items: Job에 포함될 Item 리스트 / 초기값 = []
        self.create_time: Job 생성 시점
        self.build_time: Job 인쇄 시간
        self.washing_time: Job 세척 시간
        """
        self.job_id = job_id
        self.items = items
        self.create_time = create_time 
        self.build_time = None       
        self.washing_time = None     
        self.drying_time = None      
        self.packaging_time = None 


# Customer 클래스: 지속적으로 전문 job(작업)을 생성
class Customer:
    """
    job 생성 클래스
    일정 간격으로 Job을 생성하고, Item을 추가
    Job들을 printer_store에 전달
    """
    def __init__(self, env, daily_events,  printer_store):
        """
        self.env: SimPy 환경
        self.daily_events: 일별 이벤트 로그 리스트
        self.current_item_id: Item ID(초기값 1)
        self.current_job_id: job ID(초기값 1)
        self.printer_store: Job 저장 SimPy Store 객체
        self.temp_job_list: Job 임시저장 리스트, 일정 개수가 누적 후 printer_store에 전달
        self.interval = job 생성 간격
        """
        self.env = env
        self.daily_events = daily_events
        self.current_item_id = 1
        self.current_job_id = 1
        self.printer_store = printer_store
        self.temp_job_list = [] 
        self.interval = JOB_CREATION_INTERVAL

    def create_jobs_continuously(self):
        """
        Job 생성 프로세스

        - Job 생성 -> 현재 시간을 기반으로 일(day)을 계산하고, daily_events에 기록
        - CUSTOMER["ITEM_SIZE"]만큼 Item 생성하고, 각 Item에 대해 사이즈 조건을 확인하여 적절히 할당하거나 부족 상황을 기록
        - 생성 Job은 임시 리스트(temp_job_list)에 저장, 리스트 크기가 CUSTOMER["JOB_LIST_SIZE"]에 도달하면 printer_store에 일괄 전달한 후 리스트를 초기화
        - 일정 간격(interval) 동안 대기
        """
        while True:
            if self.env.now >= SIM_TIME * 24:
                break

            day = int(self.env.now // 24) + 1

            # 고객이 전문 job 객체 생성 (빈 Item 리스트와 함께)
            new_job = Job(self.current_job_id, [], self.env.now)
            self.current_job_id += 1
            self.daily_events.append(
                f"{int(self.env.now % 24)}:{int((self.env.now % 1)*60):02d} - Job {new_job.job_id} created at time {new_job.create_time:.2f}."
            )

            # 전문 job 내부에서 CUSTOMER["ITEM_SIZE"]만큼 Item 생성 후 추가
            for _ in range(CUSTOMER["ITEM_SIZE"]):
                item = Item(self.env, self.current_item_id, JOB_TYPES["DEFAULT"], job_id=new_job.job_id)
                self.current_item_id += 1

                # JOB_LOG (이제 ITEM_LOG) 기록: 부모 전문 job의 ID와 생성된 Item의 ID 기록
                ITEM_LOG.append({
                    'day': day,
                    'job_id': new_job.job_id,   # 전문 job의 ID
                    'item_id': item.item_id,      # 생성된 Item의 ID
                    'create_time': item.create_time,
                    'size': item.size,
                    'build_time': item.build_time,
                    'post_processing_time': item.post_processing_time,
                    'packaging_time': item.packaging_time
                })

                # 생성된 Item이 프린터 크기 조건에 부합하면 Job에 추가, 아니면 부족 처리
                if (item.size <= PRINTERS_SIZE["Size_range"] ):
                    new_job.items.append(item)
                
                else:
                    self.daily_events.append(f"Item {item.item_id} could not be assigned: No suitable printer available (Item size: {item.size:.2f})")
                    
                    
            
            # 생성된 전문 job을 임시 리스트에 추가
            self.temp_job_list.append(new_job)

            # 일정 수의 전문 job이 쌓이면 printer_store에 넣음
            if len(self.temp_job_list) >= CUSTOMER["JOB_LIST_SIZE"]:
                self.daily_events.append(
                    f"{int(self.env.now % 24)}:{int((self.env.now % 1)*60):02d} - {len(self.temp_job_list)} jobs accumulated. Sending batch to printer."
                )
                for job_obj in self.temp_job_list:
                    self.printer_store.put(job_obj)
                self.temp_job_list.clear()

            interval = self.interval
            yield self.env.timeout(interval)


class Proc_Printer:
    """
    프린터 작업 클래스
    customer에게서 job을 printer_store로 받아서 처리
    작업이 끝나면 washing_store로 넘김
    """
    def __init__(self, env, daily_events, printer_id, washing_machine, printer_store, washing_store):
        """
        env: SimPy 환경 객체
        daily_events: 일별 이벤트 로그 리스트
        printer_id: 프린터의 고유 id
        washing_machine: 인쇄 완료 후 job을 전달할 워싱 머신 객체
        printer_store: printer클래스에서 job을 받는 SimPy Store 객체
        washing_store: washing클래스에서 job을 받는 SimPy Store 객체
        """
        self.env = env                          
        self.daily_events = daily_events       
        self.printer_id = printer_id            
        self.is_busy = False                   
        self.washing_machine = washing_machine  
        self.printer_store = printer_store      
        self.washing_store = washing_store      


    def seize(self):
        """
        seize 메서드
        printer_store에서 전문 job을 받아서 delay 프로세스를 실행.
        """
        while True:
            job = yield self.printer_store.get()
            # 각 item의 build_time 합산하여 job.job_build_time으로 설정 (None이면 기본값 1 사용)
            
            total_build_time = 0
            for item in job.items:
                # 만약 item의 build_time이 None이 아니라면 해당 값을 사용합니다.
                if item.build_time is not None:
                    total_build_time += item.build_time
                # build_time이 None이라면 기본값인 1을 더합니다.
                else:
                    item.build_time = 1
                    total_build_time += item.build_time

            # 계산된 총 build_time을 job의 속성으로 할당합니다.
            job.job_build_time = total_build_time
                        
            yield self.env.process(self.delay(job))

    def delay(self, job):
        """
        한 주문(Job)을 처리하는 프로세스.
        주문 내 모든 Job의 build_time 합산값(order_build_time)만큼 대기하며 인쇄 작업을 모사.
        """
        self.is_busy = True  # 주문 처리 시작
        
        # Set-up 단계
        set_up_start = self.env.now
        self.daily_events.append(
            f"{int(self.env.now % 24)}:{int((self.env.now % 1) * 60):02d} - Job {job.job_id} is starting setup on Printer {self.printer_id}."
        )
        
        set_up_end = self.env.now
        
        # Build 단계 (계산된 build_time 만큼 대기)
        start_time = self.env.now
        self.daily_events.append(
            f"{int(self.env.now % 24)}:{int((self.env.now % 1) * 60):02d} - Job {job.job_id} is printing on Printer {self.printer_id} for {job.job_build_time} time units."
        )
        yield self.env.timeout(job.job_build_time)
        end_time = self.env.now
        
        # Closing 단계
        closing_start = self.env.now
        self.daily_events.append(
            f"{int(self.env.now % 24)}:{int((self.env.now % 1) * 60):02d} - Job {job.job_id} is closing on Printer {self.printer_id}."
        )
        
        closing_end = self.env.now

    

        DAILY_REPORTS.append({
            'order_id': job.job_id,  # job_id로 표기
            'printer_id': self.printer_id,
            'set_up_start': set_up_start,
            'set_up_end': set_up_end,
            'start_time': start_time,
            'end_time': end_time,
            'closing_start': closing_start,
            'closing_end': closing_end,
            'process': 'Printing'
        })

        # release 메서드를 호출하여 프린터 상태 해제 및 Washing 단계로 전달
        self.release(job)
        
    def release(self, job):
        """
        machine을 해제하고 washing_machine으로 job을 넘기는 작업.
        """
        self.is_busy = False
        self.daily_events.append(
            f"{int(self.env.now % 24)}:{int((self.env.now % 1)*60):02d} - Printer {self.printer_id} is now available."
        )
        self.washing_store.put(job)


# Job 클래스: Job의 속성을 정의
class Item:
    def __init__(self, env, item_id, config, job_id=None):
        self.env = env
        self.item_id = item_id
        self.job_id = job_id
        self.create_time = env.now
        self.size = np.random.randint(*config["Size_range"])
        
        # 각 단계별 처리 시간 (빌드, 후처리)
        self.build_time = None      
        self.post_processing_time = None
        self.packaging_time = None  

        


# 환경 생성 함수 (create_env)
def create_env(daily_events):

    simpy_env = simpy.Environment()

    # 주문(order)을 위한 store (배치 단위로 들어갈 예정)
    printer_store = simpy.Store(simpy_env)
    washing_store = simpy.Store(simpy_env)
    drying_store = simpy.Store(simpy_env)
    
    # Satisfication, Packaging, PostProcessing, Drying, Washing, Customer, Display 생성
    
    packaging = Proc_Packaging(simpy_env, daily_events)
    post_processor = Proc_PostProcessing(simpy_env, daily_events, packaging)
    dry_machine = Proc_Drying(simpy_env, daily_events, post_processor, drying_store)
    washing_machine = Proc_Washing(simpy_env, daily_events, dry_machine, washing_store, drying_store)
    customer = Customer(simpy_env, daily_events, printer_store)
    
    # Printer 생성 시 order_store와 washing_machine (즉, Washing.assign_order 호출) 전달
    printers = [
        Proc_Printer(simpy_env, daily_events, pid, washing_machine, printer_store, washing_store)
        for pid in PRINTERS.keys()
    ]

    return simpy_env, packaging, dry_machine, washing_machine, post_processor, customer, printers, daily_events


# SimPy 이벤트 프로세스를 설정하는 함수 (simpy_event_processes)
def simpy_event_processes(simpy_env, packaging, post_processor, customer, printers, daily_events):
    """
    시뮬레이션의 주요 프로세스를 스케줄링
    
    - customer.create_orders_continuously(): 지속적으로 주문(Order)을 생성합니다.
    """
    
    # Customer가 지속적으로 주문을 생성하는 프로세스 실행
    simpy_env.process(customer.create_jobs_continuously())

    # 각 Printer의 주문 처리 프로세스 실행
    for printer in printers:
        simpy_env.process(printer.seize())



'''
class Proc_Washing:
    """
    워싱(세척) 작업 처리 클래스
    - washing_store에 넣은 job들을 seize 프로세스에서 각 워싱 머신의 capacity(용량)만큼 꺼내어 배치(batch)를 구성.
    - 배치가 완성되면 delay 프로세스를 통해 한 번에 세척 작업을 진행하고, 세척 완료 후 Drying 단계로 job들을 전달.
    """
    def __init__(self, env,  daily_events, dry_machine, washing_store, drying_store):
        """
        생성자 (__init__)
        :env: SimPy 환경 객체로, 시뮬레이션의 시간 흐름과 이벤트 스케줄링을 관리합니다.
        :daily_events: 일별 이벤트 로그 리스트로, 작업 진행 상황을 기록하는 데 사용됩니다.
        :dry_machine: 세척 후 job들을 전달할 건조(Drying) 단계 객체입니다.
        :washing_store: Printer나 다른 프로세스에서 전달된 job들이 임시로 저장되는 Store로, 세척 작업을 위한 입력 버퍼 역할을 합니다.
        :drying_store: 건조 단계에서 사용될 Store 객체로, 세척 후 job을 전달하기 위한 별도의 저장 공간(여기서는 필요에 따라 사용 가능)
        
        내부적으로 __init__에서는 다음을 수행합니다.
          - 전달받은 SimPy 환경, 비용, 로그, 건조 단계 객체, 그리고 washing_store와 drying_store를 멤버 변수에 저장.
          - WASHING_MACHINE 전역 설정(예: { 0: {"WASHING_SIZE": 2}, 1: {"WASHING_SIZE": 2} })을 참조하여,
            각 워싱 머신의 용량(capacity), 현재 배치(batch: 아직 처리되지 않은 job들의 리스트), busy 여부(is_busy)를 관리하는 딕셔너리(self.machines)를 생성.
          - 모든 워싱 머신이 즉시 job 할당을 받지 못할 경우를 대비하여, 대기열(waiting_queue)을 초기화합니다.
        """
        self.env = env                                # SimPy 환경, 시간 관리
        self.daily_events = daily_events              # 이벤트 로그 리스트
        self.dry_machine = dry_machine                # 건조 단계 객체
        self.washing_store = washing_store            # job을 저장하는 washing Store
        self.drying_store = drying_store              # job을 저장하는 drying Store
        # 각 워싱 머신의 용량 정보를 WASHING_MACHINE 설정에서 추출
        # 예를 들어, WASHING_MACHINE = { 0: {"WASHING_SIZE": 2}, 1: {"WASHING_SIZE": 2} }
        self.machines = {
            machine_id: {
                "capacity": WASHING_MACHINE[machine_id]["WASHING_SIZE"],
                "batch": [],           # 해당 머신에 할당된 job들의 리스트
                "is_busy": False       # 현재 머신이 작업 중인지 여부
            }
            for machine_id in WASHING_MACHINE.keys()
        }
        
        # 모든 머신이 busy일 경우를 위한 대기열
        self.waiting_queue = []


class Proc_Drying:
    """
    건조(Drying) 작업 처리 클래스
    - drying_store에 넣은 job들을 seize() 메서드에서 각 건조 머신의 capacity(용량)만큼 꺼내어 배치(batch)를 구성합니다.
    - 배치가 완성되면 delay() 메서드를 통해 한 번에 건조 작업을 진행하고,
      건조 완료 후 release()를 통해 각 job을 후속 단계(PostProcessing)로 전달하며, waiting_queue의 job들을 재할당합니다.
    """
    def __init__(self, env, daily_events, post_processor, drying_store):
        """
        생성자 (__init__)
        :env: SimPy 환경 객체로, 시뮬레이션의 시간 흐름과 이벤트 스케줄링을 관리합니다.
        :drying_cost: 건조 비용 단위로, 비용 계산에 사용됩니다.
        :daily_events: 일별 이벤트 로그 리스트로, 작업 진행 상황을 기록하는 데 사용됩니다.
        :post_processor: 건조 작업 완료 후 job들을 전달할 후처리(PostProcessing) 단계 객체입니다.
        :drying_store: Printer나 다른 프로세스에서 전달된 job들이 임시로 저장되는 Store로, 건조 작업을 위한 입력 버퍼 역할을 합니다.
        
        내부적으로 __init__에서는 다음을 수행합니다.
          - 전달받은 SimPy 환경, 비용, 로그, 후처리 객체, 그리고 drying_store를 멤버 변수에 저장합니다.
          - DRY_MACHINE 전역 설정(예: { 0: {"DRYING_SIZE": 3}, 1: {"DRYING_SIZE": 3} })을 참조하여,
            각 건조 머신의 용량(capacity), 현재 배치(batch: 아직 처리되지 않은 job들의 리스트), busy 여부(is_busy)를 관리하는 딕셔너리(self.machines)를 생성합니다.
          - 모든 건조 머신이 즉시 job 할당을 받지 못할 경우를 대비하여, 대기열(waiting_queue)을 초기화합니다.
        """
        self.env = env                                # SimPy 환경 객체
        self.daily_events = daily_events              # 일별 이벤트 로그 리스트
        self.post_processor = post_processor           # 후처리(PostProcessing) 객체
        self.drying_store = drying_store               # 건조 작업을 위한 입력 버퍼 역할 Store
        
        # DRY_MACHINE 전역 설정을 참조하여 각 건조 머신의 capacity, batch, busy 상태를 관리하는 딕셔너리 생성
        # 예: DRY_MACHINE = { 0: {"DRYING_SIZE": 3}, 1: {"DRYING_SIZE": 3} }
        self.machines = {
            machine_id: {
                "capacity": DRY_MACHINE[machine_id]["DRYING_SIZE"],
                "batch": [],         # 해당 머신에 할당된 job들의 리스트
                "is_busy": False     # 현재 머신이 작업 중인지 여부
            }
            for machine_id in DRY_MACHINE.keys()
        }
        
        # 모든 건조 머신이 busy일 경우 대기시킬 job들을 위한 대기열
        self.waiting_queue = []


class Proc_PostProcessing:
    def __init__(self, env,  daily_events, packaging):
        self.env = env  # SimPy 환경 객체
        self.daily_events = daily_events  # 일별 이벤트 로그 리스트
        self.packaging = packaging  # Packaging 객체 참조

        # 작업자 관리를 위한 SimPy Store를 생성 (초기에는 모든 작업자가 사용 가능)
        self.worker_store = simpy.Store(self.env, capacity=len(POST_PROCESSING_WORKER))
        for wid in POST_PROCESSING_WORKER.keys():
            self.worker_store.put(wid)


class Proc_Packaging:
    def __init__(self, env,  daily_events, ):
        self.env = env  # SimPy 환경 객체 
        self.daily_events = daily_events  # 일별 이벤트 로그 리스트
        # 포장 작업자를 관리하는 딕셔너리 (PACKAGING_MACHINE의 키 사용)
        self.workers = {worker_id: {"is_busy": False} for worker_id in PACKAGING_MACHINE.keys()}
        self.queue = []  # 대기 중인 전문 job들을 저장할 큐

'''
