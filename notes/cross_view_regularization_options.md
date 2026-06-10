# Cross-view 正則化の候補: 同時刻・異カメラの埋め込みを近づける枠組み

ステータス: 調査メモ (2026-06-10)

## 背景

Cross-view-temporal prediction loss だけではビュー不変性が保証されない. predictor がビュー変換を丸暗記し, エンコーダがビュー依存な表現を出すショートカットが生じうる. 同時刻・異カメラの埋め込みを近づける正則化が必要.

## 候補一覧

| # | 手法 | サンプルレベル一致 | 理論的根拠 | 実装工数 | SIGReg 整合性 | 推奨度 |
|---|---|---|---|---|---|---|
| 1 | Cross-view SIGReg (結合バッチ) | ✗ (分布のみ) | Cramér-Wold | 最小 | ◎ | ★★★★ |
| 2 | Cross-view InfoNCE | ◎ | MI 下界 | 中 | △ | ★★★ |
| 3 | Barlow Twins / VICReg 式 | ○ (相関行列) | 冗長性削減 | 小 | ○ | ★★★ |
| 4 | Product of Experts | ○ (統合表現) | ベイズ推論 | 大 | △ | ★★ |
| 5 | HSIC 最小化 | ✗ (独立性) | カーネル独立性 | 中 | △ | ★★ |
| 6 | Multi-View Information Bottleneck | ✗ (情報量) | 情報理論 | 大 | ✗ | ★ |
| **7** | **Cross-view Epps-Pulley** | ✗ (分布のみ) | Cramér-Wold | **小** | **◎** | **★★★★★** |

## 候補 1: Cross-view SIGReg (結合バッチ)

全カメラの埋め込みを一つのバッチとして結合し, SIGReg を適用する.

```python
z_all = concat([z_cam0, z_cam1, z_cam2], dim=0)  # (3B, D)
L_sigreg = sigreg(z_all)
```

- **根拠**: Cramér-Wold 定理により, 全 1 次元射影の一致は同時分布の一致を保証
- **利点**: 既存の SIGReg 実装をほぼそのまま使える. バッチ構成を変えるだけ. ハイパラ追加なし
- **限界**: 分布レベルの一致であり, 特定フレームのカメラ間一致は保証しない
- **先行研究**: Le MuMo JEPA (Cornelissen+ 2026) が RGB + LiDAR/Thermal の融合トークンに対して同様の構成で SIGReg を適用. ただしマルチモーダルであり, 同一モダリティの多視点ではない

## 候補 2: Cross-view InfoNCE (対比学習)

同時刻・異カメラのペアを正例, 異時刻のペアを負例とする.

```python
# 正例: (z_t^cam0, z_t^cam1)
# 負例: (z_t^cam0, z_{t'}^cam1)
L_infonce = -log(exp(sim(z_t^0, z_t^1) / tau) / sum_t'(exp(sim(z_t^0, z_{t'}^1) / tau)))
```

- **根拠**: Contrastive Multiview Coding (Tian+ ECCV 2020) の直接適用. InfoNCE は相互情報量の下界を最大化し, ビュー間の共有情報を集約. Spectral contrastive learning (HaoChen+ ICLR 2023) が示すように, 正例ペアカーネルの上位固有関数を回復
- **利点**: サンプルレベルで"同時刻は近く, 異時刻は遠く"を直接強制
- **欠点**: 温度パラメータ $\tau$ が追加. バッチサイズ感度. SIGReg の"ハイパラレス"哲学と相容れない

## 候補 3: Barlow Twins / VICReg 式

カメラ間の cross-correlation matrix を単位行列に近づける.

```python
C = (z_cam0.T @ z_cam1) / B  # (D, D)
L_bt = sum((C - I)^2)  # 対角 = 1 (alignment), 非対角 = 0 (冗長性削減)
```

- **根拠**: Barlow Twins (Zbontar+ ICML 2021). 対角が 1 → 各次元がカメラ間で一致. 非対角が 0 → 次元間の冗長性なし
- **利点**: ハイパラが少ない. 負例不要. SIGReg は VICReg の一般化 (Balestriero+ 2025 §5.2) なので思想が近い
- **欠点**: D=192 なら 36K 要素の行列. バッチサイズ < D で推定不安定

## 候補 4: Product of Experts (確率的統合)

各カメラの埋め込みをガウスの平均・分散として PoE で統合.

```python
# 各カメラ: mu_i, logvar_i を出力
# PoE: 1/var = sum(1/var_i), mu = var * sum(mu_i / var_i)
mu_fused, var_fused = product_of_experts(mus, logvars)
```

- **根拠**: Multi-View Dreaming (Kanazawa+ 2022) が Dreamer の RSSM に適用. ガウスの積はガウス. 確信度で自動重み付け
- **利点**: 各カメラの埋め込みを直接一致させる必要がない. カメラ固有情報を持ったまま統合後にビュー不変表現を得る. VJEPA (Huang+ ICML 2026) の確率的 JEPA と自然に接続
- **欠点**: エンコーダが平均+分散を出す必要あり, LeWM のアーキテクチャ変更が大きい

## 候補 5: HSIC 最小化

埋め込みからカメラ ID が推測できないことを HSIC で強制.

```python
L_hsic = HSIC(z, v)  # z: 埋め込み, v: カメラ ID の one-hot
```

- **根拠**: HSIC はカーネル空間での独立性の尺度. MInD (2024), Triple Disentangled (2024) 等がマルチモーダル disentanglement に使用
- **利点**:"埋め込みがカメラ ID と独立"を直接最適化. ビュー固有の有用情報 (手首カメラの接触情報等) を完全に捨てない可能性
- **欠点**: カーネル選択に敏感. カメラ ID は離散 3 値 → バッチ内で 3 クラスしかなく推定精度低い

## 候補 6: Multi-View Information Bottleneck

全カメラで共有される情報のみを保持し, 各カメラ固有の情報を捨てる.

```python
# max I(z; y) - beta * I(z; x_i | x_j)
```

- **根拠**: Federici+ (2020)."有用情報は全ビューに現れ, ノイズは個別ビューにしかない"という仮定. Minimal sufficient statistic を学ぶ
- **利点**: 情報理論的に最もクリーン
- **欠点**: 相互情報量は直接計算不可で変分近似が必要. 実装が複雑

## 候補 7: Cross-view Epps-Pulley 検定 (推奨)

SIGReg の Cramér-Wold + Epps-Pulley をカメラ間に拡張. 各ランダム射影方向について, 異なるカメラの 1D 射影が同一分布であることを 2 標本検定で強制.

```python
for direction in random_directions:
    proj_cam0 = z_cam0 @ direction  # (B,)
    proj_cam1 = z_cam1 @ direction  # (B,)
    L_cross += two_sample_epps_pulley(proj_cam0, proj_cam1)
```

- **根拠**: SIGReg が"埋め込み分布 = N(0,I)"を検定するのと同じ枠組みで,"カメラ 0 の分布 = カメラ 1 の分布"を検定. Cramér-Wold 定理で全 1D 射影の一致が同時分布の一致を保証. Epps-Pulley は O(N) で勾配有界
- **利点**: SIGReg と同じ数学的基盤・計算コスト・安定性."SIGReg をカメラ間に自然拡張した"と一文で説明できる
- **限界**: 分布レベルの一致. サンプルレベルは cross-view-temporal prediction loss が補完
- **新規性**: Le MuMo JEPA (2026) は結合 SIGReg をやっているが, 2 標本 Epps-Pulley 検定によるカメラ間分布一致は未提案

## 推奨構成

```
L_total = L_cvt_pred + lambda_1 * L_sigreg_per_view + lambda_2 * L_cross_ep

L_cvt_pred:        Cross-view-temporal prediction (predictor あり, dynamics + ビュー変換)
L_sigreg_per_view: 各カメラの埋め込みが等方ガウスに従う (崩壊防止, 既存 SIGReg)
L_cross_ep:        カメラ間の埋め込み分布が一致する (ビュー不変性, 候補 7)
```

役割分担:
- `L_cvt_pred` — dynamics を学ぶ. ビュー横断的な予測でエンコーダに暗黙的なビュー不変圧力
- `L_sigreg_per_view` — 各ビューの崩壊防止
- `L_cross_ep` — カメラ間の分布一致を明示的に強制. エンコーダがビュー依存構造を持つインセンティブを除去

サンプルレベル一致の不足は `L_cvt_pred` が補完: カメラ 0 の t + 行動 → カメラ 1 の t+1 を予測するには, 同時刻の埋め込みがある程度近くないと predictor が学習できない.

$\lambda$ が 2 つあるが, `L_sigreg_per_view` と `L_cross_ep` を同じ重みにする (= "ガウス性"と"カメラ間一致"に同等の圧力) のが自然な出発点. 両方とも Epps-Pulley 検定なのでスケールが揃っている.

## 代替構成 (InfoNCE 版)

SIGReg 哲学にこだわらない場合:

```
L_total = L_cvt_pred + lambda * L_sigreg_joint + L_infonce_cross_view
```

`L_sigreg_joint` = 全カメラ結合バッチの SIGReg (候補 1). `L_infonce_cross_view` = 候補 2. サンプルレベル一致が InfoNCE で直接保証される. ただしハイパラ ($\tau$, $\lambda$) が増える.

## 参考文献

- Balestriero & LeCun 2025: LeJEPA / SIGReg. Cramér-Wold + Epps-Pulley の基盤
- Cornelissen+ 2026: Le MuMo JEPA. マルチモーダルでの結合 SIGReg 適用
- Tian+ ECCV 2020: Contrastive Multiview Coding. 多視点 InfoNCE の基盤
- HaoChen+ ICLR 2023: Spectral contrastive learning. InfoNCE とカーネル PCA の接続
- Zbontar+ ICML 2021: Barlow Twins. 相互相関行列の正則化
- Bardes+ ICLR 2022: VICReg. 分散・不変性・共分散正則化. SIGReg の特殊ケース
- Kanazawa+ 2022: Multi-View Dreaming. PoE による多視点潜在統合
- Federici+ 2020: Multi-View Information Bottleneck. 情報理論的枠組み
- Huang+ ICML 2026: VJEPA. 確率的 JEPA
- Wang & Isola 2020: Alignment-Uniformity. SSL 損失の 2 軸分析
