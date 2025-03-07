```mermaid
sequenceDiagram
    participant A as Customer 
    participant B as Order
    participant C as Product_planning
    participant D as Proc_Build
    participant E as Proc_Wash
    participant F as Proc_Dry
    participant G as Proc_Inspect


    note over B : order contains Job list
    note over C : Assign ID to item and job

    A->>A: create_job_continuously
    note left of A : Job contains item list
    A->>B: transmit data
    B->>B: integrate Job and count order
    B->>C: transmit data
    C->>D: Assign Job
    D->>D: Build_job
    D->>E: Send to queue
    E->>E: Wash_job
    E->>F: Send to queue
    F->>F: Dry_job
    F->>G: Send to queue
    G->>G: Insepect_item