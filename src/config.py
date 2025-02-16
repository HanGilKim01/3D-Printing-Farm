import random  # For random number generation
import numpy as np


#### Items #####################################################################
# ID: Index of the element in the dictionary
# TYPE: Product, Material, WIP; 교정기, 재료, 진행중
# NAME: Item's name or model;
# CUST_ORDER_CYCLE: Customer ordering cycle [days]
# INIT_LEVEL: Initial inventory level [units]
# ORDER_QUANTITY: Demand quantity for the final product [units] -> THIS IS UPDATED EVERY 24 HOURS (Default: 0)
# DUE_DATE: Term of customer order to delivered [days]

#### Processes #####################################################################
# ID: Index of the element in the dictionary
# PRODUCTION_RATE [units/day] 
# INPUT_TYPE_LIST: List of types of input materials or WIPs
# QNTY_FOR_INPUT_ITEM: Quantity of input materials or WIPs [units]
# OUTPUT: Output WIP or Product
# NUM_PRINTERS : number of 3d printers
# NUM_POST_PROCESSORS : number of post processors

#### Machines #####################################################################

ORDER = {"ORDER_QUANTITY": 10, "CUST_ORDER_CYCLE": 28, "JOB_SIZE": 50 }
#"DUE_DATE": 28

ITEM = {
        0: {"ID": 0, "TYPE": "Product", "NAME": "Aligner",
         "INIT_LEVEL": 0},
        1: {"ID": 1, "TYPE": "WIP", "NAME": "WIP",
         "INIT_LEVEL": 0}
        }


MACHINE = {
            0: {"ID": 0, "TYPE": "Print", "NAME": "PRINTER-1",
               "NUM_PRINTERS" : 2,"OUTPUT": ITEM[1], "PRODUCTION_RATE": 600},
            1: {"ID": 1, "TYPE": "Post-process", "NAME": "Post-processor-1",
                "PRODUCTION_RATE": 48, "NUM_POST_PROCESSORS" : 4,
                "INPUT_TYPE_LIST": [ITEM[1]], "QNTY_FOR_INPUT_ITEM": [1], "OUTPUT": ITEM[0]}
            }


PRINTERS_SIZE = {"SIZE" : 600000}


# if this is not 0, the length of state space of demand quantity is not identical to INVEN_LEVEL_MAX
INVEN_LEVEL_MIN = 0
INVEN_LEVEL_MAX = 600  # Capacity limit of the inventory [units]

# Simulation 기간
SIM_TIME = 3  # [days] per episode

# Scenario about Demand and leadtime
ORDER_SCENARIO = {"Dist_Type": "UNIFORM",
                   "min": 10,
                   "max": 10}

def ORDER_QTY_FUNC(scenario):
    # Uniform distribution
    if scenario["Dist_Type"] == "UNIFORM":
        return random.randint(scenario['min'], scenario["max"])


PRINT_GRAPH_RECORD = True
PRINT_SIM_EVENTS = True
PRINT_SIM_REPORT = True
VISUALIZATION = True
TIME_CORRECTION = 0
