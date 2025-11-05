import pandas as pd
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Connect to database
conn = sqlite3.connect('PMIK_2025.db')

print("=" * 80)
print("직급별 EOS 응답률 분석")
print("=" * 80)

# Get response status by job title (rank)
query = """
SELECT
    m."Job Title" as job_title,
    COUNT(DISTINCT m."ID(new)") as total_members,
    COUNT(DISTINCT CASE WHEN r.completed = 1 THEN r.corporate_id END) as completed,
    COUNT(DISTINCT CASE WHEN r.completed = 0 THEN r.corporate_id END) as incomplete,
    COUNT(DISTINCT CASE WHEN r.corporate_id IS NULL THEN m."ID(new)" END) as no_response,
    ROUND(COUNT(DISTINCT CASE WHEN r.completed = 1 THEN r.corporate_id END) * 100.0 /
          COUNT(DISTINCT m."ID(new)"), 1) as completion_rate
FROM pmik_member m
LEFT JOIN pmik_raw_data r ON m."ID(new)" = r.corporate_id
WHERE m."Job Title" IS NOT NULL
GROUP BY m."Job Title"
ORDER BY
    CASE m."Job Title"
        WHEN 'E1' THEN 1
        WHEN 'E2' THEN 2
        WHEN 'S3' THEN 3
        WHEN 'S2' THEN 4
        WHEN 'B3' THEN 5
        WHEN 'B2' THEN 6
        WHEN 'B1' THEN 7
        ELSE 99
    END
"""
df = pd.read_sql_query(query, conn)

print("\n[전체 현황]")
total = df['total_members'].sum()
completed_total = df['completed'].sum()
incomplete_total = df['incomplete'].sum()
no_response_total = df['no_response'].sum()

print(f"총 대상자: {total}명")
print(f"  완료: {completed_total}명 ({completed_total/total*100:.1f}%)")
print(f"  미완료: {incomplete_total}명 ({incomplete_total/total*100:.1f}%)")
print(f"  미응답: {no_response_total}명 ({no_response_total/total*100:.1f}%)")

print("\n" + "=" * 80)
print("직급별 응답률")
print("=" * 80)

# Define rank hierarchy
rank_names = {
    'E1': 'E1 (임원 1)',
    'E2': 'E2 (임원 2)',
    'S3': 'S3 (책임 3)',
    'S2': 'S2 (책임 2)',
    'B3': 'B3 (주임 3)',
    'B2': 'B2 (주임 2)',
    'B1': 'B1 (주임 1)'
}

for _, row in df.iterrows():
    job_title = row['job_title']
    total_rank = row['total_members']
    completed_rank = row['completed']
    incomplete_rank = row['incomplete']
    no_response_rank = row['no_response']
    rate = row['completion_rate']

    # Progress bar
    bar_length = int(rate / 5)
    bar = "█" * bar_length + "░" * (20 - bar_length)

    rank_display = rank_names.get(job_title, job_title)

    print(f"\n[{rank_display}]")
    print(f"  [{bar}] {rate:.1f}%")
    print(f"  대상: {total_rank}명 | 완료: {completed_rank}명 | 미완료: {incomplete_rank}명 | 미응답: {no_response_rank}명")

# Show detailed table
print("\n" + "=" * 80)
print("직급별 상세 통계")
print("=" * 80)

print("\n{:<15} {:>8} {:>8} {:>8} {:>8} {:>10}".format(
    "직급", "대상", "완료", "미완료", "미응답", "완료율"
))
print("-" * 80)

for _, row in df.iterrows():
    job_title = row['job_title']
    total_rank = row['total_members']
    completed_rank = row['completed']
    incomplete_rank = row['incomplete']
    no_response_rank = row['no_response']
    rate = row['completion_rate']

    rank_display = rank_names.get(job_title, job_title)

    print("{:<15} {:>8}명 {:>8}명 {:>8}명 {:>8}명 {:>9.1f}%".format(
        rank_display, total_rank, completed_rank, incomplete_rank, no_response_rank, rate
    ))

# Analysis by rank group
print("\n" + "=" * 80)
print("직급 그룹별 분석")
print("=" * 80)

# Group by rank level
executive = df[df['job_title'].str.startswith('E')]
senior = df[df['job_title'].str.startswith('S')]
basic = df[df['job_title'].str.startswith('B')]

print("\n[임원급 (E)]")
if len(executive) > 0:
    exec_total = executive['total_members'].sum()
    exec_completed = executive['completed'].sum()
    exec_rate = (exec_completed / exec_total * 100) if exec_total > 0 else 0
    print(f"  대상: {exec_total}명 | 완료: {exec_completed}명 | 완료율: {exec_rate:.1f}%")
    for _, row in executive.iterrows():
        print(f"    - {row['job_title']}: {row['completed']}/{row['total_members']}명 ({row['completion_rate']:.1f}%)")
else:
    print("  데이터 없음")

print("\n[책임급 (S)]")
if len(senior) > 0:
    senior_total = senior['total_members'].sum()
    senior_completed = senior['completed'].sum()
    senior_rate = (senior_completed / senior_total * 100) if senior_total > 0 else 0
    print(f"  대상: {senior_total}명 | 완료: {senior_completed}명 | 완료율: {senior_rate:.1f}%")
    for _, row in senior.iterrows():
        print(f"    - {row['job_title']}: {row['completed']}/{row['total_members']}명 ({row['completion_rate']:.1f}%)")
else:
    print("  데이터 없음")

print("\n[주임급 (B)]")
if len(basic) > 0:
    basic_total = basic['total_members'].sum()
    basic_completed = basic['completed'].sum()
    basic_rate = (basic_completed / basic_total * 100) if basic_total > 0 else 0
    print(f"  대상: {basic_total}명 | 완료: {basic_completed}명 | 완료율: {basic_rate:.1f}%")
    for _, row in basic.iterrows():
        print(f"    - {row['job_title']}: {row['completed']}/{row['total_members']}명 ({row['completion_rate']:.1f}%)")
else:
    print("  데이터 없음")

# Show non-completers by rank
print("\n" + "=" * 80)
print("미완료/미응답자 직급별 분포")
print("=" * 80)

query_non_complete = """
SELECT
    m."Job Title" as job_title,
    m."Name(Kor.)" as name,
    m."Biz Unit." as biz_unit,
    m.Department,
    m.근속기간 as tenure,
    CASE
        WHEN r.completed = 0 THEN '미완료'
        WHEN r.corporate_id IS NULL THEN '미응답'
    END as status
FROM pmik_member m
LEFT JOIN pmik_raw_data r ON m."ID(new)" = r.corporate_id
WHERE (r.completed = 0 OR r.corporate_id IS NULL)
    AND m."Job Title" IS NOT NULL
ORDER BY
    CASE m."Job Title"
        WHEN 'E1' THEN 1
        WHEN 'E2' THEN 2
        WHEN 'S3' THEN 3
        WHEN 'S2' THEN 4
        WHEN 'B3' THEN 5
        WHEN 'B2' THEN 6
        WHEN 'B1' THEN 7
        ELSE 99
    END,
    m.근속기간 DESC
"""
df_non_complete = pd.read_sql_query(query_non_complete, conn)

if len(df_non_complete) > 0:
    print(f"\n총 {len(df_non_complete)}명:")

    for rank in ['E1', 'E2', 'S3', 'S2', 'B3', 'B2', 'B1']:
        rank_data = df_non_complete[df_non_complete['job_title'] == rank]
        if len(rank_data) > 0:
            print(f"\n[{rank_names.get(rank, rank)}] ({len(rank_data)}명)")
            for _, row in rank_data.iterrows():
                tenure = row['tenure'] if pd.notna(row['tenure']) else 'N/A'
                biz_unit = row['biz_unit'] if pd.notna(row['biz_unit']) else 'N/A'
                dept = row['Department'] if pd.notna(row['Department']) else 'N/A'
                print(f"  [{row['status']}] {tenure:12s} | {biz_unit:8s} > {dept}")
else:
    print("\n미완료/미응답자 없음")

# Correlation analysis
print("\n" + "=" * 80)
print("인사이트")
print("=" * 80)

# Find highest and lowest completion rates
highest = df.loc[df['completion_rate'].idxmax()]
lowest = df.loc[df['completion_rate'].idxmin()]

print(f"\n✓ 최고 응답률: {rank_names.get(highest['job_title'], highest['job_title'])} ({highest['completion_rate']:.1f}%)")
print(f"✗ 최저 응답률: {rank_names.get(lowest['job_title'], lowest['job_title'])} ({lowest['completion_rate']:.1f}%)")

# Check if 100% completion
complete_100 = df[df['completion_rate'] == 100.0]
if len(complete_100) > 0:
    print(f"\n✓ 100% 완료 직급 ({len(complete_100)}개):")
    for _, row in complete_100.iterrows():
        print(f"  - {rank_names.get(row['job_title'], row['job_title'])} ({row['total_members']}명)")

# Group level comparison
if len(executive) > 0 and len(senior) > 0 and len(basic) > 0:
    exec_rate = (executive['completed'].sum() / executive['total_members'].sum() * 100)
    senior_rate = (senior['completed'].sum() / senior['total_members'].sum() * 100)
    basic_rate = (basic['completed'].sum() / basic['total_members'].sum() * 100)

    print(f"\n직급 그룹별 응답률:")
    print(f"  임원급 (E): {exec_rate:.1f}%")
    print(f"  책임급 (S): {senior_rate:.1f}%")
    print(f"  주임급 (B): {basic_rate:.1f}%")

    rates = [('임원급', exec_rate), ('책임급', senior_rate), ('주임급', basic_rate)]
    rates_sorted = sorted(rates, key=lambda x: x[1], reverse=True)

    print(f"\n→ {rates_sorted[0][0]}의 응답률이 가장 높습니다.")

conn.close()

print("\n" + "=" * 80)
print("✓ 분석 완료")
print("=" * 80)
