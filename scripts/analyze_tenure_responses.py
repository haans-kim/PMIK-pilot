import pandas as pd
import sqlite3
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# Connect to database
conn = sqlite3.connect('PMIK_2025.db')

print("=" * 80)
print("근속기간별 EOS 응답률 분석")
print("=" * 80)

# Get member data with response status
query = """
SELECT
    m."ID(new)" as employee_id,
    m."Name(Kor.)" as name,
    m.근속기간 as tenure,
    m."Biz Unit." as biz_unit,
    m.Department,
    m."Job Title" as job_title,
    CASE
        WHEN r.completed = 1 THEN '완료'
        WHEN r.completed = 0 THEN '미완료'
        ELSE '미응답'
    END as response_status
FROM pmik_member m
LEFT JOIN pmik_raw_data r ON m."ID(new)" = r.corporate_id
WHERE m.근속기간 IS NOT NULL
"""
df = pd.read_sql_query(query, conn)

# Parse tenure to extract years
def parse_tenure_years(tenure_str):
    """근속기간 문자열에서 년수 추출 (예: '7년 5개월' -> 7.4)"""
    if pd.isna(tenure_str):
        return None

    years = 0
    months = 0

    # '년' 추출
    year_match = re.search(r'(\d+)년', str(tenure_str))
    if year_match:
        years = int(year_match.group(1))

    # '개월' 추출
    month_match = re.search(r'(\d+)개월', str(tenure_str))
    if month_match:
        months = int(month_match.group(1))

    return years + months / 12

df['tenure_years'] = df['tenure'].apply(parse_tenure_years)

# Categorize tenure
def categorize_tenure(years):
    """근속기간을 구간으로 분류"""
    if pd.isna(years):
        return 'N/A'
    elif years < 1:
        return '1년 미만'
    elif years < 3:
        return '1-3년'
    elif years < 5:
        return '3-5년'
    elif years < 10:
        return '5-10년'
    else:
        return '10년 이상'

df['tenure_category'] = df['tenure_years'].apply(categorize_tenure)

# Overall statistics
print("\n[전체 현황]")
total = len(df)
completed = len(df[df['response_status'] == '완료'])
incomplete = len(df[df['response_status'] == '미완료'])
no_response = len(df[df['response_status'] == '미응답'])

print(f"총 대상자: {total}명")
print(f"  완료: {completed}명 ({completed/total*100:.1f}%)")
print(f"  미완료: {incomplete}명 ({incomplete/total*100:.1f}%)")
print(f"  미응답: {no_response}명 ({no_response/total*100:.1f}%)")

# Analysis by tenure category
print("\n" + "=" * 80)
print("근속기간 구간별 응답률")
print("=" * 80)

tenure_order = ['1년 미만', '1-3년', '3-5년', '5-10년', '10년 이상']

for category in tenure_order:
    category_data = df[df['tenure_category'] == category]

    if len(category_data) == 0:
        continue

    total_cat = len(category_data)
    completed_cat = len(category_data[category_data['response_status'] == '완료'])
    incomplete_cat = len(category_data[category_data['response_status'] == '미완료'])
    no_response_cat = len(category_data[category_data['response_status'] == '미응답'])

    completion_rate = (completed_cat / total_cat * 100) if total_cat > 0 else 0

    # Progress bar
    bar_length = int(completion_rate / 5)
    bar = "█" * bar_length + "░" * (20 - bar_length)

    print(f"\n[{category}]")
    print(f"  [{bar}] {completion_rate:.1f}%")
    print(f"  대상: {total_cat}명 | 완료: {completed_cat}명 | 미완료: {incomplete_cat}명 | 미응답: {no_response_cat}명")

    # Average tenure in category
    avg_tenure = category_data['tenure_years'].mean()
    print(f"  평균 근속: {avg_tenure:.1f}년")

# Detailed statistics
print("\n" + "=" * 80)
print("상세 통계")
print("=" * 80)

# Group by tenure category and response status
summary = df.groupby(['tenure_category', 'response_status']).size().reset_index(name='count')
pivot = summary.pivot(index='tenure_category', columns='response_status', values='count').fillna(0)

# Reorder rows
pivot = pivot.reindex(tenure_order, fill_value=0)

print("\n구간별 응답 상태:")
print(pivot.to_string())

# Calculate completion rate by tenure category
print("\n\n근속기간별 완료율:")
for category in tenure_order:
    category_data = df[df['tenure_category'] == category]
    if len(category_data) > 0:
        total_cat = len(category_data)
        completed_cat = len(category_data[category_data['response_status'] == '완료'])
        rate = (completed_cat / total_cat * 100)
        print(f"  {category:12s}: {rate:5.1f}% ({completed_cat}/{total_cat}명)")

# Correlation analysis
print("\n" + "=" * 80)
print("상관관계 분석")
print("=" * 80)

completed_df = df[df['response_status'] == '완료']
not_completed_df = df[df['response_status'].isin(['미완료', '미응답'])]

if len(completed_df) > 0 and len(not_completed_df) > 0:
    avg_tenure_completed = completed_df['tenure_years'].mean()
    avg_tenure_not_completed = not_completed_df['tenure_years'].mean()

    print(f"\n평균 근속기간:")
    print(f"  완료자: {avg_tenure_completed:.1f}년")
    print(f"  미완료/미응답자: {avg_tenure_not_completed:.1f}년")
    print(f"  차이: {abs(avg_tenure_completed - avg_tenure_not_completed):.1f}년")

    if avg_tenure_completed > avg_tenure_not_completed:
        print(f"\n→ 근속기간이 긴 직원의 응답률이 더 높습니다.")
    else:
        print(f"\n→ 근속기간이 짧은 직원의 응답률이 더 높습니다.")

# Show non-responders by tenure
print("\n" + "=" * 80)
print("미완료/미응답자 상세")
print("=" * 80)

not_completed_detail = df[df['response_status'].isin(['미완료', '미응답'])].sort_values('tenure_years', ascending=False)

print(f"\n총 {len(not_completed_detail)}명:")
for _, row in not_completed_detail.iterrows():
    tenure_display = row['tenure'] if pd.notna(row['tenure']) else 'N/A'
    biz_unit = row['biz_unit'] if pd.notna(row['biz_unit']) else 'N/A'
    dept = row['Department'] if pd.notna(row['Department']) else 'N/A'
    job = row['job_title'] if pd.notna(row['job_title']) else 'N/A'

    print(f"  [{row['response_status']}] {tenure_display:12s} | {biz_unit:8s} > {dept:25s} | {job}")

conn.close()

print("\n" + "=" * 80)
print("✓ 분석 완료")
print("=" * 80)
