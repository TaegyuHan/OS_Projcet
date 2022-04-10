import json
import os
from copy import deepcopy
from dataclasses import dataclass
from pandas import json_normalize


@dataclass
class Process:
    """ 프로세스 데이터 클래스 """
    id: int
    arrival_time: int
    service_time: int
    priority: int
    schedule_id: int
    time_slice: int
    stop_time: int


class ProcessData:
    """
        프로세스 데이터 read 클래스

        ./data폴더의 input_data.json 폴더의 데이터 읽어 옵니다.
    """

    # json 데이터 읽는 부분
    with open((f'{os.path.dirname(__file__)}'
               f'/data/srt_test_data.json')) as json_file:
        data = json.load(json_file)

    # 프로레스 수
    PROCESS_COUNT = data["processesCount"]

    if PROCESS_COUNT == 0:
        raise Exception("프로세스 수가 0입니다. 프로세스를 넣어주세요")

    # 각각의 프로세스 데이터
    DATA = data["data"]

    if not DATA:
        raise Exception("json 데이터에 프로세스가 존재하지 않습니다.")

    if PROCESS_COUNT != len(DATA):
        raise Exception("json 파일의 processesCount와 data의 프로세스 수가 같지 않습니다.")

    # 판다스 데이터 프레임 타입
    PANDAS_DATA = json_normalize(DATA)

    # 프로세스 데이터 클래스 리스트
    DATA_CLASSES_LIST = []
    schedule_id = 0
    for idx, row in PANDAS_DATA.iterrows():
        DATA_CLASSES_LIST.append(
            Process(id=int(row["id"]),
                    arrival_time=int(row["arrivalTime"]),
                    service_time=int(row["serviceTime"]),
                    priority=int(row["priority"]),
                    time_slice=int(row["timeSlice"]),
                    schedule_id=schedule_id,
                    stop_time=int(row["arrivalTime"]))
        )
        schedule_id += 1

    # 프로세스 데이터 클래스 딕셔너리
    DATA_CLASSES_DICT = {}
    for process in DATA_CLASSES_LIST:
        DATA_CLASSES_DICT[str(process.schedule_id)] = process

    @staticmethod
    def data_list() -> list[Process]:
        """ 데이터 리스트 형식으로 반환 """
        return deepcopy(ProcessData.DATA_CLASSES_LIST)

    @staticmethod
    def data_dict() -> dict[str, Process]:
        """ 데이터 딕셔너리 형식으로 반환 """
        return deepcopy(ProcessData.DATA_CLASSES_DICT)


if __name__ == '__main__':
    ProcessData.DATA_CLASSES_DICT