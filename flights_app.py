import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# (Page config handled by seaborn_app.py)


# 데이터 로딩 함수 (캐싱 적용)
@st.cache_data
def load_data():
    # seaborn 내장 flights 데이터셋
    # columns: year, month, passengers
    df = sns.load_dataset('flights')
    
    # 편의를 위해 year와 month를 결합한 datetime 칼럼 생성
    # month를 숫자로 매핑 ('Jan'=1, 'Feb'=2 ...)
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    df['month_num'] = df['month'].map(month_map)
    df['date'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month_num'].astype(str) + '-01')
    return df

st.title("✈️ 항공 여객 데이터(Flights) 시계열 분석")
st.markdown("""
Seaborn에서 제공하는 1949년 ~ 1960년까지의 월별 항공 여객 데이터를 바탕으로 
**전반적인 성장 추세(Trend)**와 **매년 반복되는 계절성(Seasonality)**을 분석하는 대시보드입니다.
""")

try:
    df = load_data()
    
    # === 데이터 분석 결과 한눈에 보기 (Key Metrics) ===
    # 관련 통계치 계산
    total_passengers = df['passengers'].sum()
    max_row = df.loc[df['passengers'].idxmax()]
    
    # 1949년(첫해) vs 1960년(마지막해) 월평균 비교 (성장률 측정용)
    avg_1949 = df[df['year'] == 1949]['passengers'].mean()
    avg_1960 = df[df['year'] == 1960]['passengers'].mean()
    growth_rate = ((avg_1960 - avg_1949) / avg_1949) * 100
    
    # 가장 평균 승객이 많았던 성수기 월 계산
    # 'month' 범주형 처리 보정용: idxmax()로 가장 수치가 높은 범주 산출
    busiest_month = df.groupby('month', observed=True)['passengers'].mean().idxmax()
    
    st.info("💡 **핵심 요약 인사이트 (Key Insights)**")
    m1, m2, m3, m4 = st.columns(4)
    # Seaborn flights 데이터의 승객수는 '천 명(Thousands)' 단위입니다.
    m1.metric("총 누적 탑승객 수", f"{total_passengers:,}천 명")
    m2.metric("역대 최대 탑승 기록", f"{max_row['passengers']:,}천 명", f"{max_row['year']}년 {max_row['month']}")
    m3.metric("12년간 수요 폭발적 성장", f"{growth_rate:.1f}%", "1949년 대비 1960년")
    m4.metric("역대 최고 성수기 (평균)", f"{busiest_month}", "여름 휴가철 집중")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1. 원본 데이터 토글 보기
    with st.expander("📊 원본 데이터 프레임 보기"):
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    
    # 2. 트렌드 분석 (Plotly 선 그래프)
    st.header("📈 시간에 따른 승객 수 변화 (Trend)")
    st.markdown("1949년부터 1960년까지 꾸준히 여객 수가 증가하는 거시적 **추세(Trend)**를 확인할 수 있습니다. 그래프에 마우스를 올려 세부 수치를 확인해 보세요.")
    
    # 이동평균을 위한 슬라이더 추가
    ma_window = st.slider("📊 이동평균선(Moving Average) 계산용 개월 수 선택", 
                          min_value=1, max_value=24, value=6, 
                          help="1인 경우 이동평균선이 그려지지 않으며, 2 이상의 값을 선택하면 해당 개월 수만큼의 평균을 이은 부드러운 선이 함께 나타납니다.")
    
    df_plot = df.copy() # 원본 보존을 위해 복사
    y_cols = ['passengers']
    
    if ma_window > 1:
        ma_col = f'{ma_window}개월 이동평균'
        df_plot[ma_col] = df_plot['passengers'].rolling(window=ma_window).mean()
        y_cols.append(ma_col)
        
    fig_trend = px.line(df_plot, x='date', y=y_cols, 
                        title=f"월별 여객 수 및 추세선 ({ma_window}개월 이동평균)" if ma_window > 1 else "월별 여객 수 전체 추이",
                        labels={'date': '연-월', 'value': '여객 수 (천 명)', 'variable': '데이터 범주'},
                        markers=True)
    
    # 범례 설정 및 차트 스타일링
    fig_trend.update_layout(
        hovermode="x unified",
        legend_title_text='' # 범례 타이틀 생략
    )
    # 기존 원본 승객수는 투명도를 조금 주거나 선 굵기를 조절하면 좋지만 기본 설정도 훌륭합니다.
    st.plotly_chart(fig_trend, use_container_width=True)
    
    st.success("""
    **💡 추세 분석 결과:** 
    1949년부터 1960년까지 항공 승객 수는 연평균 약 10~15%씩 **지속적으로 성장**하고 있습니다. 
    특히 하단의 이동평균선을 조절해 보면, 단기적인 변동에도 불구하고 전체적인 우상향 곡선이 매우 뚜렷하게 유지됨을 알 수 있습니다.
    """)
    
    st.markdown("---")
    
    # 3. 계절성 분석 (월별 Boxplot 및 연도별 꺾은선)
    st.header("🌦️ 월별 변동 및 계절성 (Seasonality)")
    st.markdown("항공기 이용이 집중되는 특정 월(예: 여름 휴가철 7~8월)을 파악하여 규칙적인 **계절성 패턴**을 찾아보고, 연도별 편차를 알아봅니다.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("특정 월의 승객 분포 쏠림 (Boxplot)")
        fig_box = px.box(df, x='month', y='passengers', color='month', 
                         title="12년간 각 월별 승객수의 통계적 분포",
                         category_orders={'month': ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']})
        st.plotly_chart(fig_box, use_container_width=True)
        
    with col2:
        st.subheader("연도별 추세선 겹쳐보기")
        # 연도를 범주형으로 바꿔야 색상이 연속형이 아닌 개별 그룹으로 매핑됨
        df_plot = df.copy()
        df_plot['year_str'] = df_plot['year'].astype(str) 
        
        fig_yearly = px.line(df_plot, x='month', y='passengers', color='year_str', 
                             title="모든 연도의 각 월별 전년대비 성장 추이",
                             category_orders={'month': ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']})
        st.plotly_chart(fig_yearly, use_container_width=True)
        
    st.info("""
    **💡 계절성 패턴 발견:** 
    모든 연도에서 공통적으로 **7월(Jul)과 8월(Aug)**에 승객 수가 정점을 찍는 강력한 여름철 성수기 패턴이 발견됩니다. 
    반면, 11월(Nov)과 2월(Feb)경에는 상대적으로 수요가 감소하는 비수기 경향을 보입니다.
    """)
    
    st.markdown("---")
    
    # 4. 연도/월별 종합 히트맵 (Seaborn/Matplotlib)
    st.header("🔥 연월 종합 항공 수요 히트맵 (Heatmap)")
    st.markdown("색상이 진하고 붉어질(또는 밝아질)수록 승객 농도가 짙음을 의미합니다. 우측으로 갈수록(연도 증가), 그리고 중앙부(여름철)에서 크게 활성화되는 전경을 볼 수 있습니다.")
    
    # 히트맵을 그리기 위해 파이썬 판다스 Pivot 테이블 변환
    # index: month, columns: year, values: passengers
    flight_matrix = df.pivot(index="month", columns="year", values="passengers")
    
    # Seaborn으로 히트맵 스케치
    fig_heat, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(flight_matrix, annot=True, fmt="d", cmap="YlOrRd", ax=ax, linewidths=.5)
    plt.title("Passengers Matrix Heatmap (1949-1960)")
    plt.ylabel("Month")
    plt.xlabel("Year")
    
    # Matplotlib의 피규어를 Streamlit으로 화면에 출력
    st.pyplot(fig_heat)

    st.success("""
    **💡 종합 분석:** 
    히트맵의 우측 상단(1960년 여름)이 가장 붉은 색을 띠는 것은 **시간의 흐름(추세)**과 **여름철(계절성)**이 만나는 지점에서 항공 수요가 극대화됨을 시각적으로 증명합니다.
    """)

except Exception as e:
    st.error(f"데이터를 불러오거나 시각화하는 중 문제가 발생했습니다: {e}")
