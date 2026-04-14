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
        
        # 필터링 섹션 (사이드바) - Excel 슬라이서와 유사한 카드형 필터
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 필터 설정")

        employees = sorted(df['사원이름'].dropna().unique().tolist())
        products = sorted(df['제품이름'].dropna().unique().tolist())

        if "sales_selected_employees" not in st.session_state:
            st.session_state["sales_selected_employees"] = employees
        if "sales_selected_products" not in st.session_state:
            st.session_state["sales_selected_products"] = products

        with st.sidebar.container(border=True):
            st.markdown("**👤 사원 슬라이서**")
            emp_col1, emp_col2 = st.columns(2)
            select_all_employees = False
            clear_all_employees = False
            with emp_col1:
                if st.button("전체 선택", key="emp_select_all", width="stretch"):
                    select_all_employees = True
            with emp_col2:
                if st.button("전체 해제", key="emp_clear_all", width="stretch"):
                    clear_all_employees = True

            if select_all_employees:
                st.session_state["sales_selected_employees"] = employees
            elif clear_all_employees:
                st.session_state["sales_selected_employees"] = []

            st.caption("체크박스로 사원을 선택하세요.")
            current_selected = set(st.session_state["sales_selected_employees"])
            selected_employees = []
            for idx, employee in enumerate(employees):
                checkbox_key = f"sales_emp_chk_{idx}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = employee in current_selected
                if select_all_employees:
                    st.session_state[checkbox_key] = True
                elif clear_all_employees:
                    st.session_state[checkbox_key] = False

                is_checked = st.checkbox(employee, key=checkbox_key)
                if is_checked:
                    selected_employees.append(employee)

            st.session_state["sales_selected_employees"] = selected_employees

        with st.sidebar.container(border=True):
            st.markdown("**📦 제품 슬라이서**")
            prod_col1, prod_col2 = st.columns(2)
            select_all_products = False
            clear_all_products = False
            with prod_col1:
                if st.button("전체 선택", key="prod_select_all", width="stretch"):
                    select_all_products = True
            with prod_col2:
                if st.button("전체 해제", key="prod_clear_all", width="stretch"):
                    clear_all_products = True

            if select_all_products:
                st.session_state["sales_selected_products"] = products
            elif clear_all_products:
                st.session_state["sales_selected_products"] = []

            st.caption("체크박스로 제품을 선택하세요.")
            current_products = set(st.session_state["sales_selected_products"])
            selected_products = []
            for idx, product in enumerate(products):
                checkbox_key = f"sales_prod_chk_{idx}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = product in current_products
                if select_all_products:
                    st.session_state[checkbox_key] = True
                elif clear_all_products:
                    st.session_state[checkbox_key] = False

                is_checked = st.checkbox(product, key=checkbox_key)
                if is_checked:
                    selected_products.append(product)

            st.session_state["sales_selected_products"] = selected_products
        
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
                if not selected_employees:
                    st.info("선택된 사원이 없어 차트를 표시할 수 없습니다.")
                elif not selected_products:
                    st.info("선택된 제품이 없어 차트를 표시할 수 없습니다.")
                else:
                    # 선택된 사원은 거래가 없어도 0원으로 표시해 누락되지 않도록 보정
                    per_emp_sales = filtered_df.groupby('사원이름')['매출액'].sum().reset_index()
                    selected_emp_df = pd.DataFrame({'사원이름': pd.Series(selected_employees, dtype='string')})
                    per_emp_sales['사원이름'] = per_emp_sales['사원이름'].astype('string')
                    per_emp_sales = selected_emp_df.merge(per_emp_sales, on='사원이름', how='left')
                    per_emp_sales['매출액'] = per_emp_sales['매출액'].fillna(0)

                    if per_emp_sales['매출액'].sum() == 0:
                        st.caption("현재 필터 조건에서 선택된 사원의 매출은 모두 0원입니다.")

                    fig_emp = px.bar(per_emp_sales, x='사원이름', y='매출액', 
                                    color='매출액', color_continuous_scale='Blues',
                                    text_auto='.2s')
                    fig_emp.update_layout(showlegend=False)
                    st.plotly_chart(fig_emp, width="content")
                
            with row1_col2:
                st.subheader("제품별 매출 비중 (Donut)")
                if not selected_products:
                    st.info("선택된 제품이 없어 차트를 표시할 수 없습니다.")
                else:
                    per_prod_sales = filtered_df.groupby('제품이름')['매출액'].sum().reset_index()
                    fig_prod = px.pie(per_prod_sales, values='매출액', names='제품이름', 
                                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_prod, width="content")

            row2_col1, row2_col2 = st.columns(2)
            
            with row2_col1:
                st.subheader("거래처별 매출 Top 10")
                if not selected_products:
                    st.info("선택된 제품이 없어 차트를 표시할 수 없습니다.")
                else:
                    top_customers = filtered_df.groupby('거래처이름')['매출액'].sum().sort_values(ascending=False).head(10).reset_index()
                    fig_cust = px.bar(top_customers, x='매출액', y='거래처이름', 
                                     orientation='h', color='매출액', color_continuous_scale='Greens')
                    fig_cust.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_cust, width="content")
                
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
                    st.plotly_chart(fig_trend, width="content")
                else:
                    st.info("데이터 내 '수주일' 정보가 없거나 형식이 올바르지 않아 트렌드를 표시할 수 없습니다.")

        with tab2:
            st.subheader("전체 매출 트랜잭션 내역")
            if not filtered_df.empty:
                st.dataframe(filtered_df.sort_values(by='매출액', ascending=False), width="content")
            else:
                st.warning("표시할 데이터가 없습니다. 필터를 확인해 주세요.")

        with tab3:
            st.subheader("수량 vs 매출액 상관 분석")
            if not filtered_df.empty:
                fig_scatter = px.scatter(filtered_df, x='수량', y='매출액', 
                                        color='제품이름', size='매출액', hover_data=['거래처이름', '사원이름'])
                st.plotly_chart(fig_scatter, width="content")
            else:
                st.warning("분석할 데이터가 없습니다.")

if __name__ == "__main__":
    st.set_page_config(page_title="매출 분석", layout="wide")
    show_sales_app()
