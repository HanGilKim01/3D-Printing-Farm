from config import *
from log import *
import environment as env
import visualization
from visualization import *
from environment import *

# Define the scenario
scenario = {"DEMAND": ORDER_SCENARIO}

# Create environment
simpy_env, inventoryList, BuildList, postprocessList, customer, daily_events = env.create_env(ITEM, MACHINE, LOG_DAILY_EVENTS)

env.simpy_event_processes(simpy_env, inventoryList, BuildList, postprocessList,  customer, daily_events, ITEM, scenario)


if PRINT_SIM_EVENTS:
    print(f"============= Initial Inventory Status =============")
    for inventory in inventoryList:
        print(
            f"{ITEM[inventory.item_id]['NAME']} Inventory: {inventory.on_hand_inventory} units")

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

"""
if VISUALIZATION != False:
    visualization.generate_gantt_chart(export_Daily_Report)
"""

"""
if PRINT_GRAPH_RECORD :
    production_log = log_production(daily_events)
    generate_gantt_chart(production_log)

if PRINT_GRAPH_RECORD:
    plot_gantt_chart(gantt_data)
"""
