import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import zoneinfo

# -----------------------------------------------------------------------------
# [페이지 기본 설정]
# 앱의 타이틀과 레이아웃을 넓게(wide) 설정합니다.
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------------------------------------------------------
# [데이터 불러오기 함수]
# API를 매번 호출하지 않고, 같은 날짜 요청은 1시간(3600초) 동안 저장(캐싱)해 둡니다.
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_daily_boxoffice(target_date, api_key):
    """
    KOBIS API를 통해 특정 날짜의 일별 박스오피스 데이터를 가져오는 함수
    """
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": target_date
    }
    
    try:
        # API 요청 보내기 (타임아웃 10초 설정)
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() # HTTP 오류가 발생하면 예외를 일으킵니다.
        return response.json()
    except requests.exceptions.RequestException as e:
        # 네트워크 문제나 HTTP 에러 발생 시 처리
        return {"error": f"네트워크 통신 오류가 발생했습니다: {e}"}

# -----------------------------------------------------------------------------
# [날짜 계산]
# 배포 서버의 시계가 해외 기준일 수 있으므로, 명확하게 한국 시간(Asia/Seoul)으로 계산합니다.
# -----------------------------------------------------------------------------
seoul_tz = zoneinfo.ZoneInfo("Asia/Seoul")
now_seoul = datetime.now(seoul_tz)
yesterday = now_seoul - timedelta(days=1)
target_dt_str = yesterday.strftime("%Y%m%d") # YYYYMMDD 형식으로 변환
formatted_date_display = yesterday.strftime("%Y년 %m월 %d일")

# -----------------------------------------------------------------------------
# [메인 화면 레이아웃]
# -----------------------------------------------------------------------------
st.title("🎬 어제의 일별 박스오피스")
st.caption(f"기준일자: {formatted_date_display} (한국 시간 기준)")

# Streamlit Secrets(비밀 금고)에서 KOBIS_KEY 불러오기
if "KOBIS_KEY" not in st.secrets:
    st.error("🔑 API 키를 찾을 수 없습니다.")
    st.info("""
    **확인해 주세요:**
    1. Streamlit Cloud 설정의 **Secrets** 항목에 `KOBIS_KEY = "발급받은키"` 형태로 등록되어 있는지 확인하세요.
    2. 로컬 실행 시에는 `.streamlit/secrets.toml` 파일 안에 키가 설정되어 있어야 합니다.
    """)
    st.stop()

api_key = st.secrets["KOBIS_KEY"]

# API 데이터 가져오기
with st.spinner("박스오피스 데이터를 불러오는 중입니다..."):
    raw_data = fetch_daily_boxoffice(target_dt_str, api_key)

# -----------------------------------------------------------------------------
# [예외 및 에러 처리]
# 1) 네트워크 통신 실패
# 2) API 실패 메시지(faultInfo) 반환
# 3) 데이터가 비어 있는 경우
# -----------------------------------------------------------------------------
if "error" in raw_data:
    st.error("❌ 데이터를 가져오는 데 실패했습니다.")
    st.warning(raw_data["error"])
    st.stop()

boxoffice_result = raw_data.get("boxOfficeResult", {})

# API 키가 잘못되었을 때 나타나는 faultInfo 검사
if "faultInfo" in raw_data:
    fault = raw_data["faultInfo"]
    st.error("❌ KOBIS API 오류가 발생했습니다.")
    st.warning(f"오류 메시지: {fault.get('message', '알 수 없는 오류')}")
    st.info("""
    **확인해 주세요:**
    - Secrets에 입력한 `KOBIS_KEY` 값이 정확한지 확인해 주세요.
    - 영화진흥위원회(KOBIS) 개발자 센터에서 키가 정상적으로 발급/활성화되었는지 확인하세요.
    """)
    st.stop()

daily_list = boxoffice_result.get("dailyBoxOfficeList", [])

# 영화 목록 데이터가 비어 있는 경우
if not daily_list:
    st.warning("⚠️ 어제 날짜의 박스오피스 데이터가 비어 있습니다.")
    st.info("""
    **확인해 주세요:**
    - KOBIS API의 데이터 집계 시간이 연장되었거나 서버 점검 중일 수 있습니다.
    - 잠시 후 다시 시도해 보세요.
    """)
    st.stop()

# -----------------------------------------------------------------------------
# [데이터 가공 (전처리)]
# 문자열 형태의 숫자 데이터를 정수(int) 타입으로 변환합니다.
# -----------------------------------------------------------------------------
df = pd.DataFrame(daily_list)

# 숫자로 변환할 컬럼 지정
numeric_cols = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# 순위 기준으로 오름차순 정렬
df = df.sort_values(by="rank", ascending=True)

# -----------------------------------------------------------------------------
# [1위 영화 지표 카드]
# 1위 영화의 정보와 핵심 지표 3개를 돋보이게 표시합니다.
# -----------------------------------------------------------------------------
top_1 = df.iloc[0]

st.subheader(f"🥇 1위 영화: {top_1['movieNm']}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="어제 관객수",
        value=f"{top_1['audiCnt']:,} 명"
    )
with col2:
    st.metric(
        label="누적 관객수",
        value=f"{top_1['audiAcc']:,} 명"
    )
with col3:
    st.metric(
        label="상영 스크린수",
        value=f"{top_1['scrnCnt']:,} 개"
    )

st.divider()

# -----------------------------------------------------------------------------
# [상위 5편 관객수 막대그래프]
# -----------------------------------------------------------------------------
st.subheader("📊 관객수 상위 5개 영화")

# 상위 5개 데이터 추출
top_5_df = df.head(5)

# Streamlit 내장 막대그래프 활용 (x: 영화명, y: 관객수)
st.bar_chart(
    data=top_5_df,
    x="movieNm",
    y="audiCnt",
    color="#FF4B4B"
)

st.divider()

# -----------------------------------------------------------------------------
# [전체 순위 표 출력]
# 사용자가 보기 쉽도록 컬럼명을 한글로 변경하여 출력합니다.
# -----------------------------------------------------------------------------
st.subheader("📋 전체 박스오피스 순위")

# 화면에 보여줄 컬럼 선택 및 이름 변경
display_df = df[["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
display_df.columns = ["순위", "영화명", "개봉일", "관객수", "누적관객", "스크린수"]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)
