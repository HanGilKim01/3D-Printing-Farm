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
    def __init__(self, job_id, items, create_time, job_process_time):
        """
        self.job_id: Job ID
        self.items: Job에 포함될 Item 리스트 / 초기값 = []
        self.create_time: Job 생성 시점
        """
        self.job_id = job_id
        self.items = items
        self.create_time = create_time 
        self.job_process_time = job_process_time
        

class Item:
    """
    item 속성 정의 클래스
    """
    def __init__(self, env, item_id, config, job_id=None):
        """
        self.env: SimPy 환경
        self.item_id: Item_id
        self.job_id : Job_id
        self.create_time: Item 생성 시점
        self.volume : Item 크기
        """
        self.env = env
        self.item_id = item_id
        self.job_id = job_id
        self.create_time = env.now
        self.volume = np.random.randint(*config["Volume_range"])
        
 

# Customer 클래스: 지속적으로 전문 job(작업)을 생성
class Customer:
    """
    job 생성 클래스
    일정 간격으로 Job을 생성하고, Item을 추가
    Job들을 printer_queue에 전달
    """
    def __init__(self, env, daily_events,  printer_queue):
        """
        self.env: SimPy 환경
        self.daily_events: 일별 이벤트 로그 리스트
        self.item_id: Item ID(초기값 1)
        self.job_id: job ID(초기값 1)
        self.printer_queue: Job 저장 SimPy queue 객체
        self.temp_job_list: Job 임시저장 리스트, 일정 개수가 누적 후 printer_queue에 전달
        self.interval = job 생성 간격
        """
        self.env = env
        self.daily_events = daily_events
        self.item_id = 1
        self.job_id = 1
        self.printer_queue = printer_queue
        self.temp_job_list = [] 
        self.interval = CUSTOMER["INTERVAL"]

    def create_jobs(self):
        """
        Job 생성 프로세스

        - Job 생성 -> daily_events에 기록
        - ITEM_SIZE만큼 Item 생성하고, 각 Item에 대해 사이즈 조건을 확인
        - 생성 Job은 임시 리스트(temp_job_list)에 저장, 리스트 크기가 CUSTOMER["JOB_LIST_SIZE"]에 도달하면 printer_queue에 일괄 전달한 후 리스트를 초기화
        - 일정 간격(interval) 동안 대기
        """
        while True:
            if self.env.now >= SIM_TIME * 24:
                break

            day = int(self.env.now // 24) + 1

            # 고객이 전문 job 객체 생성 (빈 Item 리스트와 함께)
            new_job = Job(self.job_id, [], self.env.now)
            self.job_id += 1
            self.daily_events.append(
                f"{int(self.env.now % 24)}:{int((self.env.now % 1)*60):02d} - Job {new_job.job_id} created at time {new_job.create_time:.2f}."
            )

            # CUSTOMER["ITEM_SIZE"]만큼 Item 생성 후 추가
            for _ in range(CUSTOMER["ITEM_SIZE"]):
                item = Item(self.env, self.item_id, JOB_TYPES["DEFAULT"], job_id=new_job.job_id)
                self.item_id += 1

                
                ITEM_LOG.append({
                    'day': day,
                    'job_id': new_job.job_id,   
                    'item_id': item.item_id,      
                    'create_time': item.create_time,
                    'volume': item.volume,
                })

                
                if (item.volume <= PRINTERS_SIZE["Volume_range"] ):
                    new_job.items.append(item)
                
                else:
                    self.daily_events.append(f"Item {item.item_id} could not be assigned: No suitable printer available (Item volume: {item.volume:.2f})")
                    
                    
            
            # 생성된 전문 job을 임시 리스트에 추가
            self.temp_job_list.append(new_job)

            # 일정 수의 전문 job이 쌓이면 printer_store에 넣음
            if len(self.temp_job_list) >= CUSTOMER["JOB_LIST_SIZE"]:
                self.daily_events.append(
                    f"{int(self.env.now % 24)}:{int((self.env.now % 1)*60):02d} - {len(self.temp_job_list)} jobs accumulated. Sending batch to printer."
                )
                for job_obj in self.temp_job_list:
                    self.printer_queue.put(job_obj)
                self.temp_job_list.clear()

            
            yield self.env.timeout(self.interval)


      
class BaseProcess:
    """
    프로세스 기본 클래스.
    seize, delay, release 메서드의 기본 동작을 정의하여
    build, wash, dry 등에서 상속받아 사용합니다.
    """
    def __init__(self, env, daily_events, process_id, process_time, in_queue, out_queue, process_name):
        """
        env: SimPy 환경 객체.
        daily_events: 일별 이벤트 로그 리스트.
        process_id: 프로세스 id.
        in_queue: 작업을 받아오는 입력 큐.
        out_queue: 작업을 전달할 출력 큐.
        process_name: 프로세스 이름 (예: "Printing", "Washing", "Drying", "Inspection").
        process_time: job 아이템의 처리 시간이 None일 경우 사용할 기본 처리 시간.
        """
        self.env = env
        self.daily_events = daily_events
        self.process_id = process_id
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.process_name = process_name
        self.process_time = process_time
        self.is_busy = False

    def seize(self):
        """
        seize 메서드:
        입력 큐에서 job을 받아 각 아이템의 처리 시간을 합산하여 job.job_process_time을 계산하고,
        delay 프로세스를 시작합니다.
        """
        while True:
            job = yield self.in_queue.get()

            # 각 item의 build_time 합산하여 job.job_build_time으로 설정 (None이면 기본값 1 사용)
            
            total_process_time = 0
            for item in job.items:
                # 만약 item의 build_time이 None이 아니라면 해당 값을 사용합니다.
                if self.process_time is not None:
                    total_process_time += self.process_time
                # build_time이 None이라면 기본값인 1을 더합니다.
                else:
                    self.process_time = 1
                    total_process_time += self.process_time

            # 계산된 총 build_time을 job의 속성으로 할당합니다.
            job.job_process_time = total_process_time

            yield self.env.process(self.delay(job))

    def delay(self, job):
        """
        delay 메서드:
        job의 총 처리 시간(job.job_process_time)만큼 대기하면서 작업을 수행하고,
        종료 로그를 남긴 후 release 메서드를 호출합니다.
        """
        self.is_busy = True

        start_time = self.env.now
        self.daily_events.append(
            f"{int(self.env.now % 24)}:{int((self.env.now % 1)*60):02d} - Job {job.job_id} is {self.process_name} on {self.process_id} for {job.job_process_time} time units."
        )

        yield self.env.timeout(job.job_process_time)
        end_time = self.env.now

        # Closing 단계 로그 (필요 시 추가 로직 구현 가능)
        closing_start = self.env.now
        self.daily_events.append(
            f"{int(self.env.now % 24)}:{int((self.env.now % 1)*60):02d} - Job {job.job_id} is finishing {self.process_name} on {self.process_id}."
        )
        closing_end = self.env.now

        # (선택사항) 전역 DAILY_REPORTS 업데이트
        DAILY_REPORTS.append({
            'order_id': job.job_id,
            'process_id': self.process_id,
            'start_time': start_time,
            'end_time': end_time,
            'closing_start': closing_start,
            'closing_end': closing_end,
            'process': self.process_name
        })

        self.release(job)

    def release(self, job):
        """
        release 메서드:
        job 처리가 완료된 후 프로세스의 상태를 해제하고,
        출력 큐로 job을 전달합니다.
        """
        self.is_busy = False
        self.daily_events.append(
            f"{int(self.env.now % 24)}:{int((self.env.now % 1)*60):02d} - {self.process_name} {self.process_id} is now available."
        )
        self.out_queue.put(job)

class Proc_Build(BaseProcess):
    def __init__(self, env, daily_events, machine_id, process_time, printer_queue, washing_queue):
        
        
        super().__init__(env, daily_events, machine_id, process_time, in_queue=printer_queue, out_queue=washing_queue, process_name="Printing")
        #super().__init__ : 상속받은 클래스 내부에서 부모클래스의 생성자를 호출할 때 사용 문법 >> 부모클래스의 생성자를 호출하여 초기화 작업 수행

class Proc_Washing(BaseProcess):
    def __init__(self, env, daily_events, machine_id, process_time, washing_queue, drying_queue):
        

        super().__init__(env, daily_events, machine_id, process_time, in_queue=washing_queue, out_queue=drying_queue, process_name="Printing")
        #super().__init__ : 상속받은 클래스 내부에서 부모클래스의 생성자를 호출할 때 사용 문법 >> 부모클래스의 생성자를 호출하여 초기화 작업 수행

class Proc_Drying(BaseProcess):
    def __init__(self, env, daily_events, machine_id, process_time, drying_queue, post_processing_queue):
        

        super().__init__(env, daily_events, machine_id, process_time,in_queue=drying_queue, out_queue=post_processing_queue, process_name="Printing")
        #super().__init__ : 상속받은 클래스 내부에서 부모클래스의 생성자를 호출할 때 사용 문법 >> 부모클래스의 생성자를 호출하여 초기화 작업 수행

class Proc_PostProcessing(BaseProcess):
    def __init__(self, env, daily_events, machine_id, process_time, post_processing_queue, packaging_queue):
        
        super().__init__(env, daily_events, machine_id, process_time, in_queue=post_processing_queue, out_queue=packaging_queue, process_name="Printing")
        #super().__init__ : 상속받은 클래스 내부에서 부모클래스의 생성자를 호출할 때 사용 문법 >> 부모클래스의 생성자를 호출하여 초기화 작업 수행

class Proc_Packaging(BaseProcess):
    def __init__(self, env, daily_events, machine_id, process_time, packaging_queue, product_list):
        
        super().__init__(env, daily_events, machine_id, process_time, in_queue=packaging_queue, out_queue=product_list, process_name="Printing")
        #super().__init__ : 상속받은 클래스 내부에서 부모클래스의 생성자를 호출할 때 사용 문법 >> 부모클래스의 생성자를 호출하여 초기화 작업 수행




# 환경 생성 함수 (create_env)
def create_env(daily_events):

    simpy_env = simpy.Environment()

    # Queue 생성
    printer_queue = []
    washing_queue = []
    drying_queue = []
    post_processing_queue = []
    packaging_queue = []
    product_list = []

    packaging = Proc_Packaging(simpy_env, daily_events, machine_id, process_time, packaging_queue, product_list)
    post_processor = Proc_PostProcessing(simpy_env, daily_events, post_processing_queue, packaging_queue)
    dry_machine = Proc_Drying(simpy_env, daily_events, drying_queue, post_processing_queue)
    washing_machine = Proc_Washing(simpy_env, daily_events, washing_queue, drying_queue)
    customer = Customer(simpy_env, daily_events, printer_queue)
    
    # Printer 생성 시 order_store와 washing_machine (즉, Washing.assign_order 호출) 전달
    printers = [
        Proc_Build(simpy_env, daily_events, pid, printer_queue, washing_queue, process_time=PRINTERS["PROCESS_TIME"],)
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
    simpy_env.process(customer.create_jobs())

    # 각 Printer의 주문 처리 프로세스 실행
    for printer in printers:
        simpy_env.process(printer.seize())




'''
class Proc_Build:
    """
    프린터 작업 클래스
    customer에게서 job을 printer_queue로 받아서 처리
    작업이 끝나면 washing_queue로 넘김
    """
    def __init__(self, env, daily_events, printer_id, printer_queue, washing_queue):
        """
        env: SimPy 환경 객체
        daily_events: 일별 이벤트 로그 리스트
        printer_id: 프린터 id
        printer_queue: printer클래스 queue 
        washing_queue: washing클래스 queue
        """
        self.env = env                          
        self.daily_events = daily_events       
        self.printer_id = printer_id            
        self.is_busy = False                     
        self.printer_queue = []      
        self.washing_queue = washing_queue      


    def seize(self):
        """
        seize 메서드
        printer_queue에서 job을 받아서 delay 실행
        """
        while True:
            job = yield self.printer_queue.get()
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
        Job을 처리 프로세스.
        주문 내 모든 Job의 build_time 합산값(order_build_time)만큼 대기
        """
        self.is_busy = True  # 주문 처리 시작
        

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
        washing_machine으로 job을 넘기는 작업.
        """
        self.is_busy = False
        self.daily_events.append(
            f"{int(self.env.now % 24)}:{int((self.env.now % 1)*60):02d} - Printer {self.printer_id} is now available."
        )
        self.washing_queue.put(job)



class Proc_Washing:
    """
    세척 작업 클래스
    washing_queue에 넣은 job들을 꺼내 진행
    작업이 끝나면 drying_queue에 전달달
    """
    def __init__(self, env,  daily_events, dry_machine, washing_queue, drying_queue):
        """
        env: SimPy 환경 객체
        daily_events: 일별 이벤트 로그 리스트
        dry_machine: 세척 후 job들을 전달할 건조 단계 객체
        washing_queue: Printer에서 전달된 job들 저장 queue
        drying_queue: 건조 단계에서 사용될 queue, 세척 후 job 전달
        """
        self.env = env                              
        self.daily_events = daily_events             
        self.dry_machine = dry_machine                
        self.washing_queue = washing_queue            
        self.drying_queue = drying_queue              


class Proc_Drying:
    """
    건조 작업 클래스
    drying_queue에 넣은 job들을 꺼내 진행
    작업이 끝나면 post_processing_queue에 전달
    """
    def __init__(self, env, daily_events, post_processor, drying_queue, post_processing_queue):
        """
        env: SimPy 환경 객체
        daily_events: 일별 이벤트 로그 리스트로, 작업 진행 상황을 기록하는 데 사용됩니다.
        post_processor: 건조 작업 완료 후 job들을 전달할 후처리(PostProcessing) 단계 객체
        drying_queue: Washing에서 전달된 job들 저장 queue
        """
        self.env = env                               
        self.daily_events = daily_events            
        self.post_processor = post_processor          
        self.drying_queue = drying_queue               
        self.post_processing_queue = post_processing_queue


class Proc_PostProcessing:
    """
    후처리 작업 클래스
    post_processing_queue에 넣은 job들을 꺼내 진행
    작업이 끝나면 packaging_queue에 전달
    """
    def __init__(self, env,  daily_events, packaging, post_processing_queue, packaging_queue):
        """
        env: SimPy 환경 객체
        daily_events: 일별 이벤트 로그 리스트로, 작업 진행 상황을 기록하는 데 사용됩니다.
        packaging: 후처리 작업 완료 후 job들을 전달할 포장 단계 객체
        post_processing_queue: drying에서 전달된 job들 저장 queue
        packaging_queue : post_processing에서 전달된 job들 저장 queue
        """
        self.env = env  # SimPy 환경 객체
        self.daily_events = daily_events  # 일별 이벤트 로그 리스트
        self.packaging = packaging  # Packaging 객체 참조
        self.post_processing_queue = post_processing_queue
        self.packaging_queue = packaging_queue



class Proc_Packaging:
    """
    포장 작업 클래스
    packaging_queue에 넣은 job들을 꺼내 진행
    작업이 끝나면 완제품을 product_list에 보관
    """
    def __init__(self, env,  daily_events, packaging_queue, product_list):
        """
        env: SimPy 환경 객체
        daily_events: 일별 이벤트 로그 리스트로, 작업 진행 상황을 기록하는 데 사용됩니다.
        packaging_queue : post_processing에서 전달된 job들 저장 queue
        """
        self.env = env  # SimPy 환경 객체 
        self.daily_events = daily_events  # 일별 이벤트 로그 리스트
        self.packaging_queue = []  # 대기 중인 전문 job들을 저장할 큐
        self.product_list = product_list

'''
