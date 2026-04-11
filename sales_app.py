import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

@st.cache_data
def load_sales_data(file_path):
    try:
        df_employee = pd.read_excel(file_path, sheet_name='예제01-사원')
        df_customer = pd.read_excel(file_path, sheet_name='예제01-거래처')
        df_product = pd.read_excel(file_path, sheet_name='예제01-제품')
        df_sales = pd.read_excel(file_path, sheet_name='예제01-매출내역')
        
        # 데이터 결합 (거래처 추가 병합)
        merged_df = pd.merge(df_sales, df_employee[['사원코드', '사원이름']], on='사원코드', how='left')
        merged_df = pd.merge(merged_df, df_product[['제품코드', '표시가격', '제품이름']], on='제품코드', how='left')
        
        customer_cols = df_customer.columns.tolist()
        cust_name_col = '거래처이름' if '거래처이름' in customer_cols else ('거래처명' if '거래처명' in customer_cols else customer_cols[1])
        merged_df = pd.merge(merged_df, df_customer[['거래처코드', cust_name_col]], on='거래처코드', how='left')
        merged_df.rename(columns={cust_name_col: '거래처이름'}, inplace=True)
        
        # 수치 데이터 강제 변환 및 결측치 처리
        merged_df['수량'] = pd.to_numeric(merged_df['수량'], errors='coerce').fillna(0)
        
        # 날짜 데이터 변환
        if '수주일' in merged_df.columns:
            merged_df['수주일'] = pd.to_datetime(merged_df['수주일'], errors='coerce')
        
        if '단가' in merged_df.columns:
            merged_df['단가'] = pd.to_numeric(merged_df['단가'], errors='coerce').fillna(0)
            merged_df['매출액'] = merged_df['수량'] * merged_df['단가']
        else:
            if '표시가격' in merged_df.columns:
                merged_df['표시가격'] = pd.to_numeric(merged_df['표시가격'], errors='coerce').fillna(0)
                merged_df['매출액'] = merged_df['수량'] * merged_df['표시가격']
            else:
                merged_df['매출액'] = 0
            
        return merged_df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return None

def show_sales_app():
    # CSS로 스타일링 (Rich Aesthetics)
    st.markdown("""
        <style>
        .stMetric {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.05);
            border: 1px solid #e9ecef;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
        }
        .chart-container {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        h1 {
            color: #0e1117;
            font-weight: 700;
        }
        </style>
        """, unsafe_allow_html=True)

    # 사이드바 구성 (파일 업로더만 사이드바 상단에 배치)
    uploaded_file = st.sidebar.file_uploader("엑셀 파일 로드 (.xlsx)", type=["xlsx"])

    default_file = '판매내역-중복제거.xlsx'
    if uploaded_file is not None:
        df = load_sales_data(uploaded_file)
    elif os.path.exists(default_file):
        df = load_sales_data(default_file)
    else:
        st.info("데이터 파일을 업로드하거나 '판매내역-중복제거.xlsx' 파일을 확인해주세요.")
        return

    if df is not None:
        # 타이틀
        st.title("💎 매출 분석 인텔리전스 대시보드")
        
        # 필터링 섹션 (사이드바)
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 필터 설정")
        employees = sorted(df['사원이름'].dropna().unique().tolist())
        selected_employees = st.sidebar.multiselect("👤 사원 필터", options=employees, default=employees)
        
        products = sorted(df['제품이름'].dropna().unique().tolist())
        selected_products = st.sidebar.multiselect("📦 제품 필터", options=products, default=products)
        
        filtered_df = df[
            (df['사원이름'].isin(selected_employees)) & 
            (df['제품이름'].isin(selected_products))
        ]

        # KPI Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("총 매출액", f"{filtered_df['매출액'].sum():,.0f}원")
        with m2:
            st.metric("총 판매수량", f"{filtered_df['수량'].sum():,.0f}개")
        with m3:
            st.metric("거래처 수", f"{filtered_df['거래처이름'].nunique()}개")
        with m4:
            st.metric("평균 판매단가", f"{filtered_df['매출액'].mean():,.0f}원" if not filtered_df.empty else "0원")

        st.divider()

        # 분석 차트 섹션
        tab1, tab2, tab3 = st.tabs(["📊 핵심 지표 분석", "🔍 상세 데이터", "📈 상관관계 분석"])

        with tab1:
            row1_col1, row1_col2 = st.columns(2)
            
            with row1_col1:
                st.subheader("사원별 매출 기여도")
                per_emp_sales = filtered_df.groupby('사원이름')['매출액'].sum().reset_index()
                fig_emp = px.bar(per_emp_sales, x='사원이름', y='매출액', 
                                color='매출액', color_continuous_scale='Blues',
                                text_auto='.2s')
                fig_emp.update_layout(showlegend=False)
                st.plotly_chart(fig_emp, use_container_width=True)
                
            with row1_col2:
                st.subheader("제품별 매출 비중 (Donut)")
                per_prod_sales = filtered_df.groupby('제품이름')['매출액'].sum().reset_index()
                fig_prod = px.pie(per_prod_sales, values='매출액', names='제품이름', 
                                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_prod, use_container_width=True)

            row2_col1, row2_col2 = st.columns(2)
            
            with row2_col1:
                st.subheader("거래처별 매출 Top 10")
                top_customers = filtered_df.groupby('거래처이름')['매출액'].sum().sort_values(ascending=False).head(10).reset_index()
                fig_cust = px.bar(top_customers, x='매출액', y='거래처이름', 
                                 orientation='h', color='매출액', color_continuous_scale='Greens')
                fig_cust.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_cust, use_container_width=True)
                
            with row2_col2:
                st.subheader("월별 매출 트렌드")
                if '수주일' in filtered_df.columns and not filtered_df['수주일'].isnull().all():
                    monthly_sales = filtered_df.copy()
                    monthly_sales['년월'] = monthly_sales['수주일'].dt.strftime('%Y-%m')
                    monthly_trend = monthly_sales.groupby('년월')['매출액'].sum().reset_index()
                    
                    fig_trend = px.line(monthly_trend, x='년월', y='매출액', 
                                       markers=True, line_shape='spline',
                                       color_discrete_sequence=['#ff7f0e'])
                    fig_trend.update_layout(xaxis_title="수주월", yaxis_title="매출액")
                    st.plotly_chart(fig_trend, use_container_width=True)
                else:
                    st.info("데이터 내 '수주일' 정보가 없거나 형식이 올바르지 않아 트렌드를 표시할 수 없습니다.")

        with tab2:
            st.subheader("전체 매출 트랜잭션 내역")
            if not filtered_df.empty:
                st.dataframe(filtered_df.sort_values(by='매출액', ascending=False), use_container_width=True)
            else:
                st.warning("표시할 데이터가 없습니다. 필터를 확인해 주세요.")

        with tab3:
            st.subheader("수량 vs 매출액 상관 분석")
            if not filtered_df.empty:
                fig_scatter = px.scatter(filtered_df, x='수량', y='매출액', 
                                        color='제품이름', size='매출액', hover_data=['거래처이름', '사원이름'])
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.warning("분석할 데이터가 없습니다.")

if __name__ == "__main__":
    st.set_page_config(page_title="매출 분석", layout="wide")
    show_sales_app()
