import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# (Page config handled by seaborn_app.py)


# 데이터 로딩 함수 (캐싱 적용)
@st.cache_data
def load_iris_data():
    # seaborn 내장 iris 데이터셋 (붓꽃 데이터)
    # columns: sepal_length, sepal_width, petal_length, petal_width, species
    df = sns.load_dataset('iris')
    return df

st.title("🌸 Iris(붓꽃) 데이터셋 다차원 분석")
st.markdown("""
통계학과 데이터 사이언스의 고전인 **Iris 데이터셋**을 분석합니다. 
세 가지 종(Setosa, Versicolor, Virginica)의 꽃받침(Sepal)과 꽃잎(Petal)의 크기를 통해 데이터를 시각화합니다.
""")

try:
    df = load_iris_data()
    
    # === 데이터 분석 결과 한눈에 보기 (Key Metrics) ===
    st.info("💡 **붓꽃 데이터 요약 (Summary Stats)**")
    
    # 종별 평균 데이터 계산
    avg_stats = df.groupby('species', observed=True).mean()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("전체 데이터 개수", f"{len(df)}개")
    m2.metric("분석 품종 수", f"{df['species'].nunique()}종")
    m3.metric("가장 큰 꽃잎 평균", f"{avg_stats['petal_length'].max():.2f}cm", f"{avg_stats['petal_length'].idxmax()}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 1. 데이터 테이블
    with st.expander("📊 원본 데이터 및 종별 통계 보기"):
        st.write("### 원본 데이터 (상위 10개)")
        st.dataframe(df.head(10), use_container_width=True)
        st.write("### 종별 평균 측정치 (cm)")
        st.table(avg_stats)

    st.markdown("---")

    # 2. 분포 분석 (Boxplot)
    st.header("📏 부위별 크기 분포 분석")
    st.markdown("꽃의 부위별(꽃받침, 꽃잎) 크기가 품종에 따라 어떻게 다른지 확인합니다.")
    
    target_feature = st.selectbox("분석할 특징 선택", 
                                  ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
                                  format_func=lambda x: x.replace('_', ' ').title())
    
    fig_box = px.box(df, x='species', y=target_feature, color='species',
                     points="all", title=f"품종별 {target_feature} 분포",
                     labels={'species': '품종', target_feature: '크기 (cm)'})
    st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    # 3. 상관관계 분석 (Scatter Plot)
    st.header("🎯 특성 간 상관관계 (Scatter Plot)")
    st.markdown("두 가지 특성을 선택하여 품종들이 어떻게 군집(Cluster)을 형성하는지 확인해 보세요.")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        x_axis = st.selectbox("X축 선택", df.columns[:-1], index=2) # 기본 petal_length
    with col_v2:
        y_axis = st.selectbox("Y축 선택", df.columns[:-1], index=3) # 기본 petal_width
        
    fig_scatter = px.scatter(df, x=x_axis, y=y_axis, color='species',
                             symbol='species', size='sepal_length',
                             hover_data=['sepal_width'],
                             title=f"{x_axis} vs {y_axis} 상관관계",
                             labels={x_axis: x_axis.replace('_', ' ').title(), 
                                     y_axis: y_axis.replace('_', ' ').title()})
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # 4. 전체 관계 시각화 (Seaborn Pairplot)
    st.header("🧬 전체 특성 관계도 (Pair Plot)")
    st.markdown("모든 변수 간의 관계를 한눈에 보여줍니다. Seaborn의 강력한 시각화 기능을 활용한 정적 차트입니다.")
    
    # Seaborn Pairplot은 계산량이 좀 있으므로 spinner 적용
    with st.spinner("복합 차트를 생성 중입니다..."):
        fig_pair = sns.pairplot(df, hue="species", palette="husl", markers=["o", "s", "D"])
        st.pyplot(fig_pair.fig)

except Exception as e:
    st.error(f"데이터 분석 중 오류가 발생했습니다: {e}")
