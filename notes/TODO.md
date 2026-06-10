# TODO

## 文献調査

- [x] LeWorldModel (LeWM) のサマリーノート作成
- [x] LeJEPA のサマリーノート作成
- [x] V-JEPA 2-AC (Meta, 2025) のサマリーノート作成 — LeWM の実機ベースラインとして最も直接的
- [x] "Reconstruction or Semantics?" (2026) の確認 — BridgeV2 上での潜在ワールドモデル encoder 比較
- [x] stable-worldmodel プラットフォーム論文 (arXiv:2605.21800) の精読
- [x] 多視点 × JEPA × 操作の broad 文献サーベイ (50 論文, 9 ハブ深読み) → `literature/surveys/multiview-manipulation-learning-on-jepa.md`

## 環境構築

- [x] stable-worldmodel のインストールと動作確認 — v0.1.0 + lerobot 0.5.1 + FFmpeg 8.1.1
- [x] berkeley_autolab_ur5 (LeRobot, 1K ep) でパイプライン疎通 — LeWM 1 エポック学習完走 (15 min, RTX 5090). ~2.5% のサンプルにタイムスタンプ不整合あり (SafeDataset で回避)
- [x] RoboMIND UR5e データ (25K 軌跡) の取得と robomind2lerobot による LeRobot 形式への変換 — 5 タスクサブセット (354 ep, 42K frames) をダウンロード・変換済み

## LeWM の破綻箇所特定 (オフライン, RoboMIND UR5e)

データセットは embodiment 一致を優先し RoboMIND UR5e (25K 軌跡) を主軸とする.
全ステージはオフラインデータで完結. 実機検証は提案手法の方向決定後.

### Stage 0: 固有次元の事前測定

- [x] berkeley_autolab_ur5 で予備測定 — Two-NN: ~6, ViT PCA 95%: 12 成分. 192 次元に対して大幅に低い → SIGReg ミスマッチのリスク大
- [x] RoboMIND UR5e 画像で再測定する — Two-NN: ~3.4, ViT PCA 95%: 8 成分. berkeley (~6) よりさらに低い. ミスマッチリスク増大
- 判断基準: 固有次元 << 192 → SIGReg ミスマッチが起きる見込み大 / ~100+ → 深刻でない可能性

### Stage 1: LeWM 学習 + 潜在空間の診断

- [x] RoboMIND UR5e で LeWM をデフォルト設定 (192 次元) で学習する — 有効ランク ~40/192 (21%), SIGReg/pred 比 ~178. berkeley (52, 27%) よりさらに低い
- [x] 学習中の潜在表現を計測する: 埋め込みの特異値スペクトル → 有効ランク, SIGReg/pred_loss 比率の推移 — 有効ランク ~52/192 (27%), SIGReg/pred 比 ~183. ミスマッチ確認
- 判断基準: 有効ランク << 192 → SIGReg が未使用次元にノイズを詰めている (TwoRoom と同じ症状) → **確認済み (両データセット)**

### Stage 2: 予測精度の評価

- [x] held-out エピソードで multi-step 予測の誤差劣化を測定する — berkeley: h=1 0.012, h=10 0.159 (線形). RoboMIND: h=1 0.019, h=10 0.197
- [x] コピーベースラインと比較する — berkeley 全次元: 全 h でモデル優位. RoboMIND 信号次元: h=1 でコピーに負け (Pred/Copy=1.07)
- 判断基準: ホライズンに対して指数的に劣化 → 計画に使えない → **全次元は線形だが, 信号次元のみで見ると RoboMIND は h=1 でコピーに負ける. berkeley では勝つ. 固有次元の低さが直結**
- [x] 信号/ノイズ次元分離 MSE 分析 — berkeley: 信号 51 dims, 希釈 73%. RoboMIND: 信号 40 dims, 希釈 79%

### 潜在次元スイープ (素朴な次元縮小の検証)

- [x] ViT hidden_size ∈ {12, 24, 48, 96, 192} で LeWM を訓練し, SIGReg 指標と pred_loss を比較 — SIGReg 利用率は改善するが pred_loss はエンコーダ容量に支配され, 素朴な縮小は純損
- [x] 評価手法 (コピーベースライン Pred/Copy) の方法論的問題を発見 — pred_proj/projector の空間不一致による定数オフセット. h=1 の結果が誤解を招く

### Stage 2 ver 2: SIGReg weight ablation

- [x] SIGReg weight ∈ {0, 0.009, 0.03, 0.09, 0.9} で d=192 固定, RoboMIND で訓練 — pred_loss は weight と単調増加. weight=0 で崩壊確認 (コサイン類似度 0.97, 埋め込み分散 26,000 倍小さい)
- [x] weight=0 と weight=0.09 の埋め込み分散比較で表現崩壊の亜種を確認 — SIGReg は崩壊防止に必要, ただし圧力が強すぎる

### 方向決定

- [ ] Stage 0–2 + dim sweep + SIGReg ablation の結果を踏まえ, 提案手法の方向性を決定する
- [ ] 候補: (1) RDMReg (Rectified LpJEPA) の LeWM への適用, (2) 変分 JEPA ワールドモデル, (3) 崩壊防止手法の体系的比較
- [x] 新規候補 (文献サーベイ由来): 多視点 JEPA alignment による復元不要操作表現学習 → Seed 1 に集約. フレーミング C (多視点での意味 vs 復元の表現比較) を推奨 → **たたき台作成済み**
  - Seed 2 (ID 統合) は独立論文にならず → Seed 1 の ablation に吸収
  - フレーミング A (理論) / B (システム) / C (表現比較) の 3 案. C が最もリスク低い
  - ReViWo 公式実装発見 (GitHub: Trevor-emt/Reviwo) → 条件 D の工数低減

### Framing C 実装 (方向決定: 多視点での意味 vs 復元の表現比較)

- [x] berkeley_autolab_ur5 の 3 カメラ配置を確認 (実質的に多視点か) — **実質 2 視点と判明**. image_with_depth は image と同一カメラの深度チャネル (公式:"The first 3 channels are the same as 'image,' and the last dimension is depth"). 真の視点ペアは (三人称, 手首) の 1 組のみで, 手首カメラは腕と共に動く
- [ ] 主実験データセットの再検討: 静的視点ペア (exterior x 2) を持つ DROID (droid_100) を主実験に昇格するか決定
- [ ] stable-worldmodel の LeRobotAdapter を多カメラ対応に拡張
- [ ] World (LeWM) の多カメラ入力対応 (連結/alignment 切り替え)
- [ ] L_align (cross-view alignment 損失, 正則化メモ候補 0) の実装
- [ ] L_cvt_pred (cross-view-temporal prediction, cam_token 付き predictor) の実装
- [ ] 条件 B (Concat JEPA) の訓練・評価 — SIGReg は各ビュー独立適用 (連結後は不可, 2026-06-10 改訂)
- [ ] 条件 C (Alignment JEPA) の訓練・評価 — ablation 含む (C1: L_pred + L_align / C2: L_cvt_pred のみ / C3: 全部入り)
- [ ] 条件 D (ReViWo 復元系ベースライン) の移植・訓練・評価
- [ ] 条件 E (V-JEPA 2.1 凍結エンコーダ) の訓練・評価
- [ ] 5 条件の統合評価 (予測精度, 潜在表現品質, 計画性能, 視点頑健性)

## 比較実験 (方向決定後)

- [ ] DROID (Franka) で同一条件の LeWM 学習を行い, embodiment 差の影響を分離する
- [ ] UR5e 実機での閉ループ検証 (CEM 計画 → 行動 → 観測)
