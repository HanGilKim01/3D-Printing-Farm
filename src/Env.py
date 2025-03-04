import simpy
import numpy as np
from config import *  # Assuming this imports necessary configurations
from log import *  # Assuming this imports necessary logging functionalities
from visualization import *
import random



item_list = [[random.randint(8, 12) for _ in range(JOB['JOB_SIZE'])] for _ in range(JOB['JOB_QUANTITY'])]

class Item :
    """
    Item에 대한 정보를 담음
    """
    def __init__(self, item_id, value):
        self.id = item_id
        self.value = value

    def transform_list(item_list):
        """랜덤 리스트를 Item 객체 리스트로 변환하고, ID 리스트 반환"""
        return [[i + 1 for i in range(len(item_list))] for item_list in item_list]

class Job:
    """
    Job 리스트를 생성하는 클래스
    """
    def __init__(self, job_quantity, item_list):
        self.job_quantity = job_quantity
        self.item_list = item_list
        self.job_list = self.create_job_list()

    def create_job_list(self):
        """Item 클래스를 활용해 변환된 리스트를 받아 Job 리스트 생성"""
        transformed_item_list = Item.transform_list(self.item_list)
        return [{"Job_id": job_id + 1, "Item_id": item_list} for job_id, item_list in enumerate(transformed_item_list)]

    def get_jobs(self):
        """생성된 Job 리스트 반환"""
        return self.job_list

# Job 객체 생성 및 Job 리스트 출력
job = Job(JOB['JOB_QUANTITY'], item_list)


#print(job.get_jobs())