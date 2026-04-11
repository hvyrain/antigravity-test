import pandas as pd
import matplotlib.pyplot as plt
#import koreanize_matplotlib
# 한글 폰트 설정 (Windows: 맑은 고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'
# 마이너스 기호(-)가 깨지는 현상 방지
plt.rcParams['axes.unicode_minus'] = False

# 1. 데이터 로드 (실제 파일 경로로 수정 필요)
# 파일 내의 각 시트를 데이터프레임으로 읽어옵니다.
file_path = '판매내역-중복제거.xlsx'

try:
    df_employee = pd.read_excel(file_path, sheet_name='예제01-사원')  # 사원 마스터
    df_customer = pd.read_excel(file_path, sheet_name='예제01-거래처') # 거래처 마스터
    df_product = pd.read_excel(file_path, sheet_name='예제01-제품')   # 제품 마스터
    df_sales = pd.read_excel(file_path, sheet_name='예제01-매출내역')     # 판매 트랜잭션 (이 데이터가 핵심입니다)

    # 2. 데이터 전처리 및 결합 (Merging)
    # 판매 내역을 중심으로 사원 정보와 제품 정보를 결합합니다.
    # '사원코드'를 기준으로 사원 이름을 가져오고, '제품코드'를 기준으로 단가를 가져옵니다.
    
    # 판매 내역 + 사원 정보 결합
    merged_df = pd.merge(df_sales, df_employee[['사원코드', '사원이름']], on='사원코드', how='left')
    
    # 판매 내역 + 제품 정보 결합
    merged_df = pd.merge(merged_df, df_product[['제품코드', '표시가격']], on='제품코드', how='left')

    # 3. 매출액 계산
    # 매출액 = 수량 * 단가
    merged_df['매출액'] = merged_df['수량'] * merged_df['단가']

    # 4. 사원별 총 매출액 계산 (Aggregation)
    # 사원이름을 기준으로 그룹화하여 매출액의 합계를 구합니다.
    sales_by_employee = merged_df.groupby('사원이름')['매출액'].sum().reset_index()

    # 5. 결과 출력
    print("=== 사원별 총 매출액 결과 ===")
    print(merged_df.sort_values(by='매출액', ascending=False))
    sales_by_employee.sort_values(by='매출액', ascending=False).set_index('사원이름').plot(kind='bar')
    plt.show()

except FileNotFoundError:
    print("파일을 찾을 수 없습니다. 경로를 확인해주세요.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")
