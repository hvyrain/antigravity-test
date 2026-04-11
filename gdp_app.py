import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# (Page config handled by seaborn_app.py)

@st.cache_data
def get_clean_gdp_data():
    # 데이터 로드
    file_path = "gdp2015-2024.csv"
    try:
        df = pd.read_csv(file_path)
        df.columns = ["Year", "Name", "GDP"]
        
        # 1. 대륙 정보 추출 및 할당
        # GDP가 NaN인 행은 대륙 이름임
        df['Continent'] = np.where(df['GDP'].isna(), df['Name'], np.nan)
        
        # 각 연도별로 대륙명이 나타나므로 정방향 채우기(ffill) 적용
        df['Continent'] = df['Continent'].ffill()
        
        # 2. 대륙 행 제거 (GDP가 수치인 실제 국가 데이터만 남김)
        df_clean = df.dropna(subset=['GDP']).copy()
        
        # 3. 데이터 타입 정제
        df_clean['Year'] = df_clean['Year'].astype(int)
        df_clean['GDP'] = df_clean['GDP'].astype(float)
        
        # 4. 컬럼명 최종 정리
        df_clean = df_clean.rename(columns={'Name': 'Country'})
        
        return df_clean
    except Exception as e:
        st.error(f"데이터 정제 중 오류 발생: {e}")
        return pd.DataFrame()

st.title("🌐 세계 1인당 GDP 데이터 분석 (2015-2024)")
st.markdown("""
이 앱은 실시간으로 데이터를 정제하여 전 세계 국가들의 경제 성장과 대륙별 격차를 분석합니다. 
데이터 소스: `gdp2015-2024.csv`
""")

df = get_clean_gdp_data()

if not df.empty:
    # === 상단 연도 선택 슬라이더 ===
    st.markdown("---")
    selected_year = st.slider("📅 분석할 연도를 선택하세요", 
                               min_value=int(df['Year'].min()), 
                               max_value=int(df['Year'].max()), 
                               value=int(df['Year'].max()),
                               help="이 슬라이더를 통해 특정 연도의 국가 순위와 대륙별 분포를 확인할 수 있습니다.")
    st.markdown("---")

    # === Key Insights (Metrics) 업데이트 ===
    st.info(f"💡 **{selected_year}년 글로벌 주요 경제 지표 요약**")
    
    df_selected = df[df['Year'] == selected_year].sort_values('GDP', ascending=False).reset_index(drop=True)
    avg_gdp_selected = df_selected['GDP'].mean()
    top_country = df_selected.iloc[0]
    
    # 전년도 대비 평군 성장률 계산
    delta_avg = None
    if selected_year > df['Year'].min():
        avg_gdp_prev = df[df['Year'] == selected_year - 1]['GDP'].mean()
        delta_avg = f"{((avg_gdp_selected - avg_gdp_prev) / avg_gdp_prev) * 100:.2f}%"
    
    # 한국 데이터 및 순위 추출
    korea_row = df_selected[df_selected['Country'] == '대한민국']
    if not korea_row.empty:
        korea_val = korea_row['GDP'].values[0]
        korea_rank = korea_row.index[0] + 1
    else:
        korea_val = 0
        korea_rank = "-"
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🌍 전 세계 평균 GDP", f"${avg_gdp_selected:,.0f}", delta=delta_avg)
    m2.metric(f"🥇 {selected_year}년 1위", top_country['Country'], f"${top_country['GDP']:,.0f}")
    m3.metric("🇰🇷 대한민국 GDP", f"${korea_val:,.0f}")
    m4.metric("📊 한국의 경제 순위", f"{korea_rank}위", help="분석 대상 국가들 중 1인당 GDP 순위입니다.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 1. 전 세계 성장 추이 (Line Chart)
    st.header("📈 1. 전 세계 경제 성장 트렌드")
    df_trend = df.groupby('Year')['GDP'].mean().reset_index()
    fig_trend = px.line(df_trend, x='Year', y='GDP', title="연도별 전 세계 평균 1인당 GDP 변화",
                        labels={'GDP': '평균 GDP ($)'}, markers=True)
    
    # 선택 연도에 수직선 추가
    fig_trend.add_vline(x=selected_year, line_dash="dash", line_color="red", 
                        annotation_text=f"{selected_year}년 선택됨", annotation_position="top left")
    
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown(f"**인사이트:** {df['Year'].min()}년부터 {df['Year'].max()}년까지의 전체 흐름 속에서 현재 **{selected_year}년**의 위치를 확인할 수 있습니다.")

    st.markdown("---")

    # 2. 국가 간 비교 (Multi-select)
    st.header("🤝 2. 주요 국가 간 GDP 비교")
    selected_countries = st.multiselect("비교할 국가를 선택하세요", 
                                        options=df['Country'].unique(),
                                        default=['대한민국', '미국', '일본', '중국'])
    
    if selected_countries:
        df_comp = df[df['Country'].isin(selected_countries)]
        fig_comp = px.line(df_comp, x='Year', y='GDP', color='Country',
                           title="선택 국가들의 1인당 GDP 추이",
                           labels={'GDP': 'GDP ($)'}, markers=True)
        # 선택 연도 수직선 추가
        fig_comp.add_vline(x=selected_year, line_dash="dash", line_color="gray")
        st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")

    # 3. 부자 나라 Top 10 (Horizontal Bar) - 선택 연도 기준
    st.header(f"🏆 3. {selected_year}년 세계 부자 나라 Top 10")
    top_10 = df_selected.nlargest(10, 'GDP')
    fig_top10 = px.bar(top_10, x='GDP', y='Country', orientation='h', color='GDP',
                       title=f"{selected_year}년 1인당 GDP 상위 10개국",
                       labels={'GDP': 'GDP ($)'}, color_continuous_scale='Viridis')
    fig_top10.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top10, use_container_width=True)

    st.markdown("---")

    # 4. 성장률 분석 (Bar Chart) - 2015 vs 선택 연도
    if selected_year > 2015:
        st.header(f"🚀 4. 2015년 대비 {selected_year}년까지 가장 많이 성장한 나라는?")
        
        df_2015 = df[df['Year'] == 2015][['Country', 'GDP']].rename(columns={'GDP': 'GDP_2015'})
        df_sel_small = df_selected[['Country', 'GDP']].rename(columns={'GDP': 'GDP_current'})
        df_growth = pd.merge(df_2015, df_sel_small, on='Country')
        df_growth['Growth_Rate'] = ((df_growth['GDP_current'] - df_growth['GDP_2015']) / df_growth['GDP_2015']) * 100
        
        top_growth = df_growth.nlargest(10, 'Growth_Rate')
        fig_growth = px.bar(top_growth, x='Country', y='Growth_Rate', color='Growth_Rate',
                            title=f"2015-{selected_year} 성장률(%) 상위 10개국",
                            labels={'Growth_Rate': '성장률 (%)'})
        st.plotly_chart(fig_growth, use_container_width=True)
    else:
        st.header("🚀 4. 지난 10년간 성장 분석")
        st.info("2015년 이후의 연도를 선택하시면 성장률 분석 차트가 나타납니다.")

    st.markdown("---")

    # 5. 대륙별 경제 분포 (Boxplot) - 선택 연도 기준
    st.header(f"🗺️ 5. {selected_year}년 대륙별 경제 분포 및 격차")
    fig_box = px.box(df_selected, x='Continent', y='GDP', color='Continent',
                     points="all", hover_data=['Country'],
                     title=f"{selected_year}년 대륙별 GDP 분포 (박스플롯)",
                     labels={'GDP': 'GDP ($)'})
    st.plotly_chart(fig_box, use_container_width=True)
    st.markdown(f"""
    **분석 결과 ({selected_year}년 기준):** 
    - 유럽과 북아메리카의 중윗값이 상당히 높으며, 동시에 내륙 국가 간 격차가 큰 것을 확인할 수 있습니다. 
    - 아시아는 매우 넓은 분포를 보이며 신흥국과 선진국이 혼재되어 있습니다.
    """)

else:
    st.warning("데이터를 불러올 수 없습니다. 파일 경로와 형식을 확인해 주세요.")
