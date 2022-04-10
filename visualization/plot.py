import plotly.express as px
import pandas as pd

df = pd.DataFrame([
    dict(State="run", Process="P1", Start=0, Finish=30),
    dict(State="wait", Process="P2", Start=3, Finish=30),
    dict(State="run", Process="P2", Start=30, Finish=48),
    dict(State="wait", Process="P3", Start=6, Finish=48),
    dict(State="run", Process="P3", Start=48, Finish=57)
])

df['time'] = df['Finish'] - df['Start']

print(df)

fig = px.timeline(df,
                  x_start="Start", # 시작
                  x_end="Finish", # 끝
                  y="Process", # y 축 데이터
                  title="FCFS", # 제목
                  color="State", # 색
                  text="time" # 라벨
                  )

fig.layout.xaxis.type = 'linear'
fig.data[0].x = [30, 18, 9]
fig.data[1].x = [27, 42]

fig.add_vline(x=0, line_width=2, line_color="black", line_dash="dash", annotation_text=" 0")
fig.add_vline(x=3, line_width=2, line_color="black", line_dash="dash", annotation_text=" 3")
fig.add_vline(x=6, line_width=2, line_color="black", line_dash="dash", annotation_text=" 6")

fig.add_vline(x=30, line_width=2, line_color="black", line_dash="dash", annotation_text=" 30")
fig.add_vline(x=48, line_width=2, line_color="black", line_dash="dash", annotation_text=" 48")
fig.add_vline(x=57, line_width=2, line_color="black", line_dash="dash", annotation_text=" 57")

fig.update_traces(
    textfont_size=14 # 폰트 사이즈
)
fig.show()
print(fig)
