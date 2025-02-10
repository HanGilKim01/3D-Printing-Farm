import matplotlib.pyplot as plt
from log import *
from config import *


gantt_data = []

def plot_gantt_chart(gantt_data):
    fig, ax = plt.subplots(figsize=(10, 5))

    # 각 작업에 대한 y축 위치 지정
    task_positions = {"Production": 10, "PostProcess": 20}
    yticks = []
    ylabels = []

    for task, start, duration in gantt_data:
        ax.broken_barh([(start, duration)], (task_positions[task], 8), facecolors='tab:blue' if task == "Production" else 'tab:red')

        # 중복된 작업 이름이 아닌 경우만 추가
        if task_positions[task] not in yticks:
            yticks.append(task_positions[task] + 4)
            ylabels.append(task)

    ax.set_xlabel("Time (Hours)")
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    ax.grid(True)

    plt.title("SimPy Production & PostProcess Gantt Chart")
    plt.show()

"""
def viz_sq():
    for graph in GRAPH_LOG.keys(): #GRAPH_LOG 각 항목을 순회하며 데이터를 그래프로 그림
        plt.plot(GRAPH_LOG[graph], label=f'{graph}') #(시간 단위 데이터 리스트, 그래프 라벨설정)
    plt.xlabel('hours') #x축 = 시간
    plt.legend() # 그래프 범례 표시
    plt.show() # 시각화 출력
"""

def record_graph(item):
    for info in item.keys():
        GRAPH_LOG[item[info]['NAME']] = [] #그래프 초기화, 각 재고 항목에 대해 저장 공간 생성
        
    print(GRAPH_LOG)

    
'''
#태원 파일
import matplotlib.pyplot as plt
from config_SimPy import *

def visualization(export_Daily_Report, export_Cost_Report):
    Visual_Dict = {
        'Material': [],
        'Material Total': [],
        'Product': [],
        'Total Cost': [],  # Total Cost 항목 추가
        'Keys': {'Material': [], 'Material Total': [], 'Product': [], 'Total Cost': []}
    }
    Key = ['Material', 'Product', 'Total Cost']  # Total Cost를 Key에 추가

    for id in I.keys():
        temp = []
        for x in range(SIM_TIME): 
            temp.append(export_Daily_Report[x][id*8+7])  # 매일 말 재고량 기록
        Visual_Dict[export_Daily_Report[0][id*8+2]].append(temp)  # 업데이트
        Visual_Dict['Keys'][export_Daily_Report[0][2+id*8]].append(export_Daily_Report[0][id *8+1])  # Keys 업데이트
    
        if I[id]['NAME'] == 'MATERIAL 1':
            temp_transit = []
            temp_total = []
            for x in range(SIM_TIME):
                in_transition = export_Daily_Report[x][id*8+6]  # IN_TRANSITION 위치
                temp_transit.append(export_Daily_Report[x][id*8+6])  # IN_TRANSITION 위치 (id*8+6)
                temp_total.append(export_Daily_Report[x][id*8+7] + in_transition)
            Visual_Dict['Material Total'].append(temp_total)
            Visual_Dict['Keys']['Material Total'].append('Material Total')

    # Total Cost 데이터 추가
    total_cost_data = list(export_Cost_Report)  # 단순히 리스트로 변환
    Visual_Dict['Total Cost'].append(total_cost_data)
    Visual_Dict['Keys']['Total Cost'].append('Total Cost')

    # 시각화 생성
    visual = VISUALIAZTION.count(1)
    count_type = 0
    cont_len = 1
    for x in VISUALIAZTION:
        if x == 1:
            plt.subplot(int(f"{visual}1{cont_len}"))
            cont_len += 1
            if count_type < len(Key):  # Key 리스트의 길이를 초과하지 않도록 검사
                days = range(1, SIM_TIME + 1)  # Day 1, Day 2, ..., Day N 설정
                for lst in Visual_Dict[Key[count_type]]:
                    plt.plot(days, lst, label=Visual_Dict['Keys'][Key[count_type]][0])
                    if Key[count_type] == 'Material':
                        plt.plot(days, Visual_Dict['Material Total'][0], label='Material Total', linestyle='--')
                        reorder_point = REORDER_LEVEL
                        plt.axhline(y=reorder_point, color='r', linestyle='--', label='Reorder Point')
                    plt.legend()

            # x축 레이블을 Day로 설정
            plt.xticks(ticks=days, labels=[f"{day}" for day in days], rotation=45)
            plt.xlabel("Day")
            count_type += 1

    plt.savefig("Graph")
    plt.clf()

'''