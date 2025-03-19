```mermaid
classDiagram
    
    class Customer {
      + env: simpy.Environment
      + daily_events: list
      + item_id : int
      + job_id : int
      + printer_queue : queue
      + temp_job_list: list
      + interval : int
      + create_jobs()
    }

    class Job {
      + job_id: int
      + items: list
      + create_time : int
    }

    class Item {
      + env: simpy.Environment
      + item_id: int
      + job_id: int
      + volume: int
    }


    class Proc_Build {
      + env: simpy.Environment
      + daily_events: list
      + printer_id : int
      + process_id : int
      + process_name : int
      + printer_queue : list
      + washing_queue : list
    }

    class Proc_Washing {
      + env: simpy.Environment
      + daily_events: list
      + processing_time : int
      + process_id : int
      + process_name : int
      + washing_queue : list
      + drying_queue : list


    }

    class Proc_Drying {
      + env: simpy.Environment
      + daily_events: list
      + processing_time : int
      + process_id : int
      + process_name : int
      + drying_queue : list
      + postprocess_queue : list


    }

    class Proc_PostProcessing {
      + env: simpy.Environment
      + daily_events: list
      + processing_time : int
      + process_id : int
      + process_name : int
      + postprocess_queue : list
      + package_queue : list


    }

    class Proc_Packaging {
      + env: simpy.Environment
      + daily_events: list
      + processing_time : int
      + process_id : int
      + process_name : int
      + package_queue : list
      + product_list : list

    }
 
    class BaseProcess {
      + env : simpy.Environment
      + daily_events : list
      + process_id : int
      + in_queue : list
      + out_queue : list
      + process_name : int
      + process_time : int
      + is_busy : bool

      + seize()
      + delay(job)
      + release(job)
    }
    

    %% 관계 표현
    Customer --> Job : creates
    Job o-- Item : contains
    Customer --> Proc_Build : transmit
    Proc_Build --> Proc_Washing : sends
    Proc_Washing --> Proc_Drying : sends
    Proc_Drying --> Proc_PostProcessing : sends
    Proc_PostProcessing --> Proc_Packaging : sends
    BaseProcess --> Proc_Build : inherit
    BaseProcess --> Proc_Washing : inherit
    BaseProcess --> Proc_Drying : inherit
    BaseProcess --> Proc_PostProcessing : inherit
    BaseProcess --> Proc_Packaging : inherit