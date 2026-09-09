# 🔒 w11-12 — 기준 표준 출처 감사표 (reference-standard provenance audit)

> **탐색적 · exploratory (w11 · 판정 아님 / not a verdict).** 사전 등록 판정(§B 0/18) · 문턱 · Holm 묶음과 무관하다. 이 표는 CLAIM 15·16 (데이터 출처·라벨 정의)과 Limitations 의 "reference standard" 항목에 쓰인다. 새 가설검정 없음 · 판정 없음.
>
> 생성: `p6w11_refstd.py` (full 모드) · 2026-09-08T07:05:58Z · 계획 §2 W11-12 · 문헌 S8 §6. 모든 외부 접근 기록은 `w11_refstd_verification.json`.

## 0. 실행 전 예측의 판정

| 예측 | 값 | 재계산 | 판정 |
| --- | --- | --- | --- |
| P11a · Krause Table 2 (망막 전문의 3인 다수결) BACC | S8 §6 = 0.793 | **0.7934** | ✅ 재현(reproduced) |
| P11b · Krause Table 4 (안과 전문의 3인 다수결) BACC | S8 §6 = 0.712 | **0.7120** | ✅ 재현(reproduced) |
| P11c · Krause Table 6 인접(정확히 한 등급) 비율 | S8 §6 = 0.813 | **0.8135** (65+92/193) | ✅ 재현 |

전사 리터럴의 PDF 원문 대조: **전 표 통과**. 논문이 직접 싣는 세 통계(qw-κ · 민감도 · 특이도)를 같은 행렬에서 재계산해 published 값과 대조했다 — 이것이 전사·행/열 방향이 맞다는 증거다.

## 1. 기준 표준 상한 — Krause 2018 재계산 (탐색적)

| 비교 대상 (열) | N | BACC (재계산) | micro acc | qw-κ 재계산 / published | 민감도(≥moderate) 재계산 / published | 특이도 재계산 / published |
| --- | --- | --- | --- | --- | --- | --- |
| Table 2 — Majority decision of 3 retinal specialists, before adjudication | 1,813 | **0.7934** | 0.9377 | 0.9146 / 0.91 | 0.881 / 0.881 | 0.994 / 0.994 |
| Table 4 — Majority decision of 3 general ophthalmologists (independent of the panel) | 1,810 | **0.7120** | 0.8939 | 0.8709 / 0.87 | 0.838 / 0.838 | 0.981 / 0.981 |
| Table 8 — Algorithm grade (Krause et al. full model) | 1,813 | **0.7264** | 0.8582 | 0.8377 / 0.84 | 0.971 / 0.971 | 0.923 / 0.923 |
| Table S1 — Majority of all 6 graders (3 retinal specialists + 3 ophthalmologists) | 1,813 | **0.7611** | 0.9316 | 0.9047 / — | 0.848 / — | 0.995 / — |

* **두 전문가 패널의 차이 = 0.0813** — 안저 사전 등록 하한 0.019 의 **4.3배**. 우리가 검출하려던 크기는 두 전문가 집단이 서로 다른 만큼보다 훨씬 작다.
* **주의 1 (재계산).** 0.793 · 0.712 는 Krause 등이 보고한 값이 **아니다**. 그들이 공개한 혼동행렬에서 우리가 **BACC 를 새로 계산**한 것이다(논문은 qw-κ·민감도·특이도만 싣는다). 같은 행렬에서 그 세 통계를 재계산하면 published 값과 일치한다(위 표) — 전사의 증거.
* **주의 2 (자기 일치 상한).** Table 2 의 망막 전문의 3인은 **판정 표준을 만든 바로 그 3인**이다. 따라서 0.793 은 독립 판독자의 성취가 아니라 **자기 일치 상한**이다. 독립 패널은 Table 4 의 안과 전문의 3인(0.712)이다.
* **주의 3 (다른 코호트).** 이 값들은 EyePACS-2 검증셋(N = 1,813 · No DR 81.5%)의 것이고 APTOS 2019 가 아니다. 절대 BACC 를 우리 팔과 나란히 읽지 말 것 — 쓸 수 있는 것은 **패널 간 차이**다.
* **published 표의 내부 불일치 (Table 4).** published 표 자체의 총합이 1,810 (No 행 1,475) 으로 Table 1 의 1,813 (No 행 1,478) 보다 3 장 적다. 논문이 함께 싣는 특이도 98.1% 는 1,475 분모와 일치하므로 이는 전사 오류가 아니라 published 표의 내부 불일치다. 누락 3 장을 정답/오답 어느 쪽으로 두어도 BACC 는 0.7116-0.7120 → 0.712 로 변하지 않는다.
* **published 표의 내부 불일치 (Table 4 (DME)).** 행 합 1,727/78 = 1,805 로 Table 1 의 1,734/79 = 1,813 과 다르다(published 표의 불일치).

### 개별 판독자

논문은 **개별 판독자의 5×5 혼동행렬을 싣지 않는다**(Table 3·5 는 민감도·특이도·qw-κ 만). 따라서 판독자 A/B/C 각각의 BACC 는 **계산할 수 없다** — 지어내지 않는다. 패널(다수결) 단위 BACC 만 위 표에 있다.

## 2. 데이터셋 출처 감사표 (CLAIM 15·16)

가로가 길어 **항목을 행으로** 옮겼다. 각 칸은 *확인된 1차 근거* 만 담는다 — 확인하지 못한 것은 빈칸이 아니라 "미확인"으로 적는다.

| 항목 | **APTOS 2019 Blindness Detection** (fundus · 5 grades) | **MOD — Mouth and Oral Diseases** (7 classes) |
| --- | --- | --- |
| 1차 문서 | 대회 데이터 페이지 (S8-59) · https://www.kaggle.com/c/aptos2019-blindness-detection/data | Rashid et al. 2024 (S8-56 · doi:10.1007/s11042-023-16776-x) · Kaggle release v1 https://www.kaggle.com/datasets/javedrashid/mouth-and-oral-diseases-mod |
| 이미지당 판독자 수 | **1명** — "A clinician has rated each image" (✅ 원문 확인) | **미기재** — "Expert dental practitioners contributed to the labeling" 뿐 · 인원수 없음 (S8-56 전문 판독) |
| 판정(adjudication) | **없음** — 데이터 설명 어디에도 adjudication/consensus 언급 없음 (설명 블록 1891자 안에서 해당 용어 0건) | **없음** — 판정·재판독 절차 기술 없음 |
| 품질(gradability) 배제 | **없음** — "you will encounter noise in both the images and labels … artifacts, out of focus, under/overexposed" 라고 명시하되 배제 절차는 없음 (✅ 원문 확인) | **없음** — 배제 기준 기술 없음 |
| 분류 체계 출처 | ICDR 5단계(0 No DR · 1 Mild · 2 Moderate · 3 Severe · 4 Proliferative) — 대회 페이지가 척도만 제시하고 등급 정의 문서를 인용하지 않음 | 논문 저자 정의 7클래스 — CaS/CoS/Gum/MC/OC/OLP/OT · **"mouth cancer"(MC)와 "oral cancer"(OC)의 구분 기준이 원문에 없다** |
| 일치도 통계 | **없음** (κ·재판독 없음) | **없음** (κ·재판독·생검 확인 없음) |
| 윤리 | 대회 규정에 IRB 진술 없음 · 후원 Aravind Eye Hospital & PG Institute of Ophthalmology (✅ 원문 확인) | 원문 그대로 **"Ethical approval: Not applicable"** (S8-56) |
| 클래스별 n (우리 사본) | no_dr 1,805, mild 370, moderate 999, severe 193, proliferative_dr 295 · 합 3,662 | CaS 79, CoS 75, Gum 61, MC 90, OC 54, OLP 94, OT 63 · 합 **516** |
| 원문 표와의 대조 | 해당 없음(대회 페이지는 클래스별 n 을 싣지 않는다) | Rashid Table 2 = 78/79/61/90/54/93/62 = **517** ↔ 우리 **516** — 각주 참조 |
| 라이선스 | ✅ Kaggle 대회 규정 §7.A — "non-commercial purposes only … academic research and education" (Wayback 원문 확인) | ⚠️ **미확인** — Kaggle 데이터셋 페이지는 JS 렌더라 라이선스 문자열이 HTML 에 없고, 스냅샷은 있으나 인증 없이 라이선스 필드를 읽을 수 없다 (snapshot_found). 인증 필요 → **투고 전 확인 항목** |
| 접근일 | 2026-09-08T07:05:58Z (Wayback 스냅샷 20190717130619) | 2026-09-08T07:05:58Z (라이선스 미확인) |

> **각주 (516 vs 517).** 원 논문 Table 2 는 78/79/61/90/54/93/62 = 517 장을, 우리가 쓴 Kaggle release v1 사본은 79/75/61/90/54/94/63 = 516 장을 담는다. 차이는 총합 1장이 아니라 **클래스별로 -1/+4/+0/+0/+0/-1/-1** 이다 — 한 장이 빠진 것이 아니라 배포판과 논문 표가 서로 다른 것이다. 원고 §3.1 각주: "Kaggle release v1 (516 images); the source paper's Table 2 lists 517 with per-class counts differing by 1-4." ⚠️ 이 대조는 논문 Table 2 의 행 순서가 Kaggle 폴더 이름 순서와 같다는 **가정** 위에 있다(61/90/54 세 값이 정확히 일치하는 것이 그 가정의 유일한 근거다).

## 3. 라벨 해상도의 위계 — 상한 문장 (검증된 인용)

| # | 문장 | 검증 |
| --- | --- | --- |
| S8-50 | APTOS 가 배포하는 것과 같은 **단일 시야 안저 사진**에서, 12명의 안과 인력이 DR 중증도에 대해 보인 multirater κ 는 **0.34**, 그 중 망막 전문의 3인은 **0.58** 이었다 (Ruamviboonsuk 2006, doi:10.1016/j.ophtha.2005.11.021). | ✅ Crossref 서지 일치 · ✅ 초록에서 수치 확인(pubmed_abstract) |
| S8-51 | 전국 규모 선별 프로그램에서 훈련된 판독자와 판정 패널 사이의 qw-κ 는 **0.78** 이었다 (Ruamviboonsuk 2019, doi:10.1038/s41746-019-0099-8). | ✅ Crossref 서지 일치 · ✅ 초록에서 수치 확인(crossref_abstract) |
| S8-52 | 위계의 상단에서도, 3인 전문의 패널끼리의 qw-κ 는 **0.921-0.963** 이다 (Schaekermann 2019, doi:10.1167/tvst.8.6.40). | ✅ Crossref 서지 일치 · ✅ 초록에서 수치 확인(pubmed_abstract) |
| S8-57 | OLP 의 **임상** 진단에서 관찰자 간 κ 는 **0.43-0.77**, 관찰자 내 κ 는 0.62-0.92 다 (van der Meij 2002, doi:10.1046/j.0904-2512.2001.00174.x). MOD 의 최저 recall 클래스가 OLP 다. | ✅ Crossref 서지 일치 · ✅ 초록에서 수치 확인(crossref_abstract) |
| S8-58 | 임상의 전원이 OLP 로 일치한 사례의 **42%** 에서 조직병리 진단은 일치하지 않았다 (van der Meij & van der Waal 2003, doi:10.1034/j.1600-0714.2003.00125.x). MOD 에는 생검 확인이 없다. | ✅ Crossref 서지 일치 · ✅ 초록에서 수치 확인(crossref_abstract) |
| S8-49 | 판정 표준을 만든 3인 패널의 다수결조차 BACC 0.793, 독립 안과 전문의 3인은 0.712 — 차이 0.081 (Krause 2018, doi:10.1016/j.ophtha.2018.01.034). | ✅ Crossref 서지 일치 |

## 4. 우리 예측의 인접 등급 분해 vs Krause 81.3% (탐색적 · 판정 아님)

| 짝 | severe recall (fold 평균) | 새로 맞힌 severe | 그중 기준선이 moderate 로 본 것 | 오류 중 한 등급 비율 (팔 / 기준선) | 사전 등록 NB p |
| --- | --- | --- | --- | --- | --- |
| B3 vs B0 | 0.360 → 0.579 (+0.219) | 152 | 123 (80.9% · 순증 대비 96.9%) | 0.815 / 0.700 | 0.019 |
| B3d vs B0d | 0.353 → 0.549 (+0.196) | 144 | 125 (86.8% · 순증 대비 109.6%) | 0.810 / 0.699 | 0.438 · ⚠️ 잡음 수준 — 부호 해석 금지 |

* Krause 의 전문가 불일치 중 **정확히 한 등급**인 비율은 **0.813** 이다. 우리 팔의 오류 가운데 한 등급 비율은 위 표의 "오류 중 한 등급 비율" 열에 있다 — **같은 축 위의 숫자이지만 같은 코호트도, 같은 비교 대상도 아니다**(Krause: 사람 vs 판정 표준 · 우리: 헤드 vs 단일 임상의 라벨). 나란히 두는 목적은 재분배가 라벨 잡음이 사는 바로 그 축(±1 등급) 위에서 일어난다는 **서술**뿐이다.
* "순증 대비" = (기준선이 moderate 로 본 새 정답 수) / (새 정답 − 새 오답). 분모가 순증이라 **100% 를 넘을 수 있다**(한 등급 이동으로 얻은 것보다 다른 곳에서 잃은 것이 있을 때) — 오류가 아니다.
* R10 (계획 §3): 사전 등록 ΔBACC 의 NB p > 0.15 인 짝은 위 수치의 **부호를 방향으로 읽지 않는다**.

## 5. 원고 반영 (계획 §4)

* **Limitations · reference standard.** "두 데이터셋 모두 이미지당 판독자 1명(APTOS) 또는 인원 미기재(MOD)이고, 판정·품질 배제·일치도 통계가 없다. 같은 5단계 척도에서 판정 표준을 공유하는 두 전문가 패널의 BACC 차이는 0.081 로, 우리 사전 등록 하한 0.019 의 4.3배다. 우리가 검출하려 한 크기는 라벨 자체의 해상도보다 작다."
* **CLAIM 15·16.** 위 §2 표를 부록으로. 확인하지 못한 항목(MOD 라이선스)은 미확인으로 남긴다.
* 이 문서의 어떤 수치도 §B 판정(0/18)을 바꾸지 않는다.

