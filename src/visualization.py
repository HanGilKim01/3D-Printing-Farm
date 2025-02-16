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

"""
# 간트차트 생성하여 작업 시각화
def generate_gantt_chart(export_Daily_Report):
    
    #생산 로그를 기반으로 간트차트 생성
    
    daily_reports = pd.DataFrame(export_Daily_Report)

    def convert_time_to_float(time_value):
        if isinstance(time_value, str):
            try:
                hour, minutes = map(int, time_value.split(":"))
                return hour + minutes / 60.0
            except ValueError:
                return None
        elif isinstance(time_value, (int, float)):
            return time_value
        return None
    
    time_columns = ["Print_start", "Print_end", "Post_start", "Post_end"]

    for col in time_columns:
        if col in daily_reports.columns:
            daily_reports[col] = daily_reports[col].apply(convert_time_to_float)

    # 색상 생성
    def generate_color():
        return [random.random() for _ in range(3)]
    
    job_colors = {job: generate_color() for job in daily_reports["Job"].unique()}

    all_printers = sorted(daily_reports["Printer"].dropna().unique())
    all_post_processors = sorted(daily_reports["PostProcessor"].dropna().unique())

    resource_labels = (
        [f"Printer {int(printer)}" for printer in all_printers] +
        [f"PostProcessor {int(post_processor)}" for post_processor in all_post_processors]
    )

    resource_map = {label: idx for idx, label in enumerate(resource_labels)}


    fig, ax = plt.subplots(figsize=(16, 10))

    for _, row in daily_reports.iterrows():
        if not pd.isna(row["Printer"]) :
            y_pos = resource_map[f"Printer {int(row['Printer'])}"]
            duration = row["Print_end"] - row["Print_start"]
            ax.barh(
                y_pos,
                duration,
                left=row["Print_start"],
                color=job_colors[row["Job"]],
                edgecolor="black",
                label=f"Job {row['Job']}" if f"Job {row['Job']}" not in ax.get_legend_handles_labels()[1] else None
            )
            ax.text(
                row["Print_start"] + duration / 2,
                y_pos,
                f"Job {row['Job']}",
                va="center",
                ha="center",
                color="white",
                fontsize=8,
                weight="bold"
            )
            ax.text(
                row["Print_start"] + duration / 2,
                y_pos - 0.2,
                f"{duration:.2f} hours",
                va="center",
                ha="center",
                color="black",
                fontsize=8
            )

        if not pd.isna(row["PostProcessor"]) :
            y_pos = resource_map[f"PostProcessor {int(row['PostProcessor'])}"]
            duration = row["Post_end"] - row["Post_start"]
            ax.barh(
                y_pos,
                duration,
                left=row["Post_start"],
                color=job_colors[row["Job"]],
                edgecolor="black"
            )
            ax.text(
                row["Post_start"] + duration / 2,
                y_pos,
                f"Job {row['Job']}",
                va="center",
                ha="center",
                color="white",
                fontsize=8,
                weight="bold"
            )
            ax.text(
                row["Post_start"] + duration / 2,
                y_pos - 0.2,
                f"{duration:.2f} hours",
                va="center",
                ha="center",
                color="black",
                fontsize=8
            )
    

    # 라벨 설정
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Resources")
    ax.set_yticks(list(resource_map.values()))
    ax.set_yticklabels(list(resource_map.keys()))
    ax.set_title("Production Gantt Chart")
    
    # 범례 추가
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    ax.legend(unique_labels.values(), unique_labels.keys(), loc="upper right", bbox_to_anchor=(1.15, 1))
    
    plt.tight_layout
    plt.show()
"""

"""
def log_production(daily_events):
    production_log = {}

    for event in daily_events:
        if "Start:" in event and "End:" in event:
            parts = event.split(": ")
            time_info = parts[0].split()[-1]  # "HH:MM"
            process_info = parts[1]

            process_type = "Print" if "Print" in process_info else "PostProcess"
            machine_id = process_info.split("(")[1].split(")")[0]

            start_time = float(parts[-2].split(" ")[1])  # Start 시간
            end_time = float(parts[-1].split(" ")[1])    # End 시간

            if machine_id not in production_log:
                production_log[machine_id] = []
            production_log[machine_id].append((start_time, end_time, process_type))

    return production_log

gantt_data = []

def plot_gantt_chart(gantt_data):
    fig, ax = plt.subplots(figsize=(10, 5))

    # 각 작업에 대한 y축 위치 지정
    task_positions = {"Print": 10, "PostProcess": 20}
    yticks = []
    ylabels = []

    for task, start, duration in gantt_data:
        ax.broken_barh([(start, duration)], (task_positions[task], 8), facecolors='tab:blue' if task == "Print" else 'tab:red')

        # 중복된 작업 이름이 아닌 경우만 추가
        if task_positions[task] not in yticks:
            yticks.append(task_positions[task] + 4)
            ylabels.append(task)

    ax.set_xlabel("Time (Hours)")
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    ax.grid(True)

    plt.title("SimPy Print & PostProcess Gantt Chart")
    plt.show()
"""
