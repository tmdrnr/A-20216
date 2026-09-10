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
# 이를 통해 앱이 새로고침되거나 조작될 때마다 파일이 재다운로드되는 현상을 방지하여 속도를 향상시킵니다.
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
# [4. 선그래프 그리기 & 5. 기타 구역 배치]
# 앞으로 다른 그래프나 요약 수치를 계속 추가할 수 있도록 메인 영역을 구역(Section)으로 나누어 배치합니다.
# -----------------------------------------------------------------------------

# [구역 1] 선택된 영화의 기본 정보 및 핵심 요약
st.subheader(f"📌 선택한 영화: {selected_movie}")

# 선택한 영화의 최고 누적관객수 계산
max_acc_audi = filtered_df['누적관객수'].max()
st.metric(label="총 누적관객수", value=f"{max_acc_audi:,.0f} 명")

st.divider()

# [구역 2] 일별 관객수 변화 추이 선그래프
st.subheader("📈 일별 관객수 변화 추이 (선그래프)")

# Plotly Express를 활용한 선그래프 작성
fig = px.line(
    filtered_df,
    x='기준일자',
    y='해당일관객수',
    title=f"[{selected_movie}] 기준일자별 일일 관객수 변화",
    labels={'기준일자': '날짜', '해당일관객수': '해당일 관객수 (명)'},
    markers=True  # 그래프 선 위에 데이터 점 표시
)

# 그래프 레이아웃 정돈
fig.update_layout(
    xaxis_title="날짜",
    yaxis_title="관객수 (명)",
    hovermode="x unified"
)

# Streamlit 화면에 Plotly 그래프 출력
st.plotly_chart(fig, use_container_width=True)

# '이 그래프로 알 수 있는 것' 안내 문구 자리
st.info(f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 후 일자별 관객수 추이 및 최고 흥행 피크(Peak) 시점을 한눈에 파악할 수 있습니다.")

st.divider()

# [구역 3] 향후 그래프 추가를 위한 여분의 구역
st.subheader("📊 추가 데이터 및 분석 구역")
st.caption("앞으로 새로운 분석 그래프나 요약 표가 추가될 공간입니다.")

# 예시: 해당 영화의 상세 데이터 표 확인
with st.expander("📄 상세 데이터 표 확인하기"):
    st.dataframe(filtered_df, use_container_width=True)
