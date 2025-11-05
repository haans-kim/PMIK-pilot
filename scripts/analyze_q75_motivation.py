import pandas as pd
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Connect to database
conn = sqlite3.connect('PMIK_2025.db')

print("=" * 80)
print("Q75 문항 분석: 업무 몰입 동기부여 요인")
print("=" * 80)

# Get Q75 question text
query_question = """
SELECT DISTINCT 문항
FROM pmik_eos
WHERE "No." = 75.0
LIMIT 1
"""
question_text = pd.read_sql_query(query_question, conn).iloc[0]['문항']

print(f"\n[문항]")
print(f"{question_text}")

# Get all Q75 options
query_options = """
SELECT 비고 as option_number, "선택(보기)" as option_text
FROM pmik_eos
WHERE "No." = 75.0
ORDER BY CAST(비고 AS INTEGER)
"""
df_options = pd.read_sql_query(query_options, conn)

print(f"\n[선택지] (12개 중 3개 선택)")
for _, row in df_options.iterrows():
    print(f"  {row['option_number']:2s}. {row['option_text']}")

# Get response statistics
print("\n" + "=" * 80)
print("전체 응답 현황")
print("=" * 80)

query_response_count = """
SELECT
    COUNT(*) as total_responses,
    COUNT(CASE WHEN r075 IS NOT NULL AND r075 != '' THEN 1 END) as valid_responses,
    COUNT(CASE WHEN r075 IS NULL OR r075 = '' THEN 1 END) as no_responses
FROM pmik_raw_data
WHERE completed = 1
"""
df_response_count = pd.read_sql_query(query_response_count, conn)

total_resp = df_response_count.iloc[0]['total_responses']
valid_resp = df_response_count.iloc[0]['valid_responses']
no_resp = df_response_count.iloc[0]['no_responses']

print(f"\n완료된 설문: {total_resp}명")
print(f"  Q75 응답: {valid_resp}명 ({valid_resp/total_resp*100:.1f}%)")
print(f"  미응답: {no_resp}명 ({no_resp/total_resp*100:.1f}%)")

# Analyze selection frequency
print("\n" + "=" * 80)
print("선택지별 빈도 분석")
print("=" * 80)

query_frequency = """
SELECT
    e.비고 as option_number,
    e."선택(보기)" as option_text,
    COUNT(*) as selection_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM pmik_raw_data WHERE completed = 1 AND r075 IS NOT NULL), 1) as percentage
FROM pmik_raw_data r, pmik_eos e
WHERE r.completed = 1
    AND r.r075 IS NOT NULL
    AND e."No." = 75.0
    AND (',' || REPLACE(r.r075, ' ', ',') || ',') LIKE ('%,' || e.비고 || ',%')
GROUP BY e.비고, e."선택(보기)"
ORDER BY selection_count DESC
"""
df_frequency = pd.read_sql_query(query_frequency, conn)

print(f"\n{'순위':<6} {'번호':<6} {'선택지':<30} {'선택 수':<10} {'비율':<10} {'그래프'}")
print("-" * 80)

for idx, row in df_frequency.iterrows():
    rank = idx + 1
    option_num = row['option_number']
    option_text = row['option_text']
    count = int(row['selection_count'])
    percentage = row['percentage']

    # Create bar chart
    bar_length = int(percentage / 5)
    bar = "█" * bar_length

    print(f"{rank:<6} {option_num:<6} {option_text:<30} {count:<10} {percentage:>5.1f}%   {bar}")

# Top 5 and Bottom 5
print("\n" + "=" * 80)
print("Top 5 동기부여 요인")
print("=" * 80)

top5 = df_frequency.head(5)
for idx, row in top5.iterrows():
    rank = idx + 1
    print(f"{rank}. {row['option_text']} - {int(row['selection_count'])}명 ({row['percentage']:.1f}%)")

print("\n" + "=" * 80)
print("Bottom 5 동기부여 요인")
print("=" * 80)

bottom5 = df_frequency.tail(5).sort_values('selection_count')
for idx, row in bottom5.iterrows():
    rank = len(df_frequency) - list(bottom5.index).index(idx)
    print(f"{rank}. {row['option_text']} - {int(row['selection_count'])}명 ({row['percentage']:.1f}%)")

# Analysis by department
print("\n" + "=" * 80)
print("사업부별 Top 3 동기부여 요인")
print("=" * 80)

for biz_unit in ['A&R', 'O&F', 'Sales']:
    query_biz = f"""
    SELECT
        e.비고 as option_number,
        e."선택(보기)" as option_text,
        COUNT(*) as selection_count
    FROM pmik_raw_data r, pmik_eos e
    WHERE r.completed = 1
        AND r.r075 IS NOT NULL
        AND r.etc1 = '{biz_unit}'
        AND e."No." = 75.0
        AND (',' || REPLACE(r.r075, ' ', ',') || ',') LIKE ('%,' || e.비고 || ',%')
    GROUP BY e.비고, e."선택(보기)"
    ORDER BY selection_count DESC
    LIMIT 3
    """
    df_biz = pd.read_sql_query(query_biz, conn)

    print(f"\n[{biz_unit}]")
    for idx, row in df_biz.iterrows():
        print(f"  {idx+1}. {row['option_text']} ({int(row['selection_count'])}명)")

# Analysis by rank
print("\n" + "=" * 80)
print("직급별 Top 3 동기부여 요인")
print("=" * 80)

for rank in ['E1', 'E2', 'S2', 'S3', 'B1', 'B2', 'B3']:
    query_rank = f"""
    SELECT
        e.비고 as option_number,
        e."선택(보기)" as option_text,
        COUNT(*) as selection_count
    FROM pmik_raw_data r, pmik_eos e
    WHERE r.completed = 1
        AND r.r075 IS NOT NULL
        AND r.rank = '{rank}'
        AND e."No." = 75.0
        AND (',' || REPLACE(r.r075, ' ', ',') || ',') LIKE ('%,' || e.비고 || ',%')
    GROUP BY e.비고, e."선택(보기)"
    ORDER BY selection_count DESC
    LIMIT 3
    """
    df_rank = pd.read_sql_query(query_rank, conn)

    if len(df_rank) > 0:
        print(f"\n[{rank}]")
        for idx, row in df_rank.iterrows():
            print(f"  {idx+1}. {row['option_text']} ({int(row['selection_count'])}명)")

# Combination analysis (most common 3-option sets)
print("\n" + "=" * 80)
print("가장 많이 선택된 조합 (Top 10)")
print("=" * 80)

query_combinations = """
SELECT
    r075 as combination,
    COUNT(*) as count
FROM pmik_raw_data
WHERE completed = 1 AND r075 IS NOT NULL
GROUP BY r075
ORDER BY count DESC
LIMIT 10
"""
df_combinations = pd.read_sql_query(query_combinations, conn)

print(f"\n{'순위':<6} {'선택 조합':<20} {'응답 수':<10} {'선택지 내용'}")
print("-" * 80)

for idx, row in df_combinations.iterrows():
    rank = idx + 1
    combination = row['combination']
    count = int(row['count'])

    # Get option texts
    option_numbers = combination.split()
    option_texts = []
    for num in option_numbers:
        text = df_options[df_options['option_number'] == num]['option_text'].values
        if len(text) > 0:
            option_texts.append(text[0])

    options_display = ", ".join(option_texts)

    print(f"{rank:<6} {combination:<20} {count:<10} {options_display}")

# Insights
print("\n" + "=" * 80)
print("주요 인사이트")
print("=" * 80)

top1 = df_frequency.iloc[0]
top2 = df_frequency.iloc[1]
top3 = df_frequency.iloc[2]
bottom1 = df_frequency.iloc[-1]

print(f"\n✓ 가장 중요한 동기부여 요인:")
print(f"  1위: {top1['option_text']} ({top1['percentage']:.1f}%)")
print(f"  2위: {top2['option_text']} ({top2['percentage']:.1f}%)")
print(f"  3위: {top3['option_text']} ({top3['percentage']:.1f}%)")

print(f"\n✗ 가장 덜 중요한 동기부여 요인:")
print(f"  {bottom1['option_text']} ({bottom1['percentage']:.1f}%)")

# Calculate average selections per person
total_selections = df_frequency['selection_count'].sum()
avg_selections = total_selections / valid_resp

print(f"\n📊 응답 통계:")
print(f"  총 선택 수: {int(total_selections)}개")
print(f"  응답자당 평균 선택: {avg_selections:.1f}개")
print(f"  (설문 요구: 3개 선택)")

if abs(avg_selections - 3.0) < 0.1:
    print(f"  → 모든 응답자가 정확히 3개씩 선택했습니다. ✓")
elif avg_selections < 3.0:
    print(f"  → 일부 응답자가 3개 미만으로 선택했습니다.")
else:
    print(f"  → 일부 응답자가 3개 초과로 선택했습니다.")

conn.close()

print("\n" + "=" * 80)
print("✓ 분석 완료")
print("=" * 80)
