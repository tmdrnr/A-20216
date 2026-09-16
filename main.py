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

# -------------------------------------------------------------------
# 그래프 4: 개봉일 스크린수와 총 관객수의 관계 (산점도)
# -------------------------------------------------------------------
st.subheader("4. 개봉일 스크린수 vs 총 관객수 산점도")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객수의 관계",
    labels={
        "first_scrn": "개봉일 스크린수 (개)",
        "total_audi": "총 관객수 (명)",
        "genre": "장르",
    },
    hover_data={"first_scrn": ":,d", "total_audi": ":,d"},
)

fig4.update_layout(
    xaxis_title="개봉일 스크린수 (개)",
    yaxis_title="총 관객수 (명)",
)

fig4.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig4, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "초기 스크린 확보 수(초기 배급력)가 최종 총 관객수 확보에 미치는 상호 영향을 파악할 수 있으며, 적은 스크린으로 시작해 입소문으로 흥행한 아웃라이어 영화를 탐지할 수 있습니다."
)

st.markdown("---")

# -------------------------------------------------------------------
# 그래프 5: 주요 장르별 총 관객수 박스플롯
# -------------------------------------------------------------------
st.subheader("5. 주요 장르별 총 관객수 분포 (영화 10편 이상 장르)")

# 영화가 10편 이상인 장르만 필터링
genre_counts_series = df["genre"].value_counts()
major_genres = genre_counts_series[genre_counts_series >= 10].index
df_major = df[df["genre"].isin(major_genres)]

fig5 = px.box(
    df_major,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",
    hover_name="movieNm",
    title="주요 장르별 총 관객수 박스플롯",
    labels={
        "genre": "장르",
        "total_audi": "총 관객수 (명)",
    },
    hover_data={"total_audi": ":,d"},
)

fig5.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객수 (명)",
    showlegend=False,
)

fig5.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>총 관객수: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig5, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "주요 장르별 관객수의 중앙값(중위수)과 흥행의 변동성을 파악할 수 있으며, 박스 상단 이상치(Outlier) 점을 통해 장르 전체 평균을 뛰어넘은 '메가 히트작'을 탐지할 수 있습니다."
)

st.markdown("---")

# -------------------------------------------------------------------
# 그래프 6: 개봉일 스크린수, 총 관객수, 첫 주 관객수 관계 (버블 차트)
# -------------------------------------------------------------------
st.subheader("6. 개봉일 스크린수 vs 총 관객수 버블 차트 (원 크기 = 첫 주 관객수)")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=50,
    title="개봉일 스크린수, 총 관객수, 첫 주 관객수 관계 (버블 차트)",
    labels={
        "first_scrn": "개봉일 스크린수 (개)",
        "total_audi": "총 관객수 (명)",
        "first_week_audi": "개봉 첫 주 관객수 (명)",
        "genre": "장르",
    },
    hover_data={
        "first_scrn": ":,d",
        "total_audi": ":,d",
        "first_week_audi": ":,d",
    },
)

fig6.update_layout(
    xaxis_title="개봉일 스크린수 (개)",
    yaxis_title="총 관객수 (명)",
)

fig6.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,}개<br>"
        "총 관객수: %{y:,}명<br>"
        "첫 주 관객수: %{marker.size:,}명<extra></extra>"
    )
)

st.plotly_chart(fig6, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "버블 크기(첫 주 관객수)를 통해 초반 흥행 몰이(오프닝 스코어)에 성공한 영화가 최종 총 관객수까지 원활하게 연결되는지, 혹은 초반 흥행 대비 뒷심이 약했거나 반대로 뒷심이 강했는지 다차원적으로 분석할 수 있습니다."
)

st.markdown("---")

# -------------------------------------------------------------------
# 그래프 7: 제작 국가 -> 장르 선버스트 차트
# -------------------------------------------------------------------
st.subheader("7. 제작 국가 및 장르별 영화 편수 (선버스트 차트)")

# 국가 -> 장르 계층 구조 선버스트 생성 (크기 = 편수)
fig7 = px.sunburst(
    df,
    path=["nation", "genre"],
    title="제작 국가 및 장르 계층별 영화 편수 분포",
)

fig7.update_traces(
    textinfo="label+value",
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<extra></extra>",
)

st.plotly_chart(fig7, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "제작 국가별(한국, 미국 등)로 주로 수입되거나 제작되는 선호 장르의 구성을 계층적으로 한눈에 비교하고 파악할 수 있습니다."
)

st.markdown("---")
