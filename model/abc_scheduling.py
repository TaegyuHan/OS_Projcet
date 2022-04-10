from abc import ABC, abstractmethod


class Schedule(ABC):

    STATE_RUN = "run"
    STATE_WAIT = "wait"

    @abstractmethod
    def __init__(self):
        self.process_arrival_times = []
        self.process_end_times = []
        self.row_data = []
        self._init_logic()

    @abstractmethod
    def _init_logic(self):
        """ 스케줄링 로직 """

    @abstractmethod
    def _insert_row_data(self):
        """ 데이터 받기 """

    @abstractmethod
    def pandas_table(self):
        """ 시각화 데이터 프레임 """

    @abstractmethod
    def arrival_times(self):
        """ 프로세스 시작 시간 """

    @abstractmethod
    def end_times(self):
        """ 프로세스 시작 시간 """