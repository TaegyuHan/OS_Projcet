import pandas as pd
from model.data import ProcessData as PD, Process
from model.abc_scheduling import Schedule


class SRT(Schedule):
    """
        SRT 스케줄링

        Shortest Remaining Time (SRT)
        SJF 스케줄링과 라운드 로빈 스케줄링을 혼합한 방식으로, 최소 잔류
        시간 우선 스케줄링이라고 한다.
    """

    NAME = "Shortest Remaining Time (SRT)"

    def __init__(self):
        super().__init__()

    def _init_logic(self):
        """ SRT 스케줄링 로직 """

        # 빨리 온 순으로 역정렬
        self.processes_dict = PD.data_dict()
        # 처음 도착한 프로세스
        next_process = min(self.processes_dict.values(),
                           key=lambda x: x.arrival_time)
        last_process_end_time = 0 # 마지막 프로세스가 돌아간 시간

        while True: # 프로세스 데이터 전부 빠질때 까지 실행

            # 프로세스가 없으면 종료
            process = self.processes_dict.\
                pop(str(next_process.schedule_id))

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
                process.stop_time = last_process_end_time + tmp_service_time

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

            if process.service_time > 0:
                self.processes_dict[str(process.schedule_id)] = process

            # 프로세스가 없으면 종료
            if not self.processes_dict:
                break

            # 다음 프로세스 선택
            next_process = \
                self._next_next_process(last_process_end_time)

    def _next_next_process(self, last_process_end_time: int) -> Process:
        """ 다음 프로세스 선택 <핵심 로직>

        :param last_process_end_time (int): 마지막으로 끝난 프로세스 시간
        :return: (Process)
        """
        # 프로세스 종료 시간 전에 도착한 프로세스 필터링
        tmp_processes = list(filter(lambda x: x.arrival_time <= last_process_end_time,
                                    self.processes_dict.values()))

        # 종료시간전에 도착한 프로세스가 있으면
        if len(tmp_processes) != 0:
            # 그중에서 서비스 시간 가장 작은 프로세스
            next_process = min(tmp_processes,
                               key=lambda x: x.service_time)

        else:  # 없으면
            # 가장 빨리 도착하는 프로세스
            next_process = min(self.processes_dict.values(),
                               key=lambda x: x.arrival_time)

        return next_process

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
    srt = SRT()
    print(srt.pandas_table)
    # print(srt.arrival_times)
    # print(srt.end_times)