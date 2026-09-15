import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

# App 제목
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("---")


# 데이터 로드 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # genre 열 전처리: 세로막대 기호(|)로 분리된 경우 첫 번째 장르만 추출
    df["genre"] = (
        df["genre"].astype(str).apply(lambda x: x.split("|")[0].strip())
    )

    return df


df = load_data()

# -------------------------------------------------------------------
# 그래프 1: 장르별 영화 편수 (도넛 차트)
# -------------------------------------------------------------------
st.subheader("1. 장르별 영화 편수 분포")

# 장르별 영화 편수 집계
genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

# Plotly 도넛 차트 생성
fig1 = px.pie(
    genre_counts,
    values="count",
    names="genre",
    hole=0.4,
    title="장르별 영화 비율",
    hover_data=["count"],
)

fig1.update_traces(
    textinfo="percent+label",
    hovertemplate="<b>장르:</b> %{label}<br><b>편수:</b> %{value}편<br><b>비율:</b> %{percent}",
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "박스오피스 상위권 영화 중 특정 주요 장르가 차지하는 비중과 전체 장르 분포의 다변화 정도를 한눈에 파악할 수 있습니다."
)

st.markdown("---")

# -------------------------------------------------------------------
# 그래프 2: 장르 및 영화별 총 관객수 (트리맵)
# -------------------------------------------------------------------
st.subheader("2. 장르 및 개별 영화별 총 관객수 분포")

fig2 = px.treemap(
    df,
    path=[px.Constant("전체 장르"), "genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객수 (칸 크기 = 총 관객수)",
    color="genre",
    hover_data={"total_audi": ":,d"},
)

fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,}명<extra></extra>"
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "장르 내에서 특정 흥행 대작이 전체 관객수를 독식하고 있는지, 아니면 여러 영화가 고르게 관객을 모았는지 흥행 집중도를 시각적으로 파악할 수 있습니다."
)

st.markdown("---")

# -------------------------------------------------------------------
# 그래프 3: 총 관객수 분포 (히스토그램)
# -------------------------------------------------------------------
st.subheader("3. 총 관객수 분포 히스토그램")

# 히스토그램 생성
fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=25,
    title="총 관객수 구간별 영화 편수 분포",
    labels={"total_audi": "총 관객수"},
    hover_data=["movieNm"],
)

fig3.update_layout(
    xaxis_title="총 관객수 (명)",
    yaxis_title="영화 편수 (개)",
    bargap=0.1,
)

fig3.update_traces(
    hovertemplate="<b>구간:</b> %{x}명 근처<br><b>영화 수:</b> %{y}편<extra></extra>"
)

# 데이터에서 최고 관객 수 영화 탐지
max_audi_idx = df["total_audi"].idxmax()
top_movie_name = df.loc[max_audi_idx, "movieNm"]
top_movie_audi = df.loc[max_audi_idx, "total_audi"]

st.plotly_chart(fig3, use_container_width=True)

st.info(
    f"💡 **이 그래프로 알 수 있는 것:** "
    f"대부분의 영화는 관객수가 100만~300만 명대 하위 구간에 몰려 있는 롱테일 분포 형태를 보이며, "
    f"가장 관객수가 많은 최상위 영화는 **'{top_movie_name}'**({top_movie_audi:,}명)입니다."
)

st.markdown("---")
