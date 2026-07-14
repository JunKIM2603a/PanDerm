# SMART-OM 라벨 리매핑 설계 (External Validation)

> 10차 미팅 §① 이월 마무리 — 구강 데이터셋 응답 처리 / §2-4 매칭 결론의 **코드 적용본**.
> SMART-OM(Figshare)을 MOD(`Oral_Diseases`)로 학습한 PanDerm linear probe의 **외부 검증셋**으로 쓰기 위한 라벨 리매핑.

---

## 1. 한눈에 보기

| 항목 | 값 |
| --- | --- |
| 원본 4-클래스 | Normal / Variation-from-Normal / OPMD / Oral Cancer |
| 타깃 라벨 공간 | **3단계 악성 위험도** — `benign_normal(0)` · `OPMD(1)` · `oral_cancer(2)` |
| 사용 이미지 | **`01. Unannotated` 만** (raw 원본, 2,469장) |
| 역할 | 외부 검증(**test 전용**). MOD로 probe 학습 → SMART-OM으로 평가 |
| 재라벨 방식 | 파일 이동/복제 없음 — 라벨은 **CSV에만** 존재 (CC BY-NC-ND 준수) |

---

## 2. 왜 `01. Unannotated`만 쓰는가 (핵심 설계 결정)

SMART-OM은 **같은 사진을 4번** 저장한다: `01. Unannotated / 02. Region annotation / 03. Full annotation / 04. Lesion annotation`.
검증 결과 Region/Full/Lesion 버전은 **같은 파일명·같은 해상도이지만 바이트가 다르다** — 노란 폴리곤(병변/부위 경계)이 **픽셀에 구워져(baked-in)** 있다. 아래가 그 증거:

```
SMITA00187_W_LL.jpeg  Un=520b674abf | Region=570c17393d | Full=5cb37cae69 | Lesion=64f9dc0f3d   (동일 크기 562x221)
```

즉 Region/Full/Lesion을 PanDerm에 넣으면 **오버레이가 특징을 오염**시킨다. 오직 `01. Unannotated`가 깨끗한 원본이며, 그 장수(2,469)가 논문 보고치와 일치한다.

| 어노테이션 레벨 | 장수 | 사용 여부 |
| --- | --- | --- |
| 01. Unannotated | 2,469 | ✅ **사용** (raw) |
| 02. Region annotation | 2,469 | ❌ 오버레이 |
| 03. Full annotation | 2,469 | ❌ 오버레이 |
| 04. Lesion annotation | 324 | ❌ 오버레이(크롭 아님, 동일 해상도) |

---

## 3. 라벨 매핑 표

### 3-1. SMART-OM 4 → 3

| 원본 폴더 | → 3단계 | label | 근거 |
| --- | --- | --- | --- |
| `01. Normal` | benign_normal | 0 | 건강 점막 |
| `02. Variation from normal` | benign_normal | 0 | 양성 변이(암 위험 없음) |
| `03. OPMD` | OPMD | 1 | 구강잠재악성질환 |
| `04. Oral Cancer` | oral_cancer | 2 | 구강편평세포암(OSCC) |

### 3-2. MOD(`Oral_Diseases`) 7 → 3 (probe 학습 소스)

| MOD 클래스 | → 3단계 | label | 근거 (§2-4) |
| --- | --- | --- | --- |
| Gum, CaS, CoS, OT | benign_normal | 0 | 양성 염증/감염, WHO OPMD 목록 밖 |
| OLP | OPMD | 1 | WHO 2020이 OLP를 OPMD로 분류 |
| MC, OC | oral_cancer | 2 | oral cancer (MC=OC 사실상 중복) |

---

## 4. 클래스 분포 & 통계 주의

**SMART-OM (test, 2,469장 / 305 patient-id 추출됨):**

| 클래스 | 장수 | 비율 |
| --- | --- | --- |
| benign_normal | 2,324 | 94.13% |
| OPMD | 125 | 5.06% |
| oral_cancer | 20 | 0.81% |

> ⚠️ **극단적 불균형.** 특히 oral_cancer n=20, OPMD n=125. 소수 클래스 recall/precision은 **신뢰구간(부트스트랩 CI) 병기 필수** — 단일 수치로 결론 금지.

---

## 5. 설계상의 한계 (§2-4 재확인, 결과 해석 시 반드시 명시)

1. **라벨 입도(粒度) 불일치** — SMART-OM은 **환자/구강 단위** 라벨이다(환자 1명의 ~8장 부위 사진이 모두 그 환자의 진단으로 라벨링됨 → OPMD/Cancer 환자의 정상처럼 보이는 부위 사진도 abnormal로 라벨). MOD는 병변 **클로즈업** 단위. 이 차이가 benign↔abnormal 경계를 노이즈화한다.
2. **양방향 공백** — SMART-OM의 Normal/Variation ↔ MOD 대응 없음, MOD엔 정상 클래스 없음. 3단계에서만 `benign_normal`으로 억지로 합쳐지므로 그 버킷의 의미는 두 데이터셋에서 다르다(SMART-OM=건강, MOD=양성 질환).
3. **OPMD ⊋ OLP** — SMART-OM OPMD(125장)는 백반증·OSMF 등을 포함, MOD의 OLP보다 넓다. OPMD 성능을 OLP 성능으로 읽으면 안 됨.
4. **OLP 결정경계 실험에는 사용 금지** — SMART-OM은 OPMD 하위유형 라벨을 공개하지 않아 OLP만 못 고른다. §1-② OLP 진단/개입은 **MOD 내부**에서만.
5. **라이선스** — CC BY-NC-ND(비파생). 이미지 재배포·재라벨 파일 생성 지양 → 본 리매핑은 **CSV 라벨 레이어**로만 구현(원본 폴더 구조 불변).

---

## 6. 산출물

| 파일 | 내용 |
| --- | --- |
| `smart_om_3class_label_map.csv` | 3-클래스 라벨맵 (`class_name,label`) |
| `smart_om_remapping_3class.csv` | SMART-OM 단독, `image,label,split`(=test). 경로는 `SMART-OM_remapping/` 기준 |
| `smart_om_remapping_manifest.csv` | 추적용 풀 메타 (patient_id, region, 원본 4-class 포함) |
| `mod_smartom_external_val_3class.csv` | **실행용** 결합 CSV. MOD(train/val) + SMART-OM(test). 경로는 `PanDerm/data/` 기준 |
| `build_remapping.py` | 위 전부를 재생성하는 스크립트 (원본 파일 스캔 기반, 결정론적) |
| `cmd.txt` | 실행 커맨드 |

재생성:
```bash
cd "PanDerm/data/SMART-OM_remapping/Linear Evaluation"
python build_remapping.py
```

---

## 7. 실행 프로토콜 (외부 검증)

`mod_smartom_external_val_3class.csv`는:
- **train** = MOD train + test 폴드(461장) — SMART-OM이 유일한 외부 test이므로 MOD를 최대한 학습에 사용
- **val** = MOD val 폴드(55장, `valid_feats=None`이라 fit에는 미사용·비어있지 않게만 유지)
- **test** = SMART-OM 전체(2,469장)

```bash
cd PanDerm/classification
CUDA_VISIBLE_DEVICES=0 python3 linear_eval.py \
  --batch_size 16 --num_workers 8 \
  --model "PanDerm_Large_LP" \
  --nb_classes 3 \
  --percent_data 1.0 \
  --csv_filename "smartom_external_val_panderm_large_lp_result.csv" \
  --output_dir "../output_dir/smartom_external_val_panderm_large_lp/" \
  --csv_path "../data/SMART-OM_remapping/Linear Evaluation/mod_smartom_external_val_3class.csv" \
  --root_path "../data/" \
  --pretrained_checkpoint "../checkpoint/panderm_ll_data6_checkpoint-499.pth"
```

> `--nb_classes 3`, `--root_path "../data/"`(끝에 `/`)에 주의. SMART-OM 단독으로 재현·특징추출만 할 땐 `smart_om_remapping_3class.csv` + `--root_path "../data/SMART-OM_remapping/"` 사용(단, probe fit엔 train 행이 없어 그대로는 linear_eval 실행 불가 — 결합 CSV를 쓸 것).
