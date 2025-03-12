```mermaid
sequenceDiagram
    participant A as Customer 
    participant B as Proc_Printer
    participant C as Proc_Washing
    participant D as Proc_Drying
    participant E as Proc_PostProcessing
    participant F as Proc_Packaging




    A->>A: create_job
    note left of A : Job contains item list
    A->>B: transmit job_list
    B->>B: seize / delay / release
    B->>C: calls
    C->>C: seize / delay / release
    C->>D: calls
    D->>D: seize / delay / release
    D->>E: calls
    E->>E: seize / delay / release
    E->>F: calls
    F->>F: seize / delay / release
