import matplotlib.pyplot as plt
import pandas as pd
import random

from log import *
from config import *
from environment import *
from datetime import datetime, timedelta

def format_time(env_now):
    """ SimPy의 현재 시간을 'HH시' 또는 'Day X' 형식으로 변환 """
    hours = int(env_now % 24)  # 현재 시간 (0~23)
    if hours == 0:  # 24시간(=0시)이 될 때마다 Day X 추가
        days = int(env_now // 24)
        return f"Day {days + 1}"
    return f"{hours}"

def plot_gantt_chart(gantt_data):
    
    df = pd.DataFrame(gantt_data)
    fig, ax = plt.subplots(figsize=(14, 8))

    # 각 프린터에 대해 작업을 그린다.
    for machine in df['Machine'].unique():
        machine_data = df[df['Machine'] == machine]
        for idx, row in machine_data.iterrows():
            ax.barh(machine, row['End Time'] - row['Start Time'], left=row['Start Time'], height=0.3, label=row['Model'])
    
    
    max_time = df['End Time'].max()  # 최대 시간 (예: 72시간)
    x_ticks = np.arange(0, max_time + 1, 1)  # 1시간 간격으로 생성
    x_labels = [format_time(t) for t in x_ticks]  # 변환된 시간 라벨 적용

    ax.set_xticks(x_ticks[::2])  # 3시간 간격으로 눈금 표시
    ax.set_xticklabels(x_labels[::2], rotation=45, ha='right')  # X축 라벨 적용

    ax.set_xlabel('Time')
    ax.set_ylabel('Machines')
    ax.set_title('Gantt Chart for Print and PostProcess')
    ax.legend()

    
    plt.show()