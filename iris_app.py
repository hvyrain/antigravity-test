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
        st.dataframe(df.head(10), width="content")
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
    st.plotly_chart(fig_box, width="stretch")

    st.info("""
    **💡 분포 인사이트:** 
    꽃잎의 길이(`petal_length`)와 너비(`petal_width`)를 보면 **setosa** 종이 다른 두 종에 비해 압도적으로 작고 균일한 크기를 분포하고 있음을 알 수 있습니다. 
    반면 **virginica**는 전반적으로 가장 큰 크기를 보이며 개체 간 변동성(박스의 길이)도 가장 큽니다.
    """)

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
    st.plotly_chart(fig_scatter, width="stretch")

    st.success("""
    **💡 상관관계 인사이트:** 
    꽃잎의 길이와 너비 사이에는 매우 강력한 **양(+)의 상관관계**가 관찰됩니다. 
    특히 **setosa** 종은 왼쪽 하단에 완전히 독립된 군집(Cluster)을 형성하고 있어, 꽃잎 크기만으로도 다른 종과 쉽게 구분이 가능함을 시각적으로 확인할 수 있습니다.
    """)

    st.markdown("---")

    # 4. 전체 관계 시각화 (Seaborn Pairplot)
    st.header("🧬 전체 특성 관계도 (Pair Plot)")
    st.markdown("모든 변수 간의 관계를 한눈에 보여줍니다. 생성에 시간이 걸리므로 한 번 생성된 결과는 **캐시(Cache)**되어 다음에 바로 나타납니다.")
    
    # Pairplot 생성 함수 캐싱 (st.cache_resource 사용)
    @st.cache_resource
    def get_pairplot(_data):
        # 폰트 및 스타일 설정
        sns.set_theme(style="ticks")
        pair_grid = sns.pairplot(_data, hue="species", palette="husl", markers=["o", "s", "D"])
        return pair_grid.fig

    # Seaborn Pairplot은 계산량이 좀 있으므로 spinner 적용
    with st.spinner("복합 차트를 생성 중입니다. 잠시만 기다려 주세요..."):
        fig_pair = get_pairplot(df)
        st.pyplot(fig_pair)

    st.info("""
    **💡 종합 분석 (Linearly Separable):** 
    모든 특성을 종합해 볼 때, **setosa**는 어떤 조합에서도 다른 종들과 명확히 분리되는 '선형 분리 가능' 데이터를 보여줍니다. 
    반면 **versicolor**와 **virginica**는 일부 특성 영역에서 겹치는 부분이 존재하여, 머신러닝 분류 알고리즘에서 이 두 종을 구분하는 것이 핵심 과제가 됩니다.
    """)

except Exception as e:
    st.error(f"데이터 분석 중 오류가 발생했습니다: {e}")
