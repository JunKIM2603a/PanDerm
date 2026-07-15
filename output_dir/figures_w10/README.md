# W10 논문 Figure 초안 (§③ 결과 정리·논문화)

W8~W10 실험을 **새 학습 없이** 기존 수치로 논문 Figure 후보 3종으로 재구성. 모두 PNG(200dpi)+PDF(벡터).
색: Okabe–Ito CVD-safe 팔레트(dataviz 검증기 통과). 재현: `notebooks/PanDerm/Linear Evaluation/make_figures.py`.

| Figure | 파일 | 메시지 | 데이터 원천 |
|---|---|---|---|
| (a) | `fig_a_olp_layerwise_separability.*` | OLP는 **모든 deep layer에서 선형 분리 가능**(5쌍 모두 ≥0.81) → 가설 B 시각화 | `oral_diseases_olp_separability/pairwise_separability_linear.csv` (24블록 CLS 이진 probe, train+val CV) |
| (b) | `fig_b_peft_6method_comparison.*` | PEFT 6방법 스펙트럼: LoRA가 공통 스윗스팟, Full FT는 oral 최고 | `peft_ft_comparison_{aptos2019,oral_diseases}.csv` (collect_peft_table.py) |
| (c) | `fig_c_domain_distance_layer_transfer.*` | 도메인 거리 전이 패턴: aptos(원거리) 중간층 우위, oral(근거리) 마지막층 near-peak | `figures_w10/per_layer_sweep_{slug}.csv` (extract_layer_sweep.py 재도출) |

## (c) 관련 중요 주의 — 데이터 정직성

원 융합 노트북(`panderm_multilayer_fusion_layer_exploration_20260708.ipynb`)의 per_layer_sweep CSV가
디렉토리 정리로 소실 → `extract_layer_sweep.py`로 **24블록 CLS를 재추출·재도출**(마지막층 L23 test BACC가
문서 baseline과 |Δ|≤0.0003으로 일치, 방법론 검증됨).

재도출 결과 **두 데이터셋 모두 val 최적 단일층 = L11**로 나옴 → 회의록 §0-1의 "oral은 마지막층으로 충분"
서사(단일 최적층=마지막층으로 오해될 수 있는 표현)와 **표면상 불일치**. 정직한 해석:

- **aptos(원거리)**: val·test 모두 중간층(L7–L14)이 최고, 마지막층은 그 아래 → 중간층 우위 **명확**.
- **oral(근거리)**: val 최적은 L11이나(n=55 노이즈), **test는 마지막층 L23=0.811 ≈ 최대 0.820@L19** →
  마지막층이 이미 near-peak이라 "마지막층으로 충분"은 **test 기준으로 성립**.
- 따라서 (c)는 val 단일 곡선이 아니라 **val+test 2패널**로 그려야 도메인 거리 대비가 왜곡 없이 드러남.

논문화 시: (c)의 "domain gap ↑ → 중간층 우위 ↑" 주장은 **test 곡선 기준**으로 서술하고, 소표본(test n: aptos 554·oral 54)
한계를 병기할 것.

## 재생성

```bash
conda activate PanDerm
# (c) 데이터가 없으면 먼저 특징 재추출(GPU, 수 분)
CUDA_VISIBLE_DEVICES=0 python extract_layer_sweep.py
# 3종 Figure 생성
python make_figures.py
```
