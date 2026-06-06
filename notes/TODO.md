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

### 方向決定

- [ ] Stage 0–2 の結果を踏まえ, 提案手法の方向性を決定する

## 比較実験 (方向決定後)

- [ ] DROID (Franka) で同一条件の LeWM 学習を行い, embodiment 差の影響を分離する
- [ ] UR5e 実機での閉ループ検証 (CEM 計画 → 行動 → 観測)
