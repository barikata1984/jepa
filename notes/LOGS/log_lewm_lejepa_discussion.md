# LeJEPA / LeWM 議論ログ

日付: 2026-06-04

## LeJEPA と LeWM の関係

- LeJEPA (Balestriero & LeCun, 2025) が SIGReg を理論的に確立 → LeWM (Maes+, 2026) がそれをワールドモデルに持ち込んだ, という時系列
- LeWM は SIGReg を"導入"ではなく"採用 (adopt)"しており, 理論的正当化は LeJEPA への参照で済ませている
- LeJEPA では"下流タスク非依存の最適分布"という動機, LeWM では"表現崩壊の回避"という動機. 異なるベクトルから同じ正則化に到達したように見えるが, 実際は SIGReg ありきで LeWM を設計した可能性が高い (著者の重なり, 時系列, 論文の書き方から)

## エンコーダの行動非依存性と表現品質 (V-JEPA 2 × LeJEPA × LeWM)

- V-JEPA 2 のエンコーダは行動なしのインターネット動画のみで学習しており, 行動の概念を一切知らない. にもかかわらず,"Reconstruction or Semantics?" (Nilaksh+, 2026) の BridgeV2 評価では V-JEPA 2.1 の表現が行動復元性 (IDM Pearson r) で最高スコアを記録した
- これは LeJEPA の理論的主張 ("下流タスク非依存で最適な表現分布は等方ガウス") と呼応する: 十分に良い汎用表現があれば, 行動条件付けはエンコーダ側には不要で, predictor 側だけで済む可能性がある
- LeWM はエンコーダを行動条件付き予測とエンドツーエンドで学習する設計. エンコーダ側に行動情報を組み込む意義が, V-JEPA 2 の結果から問われる
- ただし V-JEPA 2 は 1B パラメータ + 100万時間の動画という圧倒的なスケールの上での結果. LeWM の 15M パラメータ・タスクデータのみの条件で同じことが成り立つかは別問題

日付: 2026-06-05

## Temporal straightening について

- LeWM では SIGReg をステップワイズに適用 (時刻ごとに独立), 時間方向の構造は predictor の予測損失に委ねる
- Temporal straightening (潜在軌跡の直線化) が明示的な正則化なしに創発 (App. H, Fig. 17)
- ただし隣接速度ベクトル間のコサイン類似度で測っているため, 1 ステップ MSE の副産物として説明可能な範囲. NN の simplicity bias とも整合. グローバルな直線性 (v_1 と v_T の collinearity) は検証されていない

## 実機ロボットでの研究方向の検討

### 話題に上がったテーマ一覧

1. **実機データでの学習効率 / SIGReg の低データ多様性問題** ← 最も検討を進めた
2. **触覚・マルチモーダル JEPA ワールドモデル**
3. **サプライズ駆動の能動データ収集**
4. **推論速度の改善**

### 1. 実機データでの学習効率 / SIGReg の低データ多様性問題

#### 論文中の既知の穴

LeWM §6 および実験結果から, 実機で問題になりうる点:

- **固有次元ミスマッチで SIGReg が劣化 (TwoRoom 問題)**: データの固有次元が潜在空間の次元より大幅に低いとき, 等方ガウス正則化が余剰次元にノイズを詰めて表現の質が落ちる. 実機で再現するかは"固定セットアップだから視覚的多様性が低い"という印象論ではなく, 実機画像多様体の固有次元を実測して判断する必要がある → **最も有望な穴だが, 前提の検証が先**
- **データカバレッジへの依存**:"十分なインタラクションカバレッジ"が前提. 実機データは疎
- **行動ラベルへの依存**: (observation, action) ペアが必須
- **短ホライゾン制約**: H=5 ステップ (フレームスキップ込みで 25 環境ステップ). 実機タスクには不足の可能性
- LeJEPA の **i.i.d. 仮定** (§3): 系列データへの拡張は未議論 (LeWM ではステップワイズ適用で暗黙的に回避)

#### 固有次元と SIGReg のミスマッチの詳細

- TwoRoom の状態は実質 2 次元 (エージェントの x, y 座標) だが, 潜在空間は 192 次元. SIGReg が 192 次元全方向を等方ガウスにしようとするが, 意味のある変動が 2 次元分しかないため, 残り 190 次元にノイズを詰めるしかなく表現の質が落ちる
- 潜在空間を 2 次元にすれば解消するが, encoder が 224×224×3 の画像を 2 次元に圧縮する必要があり極端なボトルネック. アブレーション (Fig. 15) での最小は 8 次元で, 2 次元は未検証
- 固有次元は事前にわからないため, 環境ごとに潜在次元を合わせるのは LeWM のタスク非依存の設計方針に反する — 構造的なジレンマ

#### フレーミングの検討

- "LeWM を実機データで評価しました"だけでは貢献が薄い → "評価 → 問題発見 → 解決策提案"の 3 段構成が必要
- 候補 A: データ効率の構造的優位性の検証
- 候補 B: 事前学習なし vs あり の公平な比較 (LeJEPA の in-domain 優位性のワールドモデル版)
- 候補 C: SIGReg の崩壊保証が実機ノイズ・分布シフトでどこまで有効か
- → いずれも純粋な評価で終わると弱い. まず BridgeV2 等で動かして"どこで壊れるか"を観察し, そこから解決すべき問題と提案手法を決める方が現実的

### 2. 触覚・マルチモーダル JEPA ワールドモデル

実機マニピュレーションでは視覚だけでは把持の成否や接触状態がわからない. GelSight 等の触覚センサを JEPA の追加モダリティとして組み込み, SIGReg をモダリティ間でどう適用するか (独立 vs 融合表現) が設計上の問い. 具体的な検討は未着手.

### 3. サプライズ駆動の能動データ収集

LeWM の VoE フレームワーク (物理的に非妥当な事象の検出) を内発的動機づけとして実機の探索に使う方向. オフラインデータの"十分なカバレッジ"という前提条件を能動的に満たしに行く発想. サプライズの信頼性 (偽陽性) と実機での安全性のバランスが課題. 具体的な検討は未着手.

### 4. 推論速度の改善

- LeWM の計画時間: ~0.98 秒 (CEM 300 候補 × 30 反復). 5 ステップ一括実行で実効 ~5 Hz
- ロボット制御の一般的な要求: 準静的操作で 5–20 Hz, 動的操作で 50–100 Hz 以上
- 速度改善は工学的対応 (サンプル数削減, 非同期化) で可能な範囲. 研究としての穴は浅い
- **結論: テーマ 1 (低データ多様性での SIGReg 劣化) の方が, 理論・実験ともに掘りがいがある**

## 利用可能なリソース

### 実機データセット

- **DROID**: 76K 軌跡, 350h, Franka Panda. V-JEPA 2-AC が JEPA ワールドモデル学習に使用済み
- **BridgeData V2**: 60K 軌跡, WidowX 250. ゴール画像対応. 潜在ワールドモデルの encoder 比較に使用実績あり
- **Open X-Embodiment**: 1M+ 軌跡, 22 種ロボット. 最大規模だが異種混合

### ベースライン

- **V-JEPA 2-AC** (Meta, 2025): 1.2B パラメータ, DROID 62h で post-training, 実機ゼロショット MPC で 65–80% 成功率. LeWM (15M) との規模差が明確な研究上の問いになる

### ツール

- **stable-worldmodel**: LeWM の実装フレームワーク. LeRobot 形式のインポート対応済み

## フレーミング修正: 固有次元ミスマッチと視覚的多様性の混同

日付: 2026-06-05

当初のフレーミングでは"固定セットアップ → 視覚的多様性が低い → 固有次元が低い → TwoRoom と同じ SIGReg ミスマッチが起きる"と論を展開していたが,"視覚的多様性が低い → 固有次元が低い"に根拠のない飛躍がある. 固定セットアップでも, ロボットアームの 7 自由度や物体姿勢の 6 自由度があり, 画像多様体の固有次元が低いとは限らない. 視覚的に似て見えることと, 画像多様体の固有次元が低いことは別の問題.

修正後のフレーミング: 実機で SIGReg ミスマッチが起きるかは印象論ではなく, 画像多様体の固有次元の実測 (Two-NN, PCA 等) に基づいて判断する. TODO・ISSUES ともにこの方針に修正済み.

---

## 2026-06-09: Literature Survey 完了

### multiview-manipulation-learning-on-jepa

- **出力**: `literature/surveys/multiview-manipulation-learning-on-jepa.md`
- **規模**: 50 論文採録, 9 ハブ深読み (既存 3 + 新規 6)
- **新規深読みノート**:
  - `papers/Sun-arXiv2026-VLA-JEPA_Enhancing_VLA/` — VLA-JEPA
  - `papers/Tian-ICLR2025-PIDM_Scalable_Learners/` — PIDM/Seer
  - `papers/Zhang-ICLR2026-DeFI_Disentangled_Robot/` — DeFI
  - `papers/Li-ICLR2026-4D_Latent_World/` — 4D Latent WM
  - `papers/ICLR2025-ReViWo_View-invariant_World/` — ReViWo
  - `papers/Nam-ICML2026-Causal-JEPA_Object-Level/` — Causal-JEPA
- **主要発見**:
  - JEPA alignment × 多視点の組み合わせは未開拓 (Concept Matrix で確認)
  - 順/逆動力学の分離事前学習 (DeFI) が 2026 年の新潮流
  - 意味表現 > 復元表現がロボット制御で一貫 (Nilaksh+ 2026)
- **Seed 3 本**: (1) 多視点 JEPA alignment, (2) L_align + L_fwd + L_inv 統合, (3) 多視点物体レベル JEPA

## 2026-06-09: 研究シード検討 (セッション後半)

### 多視点データセットの調査

使用可能なデータセットを調査し, stable-worldmodel との接続性を評価:

| データセット | カメラ数 | LeRobot 形式 | stable-worldmodel 接続 |
|---|---|---|---|
| **berkeley_autolab_ur5** | **3** (image, image_with_depth, hand_image) | ✓ ローカル済 | **最小工数** — adapter 拡張のみ |
| **DROID** (`lerobot/droid_100`) | **3** (exterior×2, wrist) | ✓ | 小 — DL + adapter |
| **BridgeV2** | **4** (RGBD + RGB×2 + wrist) | ✓ | 小 |
| **RLBench** | **4** (RGB-D) | ✗ | 中 — 変換必要 |
| RoboMIND UR5e | 1 | ✓ | — 多視点不適 |

重要な発見: berkeley_autolab_ur5 は既に 3 カメラ持っており, パイプライン疎通済み.

### LeRobot の多視点サポート状況

- LeRobot Dataset 層: 多視点サポート済み (`camera_keys` に複数カメラ)
- LeRobot Policy 層 (ACT, DP): 多視点サポート済み (パターン 1: 各カメラ独立エンコード → トークン連結)
- **stable-worldmodel Adapter**: 未対応 (`primary_camera_key` で 1 カメラに絞る)
- **stable-worldmodel World (LeWM)**: 未対応 (`'pixels'` 単一入力前提)
- 改修ポイントは stable-worldmodel 側の 2 箇所のみ

### 既存研究の多視点処理パターン (4 類型)

1. **独立エンコード → 連結** (ACT, PIDM, VLA-JEPA): 最も素朴. ビュー間幾何を明示的に学ばない
2. **ビュー不変/依存分離** (ReViWo, MAD, VILA): 再構成 or 対比損失で分離. 視点ラベル要
3. **3D 中間表現に統合** (4D Latent WM, SPA): キャリブレーション必須, 計算コスト大
4. **マスク予測** (MV-MWM): ピクセル再構成に計算を費やす

提案の Seed 1 はパターン 2 の alignment 版に位置づけ. パターン 3 と比べてキャリブレーション不要.

### Seed の実現可能性・採択可能性評価

- **Seed 1** (多視点 JEPA alignment): 実現可能性 高, 新規性 中, 採択 ICRA/IROS 向き
- **Seed 2** (L_align + L_fwd + L_inv 統合): 実現可能性 中, 新規性 中〜高, **CoRL/RSS が最適 venue**
- **Seed 3** (多視点物体レベル JEPA): 実現可能性 低〜中, 新規性 高, 中長期テーマ
- 推奨: Seed 1 → Seed 2 の段階設計. Seed 2 が最もバランス良い

### モチベーションの整理

説得力のある論拠 (強い順):
1. 遮蔽 — 把持時に手が物体を隠す. 単一カメラの情報理論的限界
2. 復元不要の優位性 — Nilaksh+ 2026 が意味表現 > 復元表現を実証済み
3. キャリブレーション不要 — 3D 復元 (4D Latent WM 等) と比べた実用的優位
4. 計画能力 — ACT の素朴 concat にはない長期ホライズン推論

最大リスク: JEPA alignment のビュー不変表現が復元ベース 3D 表現に勝つ条件の特定

## 2026-06-09: Seed 再評価とフレーミング検討 (セッション最終)

### Seed 2 (L_align + L_fwd + L_inv 統合) の再評価

ID 統合の必要性を既存論文のアブレーションで検証した結果, **ID 統合は強い貢献にならない**と判断:

- PIDM Table 3: L_inv 追加の効果は Avg. Len. +0.23 (+6.7%). Modest.
- DeFI: GIDM 単体 (4.16) > GFDM 単体 (3.28). **GFDM 凍結 + GIDM 更新 (4.51) > 全部更新 (4.40)**. 分離の方が良い.
- DeFI §1 が"2D 映像予測と 3D 行動予測の目標競合"を明示的に問題として報告. 統合の困難さは DeFI 自身が論拠.

結論: Seed 2 は独立論文にはならず, Seed 1 の ablation に吸収される方が自然.

### Seed 1 のフレーミング 3 案

| フレーミング | 理論要求 | 実装工数 | 結果リスク | 最適 venue |
|---|---|---|---|---|
| A. 理論拡張 (識別可能性定理の多視点拡張) | 高 | 低〜中 | 高 | ICML / NeurIPS |
| B. システム (復元不要多視点ワールドモデル) | 低 | 中 | 中 | CoRL / RSS |
| C. 表現学習比較 (多視点での意味 vs 復元) | 低〜中 | 中 | **低** | ICLR / NeurIPS / CoRL |

**推奨**: C (表現学習比較) から着手. Nilaksh+ 2026 の直接的拡張. 結果がどう転んでも知見として報告可能. 実験は A/B にも再利用できる.

### 次のアクション候補

1. stable-worldmodel の LeRobotAdapter を多カメラ対応に拡張
2. berkeley_autolab_ur5 (3 カメラ) で Seed 1 のプロトタイプ実験
3. フレーミング C の実験設計: 単一 JEPA / concat JEPA / alignment JEPA / 復元系の 4 条件比較

## 2026-06-09: Framing C たたき台作成 (セッション 2)

### 研究問いの精緻化

RQ1 を"Nilaksh の結論は多視点に拡張されるか"から"多視点で復元系が逆転しうる条件があるか"に読み替えた. 根拠:
- 復元系はクロスビュー再構成で 3D 幾何を暗黙的に学ぶ (ReViWo の VIR/VDR, 4D Latent WM のボクセル再構成). 多視点では復元系に構造的追い風
- Nilaksh §4.5 自身が"意味系は幾何・接触の精度が落ちる"と失敗モード差を報告. 多視点で幾何情報が増えるとこの弱点が露呈する可能性

3 つの RQ:
1. 多視点で復元系が意味系を逆転しうる条件はあるか
2. 多視点統合方法 (素朴連結 vs JEPA cross-view alignment) がワールドモデル予測・計画にどう影響するか
3. Cross-view alignment は SIGReg の次元ミスマッチ問題を緩和するか

### 5 条件の実験設計

| 条件 | 多視点統合 | 損失 |
|---|---|---|
| A. Single-view JEPA | なし (1 カメラ) | L_pred + SIGReg |
| B. Concat JEPA | 各ビュー独立エンコード → トークン連結 | L_pred + SIGReg (連結後) |
| C. Alignment JEPA | 各ビュー独立エンコード + cross-view alignment | L_pred + L_align + SIGReg (各ビュー) |
| D. Reconstruction (ReViWo) | VIR/VDR 分離 | L_recon + L_contrastive |
| E. Frozen semantic + concat | V-JEPA 2.1 凍結 + adaptor | L_pred のみ |

L_align = 同時刻の異なるカメラからの埋め込み間 MSE の平均 (JEPA alignment 損失をカメラ軸に適用)

### ReViWo 公式実装の発見

- オリジナル: `https://github.com/Trevor-emt/Reviwo` (スター 10, Python, PyTorch + MuJoCo + Metaworld)
- 筆頭著者フォーク: `https://github.com/lafmdp/ReViWo`
- 条件 D の工数見積もり: 3–5 日 → 1–2 日に低減
- ペーパーノートの Repository フィールドを更新済み

### 実装見積もり

合計 ~2–3 週間. 最大ボトルネックは条件 D (ReViWo 移植) だったが, 公式コード発見で緩和.
前提確認が必要: berkeley_autolab_ur5 の 3 カメラ (image, image_with_depth, hand_image) が実質的に異なる視点を持つか

## 2026-06-10: Cross-view 正則化の枠組み調査

### 問題

Cross-view-temporal prediction loss だけではビュー不変性が保証されない. predictor がビュー変換を丸暗記し, エンコーダがビュー依存な表現を出すショートカットが生じる (I-JEPA で predictor が強すぎると起きるのと同じ構造).

### L_align の格上げ検討

- 素朴 MSE (たたき台の L_align) は VICReg の invariance 項と区別がつかない
- Cross-view predictive alignment (predictor を挟む) を検討したが, predictor がビュー変換を吸収してエンコーダがサボる問題は解消しない
- Cross-view-temporal prediction (カメラ 0 の t + 行動 → カメラ 1 の t+1) は統一的で魅力的だが, 単独ではビュー不変性を保証しない

### 結論: 正則化項の追加が必要

7 候補を調査 (→ `notes/cross_view_regularization_options.md`):
1. Cross-view SIGReg (結合バッチ)
2. Cross-view InfoNCE
3. Barlow Twins / VICReg 式
4. Product of Experts
5. HSIC 最小化
6. Multi-View Information Bottleneck
7. **Cross-view Epps-Pulley 検定** ← 推奨

### 推奨構成

```
L_total = L_cvt_pred + lambda_1 * L_sigreg_per_view + lambda_2 * L_cross_ep
```

- L_cvt_pred: cross-view-temporal prediction (dynamics 学習)
- L_sigreg_per_view: 各カメラの崩壊防止 (既存 SIGReg)
- L_cross_ep: カメラ間分布一致 (Cross-view Epps-Pulley, 候補 7)

推奨理由: SIGReg と同じ数学的基盤 (Cramér-Wold + Epps-Pulley) でカメラ間分布一致を強制. 実装は SIGReg を複製して 2 標本版にするだけ. Le MuMo JEPA (2026) が結合 SIGReg をマルチモーダルでやっているが, 2 標本検定は未提案.

### 発見した関連論文

- Le MuMo JEPA (Cornelissen+ 2026): マルチモーダル JEPA で融合トークンに SIGReg 適用
- HaoChen+ ICLR 2023: Spectral contrastive learning, InfoNCE とカーネル PCA の接続
- Matrix-SSL (2023): 行列情報理論で VICReg/Barlow Twins を統一的に理解

## 2026-06-10: Cross-view alignment に至った議論の経緯

### 出発点: LeJEPA × neural fields の組み合わせ

最初のシードは"LeJEPA の alignment 損失と NeRF/3DGS のビュー依存性が構造的に似ている — 同じものを別視点から眺めて単一の表現を獲得する"という直感だった. NeRF/3DGS は復元ベースで多視点一貫性を獲得するが, JEPA の alignment は復元なしでそれができるのではないか, という問い.

### リフレーミング: 3D 表現 → 潜在空間での 3 項損失

"無理に 3D 表現と言わなくても, 多視点データから物体操作を復元ベースではなく潜在空間での alignment + 順動力学 + 逆動力学として解く"方向に転換. 先行研究の地図が NeRF/3DGS 論文群からロボット学習 (PIDM, LAPA, DeFI) + 表現学習理論 (LeJEPA, Klindt) にシフトした.

### 文献サーベイ (50 論文) の結果

Concept Matrix で確認した最大の空白: **JEPA alignment × 多視点/ビュー不変** に該当する論文がゼロ. V-JEPA 2 は単一視点の時間マスク予測, ReViWo は復元ベースのビュー分離, MV-MWM はマスク再構成.

### Seed 2 (ID 統合) の棄却

PIDM のアブレーション (L_inv 追加で +6.7%) と DeFI の知見 (GFDM 凍結 + GIDM 更新が全部更新より良い, 目標競合の報告) から, 逆動力学の統合は強い貢献にならないと判断. Seed 2 は Seed 1 の ablation に吸収.

### フレーミングの検討

3 案 (A: 理論拡張, B: システム, C: 表現学習比較) を検討. C (Nilaksh+ 2026 の多視点拡張) が最もリスク低い. ただしたたき台の L_align が VICReg の invariance 項と区別がつかず,"提案手法"として弱い問題が判明.

### L_align の格上げ → cross-view-temporal prediction

"時空間を混ぜたい"という発想から, L_pred と L_align を統一する案が浮上:
- 標準 LeWM: predictor(f(x_t^0), a_t) → f(x_{t+1}^0) (同カメラ, 次時刻)
- 提案: predictor(f(x_t^0), a_t, cam_token[j]) → f(x_{t+1}^j) (別カメラ, 次時刻)

DeFI の"目標競合"は ピクセル復元 vs 行動予測の間で起きたものであり, 両方とも潜在空間予測である本提案には当てはまらないことを確認. L_pred と L_align を 2 つの損失として足す必要がなく, 1 つの予測目的に統一できる点が美しい.

### ビュー不変性の保証問題

ただし cross-view-temporal prediction 単独ではビュー不変性が保証されない. predictor がビュー変換を丸暗記してエンコーダがサボるショートカットが生じる (I-JEPA の predictor 容量問題と同構造). このため, 同時刻・異カメラの埋め込みを近づける正則化が別途必要.

### Cross-view Epps-Pulley の発見

7 つの候補を調査した結果, SIGReg の自然な拡張として"2 標本 Epps-Pulley 検定でカメラ間分布一致を強制"する Cross-view Epps-Pulley を推奨. SIGReg と同じ数学的基盤 (Cramér-Wold 定理) で, 実装は数十行の追加.

### 現在の提案構成

```
L_total = L_cvt_pred + lambda_1 * L_sigreg_per_view + lambda_2 * L_cross_ep
```

3 項の役割分担:
- L_cvt_pred: cross-view-temporal prediction. dynamics + ビュー横断予測 (統一的予測目的)
- L_sigreg_per_view: 各カメラの崩壊防止 (既存 SIGReg)
- L_cross_ep: カメラ間分布一致 (Cross-view Epps-Pulley). エンコーダにビュー不変性を明示的に強制

この構成は"JEPA の予測目的を時空間 × カメラ軸に統一し, SIGReg をカメラ間に自然拡張した"として, Concept Matrix の空白セルを埋めつつ手法的新規性を主張できる.

## 2026-06-10: Cross-view 正則化メモの批評と改訂 (セッション 3)

### 候補 7 (Cross-view Epps-Pulley) 推奨の取り下げ

批評セッションにより, 前エントリの推奨 (候補 7) を以下の理由で取り下げた:

1. **等長変換への盲目性**: 分布レベルの一致は z^cam1 = R z^cam0 (R: 任意の直交変換) を罰せられない. これは"predictor がビュー変換を丸暗記するショートカット"そのものであり, 本メモの目的を達成しない
2. **per-view SIGReg との冗長性**: 各ビューが N(0,I) に収束すれば分布一致は自動的に成立する. L_cross_ep が独立の価値を持つのは学習途中の過渡期のみで, その論証はなかった
3. **安定性の未検証**: LeJEPA の勾配有界性解析は対固定ガウス特性関数の 1 標本検定前提. 2 標本版への移植可能性は自明でない
4. **新規性の脆さ**: 特性関数 2 標本検定は Epps-Singleton (1986) が先行. JEPA 文脈でも Rectified LpJEPA (arXiv:2602.01456) の RDMReg が sliced 2 標本分布マッチングを導入済み

### 新推奨: 候補 0 (素朴 cross-view MSE)

評価基準を"サンプルレベル一致"主軸に変更し, framing C 草案の L_align (同時刻・異カメラのペア MSE) を候補 0 として表に追加, 推奨に格上げ. 前エントリで素朴 MSE を外した理由 (VICReg invariance 項と区別がつかない) は novelty の問題であり有効性の問題ではない. 新規性は L_cvt_pred を含む構成全体で主張する.

```
L_total = L_cvt_pred + lambda_1 * L_sigreg_per_view + lambda_2 * L_align
```

### 波及修正

- **framing_c_draft.md**: 条件 C の予測項を L_pred → L_cvt_pred に更新 (06-10 の設計変更を反映). 条件 C 内 ablation (C1: L_pred + L_align / C2: L_cvt_pred のみ / C3: 全部入り) を追加. 条件 B の SIGReg を連結後 → 各ビュー独立に変更 (連結後適用は非対角ブロック = 0 でカメラ間無相関化を強制し, B vs C 比較を汚染するため)
- **Klindt+ 2026 の同型主張の弱め**: サーベイ Gap 1 と正則化メモの"数学的に同型"を"構造的に対応 (空間的ペアへの拡張は未証明)"に修正. サーベイ Seed 1 Readiness の記述と整合させた
- **サーベイの計数修正**: Papers mapped 50 → 51 (Paper Catalogue 実数・年別合計と一致). Concept Matrix の"VLA-JEPA (repeat)"重複行を削除し, 欠落していた I-JEPA / V-JEPA 2.1 の行を追加 (これで Concept Distribution の JEPA alignment 15 件・順動力学 24 件と Matrix が一致). Rectified LpJEPA の arXiv ID プレースホルダを 2602.01456 に修正. LaVA-Man が単一視点手法である旨を注記

## 2026-06-10: berkeley_autolab_ur5 カメラ配置の確認 (セッション 3 続き)

### 確認方法

1. ローカルデータの目視: 各カメラキーの動画からフレームを抽出. image = 三人称 RGB, image_with_depth = 深度のカラーマップ動画, hand_image = 手首 RGB
2. 公式ドキュメント (Berkeley UR5 Demonstration Dataset サイト + TFDS カタログ): third_person_image (TFDS では image_with_depth) は "The first 3 channels are the same as 'image,' and the last dimension is depth"

### 結論: 実質 2 視点

- image と image_with_depth は同一 RGB-D カメラ (同一視点) の RGB と深度
- 真の視点は (三人称, 手首) の 2 つのみ. 手首カメラは腕と共に動く
- (image, image_with_depth) ペアの alignment は cross-view ではなく cross-modal であり, 実験に含めると検証を汚染する

### 波及

- framing_c_draft のデータセット表と前提確認を更新. L_align ペア集合から (image, image_with_depth) を除外
- ISSUES に「berkeley_autolab_ur5 の視点多様性不足」を追加
- 未決定事項: 静的視点ペア (exterior x 2) を持つ DROID (droid_100) を主実験に昇格するか. berkeley は Stage 0-2 測定値との直接比較という利点があるため, 予備実験への降格が対案
