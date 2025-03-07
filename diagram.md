```mermaid
classDiagram
    
    class Customer {
      - env: simpy.Environment
      - daily_events: list
      - temp_job_list: list
      + create_jobs_continuously()
    }

    class Order {
      - env : simpy.Environment
      - daily_events: list
      - current_order_id : int
      - temp_order_list : list
    }


    class Job {
      - env : simpy.Environment
      - job_id: int
      - items: list~Item~
      - Proc_Build_time : int
      - Proc_Wash_time : int
      - Proc_Dry_time : int
    }

    class Item {
      - env: simpy.Environment
      - item_id: int
      - job_id: int
      - create_time: float
      - volume: int
      - Proc_Inspect_time : int
    }

    class Product_Planning {
      - env: simpy.Environment
      - daily_events: list
      - current_item_id: int
      - current_job_id: int
      - Build_queue: Proc_Build
    }

    class Proc_Build {
      - env: simpy.Environment
      - daily_events: list
      - processing_time : int
      - is_busy: bool
      - machines: dict

      - Build_queue: list
      - Wash_queue : Proc_Wash
      + _Build__jobs()
      + _Build_job(job)
    }

    class Proc_Wash {
      - env: simpy.Environment
      - daily_events: list
      - processing_time : int
      - is_busy: bool
      - machines: dict

      - Wash_queue: list
      - Dry_queue : Proc_Dry
      + _washing_job(job)
    }

    class Proc_Dry {
      - env: simpy.Environment
      - daily_events: list
      - processing_time : int
      - is_busy: bool
      - machines: dict

      - Dry_queue: list
      - Inspect_queue : Proc_Inspect
      + _drying_job(job)
    }

    class Proc_Inspect {
      - env: simpy.Environment
      - daily_events: list
      - processing_time : int
      - is_busy: bool
      - machines: dict

      - Inspect_queue: list
      + _inspect_item(item)
    }

 

    

    %% 관계 표현
    Customer --> Job : creates
    Order o-- Job : contains
    Job o-- Item : contains
    Order --> Product_Planning : transmit
    Product_Planning --> Proc_Build : assign
    Proc_Build --> Proc_Wash : calls
    Proc_Wash --> Proc_Dry : calls
    Proc_Dry --> Proc_Inspect : calls
    