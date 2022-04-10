import pandas as pd
from model.data import ProcessData as PD
from model.abc_scheduling import Schedule


class PS(Schedule):
    """
        선점 스케쥴링(Preemptive Scheduling) 스케줄링

        Preemptive Scheduling (NPS)
        선점 스케쥴링(Preemptive Scheduling)은 하나의 프로세스가 CPU를
        점유하고 있을 때 다른 프로세스가 CPU를 뺴앗아 차지 할 수 있는 방법
    """

    NAME = "Preemptive Scheduling (PS)"

    def __init__(self):
        super().__init__()

    def _init_logic(self):
        """ PS 스케줄링 로직 """

        # 빨리 온 순으로 역정렬
        self.processes_dict = PD.data_dict()
        # 처음 도착한 프로세스
        next_process = min(self.processes_dict.values(),
                           key=lambda x: x.arrival_time)
        last_process_end_time = 0 # 마지막 프로세스가 돌아간 시간

        while True:
            # 1개의 프로세스
            process = self.processes_dict.\
                pop(str(next_process.schedule_id))

            # 프로세스 도착 시간 저장
            self.process_arrival_times.\
                append(process.arrival_time)

            # 기다린적 있는 시간이 있음
            if last_process_end_time > process.stop_time:
                # 대기 기록

                self._insert_row_data(
                    state=self.STATE_WAIT,
                    process=f"P{process.id}",
                    start=process.stop_time,
                    finish=last_process_end_time,
                    time=last_process_end_time - process.stop_time
                )

                # 실행 중간에 우선순위가 높은 프로세스가 있는지 확인
                tmp_processes = list(filter(lambda x: x.stop_time < (last_process_end_time + process.service_time),
                                            self.processes_dict.values()))

                tmp_processes = list(filter(lambda x: x.priority < process.priority,
                                            tmp_processes))

                if len(tmp_processes) != 0:
                    # 그중에서 서비스 시간 가장 작은 프로세스
                    next_process = min(tmp_processes,
                                       key=lambda x: x.priority)
                    # 있는경우
                    self._insert_row_data(
                        state=self.STATE_RUN,
                        process=f"P{process.id}",
                        start=last_process_end_time,
                        finish=next_process.stop_time,
                        time=next_process.stop_time - last_process_end_time
                    )

                    # 다음 스케줄 까지 실행하고 넘기기
                    process.service_time -= next_process.stop_time - last_process_end_time
                    process.stop_time = next_process.stop_time
                    last_process_end_time = next_process.stop_time
                    self.processes_dict[str(process.schedule_id)] = process
                    continue

                else: # 없는 경우
                    # 해당 프로세스 전부 실행
                    self._insert_row_data(
                        state=self.STATE_RUN,
                        process=f"P{process.id}",
                        start=last_process_end_time,
                        finish=last_process_end_time + process.service_time,
                        time=process.service_time
                    )

                    # 프로세스실행 끝난 시간 저장
                    last_process_end_time = \
                        last_process_end_time + process.service_time

            # 기다린적 없는 프로세스
            elif last_process_end_time <= process.stop_time:

                # 실행 중간에 우선순위가 높은 프로세스가 있는지 확인
                tmp_processes = list(filter(lambda x: x.stop_time < (process.stop_time + process.service_time),
                                            self.processes_dict.values()))
                tmp_processes = list(filter(lambda x: x.priority < process.priority,
                                            tmp_processes))

                if len(tmp_processes) != 0:
                    # 그중에서 서비스 시간 가장 작은 프로세스
                    next_process = min(tmp_processes,
                                       key=lambda x: x.stop_time)
                    # 있는경우
                    self._insert_row_data(
                        state=self.STATE_RUN,
                        process=f"P{process.id}",
                        start=process.stop_time,
                        finish=next_process.stop_time,
                        time=next_process.stop_time - process.stop_time
                    )

                    # 다음 스케줄 까지 실행하고 넘기기
                    process.service_time -= next_process.stop_time - process.stop_time
                    process.stop_time = next_process.stop_time
                    last_process_end_time = next_process.stop_time
                    self.processes_dict[str(process.schedule_id)] = process
                    continue

                else: # 없는 경우
                    # 해당 프로세스 전부 실행
                    self._insert_row_data(
                        state=self.STATE_RUN,
                        process=f"P{process.id}",
                        start=process.stop_time,
                        finish=process.stop_time + process.service_time,
                        time=process.service_time
                    )

                    # 프로세스실행 끝난 시간 저장
                    last_process_end_time = \
                        process.stop_time + process.service_time

            # 프로세스 실행 완료 시각 저장
            self.process_end_times. \
                append(last_process_end_time)

            # 프로세스가 없으면 종료
            if not self.processes_dict:
                break

            # 프로세스 종료 시간 전에 도착한 프로세스 필터링
            tmp_processes = list(filter(lambda x: x.stop_time <= last_process_end_time,
                                   self.processes_dict.values()))

            # 종료시간전에 도착한 프로세스가 있으면
            if len(tmp_processes) != 0:
                # 그중에서 서비스 시간 가장 작은 프로세스
                next_process = min(tmp_processes,
                                   key=lambda x: x.priority)
            else: # 없으면
                # 가장 빨리 도착하는 프로세스
                next_process = min(self.processes_dict.values(),
                                   key=lambda x: x.stop_time)

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
    ps = PS()
    print(ps.pandas_table)
    # print(fcfs.arrival_times)
    # print(fcfs.end_times)