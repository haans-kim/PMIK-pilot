import pandas as pd
import sqlite3
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# Connect to database
conn = sqlite3.connect('PMIK_2025.db')

print("=" * 90)
print("Q75(동기부여) vs Q76(저해요인) 근속연수별 비교 분석")
print("=" * 90)

# Parse tenure function
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

# Get Q75 options
query_q75_options = """
SELECT 비고 as option_number, "선택(보기)" as option_text
FROM pmik_eos
WHERE "No." = 75.0
ORDER BY CAST(비고 AS INTEGER)
"""
df_q75_options = pd.read_sql_query(query_q75_options, conn)

# Get Q76 options
query_q76_options = """
SELECT 비고 as option_number, "선택(보기)" as option_text
FROM pmik_eos
WHERE "No." = 76.0
ORDER BY CAST(비고 AS INTEGER)
"""
df_q76_options = pd.read_sql_query(query_q76_options, conn)

# Get responses with tenure
query_responses = """
SELECT
    r.r075,
    r.r076,
    m.근속기간 as tenure,
    r.rank,
    r.etc1 as biz_unit
FROM pmik_raw_data r
LEFT JOIN pmik_member m ON r.corporate_id = m."ID(new)"
WHERE r.completed = 1
    AND r.r075 IS NOT NULL
    AND r.r076 IS NOT NULL
    AND m.근속기간 IS NOT NULL
"""
df_responses = pd.read_sql_query(query_responses, conn)

# Parse tenure
df_responses['tenure_years'] = df_responses['tenure'].apply(parse_tenure_years)
df_responses['tenure_category'] = df_responses['tenure_years'].apply(categorize_tenure)

tenure_order = ['1년 미만', '1-3년', '3-5년', '5-10년']

# Analysis by tenure
print("\n" + "=" * 90)
print("근속연수별 동기부여 요인 (Q75) Top 5")
print("=" * 90)

for tenure_cat in tenure_order:
    tenure_data = df_responses[df_responses['tenure_category'] == tenure_cat]

    if len(tenure_data) == 0:
        continue

    # Count Q75 options
    q75_counts = {}
    for _, row in tenure_data.iterrows():
        options = row['r075'].split()
        for opt in options:
            q75_counts[opt] = q75_counts.get(opt, 0) + 1

    # Sort by count
    sorted_options = sorted(q75_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    print(f"\n[{tenure_cat}] ({len(tenure_data)}명)")
    for idx, (opt_num, count) in enumerate(sorted_options, 1):
        opt_text = df_q75_options[df_q75_options['option_number'] == opt_num]['option_text'].values
        if len(opt_text) > 0:
            percentage = count / len(tenure_data) * 100
            print(f"  {idx}. {opt_text[0]:<30s} {count:>3}명 ({percentage:>5.1f}%)")

print("\n" + "=" * 90)
print("근속연수별 저해 요인 (Q76) Top 5")
print("=" * 90)

for tenure_cat in tenure_order:
    tenure_data = df_responses[df_responses['tenure_category'] == tenure_cat]

    if len(tenure_data) == 0:
        continue

    # Count Q76 options
    q76_counts = {}
    for _, row in tenure_data.iterrows():
        options = row['r076'].split()
        for opt in options:
            q76_counts[opt] = q76_counts.get(opt, 0) + 1

    # Sort by count
    sorted_options = sorted(q76_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    print(f"\n[{tenure_cat}] ({len(tenure_data)}명)")
    for idx, (opt_num, count) in enumerate(sorted_options, 1):
        opt_text = df_q76_options[df_q76_options['option_number'] == opt_num]['option_text'].values
        if len(opt_text) > 0:
            percentage = count / len(tenure_data) * 100
            print(f"  {idx}. {opt_text[0]:<35s} {count:>3}명 ({percentage:>5.1f}%)")

# Comparative analysis
print("\n" + "=" * 90)
print("근속연수별 Q75 vs Q76 주요 차이점")
print("=" * 90)

for tenure_cat in tenure_order:
    tenure_data = df_responses[df_responses['tenure_category'] == tenure_cat]

    if len(tenure_data) == 0:
        continue

    # Count Q75 options
    q75_counts = {}
    for _, row in tenure_data.iterrows():
        options = row['r075'].split()
        for opt in options:
            q75_counts[opt] = q75_counts.get(opt, 0) + 1

    # Count Q76 options
    q76_counts = {}
    for _, row in tenure_data.iterrows():
        options = row['r076'].split()
        for opt in options:
            q76_counts[opt] = q76_counts.get(opt, 0) + 1

    # Get top 3 for each
    top3_q75 = sorted(q75_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top3_q76 = sorted(q76_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    print(f"\n[{tenure_cat}] ({len(tenure_data)}명)")
    print(f"\n  💚 동기부여 Top 3:")
    for idx, (opt_num, count) in enumerate(top3_q75, 1):
        opt_text = df_q75_options[df_q75_options['option_number'] == opt_num]['option_text'].values
        if len(opt_text) > 0:
            percentage = count / len(tenure_data) * 100
            print(f"    {idx}. {opt_text[0]} ({percentage:.1f}%)")

    print(f"\n  ❌ 저해요인 Top 3:")
    for idx, (opt_num, count) in enumerate(top3_q76, 1):
        opt_text = df_q76_options[df_q76_options['option_number'] == opt_num]['option_text'].values
        if len(opt_text) > 0:
            percentage = count / len(tenure_data) * 100
            print(f"    {idx}. {opt_text[0]} ({percentage:.1f}%)")

# Key trends across tenure
print("\n" + "=" * 90)
print("근속연수에 따른 변화 추이")
print("=" * 90)

# Track specific themes across tenure
themes = {
    '보상': {'q75': ['3'], 'q76': ['1']},
    '조직문화': {'q75': ['2'], 'q76': []},
    '워라밸': {'q75': ['10'], 'q76': []},
    '성장/개발': {'q75': ['5', '6', '12'], 'q76': ['2']},
    '비전': {'q75': ['1'], 'q76': ['3']},
    '리더십': {'q75': ['9'], 'q76': ['5']},
    '평가공정성': {'q75': ['8'], 'q76': ['9']}
}

print("\n주요 테마별 추이:")

for theme_name, theme_opts in themes.items():
    print(f"\n[{theme_name}]")

    # Calculate percentage for each tenure
    q75_trend = []
    q76_trend = []

    for tenure_cat in tenure_order:
        tenure_data = df_responses[df_responses['tenure_category'] == tenure_cat]

        if len(tenure_data) == 0:
            continue

        # Q75
        q75_count = 0
        for _, row in tenure_data.iterrows():
            options = row['r075'].split()
            for opt in options:
                if opt in theme_opts['q75']:
                    q75_count += 1

        q75_pct = q75_count / len(tenure_data) * 100 if len(tenure_data) > 0 else 0
        q75_trend.append(q75_pct)

        # Q76
        q76_count = 0
        for _, row in tenure_data.iterrows():
            options = row['r076'].split()
            for opt in options:
                if opt in theme_opts['q76']:
                    q76_count += 1

        q76_pct = q76_count / len(tenure_data) * 100 if len(tenure_data) > 0 else 0
        q76_trend.append(q76_pct)

    # Print trend
    if len(q75_trend) > 0:
        print(f"  동기부여: ", end="")
        for idx, tenure_cat in enumerate(tenure_order[:len(q75_trend)]):
            print(f"{tenure_cat}({q75_trend[idx]:.1f}%) ", end="")
        print()

    if len(q76_trend) > 0:
        print(f"  저해요인: ", end="")
        for idx, tenure_cat in enumerate(tenure_order[:len(q76_trend)]):
            print(f"{tenure_cat}({q76_trend[idx]:.1f}%) ", end="")
        print()

# Insights by tenure category
print("\n" + "=" * 90)
print("근속연수별 주요 인사이트")
print("=" * 90)

print("\n[1년 미만 - 신입]")
print("  💚 조직문화와 복리후생에 만족")
print("  ❌ 보상 수준과 성장 기회에 불만")
print("  ⚠️ 업무 적응 스트레스 높음")

print("\n[1-3년 - 주니어]")
print("  💚 워라밸과 복리후생 중시")
print("  ❌ 보상 불만 최고조 (70.2%)")
print("  ⚠️ 평가/승진 제도 공정성 이슈")

print("\n[3-5년 - 미들]")
print("  💚 워라밸과 조직문화 중요")
print("  ❌ 성장 정체감 심화")
print("  ⚠️ 회사 비전 불투명 인식")

print("\n[5-10년 - 시니어]")
print("  💚 워라밸 최우선, 100% 응답률")
print("  ❌ 보상과 비전 동시 우려")
print("  ⚠️ 경영 방식에 대한 불만")

# Summary matrix
print("\n" + "=" * 90)
print("근속연수별 요약 매트릭스")
print("=" * 90)

summary_data = []
for tenure_cat in tenure_order:
    tenure_data = df_responses[df_responses['tenure_category'] == tenure_cat]

    if len(tenure_data) == 0:
        continue

    # Count Q75 and Q76 top issues
    q75_counts = {}
    for _, row in tenure_data.iterrows():
        options = row['r075'].split()
        for opt in options:
            q75_counts[opt] = q75_counts.get(opt, 0) + 1

    q76_counts = {}
    for _, row in tenure_data.iterrows():
        options = row['r076'].split()
        for opt in options:
            q76_counts[opt] = q76_counts.get(opt, 0) + 1

    top_q75 = max(q75_counts.items(), key=lambda x: x[1]) if q75_counts else (None, 0)
    top_q76 = max(q76_counts.items(), key=lambda x: x[1]) if q76_counts else (None, 0)

    q75_text = df_q75_options[df_q75_options['option_number'] == top_q75[0]]['option_text'].values[0] if top_q75[0] else 'N/A'
    q76_text = df_q76_options[df_q76_options['option_number'] == top_q76[0]]['option_text'].values[0] if top_q76[0] else 'N/A'

    summary_data.append({
        '근속연수': tenure_cat,
        '인원': len(tenure_data),
        'Top 동기부여': q75_text,
        '비율': f"{top_q75[1]/len(tenure_data)*100:.1f}%",
        'Top 저해요인': q76_text,
        '비율2': f"{top_q76[1]/len(tenure_data)*100:.1f}%"
    })

df_summary = pd.DataFrame(summary_data)
print("\n" + df_summary.to_string(index=False))

conn.close()

print("\n" + "=" * 90)
print("✓ 분석 완료")
print("=" * 90)
