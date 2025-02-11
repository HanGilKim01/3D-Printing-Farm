import random  # For random number generation
import os
import numpy as np
import shutil

#### Items #####################################################################
# ID: Index of the element in the dictionary
# TYPE: Product, Material, WIP; 교정기, 재료, 진행중
# NAME: Item's name or model;
# CUST_ORDER_CYCLE: Customer ordering cycle [days]
# INIT_LEVEL: Initial inventory level [units]
# DEMAND_QUANTITY: Demand quantity for the final product [units] -> THIS IS UPDATED EVERY 24 HOURS (Default: 0)
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
#수정사항 변경 되었는지 확인용



# Assembly Process 1

I = {0: {"ID": 0, "TYPE": "Product",      "NAME": "PRODUCT",
         "CUST_ORDER_CYCLE": 28,
         "INIT_LEVEL": 0,
         "DEMAND_QUANTITY": 0,
         "DUE_DATE": 28,},
     1: {"ID": 1, "TYPE": "WIP", "NAME": "WIP",
         "INIT_LEVEL": 0}}

#1: {"ID": 1, "TYPE": "Material", "NAME": "MATERIAL 1", "INIT_LEVEL": 500,}


P = {0: {"ID": 0, "TYPE": "Build",      "NAME": "Build",
         "PRODUCTION_RATE": 600, "NUM_PRINTERS" : 2,
         "OUTPUT": I[1], 
         },
     1: {"ID": 1, "TYPE": "Post-process", "NAME": "Post-process",
         "PRODUCTION_RATE": 48, "NUM_POST_PROCESSORS" : 4,
         "INPUT_TYPE_LIST": [I[1]], "QNTY_FOR_INPUT_ITEM": [1], "OUTPUT": I[0]
         }}

M = {0: {"ID": 0, "TYPE": "Printer", "NAME": "Printer-1","PRODUCTION_RATE": 600}, 1:{"ID": 0, "TYPE": "Printer", "NAME": "Printer-2","PRODUCTION_RATE": 600}}


# State space
# if this is not 0, the length of state space of demand quantity is not identical to INVEN_LEVEL_MAX
INVEN_LEVEL_MIN = 0
INVEN_LEVEL_MAX = 600  # Capacity limit of the inventory [units]

# Simulation
SIM_TIME = 3  # [days] per episode

# Count for intransit inventory
# 재고 항목 I 에서 Material 유형의 항목 수를 계산 하는 부분.
# MAT_COUNT는 material 재고 항목수를 저장하는 변수, 초기값0
# 즉, 속성을 확인해서 해당 항목이 Material이면 1씩 증가시켜서 총 항목 수를 정리. 이 파일의 경우 1개
MAT_COUNT = 0
for id in I.keys():
    if I[id]["TYPE"] == "Material":
        MAT_COUNT += 1

# Scenario about Demand and leadtime
ORDER_SCENARIO = {"Dist_Type": "UNIFORM",
                   "min": 500,
                   "max": 500}


def DEFINE_FOLDER(folder_name):
    if os.path.exists(folder_name):
        file_list = os.listdir(folder_name)
        folder_name = os.path.join(folder_name, f"Train_{len(file_list)+1}")
    else:
        folder_name = os.path.join(folder_name, "Train_1")
    os.makedirs(folder_name)
    return folder_name


def save_path(path):
    if os.path.exists(path):
        shutil.rmtree(path)

    # Create a new folder
    os.makedirs(path)
    return path


def DEMAND_QTY_FUNC(scenario):
    # Uniform distribution
    if scenario["Dist_Type"] == "UNIFORM":
        return random.randint(scenario['min'], scenario["max"])
    # Gaussian distribution
    elif scenario["Dist_Type"] == "GAUSSIAN":
        # Gaussian distribution
        demand = round(np.random.normal(scenario['mean'], scenario['std']))
        if demand < 0:
            return 1
        elif demand > INVEN_LEVEL_MAX:
            return INVEN_LEVEL_MAX
        else:
            return demand



PRINT_GRAPH_RECORD = True
# Ordering rules : Reorder point (S) and Order quantity (Q)
# USE_SQPOLICY = True  : When using SQpolicy (DRL is NOT used)
# USE_SQPOLICY = False  : When NOT using SQpolicy (DRL is used)
USE_SQPOLICY = False

# Print logs
PRINT_SIM_EVENTS = True
PRINT_SIM_REPORT = True

TIME_CORRECTION = 0.0001
