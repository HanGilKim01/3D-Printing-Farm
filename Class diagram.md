```mermaid
classDiagram
    
    class Customer {
      - env: simpy.Environment
      - daily_events: list
      - item_id : int
      - job_id : int
      - printer_queue : queue
      - temp_job_list: list
      - interval : int
      + create_jobs()
    }

    class Job {
      - job_id: int
      - items: list
      - build_time : int
      - washing_time : int
      - drying_time : int
    }

    class Item {
      - env: simpy.Environment
      - item_id: int
      - job_id: int
      - volume: int
      - post_process_time : int
      - packaging_time : int
    }


    class Proc_Printer {
      - env: simpy.Environment
      - daily_events: list
      - printer_id : int
      - is_busy: bool
      - printer_queue : queue
      - washing_queue : queue

      + seize()
      + delay()
      + release()
    }

    class Proc_Washing {
      - env: simpy.Environment
      - daily_events: list
      - processing_time : int
      - is_busy: bool
      - washing_queue : queue
      - drying_queue : queue

      + seize()
      + delay()
      + release()
    }

    class Proc_Drying {
      - env: simpy.Environment
      - daily_events: list
      - processing_time : int
      - is_busy: bool
      - drying_queue : queue
      - postprocess_queue : queue

      + seize()
      + delay()
      + release()
    }

    class Proc_PostProcessing {
      - env: simpy.Environment
      - daily_events: list
      - processing_time : int
      - is_busy: bool
      - postprocess_queue : queue
      - package_queue : queue

      + seize()
      + delay()
      + release()
    }

    class Proc_Packaging {
      - env: simpy.Environment
      - daily_events: list
      - processing_time : int
      - is_busy: bool
      - package_queue : queue
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