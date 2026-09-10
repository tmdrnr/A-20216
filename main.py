import streamlit as st
import pandas as pd
import plotly.express as px

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

# [구역 4] 조건 기반 상위 5개 영화 누적관객수 비교 다중 선그래프 (수정된 그래프)
st.subheader("🏆 3. 장기 흥행 TOP 5 영화 누적관객수 비교 (다중 선그래프)")

# 1) 영화별 TOP10 등장 일수 계산 (데이터프레임 내 행 수가 곧 등장 일수)
days_in_top10 = df.groupby('영화명')['기준일자'].count()

# 2) 20일 이상 등장한 영화 목록 필터링
long_running_movies = days_in_top10[days_in_top10 >= 20].index

# 3) 조건에 맞는 영화 중 누적관객수 기준 상위 5개 선택
filtered_movie_rank = movie_rank[movie_rank.index.isin(long_running_movies)]
top_5_filtered_movies = filtered_movie_rank.head(5).index.tolist()

# 4) 상위 5개 영화의 전체 일자별 데이터 필터링
top_5_filtered_df = df[df['영화명'].isin(top_5_filtered_movies)]

# 다중 선그래프 그리기
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

# [구역 5] 상세 데이터 표
st.subheader("📊 상세 데이터 확인")

with st.expander("📄 선택한 영화 상세 데이터 표 확인하기"):
    st.dataframe(filtered_df, use_container_width=True)
