# EOS 분석 스크립트

이 디렉토리에는 EOS(Employee Opinion Survey) 데이터 분석을 위한 Python 스크립트가 포함되어 있습니다.

## 스크립트 목록

### 1. analyze_department_responses.py
**목적**: 부서별 응답 현황 분석

**분석 내용**:
- 사업부별 응답률 (A&R, O&F, Sales)
- 부서 및 팀별 상세 응답 현황
- 완료/미완료/미응답 인원 현황
- 응답률 시각화 (프로그레스 바)

**실행 방법**:
```bash
python scripts/analyze_department_responses.py
```

**주요 결과**:
- 전체 응답률: 95.0% (132/138명)
- O&F: 96.7%, Sales: 96.3%, A&R: 89.3%

---

### 2. analyze_tenure_responses.py
**목적**: 근속기간별 응답률 분석

**분석 내용**:
- 근속기간 구간별 응답률
- 완료자 vs 미완료자 평균 근속기간 비교
- 미완료/미응답자 상세 프로필

**실행 방법**:
```bash
python scripts/analyze_tenure_responses.py
```

**주요 결과**:
- 5-10년: 100% 완료율
- 근속기간이 긴 직원의 응답률이 더 높음

---

### 3. analyze_rank_responses.py
**목적**: 직급별 응답률 분석

**분석 내용**:
- 직급별/직급 그룹별 응답률
- 미완료/미응답자 직급별 분포

**실행 방법**:
```bash
python scripts/analyze_rank_responses.py
```

**주요 결과**:
- 임원급(E): 100%, 주임급(B): 96.5%, 책임급(S): 83.3%

---

### 4. analyze_q75_motivation.py
**목적**: Q75 업무 몰입 동기부여 요인 분석

**분석 내용**:
- 선택지별 빈도 분석
- 사업부별/직급별 Top 3 동기부여 요인
- 가장 많이 선택된 조합

**실행 방법**:
```bash
python scripts/analyze_q75_motivation.py
```

**주요 결과**:
- 1위: 조직문화 및 분위기 (45.5%)
- 2위: 일과 개인생활의 조화 (43.9%)
- 3위: 충분한 복리후생 지원 (38.6%)

---

### 5. analyze_q76_hindrance.py
**목적**: Q76 업무 몰입 저해 요인 분석

**분석 내용**:
- 선택지별 빈도 분석
- 근속기간별/사업부별/직급별 Top 3 저해 요인
- 가장 많이 선택된 조합

**실행 방법**:
```bash
python scripts/analyze_q76_hindrance.py
```

**주요 결과**:
- 1위: 경쟁사보다 낮은 보상 수준 (62.9%)
- 2위: 회사의 불투명한 성장 비전 (37.9%)
- 3위: 자기 성장의 기회 부족 (36.4%)

---

### 6. compare_q75_q76_by_tenure.py
**목적**: Q75 vs Q76 근속연수별 비교 분석

**분석 내용**:
- 근속연수별 동기부여/저해요인 Top 5
- Q75 vs Q76 주요 차이점
- 근속연수에 따른 테마 변화 추이

**실행 방법**:
```bash
python scripts/compare_q75_q76_by_tenure.py
```

**주요 결과**:
- 보상 불만은 전 구간 지속 (64%→70%→61%→48%)
- 워라밸 중요도는 경력 쌓을수록 증가 (29%→49%→39%→62%)

---

## 실행 전 준비

### 1. 가상환경 활성화
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. 프로젝트 루트로 이동
```bash
cd c:\Project\PMIK-pilot
```

### 3. 스크립트 실행
```bash
python scripts/<script_name>.py
```

---

## 필수 요구사항

- **Python**: 3.10 이상
- **라이브러리**: pandas, sqlite3, openpyxl
- **데이터베이스**: PMIK_2025.db (프로젝트 루트)

---

## 전체 분석 실행

```bash
python scripts/analyze_department_responses.py
python scripts/analyze_tenure_responses.py
python scripts/analyze_rank_responses.py
python scripts/analyze_q75_motivation.py
python scripts/analyze_q76_hindrance.py
python scripts/compare_q75_q76_by_tenure.py
```

---

## 관련 문서

- [CLAUDE.md](../CLAUDE.md) - 프로젝트 전체 문서
- [분석1.md](../분석1.md) - EOS 분석 종합 보고서
- [Q75_Q76_structure_analysis.md](../Q75_Q76_structure_analysis.md) - Q75/Q76 구조 분석
