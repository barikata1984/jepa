---
Title: "Rectified LpJEPA: Joint-Embedding Predictive Architectures with Sparse and Maximum-Entropy Representations"
Authors:
  - Kuang, Yilun
  - Dagade, Yash
  - Rudner, Tim G. J.
  - Balestriero, Randall
  - LeCun, Yann
Year: 2026
Venue: arXiv
Tags:
  - "self-supervised-learning"
  - "jepa"
  - "sparse-representations"
  - "distribution-matching"
  - "maximum-entropy"
  - "non-negative-representations"
PDF: "[[papers/Kuang-arXiv2026-Rectified_LpJEPA/main.pdf|📃]]"
Import Date: "2026-06-08"
Read Date: 2026-06-08
Executive Summary: "LeJEPA の SIGReg が強制する等方 Gaussian 正則化はスパース表現を許容しない. この制約を Rectified Generalized Gaussian (RGG) 分布へのマッチングに置き換える Rectified Distribution Matching Regularization (RDMReg) を提案し, JEPA の表現にスパース性と非負性を導入する. RGG はパラメータ {mu, sigma, p} で期待 l0 ノルムを制御でき, Renyi 情報次元でスケーリングした最大エントロピー性を保持する. 手法は sliced 2-Wasserstein 距離による二標本分布マッチングとして実装され, LeJEPA の厳密な一般化となる. ImageNet-100 での事前学習において, 95% 以上のエントリがゼロになるまで性能低下が緩やかであり, スパース性と分類精度の良好なトレードオフを達成した."
Citekey: Kuang-arXiv2026-Rectified_LpJEPA
BibTeX Key: kuang2026rectified
DOI: ""
Relevance: 5
Repository: "none"
Category: note
Template Version: v2.3
---

## Executive Summary
LeJEPA の SIGReg が強制する等方 Gaussian 正則化はスパース表現を許容しない. この制約を Rectified Generalized Gaussian (RGG) 分布へのマッチングに置き換える Rectified Distribution Matching Regularization (RDMReg) を提案し, JEPA の表現にスパース性と非負性を導入する. RGG はパラメータ {mu, sigma, p} で期待 l0 ノルムを制御でき, Renyi 情報次元でスケーリングした最大エントロピー性を保持する. 手法は sliced 2-Wasserstein 距離による二標本分布マッチングとして実装され, LeJEPA の厳密な一般化となる. ImageNet-100 での事前学習において, 95% 以上のエントリがゼロになるまで性能低下が緩やかであり, スパース性と分類精度の良好なトレードオフを達成した.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

LeJEPA ([[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics|Balestriero+ 2025]]) の SIGReg 損失は, 特徴分布を等方 Gaussian に一致させることで崩壊を防ぐが, 等方 Gaussian は本質的に密な表現しか生成できず, 神経科学や信号処理で効率的とされるスパースかつ非負な表現を捉えられない. 本論文はこの制限を解消し, JEPA の正則化ターゲットを等方 Gaussian からスパース性を制御可能な分布族へ一般化する方法を提示した.

### 提案手法のアプローチと, その根幹をなす要素は何か?

JEPA の特徴に ReLU を適用して非負化した後, その分布を Rectified Generalized Gaussian (RGG) 分布に sliced 2-Wasserstein 距離で一致させる. RGG はパラメータ (mu, sigma, p) により期待 l0 ノルムを連続的に制御でき, Renyi 情報次元のスケーリングの下で最大エントロピー性を保つため, スパースな領域でも崩壊を防止できる.

- **Rectified Generalized Gaussian (RGG) 分布**: Generalized Gaussian を ReLU で整流した分布族. Dirac 質量と Truncated Generalized Gaussian の混合として定義され, p=2 で Rectified Gaussian, p=1 で Rectified Laplace に帰着する. 期待 l0 ノルムは E[||x||_0] = d * Phi_{GNp(0,1)}(mu/sigma) で陽に決まる.
- **RDMReg (Rectified Distribution Matching Regularization)**: Cramer-Wold の定理に基づき, ランダム射影上の一次元マージナルで二標本分布マッチングを行う正則化損失. RGG は線形結合に関して閉じていないため, LeJEPA の SIGReg のような一標本 CDF マッチングではなく, sliced 2-Wasserstein 距離によるソート済みサンプル間の l2 距離として実装される.
- **特徴の ReLU 整流**: エンコーダ + プロジェクタの出力に ReLU を適用し, 非負性を明示的に強制する. 連続写像定理により, 非整流特徴を Generalized Gaussian にマッチさせてから後で ReLU を適用する方法では性能が大幅に低下するため, 学習時の整流が不可欠であることを実証した.

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

LeJEPA / SIGReg ([[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics|Balestriero+ 2025]]) が最も直接的な先行研究であり, 等方 Gaussian ターゲットによる射影ベースの分布マッチングを導入した. 本手法はそのターゲット分布を RGG に置き換えることで LeJEPA を厳密に一般化している (p=2, 整流なしの場合に LeJEPA に帰着する).

VICReg は二次統計量のみを正則化するが, RDMReg は Cramer-Wold の定理により高次依存性も抑制する. NCL (Non-Negative Contrastive Learning) は対照学習損失を整流特徴に適用するが, 分布マッチングによるスパース性制御は行わない.

新規性は, (1) RGG 分布族の導入とその最大エントロピー特性の証明, (2) RGG が線形結合に関して閉じないことに起因する二標本マッチングの必要性の理論的解明, (3) RDMReg が Non-Negative VCReg を回復することの証明 (線形個数の射影で共分散行列を等方化できる), の 3 点にある.

### どのように訓練・最適化したのか?

- **損失関数 / 最適化目的**: 不変性項 + RDMReg の和. 不変性項は 2 つのビュー間の整流特徴の l2 距離 E[||z - z'||_2^2], RDMReg は N 本のランダム射影について sliced 2-Wasserstein 距離 (1/B)||sort(Z c_i) - sort(Y c_i)||_2^2 の期待値. 重みは lambda_sim = 25.0, lambda_dist = 125.0. 射影数は 8192.
- **データセット**: ImageNet-100 で事前学習 (100 クラス). CIFAR-100 でもアブレーション実験を実施. 転移評価は DTD, CIFAR-10, CIFAR-100, Flowers-102, Food-101, Oxford-IIIT Pets の 6 データセット. 1-shot, 10-shot, all-shot の 3 設定.

訓練詳細 (Appendix L): ResNet-50 エンコーダ + 3 層 MLP プロジェクタ (隠れ層・出力次元 2048). LARS オプティマイザ, 1000 エポック, バッチサイズ 128, エンコーダ学習率 0.0825, ウォームアップ 10 エポック + コサインスケジュール, 重み減衰 10^{-4}. 単一 NVIDIA L40S GPU で約 2 日 7 時間.

### どのように検証したか? 指標と結果は?

線形プローブ精度 (Acc1) と l0 / l1 スパース性指標を同時に報告.

ImageNet-100 (Table 1): Rectified LpJEPA RGN_{2.0}(0, sigma_GN) はエンコーダ精度 85.08%, l0 スパース性 0.7298 を達成. LeJEPA のエンコーダ精度 84.80% と同等以上で, LeJEPA の l0 スパース性 1.0000 (完全密) に対し大幅にスパースな表現を学習. RGN_{2.0}(1.0, sigma_GN) では l0 スパース性 0.8668 (約 87% 非ゼロ) でエンコーダ精度 85.08% を維持.

スパース性と精度のトレードオフ (Figure 3c): エントリの約 95% がゼロになるまで精度低下が緩やか. それ以降に崖状の性能劣化が生じる.

HSIC (Figure 4b): Rectified LpJEPA は VICReg や NVICReg より低い正規化 HSIC を達成し, 二次以上の統計的依存性がより効果的に除去されていることを示した.

制御可能なスパース性 (Figure 3b): mu と p を変化させたとき, 経験的 l0 ノルムが Proposition 3.5 の理論予測と良好に一致.

転移評価 (Tables 3-8): 6 データセット, 3 ラベル設定で LeJEPA や VICReg と競争力のある精度を達成.

### 検証結果に基づいた議論, 明らかになった課題はあるか?

(Section 6, Conclusion) 著者はスパース性をターゲット分布設計で達成できることを示したと述べ, JEPA 正則化子の基礎研究に新たな道を開くとしている.

(Appendix H) ReLU と RepReLU の選択について, 本研究では ReLU のみ使用しており, 活性化関数の詳細な検討は future work に委ねている.

(Appendix I 末尾) NCL との NMF に関する Gram-共分散行列の双対性について, 詳細な調査を future work としている.

(Section J.5) スパース性指標を分布内/分布外の判別に使えるかについて, 事前学習データセットでは正誤分類の l1 スパース性分布に差が見られるが, 転移タスクでは差が小さく, さらなる調査を future work としている.

著者は大規模データセット (完全な ImageNet-1K 等) でのスケーラビリティや, 画像分類以外のタスクへの適用可能性については明示的に議論していない.

---
## 自身の研究との関連

本論文は我々が研究する LeWM の SIGReg と次元ミスマッチ問題 (固有次元 ~6 vs 潜在次元 192) に対して最も直接的な解決策を提供しうる. SIGReg が強制する等方 Gaussian ターゲットは全次元を等しく使わせるため, 固有次元が低いタスクでは潜在空間の大部分が情報を持たないノイズ次元に占有される. RDMReg は RGG 分布のパラメータ mu を負方向にシフトすることで, l0 スパース性を制御的に高め, 少数の非ゼロ次元に情報を集約できる. これは固有次元と実効的に使用される次元を近づける方向に作用する.

ただし, 本論文は静的画像の自己教師あり学習でのみ検証されており, ワールドモデルのような時系列予測タスクでの有効性は未検証である. ワールドモデルでは表現のスパース性が予測精度にどう影響するか, また RGG ターゲットの mu, sigma, p をどう設定すべきかが追加の研究課題となる. 同じ研究グループ (Balestriero, LeCun ら) からの研究であり ([[papers/Klindt-arXiv2026-When_LeJEPA_Learn/when-does-lejepa-learn-a-world-model|Klindt+ 2026]] も同系統), SIGReg の後継正則化子として最も有力な候補である.

---
## 追加議論


---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@article{kuang2026rectified,
  title={Rectified {LpJEPA}: Joint-Embedding Predictive Architectures with Sparse and Maximum-Entropy Representations},
  author={Kuang, Yilun and Dagade, Yash and Rudner, Tim G. J. and Balestriero, Randall and LeCun, Yann},
  journal={arXiv preprint arXiv:2602.01456},
  year={2026}
}
```
</details>
