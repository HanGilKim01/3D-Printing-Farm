```mermaid
classDiagram
    
    class Customer {
      - env: simpy.Environment
      - daily_events: list
      - current_item_id : int
      - current_job_id : int
      - printer_store : Store
      - temp_job_list: list
      + create_jobs_continuously()
    }

    class Job {
      - job_id: int
      - items: list~Item~
      - build_time : int
      - washing_time : int
      - drying_time : int
    }

    class Item {
      - env: simpy.Environment
      - item_id: int
      - job_id: int
      - size: int
      - post_process_time : int
      - packaging_time : int
    }


    class Proc_Printer {
      - env: simpy.Environment
      - daily_events: list
      - printer_id : int
      - is_busy: bool
      - printer_store : Store
      - washing_store : Store

      + seize()
      + delay()
      + release()
    }

    class Proc_Washing {
      - env: simpy.Environment
      - daily_events: list
      - processing_time : int
      - is_busy: bool
      - washing_store : Store
      - drying_store : Store

      + seize()
      + delay()
      + release()
    }

    class Proc_Drying {
      - env: simpy.Environment
      - daily_events: list
      - processing_time : int
      - is_busy: bool
      - drying_store : Store
      - postprocess_store : Store

      + seize()
      + delay()
      + release()
    }

    class Proc_PostProcessing {
      - env: simpy.Environment
      - daily_events: list
      - processing_time : int
      - is_busy: bool
      - postprocess_store : Store
      - package_store : Store

      + seize()
      + delay()
      + release()
    }

    class Proc_Packaging {
      - env: simpy.Environment
      - daily_events: list
      - processing_time : int
      - is_busy: bool
      - package_store : Store
      - product_list : list

      + seize()
      + delay()
      + release()
    }
 

    

    %% 관계 표현
    Customer --> Job : creates
    Job o-- Item : contains
    Customer --> Proc_Printer : transmit
    Proc_Printer --> Proc_Washing : calls
    Proc_Washing --> Proc_Drying : calls
    Proc_Drying --> Proc_PostProcessing : calls
    Proc_PostProcessing --> Proc_Packaging : calls