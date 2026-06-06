# 固有次元推定ログ

## 2026-06-05: berkeley_autolab_ur5 (UR5, 1K ep)

### 実験設定

- データセット: `lerobot/berkeley_autolab_ur5` (1,000 エピソード, 5 タスク)
- カメラ: `observation.images.image` (480x640, RGB)
- サンプル数: 1,946 / 2,000 (54 サンプルはタイムスタンプ不整合でスキップ)
- 手法: Two-NN (Facco+ 2017) + PCA 累積寄与率
- 空間: (1) ピクセル空間 (64x64 にダウンサンプル, 12,288 次元), (2) ViT-tiny CLS トークン (192 次元, 未学習)

### 結果

| 空間 | Two-NN | PCA 90% | PCA 95% | PCA 99% |
|---|---|---|---|---|
| ピクセル (12,288-dim) | 4.4 | 286 | 513 | 513 |
| ViT-tiny CLS (192-dim) | 6.0 | 6 | 12 | 36 |

ViT 特徴空間の特異値は第 1 成分 (56.6) が突出し, 急速に減衰 (第 10 成分で 5.8). 192 次元中 6 成分で分散の 90% を説明.

### 解釈

- Two-NN と PCA (ViT 空間) が整合的に低固有次元 (~6) を示す
- LeWM の潜在次元 192 に対して ~30 倍の乖離
- TwoRoom (~2 次元, 潜在 192 次元 → ~96 倍) ほど極端ではないが, SIGReg が未使用次元にノイズを注入する同じメカニズムが作動する条件

### 注意事項

- ViT は未学習 (ランダム初期化). 学習後は表現構造が変わるため, Stage 1 で学習中の有効ランクを追跡して再評価が必要
- berkeley_autolab_ur5 はパイプライン確認用. RoboMIND UR5e (25K 軌跡) での再測定が必要
- ピクセル空間の PCA 95% (513) と Two-NN (4.4) の乖離は, 高次元ピクセルノイズによる典型的なアーティファクト

## 2026-06-05: RoboMIND UR5e (5 タスクサブセット, 354 ep)

### 実験設定

- データセット: RoboMIND v1.1 UR5e, 5 タスク (placebananaonaplate, pick_up_red_pepper_from_table, uncap_open_the_trash_can_1104, put_the_green_vegetable_in_the_basket_1121, insert_the_flowers_from_the_vase_1025)
- エピソード: 354, フレーム: 42,280
- カメラ: `observation.images.camera_top` (480x640, RGB, 元は BGR → 変換済み)
- サンプル数: 2,000 (各タスク 400)
- 手法・空間: 同上

### 結果

| 空間 | Two-NN | PCA 90% | PCA 95% | PCA 99% |
|---|---|---|---|---|
| ピクセル (12,288-dim) | 2.5 | 283 | 417 | 417 |
| ViT-tiny CLS (192-dim) | 3.4 | 4 | 8 | 23 |

### 解釈

1. **berkeley_autolab_ur5 よりさらに低固有次元** — ViT 空間 Two-NN 3.4 (berkeley: 6.0), PCA 95% 8 (berkeley: 12). 192 次元に対する乖離は ~56 倍 (berkeley の ~32 倍より深刻).

2. **SIGReg ミスマッチのリスクはさらに高い** — 有効に使える次元が少ないほど, SIGReg が"等方化すべきノイズ次元"の割合が増え, 予測損失の最適化を妨げる圧力が強くなる.

3. **カメラ 1 台 + 固定視点** — RoboMIND UR5e は固定カメラ 1 台で, berkeley_autolab_ur5 (やはり 1 台だがアングルが異なる) よりも視覚的変動が小さい可能性がある. これが低固有次元の一因.

### 判断

RoboMIND UR5e でも固有次元 (~3) << 潜在次元 (192). berkeley_autolab_ur5 以上に SIGReg ミスマッチが深刻になる見込みが確認された.
