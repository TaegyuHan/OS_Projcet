import plotly.express as px
from model.fcfs import FCFS
from model.sjf import SJF
from model.hrn import HRN
from model.rr import RR
from model.srt import SRT
from model.non_preemptive_priority import NPS
from model.preemptive_priority import PS


class TimeLinePlot:
    """
        프로세스 스케줄링 시각화
    """
    MODLE = {
        "fcfs": FCFS(),
        "sjf": SJF(),
        "hrn": HRN(),
        "rr": RR(),
        "srt": SRT(),
        "nps": NPS(),
        "ps": PS()
    }

    @staticmethod
    def show_plot(logic_name: str):
        """ 원하는 로직에 맞춰서 시각화 보여주기 """

        model = TimeLinePlot.MODLE[logic_name] # 모델 선택
        df = model.pandas_table # 데이터 프레임 가져오기
        # 시각화 객체
        fig = px.timeline(df,
                          x_start="start",  # 시작
                          x_end="finish",  # 끝
                          y="process",  # y 축 데이터
                          title=model.NAME,  # 제목
                          color="state",  # 색
                          text="time"  # 라벨
                          )

        fig.layout.xaxis.type = 'linear' # x축 시간에서 숫자로 변경

        # state : run < 작동 기간 데이터
        fig.data[0].x = df["time"][df.state == model.STATE_RUN].tolist()
        try:
            # state : wait < 대기 시간 데이터
            fig.data[1].x = df["time"][df.state == model.STATE_WAIT].tolist()
        except IndexError: pass# 대기상태가 없는 경우

        # 프로세스 시작, 종료선
        for time in model.arrival_times:
            fig.add_vline(x=time,
                          line_width=2,
                          line_color="black",
                          line_dash="dash",
                          annotation_text=f" {time}")

        for time in model.end_times:
            fig.add_vline(x=time,
                          line_width=2,
                          line_color="black",
                          line_dash="dash",
                          annotation_text=f" {time}")

        fig.update_traces(textfont_size=14) # 프로세스 라벨 폰트 사이즈
        # print(fig)
        return fig

if __name__ == '__main__':
    TimeLinePlot.show_plot("srt").show()