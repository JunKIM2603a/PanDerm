# Oto-Endoscopic — PanDerm 선형 평가(Linear Probe) 기록

`PanDerm/data/` 의 다른 데이터셋과 **동일한 절차**(매니페스트 CSV → `PanDerm/classification/linear_eval.py`,
`PanDerm_Large_LP` + `panderm_ll_data6_checkpoint-499.pth` 동결 인코더 + 선형 프로브)로 시험했다.
실행일 2026-09-17, GPU GTX 1060 6GB, conda env `PanDerm`.

## 1. 데이터

- 이미지 3,014장 / 5개 클래스, 모두 `.jpg`, 클래스별 601~605장(불균형비 1.007 — 사실상 균형).
- 라벨은 `Oto-Endoscopic_Images/` 의 폴더 이름에서 가져온다. 디스크의 이미지 파일은 이동·개명·수정하지 않았다.

| label | class_name | n |
| --- | --- | --- |
| 0 | Acute_Otitis_Media | 601 |
| 1 | Cerumen_Impaction | 602 |
| 2 | Chronic_Otitis_Media | 602 |
| 3 | Myringosclerosis | 605 |
| 4 | Normal | 604 |

배포본에 train/val/test 분할이 없어서, 분할이 없던 다른 데이터셋(`aptos2019`, `Oral_Cancer`)과 같은
**층화 70/15/15**(고정 시드 0, 정렬된 파일 순서로 결정적)로 만들었다.

생성 스크립트: `build_oto_endoscopic.py` (재실행하면 동일 결과).

## 2. 중복 감사 — 이 데이터셋의 핵심 주의사항

| 감사 | 결과 |
| --- | --- |
| 정확 중복 (sha256) | 92 군집 / 184장, 그중 **47 군집이 분할 경계를 넘음** |
| 근접 중복 (dHash, Hamming ≤ 5, 전이 폐포) | 490 군집 / 2,150장, 고유 군 1,354개 |
| 평문 층화 분할의 test 누수 | **test 452장 중 316장(69.9%)** 이 train/val 에 근접 중복 쌍을 가짐 |

파일명이 연속인 장면(`AOM_014`/`AOM_015` 등)이 바이트 단위로 같거나 거의 같다 — 연속 촬영/동영상 프레임으로 보인다.
따라서 평문 층화 분할 점수는 그대로 신뢰하면 안 되고, 아래 두 복제 시험을 함께 읽어야 한다.

`oto_endoscopic_manifest.csv` 가 이미지별 `sha256`, `dup_group`, `neardup_group`, 세 분할을 모두 담는다.

**한계.** sha256 은 바이트 동일만, dHash 는 시각적 근접 중복만 잡는다. 둘 다 **환자 수준 독립성을 보장하지 않는다** —
배포본에 환자 ID 가 없어 같은 귀를 다른 각도에서 찍은 사진은 여전히 다른 폴드로 갈 수 있다(AGENTS.md §2.1 범위 단서와 동일한 상황).

## 3. 결과 (동결 인코더 선형 프로브, seed 0)

| 분할 | test n | BACC | ACC | W_F1 | AUROC | AUPR | 산출물 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 층화 70/15/15 (기본, 타 데이터셋과 동일 방식) | 452 | 0.9978 | 0.9978 | 0.9978 | 1.0000 | 1.0000 | `../../../output_dir/oto_endoscopic_panderm_large_lp/` |
| 정확 중복 인지 복제 | 456 | 0.9978 | 0.9978 | 0.9978 | 1.0000 | 1.0000 | `../../../output_dir/oto_endoscopic_dupaware_panderm_large_lp/` |
| 근접 중복 인지 복제 | 689 | **0.9937** | 0.9942 | 0.9942 | 0.9976 | 0.9915 | `../../../output_dir/oto_endoscopic_neardup_panderm_large_lp/` |

**해석.** test 의 70%가 누수 상태였는데도 근접 중복을 완전히 통제한 뒤 BACC 가 0.9978 → 0.9937 로
0.004 만 떨어졌다. 즉 이 과제의 쉬움은 누수의 산물이 아니라 데이터셋 자체 성질이다 —
5개 클래스가 PanDerm 동결 특징공간에서 거의 선형 분리된다.

**함의.** 이 데이터셋은 저자원 OOD 전이의 *어려운* 시험대가 아니다. 프로브 단계에서 이미 천장(BACC≈0.99)이라
처치 간 차이를 볼 여지가 없다 — 사전 등록 게이트(안저 0.019 / 구강 0.032 수준의 Δ 바닥)를 적용할 대상으로는
부적합하다. 난이도 있는 비교가 필요하면 저데이터 체제(`--percent_data` 축소)나 클래스 통합 쪽을 봐야 한다.

## 4. 재현

```bash
# 매니페스트 재생성
python3 "PanDerm/data/Oto-Endoscopic/Linear Evaluation/build_oto_endoscopic.py" --seed 0
# 시험 3건
# -> cmd.txt 참조 (원문 로그: result.txt / result_dupaware.txt / result_neardup.txt)
```
