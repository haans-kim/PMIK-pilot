import pandas as pd
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Connect to database
conn = sqlite3.connect('PMIK_2025.db')

print("=" * 80)
print("부서별 EOS 응답 현황 분석")
print("=" * 80)

# Get department structure from pmik_member
query_structure = """
SELECT
    "Biz Unit." as biz_unit,
    Department,
    Team,
    COUNT(*) as total_members
FROM pmik_member
WHERE "Biz Unit." IS NOT NULL
GROUP BY "Biz Unit.", Department, Team
ORDER BY "Biz Unit.", Department, Team
"""
df_structure = pd.read_sql_query(query_structure, conn)

print("\n[조직 구조]")
print(f"총 구성: {len(df_structure)} 팀")
print()

for biz_unit in df_structure['biz_unit'].unique():
    if pd.notna(biz_unit):
        unit_data = df_structure[df_structure['biz_unit'] == biz_unit]
        print(f"\n{biz_unit}:")
        for _, row in unit_data.iterrows():
            dept = row['Department'] if pd.notna(row['Department']) else 'N/A'
            team = row['Team'] if pd.notna(row['Team']) else 'N/A'
            print(f"  - {dept} > {team}: {row['total_members']}명")

# Analyze response status by department
print("\n" + "=" * 80)
print("부서별 응답 현황")
print("=" * 80)

query_responses = """
SELECT
    m."Biz Unit." as biz_unit,
    m.Department,
    m.Team,
    COUNT(DISTINCT m."ID(new)") as total_members,
    COUNT(DISTINCT CASE WHEN r.completed = 1 THEN r.corporate_id END) as completed_responses,
    COUNT(DISTINCT CASE WHEN r.completed = 0 THEN r.corporate_id END) as incomplete_responses,
    COUNT(DISTINCT CASE WHEN r.corporate_id IS NULL THEN m."ID(new)" END) as no_response
FROM pmik_member m
LEFT JOIN pmik_raw_data r ON m."ID(new)" = r.corporate_id
WHERE m."Biz Unit." IS NOT NULL
GROUP BY m."Biz Unit.", m.Department, m.Team
ORDER BY m."Biz Unit.", m.Department, m.Team
"""
df_responses = pd.read_sql_query(query_responses, conn)

print(f"\n전체 현황:")
total_members = df_responses['total_members'].sum()
total_completed = df_responses['completed_responses'].sum()
total_incomplete = df_responses['incomplete_responses'].sum()
total_no_response = df_responses['no_response'].sum()

print(f"  총 대상자: {total_members}명")
print(f"  완료: {total_completed}명 ({total_completed/total_members*100:.1f}%)")
print(f"  미완료: {total_incomplete}명 ({total_incomplete/total_members*100:.1f}%)")
print(f"  미응답: {total_no_response}명 ({total_no_response/total_members*100:.1f}%)")

# Detailed by business unit
for biz_unit in df_responses['biz_unit'].unique():
    if pd.notna(biz_unit):
        unit_data = df_responses[df_responses['biz_unit'] == biz_unit]

        unit_total = unit_data['total_members'].sum()
        unit_completed = unit_data['completed_responses'].sum()
        unit_incomplete = unit_data['incomplete_responses'].sum()
        unit_no_response = unit_data['no_response'].sum()

        print(f"\n[{biz_unit}]")
        print(f"  총 {unit_total}명 | 완료: {unit_completed}명 ({unit_completed/unit_total*100:.1f}%) | 미완료: {unit_incomplete}명 | 미응답: {unit_no_response}명")
        print()

        for _, row in unit_data.iterrows():
            dept = row['Department'] if pd.notna(row['Department']) else 'N/A'
            team = row['Team'] if pd.notna(row['Team']) else 'N/A'
            total = row['total_members']
            completed = row['completed_responses']
            incomplete = row['incomplete_responses']
            no_resp = row['no_response']

            completion_rate = (completed / total * 100) if total > 0 else 0

            status = "✓" if completion_rate == 100 else "△" if completion_rate >= 80 else "✗"

            print(f"  {status} {dept} > {team}")
            print(f"     대상: {total}명 | 완료: {completed}명 ({completion_rate:.1f}%) | 미완료: {incomplete}명 | 미응답: {no_resp}명")

# Summary by business unit
print("\n" + "=" * 80)
print("사업부별 요약")
print("=" * 80)

query_summary = """
SELECT
    m."Biz Unit." as biz_unit,
    COUNT(DISTINCT m."ID(new)") as total_members,
    COUNT(DISTINCT CASE WHEN r.completed = 1 THEN r.corporate_id END) as completed,
    ROUND(COUNT(DISTINCT CASE WHEN r.completed = 1 THEN r.corporate_id END) * 100.0 /
          COUNT(DISTINCT m."ID(new)"), 1) as completion_rate
FROM pmik_member m
LEFT JOIN pmik_raw_data r ON m."ID(new)" = r.corporate_id
WHERE m."Biz Unit." IS NOT NULL
GROUP BY m."Biz Unit."
ORDER BY completion_rate DESC
"""
df_summary = pd.read_sql_query(query_summary, conn)

print()
for _, row in df_summary.iterrows():
    biz_unit = row['biz_unit']
    total = row['total_members']
    completed = row['completed']
    rate = row['completion_rate']

    bar_length = int(rate / 5)
    bar = "█" * bar_length + "░" * (20 - bar_length)

    print(f"{biz_unit:15s} [{bar}] {rate:5.1f}% ({completed}/{total}명)")

conn.close()

print("\n" + "=" * 80)
print("✓ 분석 완료")
print("=" * 80)
