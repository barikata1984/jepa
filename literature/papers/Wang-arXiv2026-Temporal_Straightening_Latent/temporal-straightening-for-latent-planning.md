---
Title: "Temporal Straightening for Latent Planning"
Authors:
  - Wang, Ying
  - Bounou, Oumayma
  - Zhou, Gaoyue
  - Balestriero, Randall
  - Rudner, Tim G. J.
  - LeCun, Yann
  - Ren, Mengye
Year: 2026
Venue: arXiv
Tags:
  - "latent-planning"
  - "world-models"
  - "representation-learning"
  - "temporal-straightening"
  - "gradient-based-planning"
PDF: "[[papers/Wang-arXiv2026-Temporal_Straightening_Latent/main.pdf|📃]]"
Import Date: "2026-06-08"
Read Date: 2026-06-08
Executive Summary: "潜在世界モデルにおけるプランニングの困難さに対し, 人間の視覚系における perceptual straightening 仮説に着想を得た曲率正則化を提案する. エンコーダと予測器を同時学習する際に, 連続する潜在速度ベクトル間のコサイン類似度を最大化する損失項を加えることで, 潜在軌道を直線化する. これにより潜在空間のユークリッド距離が測地距離の良い近似となり, 勾配ベースプランニングのヘシアンの条件数が改善される. 2D ゴール到達タスク群でオープンループ成功率が 20–60%, MPC で 20–30% 向上する一方, 評価は比較的単純な環境に限定されている."
Citekey: Wang-arXiv2026-Temporal_Straightening_Latent
BibTeX Key: wang2026temporal
DOI: ""
Relevance: 3
Repository: "https://agenticlearning.ai/temporal-straightening"
Category: note
Template Version: v2.3
---

## Executive Summary
潜在世界モデルにおけるプランニングの困難さに対し, 人間の視覚系における perceptual straightening 仮説に着想を得た曲率正則化を提案する. エンコーダと予測器を同時学習する際に, 連続する潜在速度ベクトル間のコサイン類似度を最大化する損失項を加えることで, 潜在軌道を直線化する. これにより潜在空間のユークリッド距離が測地距離の良い近似となり, 勾配ベースプランニングのヘシアンの条件数が改善される. 2D ゴール到達タスク群でオープンループ成功率が 20–60%, MPC で 20–30% 向上する一方, 評価は比較的単純な環境に限定されている.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

潜在世界モデルで勾配ベースのプランニングを行う際, 潜在軌道が高い曲率をもつために (1) ユークリッド距離が測地距離を正しく反映せず誤った計画コストとなる問題と, (2) 計画目的関数が非凸化し勾配降下法が局所解に陥りやすい問題を解決した. (§1 Introduction)

### 提案手法のアプローチと, その根幹をなす要素は何か?

JEPA 型の世界モデルを訓練する際に, 潜在軌道の局所的な曲率を正則化することで表現空間を計画に適した幾何にする. 感覚エンコーダ・アクションエンコーダ・予測器を同時学習し, 予測損失と曲率損失の合計を最小化する.

- **曲率正則化 (Lcurv)**: 連続する 3 フレームの潜在表現から速度ベクトル vt = zt+1 - zt を計算し, 隣接速度間のコサイン類似度 C を最大化する損失 Lcurv = 1 - C を課す (Eq. 4, 6)
- **予測損失 (Lpred)**: 予測された潜在状態と目標潜在状態の MSE を stop-gradient 付きで最小化する (Eq. 5). stop-gradient が崩壊防止を兼ねる
- **学習可能な pooling head**: 空間特徴に対して学習可能な集約ヘッドでコサイン類似度を計算することで, パッチレベルの局所的変動に影響されずグローバルな軌道直線化を実現する (§5.1, §B.5)

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

主要な先行研究として, (1) DINO-WM ([[papers/Klindt-arXiv2026-When_LeJEPA_Learn/when-does-lejepa-learn-a-world-model|Klindt+ 2026]] でも議論される DINOv2 凍結特徴上の世界モデル, Zhou et al. 2025) をベースラインとし, (2) perceptual straightening 仮説 (Henaff et al., 2019) を計画に応用する着想を得ている. また [[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics|Balestriero & LeCun 2025]] の LeJEPA を崩壊防止手法の文脈で参照している.

新規性は, (1) 時間的直線化を潜在プランニングの改善に初めて適用した点, (2) 線形力学系において曲率低減がプランニングヘシアンの条件数を指数的に改善することを理論的に証明した点 (Theorem 4.4), (3) 対照学習のような負例を必要とせず, 局所的な正則化のみで表現幾何を改善できる点である. (§2 Related Work)

### どのように訓練・最適化したのか?

- **損失関数 / 最適化目的**: Ltotal = Lpred + λ Lcurv. Lpred = ||ẑt+1 - sg(zt+1)||² (MSE with stop-gradient), Lcurv = 1 - C (コサイン類似度の負値). λ は 0.001–0.1 の範囲で調整, 最良値は λ = 0.1 (pooling head 使用時) (Eq. 7, §B.5)
- **データセット**: Wall (1,920 軌道, 各 50 ステップ), PointMaze-UMaze (2,000 軌道, 各 100 ステップ), PointMaze-Medium (4,000 軌道, 各 100 ステップ), PushT (18,500 軌道, 各 100–300 ステップ). いずれもシミュレータからランダムに収集した非エキスパートデータ. エポック数は Wall・PointMaze が 20, PushT が 2. (§A.1–A.3, Table 4)

### どのように検証したか? 指標と結果は?

4 環境 (Wall, PointMaze-UMaze, PointMaze-Medium, PushT) で, 50 テストサンプルに対するゴール到達成功率 (3 シード平均 ± 標準偏差) を報告. ベースラインは凍結 DINOv2 特徴を用いる DINO-WM. プランナーは勾配降下法 (GD) を使用し, オープンループとクローズドループ (MPC) の両方で評価.

主要結果 (Table 1, DINOv2 patch + 空間プロジェクタ, 14x14x8):
- Wall: オープンループ 80.0% → 90.7% (Lcurv あり), MPC 90.7% → 100%
- UMaze: オープンループ 44.0% → 94.0%, MPC 81.3% → 100%
- Medium: オープンループ 72.0% → 82.7%, MPC 96.7% → 98.7%
- PushT: オープンループ 70.0% → 77.3%, MPC 78.7% → 85.3%

GD と CEM の比較 (Table 3) では, 直線化により GD と CEM の性能差が大幅に縮小し, 一部設定では GD が CEM を上回った. 長ホライズン (50 ステップ) 設定 (Table 2) でも一貫した改善を確認. Teleported-PointMaze では, 視覚的類似性ではなく時間的ダイナミクスを捉えていることを検証.

### 検証結果に基づいた議論, 明らかになった課題はあるか?

(§6 Conclusion) 著者はこの手法がより豊かで困難な環境への適用を今後の方向として挙げている.

(§4, Theorem 4.4 後の議論) 非線形予測器に対する理論的保証の拡張 (状態依存ヤコビアンの制御) が今後の課題として言及されている.

(§5.3, Table 2 付近) 長ホライズンロールアウトでは予測誤差が蓄積し軌道がドリフトする問題が残ることを認めている. 失敗事例ではデコードされたロールアウトがぼやけたりシミュレータと不整合になる.

(§A.2) UMaze と Medium-Maze のみで実験しており, 他の迷路レイアウトは今後テスト予定と述べている.

---
## 自身の研究との関連

LeWM の研究において CEM に代わる勾配ベースプランニングを模索している我々にとって, 本論文の曲率正則化は直接的に関連する. 特に以下の点が有用:

- **勾配ベースプランニングの安定化**: Lcurv の追加のみで GD プランナーの成功率が 20–60% 向上し, CEM との性能差を大幅に縮小できることが示された. LeWM に同様の正則化を導入すれば, CEM の計算コストを回避しつつ計画性能を維持できる可能性がある
- **理論的裏付け**: ε-straight 遷移がプランニングヘシアンの条件数を κ(B)² e^(6εK) に抑えるという定理 (Theorem 4.4) は, 表現空間の幾何が計画の収束に直結するという主張に対する定量的根拠を与える
- **LeWM との差分**: 本論文は [[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/leworldmodel-stable-end-to-end-joint-embedding-predictive-architecture-from-pixels|Maes+ 2026]] の LeWM とは異なり, DINOv2 凍結特徴上の軽量プロジェクタまたはスクラッチ ResNet を使用する. LeWM のエンドツーエンド JEPA フレームワークに曲率正則化を組み込む際には, エンコーダの学習自由度が異なるため, λ の調整や崩壊防止との相互作用に注意が必要

制約として, 評価が 2D の比較的単純なタスクに限られており, ロボットマニピュレーション等のより複雑なタスクへの適用可能性は未検証である.

---
## 追加議論


---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@article{wang2026temporal,
  title={Temporal Straightening for Latent Planning},
  author={Wang, Ying and Bounou, Oumayma and Zhou, Gaoyue and Balestriero, Randall and Rudner, Tim G. J. and LeCun, Yann and Ren, Mengye},
  journal={arXiv preprint arXiv:2603.12231},
  year={2026}
}
```
</details>
