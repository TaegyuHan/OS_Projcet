from collections import deque

import pandas as pd
from model.data import ProcessData as PD, Process
from model.abc_scheduling import Schedule


class RR(Schedule):
    """
        RR 스케줄링

        Round-robin (RR)
        프로세스가 할당받은 시간 ( 타임 슬라이스 ) 동안 작업을 하다가
        작업을 완료하지 못하면 준비 큐의 맨뒤로 가서 자기 차례를 기다
        리는 방식이다.
    """

    NAME = "Round-robin (RR)"

    def __init__(self):
        super().__init__()

    def _init_logic(self):
        """ RR 스케줄링 로직 """

        # 프로세스 빨리온 순으로 정렬
        process_arrival_time_sorted = \
            sorted(PD.data_list(),
                   key=lambda x: x.arrival_time)

        d = deque([process_arrival_time_sorted.pop(0)]) # 큐에 저장
        last_process_end_time = 0 # 마지막 프로세스가 돌아간 시간

        # 프로세스 데이터 전부 빠질때 까지 실행
        while process_arrival_time_sorted or d:

            if d: # 동작 프로세스 선택
                process = d.popleft() # 기존의 큐에서 선택
            else: # 큐에 데이터가 없어서
                d.append(process_arrival_time_sorted.pop(0))
                process = d.popleft()

            # 프로세스 도착 시간 저장
            self.process_arrival_times.\
                append(process.arrival_time)

            # 프로세스 대기가 존재했는지 확인
            if last_process_end_time > process.stop_time:

                # 대기 기록
                self._insert_row_data(
                    state=self.STATE_WAIT,
                    process=f"P{process.id}",
                    start=process.stop_time,
                    finish=last_process_end_time,
                    time=last_process_end_time - process.stop_time
                )

                # 타임슬라이스 계산
                tmp_service_time, process = \
                    self._calc_time_slice(process)

                # 대기 후 실행 기록
                self._insert_row_data(
                    state=self.STATE_RUN,
                    process=f"P{process.id}",
                    start=last_process_end_time,
                    finish=last_process_end_time + tmp_service_time,
                    time=tmp_service_time
                )

                # 프로세스 데이터 수정
                process.stop_time = \
                    last_process_end_time + tmp_service_time

                # 프로세스실행 끝난 시간 저장
                last_process_end_time += tmp_service_time

            # 프로세스 실행이 끝난뒤에 프로세스가 도착한 경우
            elif last_process_end_time <= process.stop_time:

                # 타임슬라이스 계산
                tmp_service_time, process = \
                    self._calc_time_slice(process)

                self._insert_row_data(
                    state=self.STATE_RUN,
                    process=f"P{process.id}",
                    start=process.stop_time,
                    finish=process.stop_time + tmp_service_time,
                    time=tmp_service_time
                )

                # 프로세스실행 끝난 시간 저장
                last_process_end_time = process.stop_time + tmp_service_time
                process.stop_time = process.stop_time + tmp_service_time

            # 프로세스 실행 완료 시각 저장
            self.process_end_times. \
                append(last_process_end_time)

            # 프로세스 동작 시간이 남으면 다시 큐에 넣기
            if len(process_arrival_time_sorted) > 0:
                process_check = min(process_arrival_time_sorted,
                                    key=lambda x: x.arrival_time)

                if process_check.arrival_time <= last_process_end_time:
                    d.appendleft(process_arrival_time_sorted.pop(0))

            if process.service_time > 0:
                d.append(process)

    def _calc_time_slice(self, process: Process):
        """ 타임슬라이스 계산

        :param process: 프로세스
        :return:
            tmp_service_time : int
            process : Process
        """

        # 타임슬라이스 계산
        if process.service_time > process.time_slice:
            tmp_service_time = process.time_slice
            process.service_time -= process.time_slice
        else:
            tmp_service_time = process.service_time
            process.service_time -= process.service_time

        return tmp_service_time, process

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
    def pandas_table(self):
        """ 시각화 데이터 프레임 """
        return pd.DataFrame(self.row_data)

    @property
    def arrival_times(self):
        """ 프로세스 도착 시간 """
        return self.process_arrival_times

    @property
    def end_times(self):
        """ 프로세스 끝나는 시간 """
        return self.process_end_times


if __name__ == '__main__':
    rr = RR()
    print(rr.pandas_table)
    # print(fcfs.arrival_times)
    # print(fcfs.end_times)