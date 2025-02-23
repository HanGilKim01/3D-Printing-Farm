from config import *
from log import *
import environment as env
import visualization
from visualization import *
from environment import *

# Define the scenario
scenario = {"DEMAND": ORDER_SCENARIO}

# Create environment
simpy_env, printer, postprocessor, customer, daily_events = env.create_env(ITEM, MACHINE, LOG_DAILY_EVENTS)

env.simpy_event_processes(simpy_env, printer, postprocessor, customer, daily_events, ITEM, scenario)


if PRINT_SIM_EVENTS:
    print(f"============= SimPy Simulation Begins =============")

for x in range(SIM_TIME):
    print(f"\nDay {(simpy_env.now) // 24+1} Report:")
    simpy_env.run(until=simpy_env.now+24)  # Run the simulation for 24 hours

    # Print the simulation log every 24 hours (1 day)
    if PRINT_SIM_EVENTS:
        for log in daily_events:
            print(log)
    daily_events.clear()

  # 간트차트 데이터 저장


plot_gantt_chart(gantt_data)    

export_Daily_Report = []
