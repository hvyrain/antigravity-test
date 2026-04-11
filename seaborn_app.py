import streamlit as st

# 전체 앱의 전역 설정 (모든 하위 페이지에 적용됨)
st.set_page_config(
    page_title="📊 Seaborn 통합 분석 플랫폼",
    page_icon="📈",
    layout="wide"
)

# 홈 페이지 정의 함수
def home_page():
    st.title("🏠 Seaborn 데이터 분석 통합 대시보드")
    st.info("💡 **상단 메뉴에서 분석할 데이터를 선택하세요.**")
    st.markdown("""
    이 플랫폼은 주요 데이터셋들을 분석하는 개별 앱들을 하나로 통합한 공간입니다.
    
    *   **✈️ Flights Analysis**: 항공 여객 데이터의 트랜드와 계절성 분석.
    *   **🌸 Iris Analysis**: 붓꽃 품종별 상관관계 및 분포 분석.
    *   **🌐 GDP Analysis**: 전 세계 1인당 GDP 성장 및 대륙별 격차 분석.
    
    원하시는 분석 도구를 상단 네비게이션 바에서 선택하여 시작해 보세요!
    """)
    
    # 대표 카드 시각화
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("✈️ 항공 여객")
        st.write("시계열 데이터의 추세와 이동평균 분석")
        if st.button("✈️ Flights 이동", use_container_width=True):
            st.switch_page("flights_app.py")
    with c2:
        st.subheader("🌸 붓꽃 데이터")
        st.write("품종별 특성 상관관계 시각화")
        if st.button("🌸 Iris 이동", use_container_width=True):
            st.switch_page("iris_app.py")
    with c3:
        st.subheader("🌐 GDP 데이터")
        st.write("전 세계 경제 성장 추이 분석")
        if st.button("🌐 GDP 이동", use_container_width=True):
            st.switch_page("gdp_app.py")

# 페이지들을 구성 (st.Page 객체 활용)
pages = [
    st.Page(home_page, title="Home", icon="🏠", default=True),
    st.Page("flights_app.py", title="Flights Analysis", icon="✈️"),
    st.Page("iris_app.py", title="Iris Analysis", icon="🌸"),
    st.Page("gdp_app.py", title="GDP Analysis", icon="🌐"),
]

# 네비게이션 생성 (상단 메뉴 배치)
pg = st.navigation(pages, position="top")

# 선택된 페이지 실행
pg.run()
