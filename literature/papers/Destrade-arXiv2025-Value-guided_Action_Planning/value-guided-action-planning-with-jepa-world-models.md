---
Title: "Value-guided Action Planning with JEPA World Models"
Authors:
  - Destrade, Matthieu
  - Bounou, Oumayma
  - Le Lidec, Quentin
  - Ponce, Jean
  - LeCun, Yann
Year: 2025
Venue: arXiv
Tags:
  - "jepa"
  - "world-models"
  - "latent-planning"
  - "value-function"
  - "quasimetric-learning"
  - "model-predictive-control"
PDF: "[[papers/Destrade-arXiv2025-Value-guided_Action_Planning/main.pdf|📃]]"
Import Date: "2026-06-08"
Read Date: 2026-06-08
Executive Summary: "JEPA ワールドモデルの潜在空間を, ゴール条件付き価値関数の負値がユークリッド距離 (または準距離) で近似されるように整形し, MPPI ベースの MPC 計画を改善. Implicit Q-Learning (IQL) 損失で状態 encoder を訓練し, 準距離 (quasimetric) を用いた変種が最も高い計画精度を達成. 壁環境・迷路環境で標準 JEPA (VCReg/EMA) を一貫して上回るが, 遠距離状態間の価値推定精度やデータセット品質への依存が課題として残る."
Citekey: Destrade-arXiv2025-Value-guided_Action_Planning
BibTeX Key: destrade2025value
DOI:
Relevance: 4
Repository: "none"
Category: note
Template Version: v2.3
---

## Executive Summary

JEPA ワールドモデルの潜在空間を, ゴール条件付き価値関数の負値がユークリッド距離 (または準距離) で近似されるように整形し, MPPI ベースの MPC 計画を改善. Implicit Q-Learning (IQL) 損失で状態 encoder を訓練し, 準距離 (quasimetric) を用いた変種が最も高い計画精度を達成. 壁環境・迷路環境で標準 JEPA (VCReg/EMA) を一貫して上回るが, 遠距離状態間の価値推定精度やデータセット品質への依存が課題として残る.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

JEPA ワールドモデルにおける行動計画の限界を改善する方法を提示した (§1). 標準的な JEPA では, 予測表現とゴール表現のユークリッド距離を計画コストとして最小化するが, この距離は環境構造 (壁や障害物) を反映しないため局所最適に陥りやすい. 本研究は, 潜在空間の距離がゴール到達コストに対応するゴール条件付き価値関数を近似するよう表現を学習することで, この問題に対処した.

### 提案手法のアプローチと, その根幹をなす要素は何か?

状態 encoder の潜在空間において, 2 状態間のユークリッド距離 (または準距離) の負値がゴール条件付き価値関数 $V^{\star}$ を近似するように encoder を訓練する. 推論時にはこの距離を計画コストとして MPPI オプティマイザによる MPC で行動列を最適化する (§3).

- **IQL 損失 $L_{VF}$**: ゴール条件付き価値関数 $V_\theta(s,g) = -\|E_\theta(s) - E_\theta(g)\|_2$ を, 到達コスト $C(s,a,g) = \mathbf{1}_{s \neq g}$ に対する Implicit Q-Learning (expectile regression) で学習 (式 1). 割引率 $\gamma$ と expectile パラメータ $\tau$ で制御
- **準距離 (quasimetric) 変種**: 価値関数が一般に非対称であることを考慮し, ユークリッド距離を Wang & Isola (2022) の汎用準距離に置換. 表現力が向上し, 対称な価値関数を持つ環境でも性能が改善
- **分離訓練 (Sep) と統合訓練**: encoder を $L_{VF}$ のみで先に訓練した後に predictor を $L_{pred}$ で訓練する Sep 方式と, 両損失を同時に最適化する統合方式を検討. Sep 方式が一般に優位

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

主要な先行研究は以下の通り.

- **Park et al. (2024b)** (Foundation Policies with Hilbert Representations): ユークリッド距離がゴール条件付き価値関数の負値を近似する表現空間を学習し, 強化学習タスクに適用. 本研究はこのアイデアを JEPA ワールドモデル + MPC 計画に転用した点が新規
- **Wang et al. (2023)** (Quasimetric Learning): 非対称な価値関数を準距離で学習. 本研究はこれを JEPA の表現空間に統合
- **Sobal et al. (2025)**: JEPA を行動計画に適用した先行研究. VCReg や予測損失で表現を学習し MPC で計画. 本研究のベースラインの一つ
- **[[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/leworldmodel-stable-end-to-end-joint-embedding-predictive-architecture-from-pixels|Maes+ 2026]]**: JEPA の表現崩壊を SIGReg 正則化で解決し CEM ベース MPC で計画. 本研究は正則化ではなく価値関数による潜在空間整形というアプローチで計画性能を改善

新規性は, 強化学習で確立された価値関数近似表現 (Hilbert representations / quasimetric learning) を JEPA ワールドモデルの MPC 計画に初めて適用した点にある (§3).

### どのように訓練・最適化したのか?

- **損失関数 / 最適化目的**: IQL 損失 $L_{VF}$ (式 1) を状態 encoder に適用. expectile regression $L^2_\tau(x) = |\tau - \mathbf{1}_{x<0}| \cdot x^2$ を用い, 到達コスト $C(s,a,g) = \mathbf{1}_{s \neq g}$ に対するゴール条件付き価値関数を学習. Predictor は標準的な予測損失 $L_{pred}$ で訓練. VCReg ベースラインでは $L_{VCReg}$ (分散・共分散・不変性の 3 項正則化) を使用. ハイパーパラメータは $\gamma = 0.98, \tau = 0.80$ (VF 系) および $\gamma = 0.93, \tau = 0.60$ (VF quasi 系) で, WS データセットでグリッドサーチにより最適化 (§7.3)
- **データセット**: 2 つの環境で生成したオフラインデータセット. (1) 壁環境 (Wall): 64×64 の 2 チャネル画像, 1000 軌道×長さ 64. 行動ノルム小 (WS: 平均 1 px) と大 (WB: 平均 2 px) の 2 設定. (2) 迷路環境 (Maze): MuJoCo PointMaze ベース, 4×4 グリッド, 64×64 の 3 チャネルカラー画像, 1000 軌道×長さ 101. 訓練と評価で異なる迷路レイアウトを使用 (§7.1)

### どのように検証したか? 指標と結果は?

計画精度 (ランダムな初期状態–ゴール対に対する成功率) を指標とし, 壁環境は 200 インスタンス, 迷路環境は 80 インスタンスで評価 (§4.2). MPPI オプティマイザによる MPC で計画を実行.

主要結果 (Table 2):
- **WB (壁, 大行動ノルム)**: VF quasi が 0.96 で最高. VF が 0.94, pred VCReg が 0.89. EMA は 0.43 と低迷
- **WS (壁, 小行動ノルム)**: VF quasi が 0.71 で最高. VF が 0.63. 他の手法は 0.46–0.55
- **Maze**: VF quasi が 0.63 で最高. pred VCReg が 0.54, VF が 0.49. 迷路では全体的に精度が低い

IQL ベースの手法, 特に準距離を用いた VF quasi が全環境で最良. 予測損失と IQL 損失の同時学習 (VF pred) は IQL 単独より劣化. VCReg との併用 (VF VCReg) も性能低下を招いた.

### 検証結果に基づいた議論, 明らかになった課題はあるか?

(§5 Discussion) 著者は 2 つの主要課題を明示的に述べている:

1. **訓練の局所性**: 遠距離の状態–ゴール対は訓練データで疎にサンプリングされ, かつ割引価値関数の勾配がゴールから遠い状態で小さくなるため, 信号対雑音比が低下する. 階層的な表現空間の導入が改善策として示唆されている
2. **データセットの影響**: 理論的には $\tau \to 1$ で訓練データの方策の台のみが重要だが, 実際には大幅に非最適な軌道では近接状態が遠くに見え, 学習を困難にする."エキスパート" 軌道の使用が望ましいが, 多様性と探索のコストがある. 状態空間全体を網羅するデータ収集戦略が重要

(§6 Conclusion) 確率的環境への拡張について, 予測ベース手法は確率的環境でより頑健な表現を学習できる可能性がある一方, IQL アプローチは確率的環境でバイアスを持つことが知られていると述べている.

---
## 自身の研究との関連

本研究は LeWM の計画能力を調査する我々の研究と直接的に関連する. LeWM は CEM ベースの MPC で計画を行うが, 本論文は潜在空間の距離構造自体を価値関数で整形するという代替アプローチを提案しており, 以下の点で相補的である.

- **計画オプティマイザの比較**: LeWM は CEM を使用するのに対し, 本論文は MPPI を採用. 潜在空間が価値関数を反映する構造を持つ場合, MPPI の勾配情報を活用した探索が CEM のサンプリングベース探索より有利になり得る
- **潜在空間の幾何学的構造**: LeWM の SIGReg は等方ガウス分布への正則化であり, 距離構造に直接的な意味を持たせていない. 本論文の quasimetric learning による距離整形は, 潜在空間に到達可能性の情報を埋め込む点で異なる設計思想. LeWM の表現空間にこの距離整形を追加適用できるかは検討に値する
- **スケーラビリティの課題**: 本論文の手法は壁・迷路という単純な 2D 環境のみで検証されており, LeWM が扱う 3D 制御タスクへのスケーラビリティは未知. 遠距離状態間の価値推定精度の問題は, 高次元タスクでさらに深刻化する可能性がある

---
## 追加議論


---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@article{destrade2025value,
  title={Value-guided Action Planning with {JEPA} World Models},
  author={Destrade, Matthieu and Bounou, Oumayma and Le Lidec, Quentin and Ponce, Jean and LeCun, Yann},
  journal={arXiv preprint arXiv:2601.00844},
  year={2025}
}
```
</details>
