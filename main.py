import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# [페이지 기본 설정]
# 웹앱의 웹브라우저 탭 제목과 레이아웃을 넓게(wide) 설정합니다.
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="영화 박스오피스 분석 데이터 앱",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 1개년 박스오피스 영화 관객수 분석")
st.caption("KOBIS 데이터를 바탕으로 한 영화별 관객수 변화 추이 분석 앱입니다.")

# -----------------------------------------------------------------------------
# [1. 데이터 불러오기 및 2. 데이터 전처리]
# @st.cache_data 데코레이터를 사용하여 데이터를 한 번 불러온 후 메모리에 캐싱(저장)합니다.
# -----------------------------------------------------------------------------
@st.cache_data
def load_and_preprocess_data():
    # 깃허브의 원본 CSV 파일 URL
    csv_url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    
    # pandas를 활용해 CSV 파일 불러오기
    df = pd.read_csv(csv_url)
    
    # 결측치(빈 데이터)가 포함된 행 삭제
    df = df.dropna()
    
    # '기준일자' 컬럼을 datetime(날짜) 형식으로 변환
    df['기준일자'] = pd.to_datetime(df['기준일자'])
    
    # 전체 데이터를 기준일자 오름차순으로 정렬
    df = df.sort_values(by='기준일자', ascending=True)
    
    return df

# 데이터 로딩 실행
df = load_and_preprocess_data()

# -----------------------------------------------------------------------------
# [3. 영화 선택 기능 (사이드바)]
# 영화명 컬럼에서 중복을 제거한 뒤, 누적관객수의 최대값 기준으로 내림차순 정렬하여 목록을 생성합니다.
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 영화 선택 메뉴")

# 각 영화별 최고 누적관객수를 구해서 내림차순 정렬
movie_rank = df.groupby('영화명')['누적관객수'].max().sort_values(ascending=False)
movie_list = movie_rank.index.tolist()

# 드롭다운 선택 상자 만들기 (기본값: 누적관객수 1위 영화)
selected_movie = st.sidebar.selectbox(
    "분석할 영화를 선택하세요:",
    options=movie_list
)

# 사용자가 선택한 영화의 데이터만 필터링
filtered_df = df[df['영화명'] == selected_movie]

# -----------------------------------------------------------------------------
# [4. 그래프 및 영역별 배치]
# -----------------------------------------------------------------------------

# [구역 1] 선택된 영화의 기본 정보 및 핵심 요약
st.subheader(f"📌 선택한 영화: {selected_movie}")

# 선택한 영화의 최고 누적관객수 계산
max_acc_audi = filtered_df['누적관객수'].max()
st.metric(label="총 누적관객수", value=f"{max_acc_audi:,.0f} 명")

st.divider()

# [구역 2] 일별 관객수 변화 추이 선그래프
st.subheader("📈 1. 일별 관객수 변화 추이 (선그래프)")

fig_line = px.line(
    filtered_df,
    x='기준일자',
    y='해당일관객수',
    title=f"[{selected_movie}] 기준일자별 일일 관객수 변화",
    labels={'기준일자': '날짜', '해당일관객수': '해당일 관객수 (명)'},
    markers=True
)

fig_line.update_layout(
    xaxis_title="날짜",
    yaxis_title="관객수 (명)",
    hovermode="x unified"
)

st.plotly_chart(fig_line, use_container_width=True)

st.info(f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 후 일자별 관객수 추이 및 최고 흥행 피크(Peak) 시점을 한눈에 파악할 수 있습니다.")

st.divider()

# [구역 3] 누적 관객수 변화 추이 영역차트
st.subheader("🌊 2. 누적 관객수 변화 추이 (영역차트)")

fig_area = px.area(
    filtered_df,
    x='기준일자',
    y='누적관객수',
    title=f"[{selected_movie}] 기준일자별 누적 관객수 증가 추이",
    labels={'기준일자': '날짜', '누적관객수': '누적 관객수 (명)'}
)

fig_area.update_layout(
    xaxis_title="날짜",
    yaxis_title="누적 관객수 (명)",
    hovermode="x unified"
)

st.plotly_chart(fig_area, use_container_width=True)

st.info(f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 관객수가 시간이 지남에 따라 얼마나 가파르게 누적 가중되는지, 흥행 지속성을 한눈에 확인할 수 있습니다.")

st.divider()

# [구역 4] 조건 기반 상위 5개 영화 누적관객수 비교 다중 선그래프
st.subheader("🏆 3. 장기 흥행 TOP 5 영화 누적관객수 비교 (다중 선그래프)")

days_in_top10 = df.groupby('영화명')['기준일자'].count()
long_running_movies = days_in_top10[days_in_top10 >= 20].index

filtered_movie_rank = movie_rank[movie_rank.index.isin(long_running_movies)]
top_5_filtered_movies = filtered_movie_rank.head(5).index.tolist()

top_5_filtered_df = df[df['영화명'].isin(top_5_filtered_movies)]

fig_multi = px.line(
    top_5_filtered_df,
    x='기준일자',
    y='누적관객수',
    color='영화명',
    title="TOP10 20일 이상 유지 영화 중 누적관객수 TOP 5 추이 비교",
    labels={'기준일자': '날짜', '누적관객수': '누적 관객수 (명)', '영화명': '영화 제목'}
)

fig_multi.update_layout(
    xaxis_title="날짜",
    yaxis_title="누적 관객수 (명)",
    hovermode="x unified",
    legend_title_text="장기 흥행 TOP 5"
)

st.plotly_chart(fig_multi, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 단기 반짝 흥행을 넘어 TOP 10 순위를 20일 이상 장기 유지한 주요 흥행작들의 누적 관객수 성장 속도와 장기 흥행 파워를 비교 분석할 수 있습니다.")

st.divider()

# [구역 5] 전체 TOP10 관객수 합계 및 7일 이동평균선
st.subheader("📉 4. 전체 박스오피스 일별 관객수 및 7일 이동평균선")

daily_total = df.groupby('기준일자')['해당일관객수'].sum().reset_index()
daily_total['7일_이동평균'] = daily_total['해당일관객수'].rolling(window=7).mean()

fig_ma = go.Figure()

fig_ma.add_trace(go.Scatter(
    x=daily_total['기준일자'],
    y=daily_total['해당일관객수'],
    mode='lines',
    name='일별 관객수 합계 (일일)',
    line=dict(color='rgba(150, 150, 150, 0.4)', width=1.5)
))

fig_ma.add_trace(go.Scatter(
    x=daily_total['기준일자'],
    y=daily_total['7일_이동평균'],
    mode='lines',
    name='7일 이동평균',
    line=dict(color='#FF4B4B', width=3)
))

fig_ma.update_layout(
    title="기준일자별 TOP10 전체 관객수 합계 및 7일 이동평균 추이",
    xaxis_title="날짜",
    yaxis_title="관객수 합계 (명)",
    hovermode="x unified"
)

st.plotly_chart(fig_ma, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 요일(주말 vs 평일)에 따른 일일 관객수의 극심한 변동(노이즈)을 제거하고, 전체 영화 시장의 전반적인 흥행 흐름과 계절/시기별 시장 규모 변화 추세를 명확하게 파악할 수 있습니다.")

st.divider()

# [구역 6] 월별 전체 관객수 합계 막대그래프
st.subheader("📊 5. 월별 전체 관객수 총합계 (막대그래프)")

daily_total['연월'] = daily_total['기준일자'].dt.strftime('%Y-%m')
monthly_total = daily_total.groupby('연월')['해당일관객수'].sum().reset_index()

fig_bar = px.bar(
    monthly_total,
    x='연월',
    y='해당일관객수',
    title="월별(YYYY-MM) 극장 전체 관객수 합계",
    labels={'연월': '년-월', '해당일관객수': '월 총 관객수 (명)'},
    text_auto=',.0f',
    color_discrete_sequence=['#3366CC']
)

fig_bar.update_layout(
    xaxis_title="연-월",
    yaxis_title="총 관객수 (명)",
    xaxis=dict(type='category')
)

st.plotly_chart(fig_bar, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 연중 어떤 월(성수기 vs 비수기)에 극장가 전체 관객 동원력이 가장 높았는지 월별 시장 총규모를 직관적으로 비교할 수 있습니다.")

st.divider()

# [구역 7] 캘린더 히트맵 (X축: 주차, Y축: 요일 - 반전 반영)
st.subheader("🗓️ 6. 요일별 x 주차별 관객수 분포 (캘린더 히트맵)")

# 1) 요일 및 주차, 날짜 텍스트 가공
heatmap_df = daily_total.copy()
heatmap_df['요일_num'] = heatmap_df['기준일자'].dt.dayofweek  # 0:월, 1:화 ... 6:일

# 월요일~일요일 매핑
weekday_korean = {0: '월', 1: '화', 2: '수', 3: '목', 4: '금', 5: '토', 6: '일'}
heatmap_df['요일_한글'] = heatmap_df['요일_num'].map(weekday_korean)

# 주차 및 날짜 문자열 생성
heatmap_df['주차'] = heatmap_df['기준일자'].dt.strftime('%Y-%U주차')
heatmap_df['날짜_str'] = heatmap_df['기준일자'].dt.strftime('%Y-%m-%d')

# 2) 요일 순서 지정 (월~일)
days_order = ['월', '화', '수', '목', '금', '토', '일']

# 3) 피벗 테이블 생성 (행: 요일, 열: 주차 - X축과 Y축 교체)
pivot_audi = heatmap_df.pivot(index='요일_한글', columns='주차', values='해당일관객수').reindex(index=days_order)
pivot_date = heatmap_df.pivot(index='요일_한글', columns='주차', values='날짜_str').reindex(index=days_order)

# 4) Plotly Heatmap 생성 (x: 주차, y: 요일)
fig_heatmap = go.Figure(data=go.Heatmap(
    z=pivot_audi.values,
    x=pivot_audi.columns,  # X축: 주차
    y=days_order,          # Y축: 요일 (월~일)
    customdata=pivot_date.values,
    colorscale='Reds',     # 관객수가 많을수록 진한 색상
    hovertemplate="<b>날짜: %{customdata}</b><br>주차: %{x}<br>요일: %{y}<br>일 관객수: %{z:,.0f}명<extra></extra>"
))

fig_heatmap.update_layout(
    title="요일별 x 주차별 일일 관객수 히트맵 (날짜 Hover 기능 제공)",
    xaxis_title="주차 (연도-주차)",
    yaxis_title="요일",
    yaxis=dict(autorange="reversed") # 위쪽부터 월요일 -> 일요일 순서로 정렬
)

st.plotly_chart(fig_heatmap, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 주차 흐름(X축)에 따른 요일별(Y축) 관객수 패턴을 한눈에 파악할 수 있으며, 특정 주차의 주말 또는 공휴일에 관객 수가 진하게 몰린 지점을 쉽게 확인할 수 있습니다.")

st.divider()

# [구역 8] 상세 데이터 표
st.subheader("📊 상세 데이터 확인")

with st.expander("📄 선택한 영화 상세 데이터 표 확인하기"):
    st.dataframe(filtered_df, use_container_width=True)
