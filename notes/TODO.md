# TODO

## 文献調査

- [x] LeWorldModel (LeWM) のサマリーノート作成
- [x] LeJEPA のサマリーノート作成
- [x] V-JEPA 2-AC (Meta, 2025) のサマリーノート作成 — LeWM の実機ベースラインとして最も直接的
- [x] "Reconstruction or Semantics?" (2026) の確認 — BridgeV2 上での潜在ワールドモデル encoder 比較
- [x] stable-worldmodel プラットフォーム論文 (arXiv:2605.21800) の精読

## 環境構築

- [x] stable-worldmodel のインストールと動作確認 — v0.1.0 + lerobot 0.5.1 + FFmpeg 8.1.1
- [x] berkeley_autolab_ur5 (LeRobot, 1K ep) でパイプライン疎通 — LeWM 1 エポック学習完走 (15 min, RTX 5090). ~2.5% のサンプルにタイムスタンプ不整合あり (SafeDataset で回避)
- [ ] RoboMIND UR5e データ (25K 軌跡) の取得と robomind2lerobot による LeRobot 形式への変換

## LeWM の破綻箇所特定 (オフライン, RoboMIND UR5e)

データセットは embodiment 一致を優先し RoboMIND UR5e (25K 軌跡) を主軸とする.
全ステージはオフラインデータで完結. 実機検証は提案手法の方向決定後.

### Stage 0: 固有次元の事前測定

- [x] berkeley_autolab_ur5 で予備測定 — Two-NN: ~6, ViT PCA 95%: 12 成分. 192 次元に対して大幅に低い → SIGReg ミスマッチのリスク大
- [ ] RoboMIND UR5e 画像で再測定する (データ取得後)
- 判断基準: 固有次元 << 192 → SIGReg ミスマッチが起きる見込み大 / ~100+ → 深刻でない可能性

### Stage 1: LeWM 学習 + 潜在空間の診断

- [ ] RoboMIND UR5e で LeWM をデフォルト設定 (192 次元) で学習する
- [x] 学習中の潜在表現を計測する: 埋め込みの特異値スペクトル → 有効ランク, SIGReg/pred_loss 比率の推移 — 有効ランク ~52/192 (27%), SIGReg/pred 比 ~183. ミスマッチ確認
- 判断基準: 有効ランク << 192 → SIGReg が未使用次元にノイズを詰めている (TwoRoom と同じ症状) → **確認済み**

### Stage 2: 予測精度の評価

- [x] held-out エピソードで multi-step 予測の誤差劣化を測定する (1, 5, 10 step, 潜在空間 MSE) — h=1: 0.012, h=5: 0.070, h=10: 0.159. 線形増加 (0.016/step)
- [x] コピーベースライン (前フレームをそのまま返す) と比較する — 全ホライズンでモデルが優位 (pred/copy: h=1 0.62, h=5 0.24, h=10 0.22)
- 判断基準: ホライズンに対して指数的に劣化 → ワールドモデルとして計画に使えない → **線形増加. ただし全次元平均であり, SIGReg ノイズ次元がマスクしている可能性あり**

### 方向決定

- [ ] Stage 0–2 の結果を踏まえ, 提案手法の方向性を決定する

## 比較実験 (方向決定後)

- [ ] DROID (Franka) で同一条件の LeWM 学習を行い, embodiment 差の影響を分離する
- [ ] UR5e 実機での閉ループ検証 (CEM 計画 → 行動 → 観測)
