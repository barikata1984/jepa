---
Title: "LeWorldModel: Stable End-to-End Joint-Embedding Predictive Architecture from Pixels"
Authors:
  - Maes, Lucas
  - Le Lidec, Quentin
  - Scieur, Damien
  - LeCun, Yann
  - Balestriero, Randall
Year: 2026
Venue: arXiv
Tags:
  - "world-models"
  - "jepa"
  - "representation-learning"
  - "latent-planning"
  - "anti-collapse"
  - "model-predictive-control"
PDF: "[[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/main.pdf|📃]]"
Import Date: "2026-06-04"
Read Date: 2026-06-04
Executive Summary: "JEPA の表現崩壊問題を, 予測損失と SIGReg (Cramér–Wold 定理に基づく等方ガウス正則化) の 2 項損失のみで解決し, 生画素からのエンドツーエンド安定学習を実現. ~15M パラメータ, 単一 GPU で数時間の学習で, 基盤モデルベース手法より最大 48 倍高速な計画を達成しつつ, 2D/3D 制御タスクで競合的性能を維持. 潜在空間は物理量を符号化し, 物理的に非妥当な事象の検出も可能."
Citekey: Maes-arXiv2026-LeWorldModel_Stable_End-to-End
BibTeX Key: maes2026leworldmodel
DOI:
Relevance: 4
Repository: "https://github.com/lucas-maes/le-wm"
Category: note
Template Version: v2.3
---

## Executive Summary

JEPA の表現崩壊問題を, 予測損失と SIGReg (Cramér–Wold 定理に基づく等方ガウス正則化) の 2 項損失のみで解決し, 生画素からのエンドツーエンド安定学習を実現. ~15M パラメータ, 単一 GPU で数時間の学習で, 基盤モデルベース手法より最大 48 倍高速な計画を達成しつつ, 2D/3D 制御タスクで競合的性能を維持. 潜在空間は物理量を符号化し, 物理的に非妥当な事象の検出も可能.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

JEPA (Joint-Embedding Predictive Architecture) を生画素からエンドツーエンドで安定的に学習する方法を提示した (§1). 既存の JEPA は表現崩壊 — encoder が全入力をほぼ同一の表現に写像し, 予測目的を自明に満たすが無意味な表現を生む — に脆弱であり, これを回避するために EMA (指数移動平均), stop-gradient, 事前学習済み encoder, 多項損失関数などのヒューリスティクスに依存していた. LeWM はこれらのヒューリスティクスを一切使わず, 2 項損失のみで安定学習を実現する.

### 提案手法のアプローチと, その根幹をなす要素は何か?

画像観測を encoder でコンパクトな潜在表現に写像し, predictor が行動条件付きで次ステップの潜在状態を自己回帰的に予測する. 学習は完全にエンドツーエンドで, 2 項損失のみを最適化する. 推論時は Cross-Entropy Method (CEM) による MPC で潜在空間上の軌道最適化を行う (§3.2).

- **予測損失 Lpred**: 予測された次ステップ埋め込み ẑ_{t+1} と実際の次ステップ埋め込み z_{t+1} の MSE (式 1)
- **SIGReg 正則化**: 潜在埋め込みを M 個のランダムな単位方向に射影し, 各 1 次元射影に対して Epps–Pulley 正規性検定統計量を最適化. Cramér–Wold 定理により, 全 1 次元周辺分布の一致が同時分布の一致を保証するため, 等方ガウス分布への収束が理論的に保証される (式 2, Appendix A)
- **エンドツーエンド学習**: stop-gradient, EMA, 事前学習済み encoder を使わず, encoder (ViT-Tiny, ~5M パラメータ) と predictor (Transformer, ~10M パラメータ) の全パラメータを統合的に最適化

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

主な比較対象 (§2, Fig. 2):

- **PLDM** [21, 22]: VICReg ベースの 7 項損失でエンドツーエンド JEPA を学習. 学習不安定性と 6 個のハイパラチューニング (O(n^6) の探索) が課題
- **DINO-WM** [18]: DINOv2 事前学習済み encoder を凍結して崩壊を回避. エンドツーエンド学習を放棄し, 表現力が事前学習知識に制約される
- **Dreamer** [27–29, 4] / **TD-MPC** [31, 32]: タスク固有の報酬信号や特権的状態アクセスが必要
- **SIGReg / LeJEPA** [25]: 本手法の崩壊防止正則化の直接的な基盤

LeWM の新規性:

1. エンドツーエンド JEPA としてチューナブルなハイパラを 6 個から 1 個 (λ) に削減. 二分探索で O(log n) のチューニングが可能
2. SIGReg による証明可能な崩壊防止保証 (Cramér–Wold 定理)
3. タスク非依存・報酬不要・再構成不要でありながら, 基盤モデルベース手法と競合的な性能

### どのように訓練・最適化したのか?

- **損失関数**: L_LeWM = Lpred + λ · SIGReg(Z) (式 3). 既定値: λ = 0.1, M = 1024 射影
- **データセット**:
  - TwoRoom: 10,000 エピソード, 平均 92 ステップ, ノイズ付きヒューリスティクスポリシーで収集
  - PushT: 20,000 エキスパートエピソード, 平均 196 ステップ (DINO-WM [18] と同一データ)
  - OGBench-Cube: 10,000 エピソード, 各 200 ステップ, ベンチマークライブラリのヒューリスティクスで収集
  - Reacher: 10,000 エピソード, 各 200 ステップ, SAC ポリシーで収集
- 全環境で 10 エポック学習. フレームスキップ 5, バッチサイズ 128, サブ軌跡長 4, 解像度 224×224
- 単一 NVIDIA L40S GPU で学習・計画を実行 (App. D)
- フレームワーク: stable-worldmodel [50] / stable-pretraining [49] / PyTorch [51] / Gymnasium [52]

### どのように検証したか? 指標と結果は?

**ベースライン**: DINO-WM, PLDM, GCBC, GCIQL, GCIVL, Random. 全手法でハイパラは環境間で固定 (§4.1).

**メトリクス**: 成功率 (Success Rate), 計画時間. 各 50 軌跡で評価.

**主要結果** (Fig. 6):

| 環境 | LeWM | DINO-WM | PLDM |
|---|---|---|---|
| PushT | **96** | 92 | 78 |
| Reacher | **87** | 86 | 79 |
| OGBench-Cube | 74 | **84** | 65 |
| TwoRoom | 79 | **~87** | **~86** |

- PushT で PLDM に対し +18% (§4.2). DINO-WM は固有受容情報なし (§4.1 のデフォルト) で 92.0 (Tab. 5) だが, 固有受容情報を追加しても LeWM (画素のみ, 96.0) を下回る (§4.2)
- Reacher, TwoRoom の数値は Fig. 6 棒グラフからの読み取り (概算)
- 計画速度 (Fig. 3): DINO-WM ~47 秒 に対し LeWM ~0.98 秒 → **最大 48 倍高速**
- 学習安定性 (Tab. 5, PushT 3 シード): LeWM 96.0 ± 2.83, PLDM 78.0 ± 5.0, DINO-WM 92.0 ± 1.63
- 物理量プロービング (Tab. 1, PushT): 線形プローブでエージェント位置 MSE — LeWM: 0.052, PLDM: 0.090, DINO-WM: 1.888. MLP プローブでは DINO-WM と同等水準
- VoE 評価 (Fig. 10): 物理的摂動 (テレポーテーション) に対し全 3 環境で有意なサプライズスパイク (paired t-test, p < 0.01). 色変更 (視覚的摂動) への反応は弱く有意でない

**アブレーション** (App. G): SIGReg の射影数・積分ノット数は性能にほぼ影響なし. λ ∈ [0.01, 0.2] で成功率 80% 以上を維持 (Fig. 16). ViT と ResNet-18 の両方で競合的性能 (Tab. 8). Predictor のドロップアウト 0.1 が最良 (Tab. 9).

### 検証結果に基づいた議論, 明らかになった課題はあるか?

(§6 Limitations & Future Work より)

1. 現在の潜在ワールドモデルでの計画は**短いホライゾンに制限**される. 階層的ワールドモデリングが長期的推論と計画に有望な方向として挙げられている
2. **十分なインタラクションカバレッジのあるオフラインデータセットへの依存**. データ多様性の制限は, 特に低固有次元環境 (TwoRoom) で SIGReg の有効性に影響する — 高次元潜在空間で等方ガウス事前分布を満たすことが困難になる
3. **大規模自然動画データセットでの事前学習**が表現プライアの獲得とドメイン固有データへの依存低減に有望
4. 現在のエンドツーエンド潜在ワールドモデルは**行動ラベルに依存**. 逆ダイナミクスモデリングによる行動表現の学習が, 明示的な行動アノテーションへの依存を低減する方向として提示されている

---
## 自身の研究との関連

JEPA ベースのワールドモデルにおける表現崩壊問題に対する実用的な解決策を提示しており, JEPA フレームワークの実装指針として直接参考になる. SIGReg による潜在空間正則化手法は, 類似の埋め込み学習問題への応用可能性がある. ~15M パラメータ・単一 GPU で学習可能な軽量設計は, 計算資源が限られた環境での再現・拡張実験に利点. stable-worldmodel フレームワークとの組み合わせにより, 実験の再現性と比較可能性も担保されている.

---
## 追加議論

### SIGReg は LeJEPA ありきの設計

LeWM の SIGReg は LeJEPA [25] で確立された手法の応用. LeWM 論文は SIGReg を"導入"ではなく"採用 (adopt)"しており, 理論的正当化は LeJEPA への参照で済ませている. LeWM の貢献は SIGReg 自体ではなく, それを行動条件付き潜在予測 + MPC 計画と組み合わせてエンドツーエンド JEPA ワールドモデルとして機能させた点にある.

### Temporal straightening は MSE の副産物か

SIGReg をステップワイズに適用し, 時間方向の構造は predictor の予測損失 (MSE) に委ねる設計. Temporal straightening の創発 (App. H, Fig. 17) は著者が強調するが, 隣接速度ベクトル間のコサイン類似度で測定しており, 1 ステップ MSE が最短距離方向の予測を促す副産物として説明できる範囲. NN の simplicity bias とも整合. 複数ステップにまたがるグローバルな直線性 (v_1 と v_T の collinearity) は検証されていない.

### 固有次元と SIGReg のミスマッチ — 実機での懸念

TwoRoom での性能低下 (§4.2) は, データの固有次元 (~2) と潜在空間 (192 次元) のミスマッチに起因する. SIGReg が全方向を等方ガウスにしようとするが, 意味のある変動が 2 次元分しかないため残り 190 次元にノイズを詰めるしかなく, 表現の質が落ちる. 実機の固定セットアップ (固定カメラ, 固定背景, 限られた物体セット) は視覚的多様性が低く, 同様の問題が起きうる. 固有次元は事前にわからないため, 環境ごとに潜在次元を合わせるのはタスク非依存の設計方針に反する — この構造的なジレンマは未解決.

### 推論速度

計画時間 ~0.98 秒 (CEM 300 候補 × 30 反復) で実効 ~5 Hz. 準静的な操作 (5–20 Hz) にはぎりぎり, 動的操作 (50–100 Hz) には不足. ただし CEM のパラメータ削減や非同期パイプライン化で工学的に改善可能な範囲であり, 研究上の本質的な穴ではない.

---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@article{maes2026leworldmodel,
  title={LeWorldModel: Stable End-to-End Joint-Embedding Predictive Architecture from Pixels},
  author={Maes, Lucas and Le Lidec, Quentin and Scieur, Damien and LeCun, Yann and Balestriero, Randall},
  journal={arXiv preprint arXiv:2603.19312},
  year={2026}
}
```
</details>
