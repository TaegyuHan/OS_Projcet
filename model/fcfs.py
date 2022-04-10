from collections import deque
import pandas as pd
from pandas import DataFrame

from model.data import ProcessData as PD
from model.abc_scheduling import Schedule


class FCFS(Schedule):
    """
        FCFS 스케줄링

        First Come First Served (FCFS)
        준비큐에 도착한 순서대로 CPU를 할당하는 비선점형 방식으로,
        선입선출 스케줄링이라고도 한다.
    """

    NAME = "First Come First Served (FCFS)"

    def __init__(self):
        super().__init__()

    def _init_logic(self):
        """ FCFS 스케줄링 로직 """

        # 프로세스 빨리온 순으로 정렬
        process_arrival_time_sorted = \
            sorted(PD.data_list(),key=lambda x: x.arrival_time)

        d = deque(process_arrival_time_sorted) # 큐에 저장
        last_process_end_time = 0 # 마지막 프로세스가 돌아간 시간

        # 프로세스 전부 실행시킬 때 까지 실행
        while d:
            # 1개의 프로세스
            process = d.popleft()

            # 프로세스 도착 시간 저장
            self.process_arrival_times.\
                append(process.arrival_time)

            # 대기가 있는 프로세스
            if last_process_end_time > process.arrival_time:
                # 대기 기록
                self._insert_row_data(
                    state=self.STATE_WAIT,
                    process=f"P{process.id}",
                    start=process.arrival_time,
                    finish=last_process_end_time,
                    time=last_process_end_time - process.arrival_time
                )

                # 대기 후 실행 기록
                self._insert_row_data(
                    state=self.STATE_RUN,
                    process=f"P{process.id}",
                    start=last_process_end_time,
                    finish=last_process_end_time + process.service_time,
                    time=process.service_time
                )

                # 프로세스실행 끝난 시간 저장
                last_process_end_time += process.service_time

            # 프로세스 실행이 끝난뒤에 프로세스가 도착한 경우
            elif last_process_end_time <= process.arrival_time:

                self._insert_row_data(
                    state=self.STATE_RUN,
                    process=f"P{process.id}",
                    start=process.arrival_time,
                    finish=process.arrival_time + process.service_time,
                    time=process.service_time
                )

                # 프로세스실행 끝난 시간 저장
                last_process_end_time = \
                    process.arrival_time + process.service_time

            # 프로세스 실행 완료 시각 저장
            self.process_end_times. \
                append(last_process_end_time)

    def _insert_row_data(self,
                         state: str,
                         process: str,
                         start: int,
                         finish: int,
                         time: int) -> None:
        """ row 데이터 받기 """

        self.row_data.append(dict(
            state=state,
            process=process,
            start=start,
            finish=finish,
            time=time
        ))

    @property
    def pandas_table(self) -> DataFrame:
        """
            판다스 데이터 프레임
            list > DataFrame 로 변경
        """
        return pd.DataFrame(self.row_data)

    @property
    def arrival_times(self) -> list[int]:
        """ 프로세스 도착 시간 """
        return self.process_arrival_times

    @property
    def end_times(self) -> list[int]:
        """ 프로세스 끝나는 시간 """
        return self.process_end_times


if __name__ == '__main__':
    fcfs = FCFS()
    print(fcfs.pandas_table)
    # print(fcfs.arrival_times)
    # print(fcfs.end_times)