from config import *
from log import *
import environment as env
from collections import deque
from visualization import *
viz_sq = deque()



# Define the scenario
scenario = {"DEMAND": DEMAND_SCENARIO, }

# Create environment
simpy_env, inventoryList, productionList, postprocessList, sales, customer, daily_events = env.create_env(
    I, P, LOG_DAILY_EVENTS)
env.simpy_event_processes(simpy_env, inventoryList, 
                          productionList, postprocessList, sales, customer, daily_events, I, scenario)


if PRINT_SIM_EVENTS:
    print(f"============= Initial Inventory Status =============")
    for inventory in inventoryList:
        print(
            f"{I[inventory.item_id]['NAME']} Inventory: {inventory.on_hand_inventory} units")

    print(f"============= SimPy Simulation Begins =============")

for x in range(SIM_TIME):
    print(f"\nDay {(simpy_env.now) // 24+1} Report:")
    simpy_env.run(until=simpy_env.now+24)  # Run the simulation for 24 hours

    # Print the simulation log every 24 hours (1 day)
    if PRINT_SIM_EVENTS:
        for log in daily_events:
            print(log)
    daily_events.clear()

    env.update_daily_report(inventoryList)

"""
if PRINT_GRAPH_RECORD:
    plot_gantt_chart(gantt_data)
"""