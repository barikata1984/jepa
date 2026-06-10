# Cross-view 正則化の候補: 同時刻・異カメラの埋め込みを近づける枠組み

ステータス: 調査メモ (2026-06-10, 同日改訂: 評価基準をサンプルレベル一致主軸に変更, 推奨を候補 7 から候補 0 へ)

## 背景

Cross-view-temporal prediction loss だけではビュー不変性が保証されない. predictor がビュー変換を丸暗記し, エンコーダがビュー依存な表現を出すショートカットが生じうる. 同時刻・異カメラの埋め込みを近づける正則化が必要.

## 候補一覧

| # | 手法 | サンプルレベル一致 | 理論的根拠 | 実装工数 | SIGReg 整合性 | 推奨度 |
|---|---|---|---|---|---|---|
| **0** | **Cross-view MSE (素朴 alignment)** | **◎ (ペア MSE)** | LeJEPA alignment と同型 | **最小** | **◎** | **★★★★★** |
| 1 | Cross-view SIGReg (結合バッチ) | ✗ (混合分布のみ) | Cramér-Wold | 最小 | ◎ | ★ |
| 2 | Cross-view InfoNCE | ◎ | MI 下界 | 中 | △ | ★★★★ |
| 3 | Barlow Twins / VICReg 式 | ○ (相関行列) | 冗長性削減 | 小 | ○ | ★★★ |
| 4 | Product of Experts | ○ (統合表現) | ベイズ推論 | 大 | △ | ★★ |
| 5 | HSIC 最小化 | ✗ (独立性) | カーネル独立性 | 中 | △ | ★ |
| 6 | Multi-View Information Bottleneck | ✗ (情報量) | 情報理論 | 大 | ✗ | ★ |
| 7 | Cross-view Epps-Pulley | ✗ (分布のみ) | Cramér-Wold | 小 | ◎ | ★ |

**評価基準の改訂 (2026-06-10)**:"サンプルレベル一致"を主基準とする. 目的は同時刻・異カメラの観測を同じ潜在表現に埋め込むことであり, 分布レベルの一致では原理的に達成できない. 分布を保つ変換 (N(0,I) なら任意の直交変換 R: z^cam1 = R z^cam0) を片方のビューに適用しても分布一致は破れないため, ビューごとの恒等的なズレを罰せられない. さらに分布レベルのみの候補 (1, 5, 7) は, L_total に含まれる per-view SIGReg の最適解 (各ビュー → N(0,I)) が分布一致を含意するため, 追加項として冗長.

## 候補 0: Cross-view MSE (素朴 alignment, 推奨)

同時刻・異カメラの埋め込みペアの MSE. framing_c_draft.md の条件 C で定義した L_align と同一.

```python
# P: カメラペアの集合 (3 カメラなら {(0,1), (0,2), (1,2)})
L_align = mean([mse(z_t_i, z_t_j) for (i, j) in P])
```

- **根拠**: LeJEPA の処方箋 (alignment MSE + SIGReg による崩壊防止) をカメラ軸に適用したもの. Klindt+ 2026 の識別可能性定理の設定 ("同一潜在状態から生成された 2 つの観測") と構造的に対応する. ただし定理は時間的ビューペアを仮定しており, カメラごとに生成関数が異なる空間的ペアへの拡張は未証明 (Seed 1 の理論課題)
- **利点**: サンプルレベル一致を直接強制する唯一のハイパラレス候補. 実装は数行. 崩壊は per-view SIGReg が防止 (LeJEPA と同じ役割分担)
- **欠点**: (1) VICReg の invariance 項と形式上区別がつかず, 正則化項単体では手法的新規性が弱い. ただしこれは novelty の問題であり有効性の問題ではない. 新規性は L_cvt_pred を含む構成全体で主張する. (2) 全次元の一致を強制するため, ビュー固有の有用情報 (手首カメラの接触情報等) を捨てる. 共有次元 + ビュー固有次元の分割 (MVD / ReViWo 式) が緩和策

## 候補 1: Cross-view SIGReg (結合バッチ)

全カメラの埋め込みを一つのバッチとして結合し, SIGReg を適用する.

```python
z_all = concat([z_cam0, z_cam1, z_cam2], dim=0)  # (3B, D)
L_sigreg = sigreg(z_all)
```

- **根拠**: Cramér-Wold 定理により, 全 1 次元射影の一致は同時分布の一致を保証
- **利点**: 既存の SIGReg 実装をほぼそのまま使える. バッチ構成を変えるだけ. ハイパラ追加なし
- **限界**: 特定フレームのカメラ間一致は保証しない. さらに結合バッチの等方ガウス性は各ビュー分布の一致すら含意しない (混合が N(0,I) でも成分分布は異なりうる). per-view SIGReg を使う構成では冗長
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

## 候補 7: Cross-view Epps-Pulley 検定

SIGReg の Cramér-Wold + Epps-Pulley をカメラ間に拡張. 各ランダム射影方向について, 異なるカメラの 1D 射影が同一分布であることを 2 標本検定で強制.

```python
for direction in random_directions:
    proj_cam0 = z_cam0 @ direction  # (B,)
    proj_cam1 = z_cam1 @ direction  # (B,)
    L_cross += two_sample_epps_pulley(proj_cam0, proj_cam1)
```

- **根拠**: SIGReg が"埋め込み分布 = N(0,I)"を検定するのと同じ枠組みで,"カメラ 0 の分布 = カメラ 1 の分布"を検定. Cramér-Wold 定理で全 1D 射影の一致が同時分布の一致を保証. Epps-Pulley は O(N) で勾配有界
- **利点**: SIGReg と同じ数学的基盤."SIGReg をカメラ間に自然拡張した"と一文で説明できる
- **限界 (2026-06-10 改訂で格下げ)**: (1) 分布レベルの一致のみで, ビューごとの等長変換 (z^cam1 = R z^cam0) に盲目. ショートカット排除という本メモの目的を達成しない. (2) per-view SIGReg の最適解 (各ビュー → N(0,I)) が分布一致を含意するため, 追加項として理論的に冗長. 主張できるのは学習途中の過渡期における効果のみで, その論証はない. (3) LeJEPA の勾配有界性の解析は対固定ガウス特性関数の 1 標本検定が前提. 両標本がパラメータ依存になる 2 標本版で同じ安定性が成り立つかは未検証
- **新規性**: 特性関数ベースの 2 標本検定自体は Epps-Singleton (1986, scipy 実装あり) として確立済み. ランダム 1D 射影 + 分布一致でドメイン間を揃える発想も sliced Wasserstein 系のドメイン適応に先行がある. さらに JEPA 文脈でも Rectified LpJEPA (Kuang+ 2026, arXiv:2602.01456) の RDMReg が sliced 2 標本分布マッチング損失を導入済み (対固定目標分布 RGG). 残る差分は"固定目標分布ではなくカメラ間"という点のみ

## 推奨構成 (2026-06-10 改訂)

```
L_total = L_cvt_pred + lambda_1 * L_sigreg_per_view + lambda_2 * L_align

L_cvt_pred:        Cross-view-temporal prediction (predictor あり, dynamics + ビュー変換)
L_sigreg_per_view: 各カメラの埋め込みが等方ガウスに従う (崩壊防止, 既存 SIGReg)
L_align:           同時刻・異カメラのサンプルレベル一致 (ビュー不変性, 候補 0)
```

役割分担:
- `L_cvt_pred` — dynamics を学ぶ. ビュー横断的な予測でエンコーダに暗黙的なビュー不変圧力
- `L_sigreg_per_view` — 各ビューの崩壊防止. 分布レベルの一致はこの項の最適解が含意するため, 分布レベル項 (候補 1/7) は追加しない
- `L_align` — 同時刻・異カメラの埋め込みを同じ潜在表現へ明示的に近づける. predictor がビュー変換を丸暗記するショートカットのインセンティブを除去

この構成は LeJEPA の処方箋 (alignment MSE + SIGReg) のカメラ軸版であり, Klindt+ 2026 の識別可能性の設定 (同一潜在状態の 2 観測ペア) と構造的に対応する (ただし定理の空間的ペアへの拡張は未証明). 手法的新規性は正則化項単体ではなく, L_cvt_pred (時間 × カメラ軸の統一予測目的) を含む構成全体で主張する.

$\lambda_2$ はスケール論で固定できないため探索が必要. 出発点は LeJEPA における alignment : SIGReg の比 (時間ペアをカメラペアに読み替えた対応). `L_align` が強すぎるとビュー固有情報 (手首カメラの接触等) を潰すため, 視点頑健性だけでなく下流操作性能でも ablation する.

旧推奨 (候補 7, `L_cross_ep`) は分布レベルのみでビューごとの等長変換に盲目, かつ per-view SIGReg と冗長なため取り下げた. 採用する場合は "per-view SIGReg + L_cvt_pred に対して何を改善するか" を示す ablation が必須.

## 代替構成 (InfoNCE 版)

素朴 MSE では一致圧力が弱い (全埋め込みが近づくだけで識別性が落ちる) ことが実験で判明した場合:

```
L_total = L_cvt_pred + lambda * L_sigreg_per_view + L_infonce_cross_view
```

`L_infonce_cross_view` = 候補 2. 負例 (異時刻ペア) により"同時刻は近く, 異時刻は遠く"を直接強制する. ただしハイパラ ($\tau$, バッチサイズ感度) が増える. 崩壊防止は候補 1 (結合バッチ) ではなく per-view SIGReg を維持する (結合バッチは各ビュー分布の一致を含意しないため).

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
- Epps & Singleton 1986: 特性関数ベースの 2 標本検定 (候補 7 の検定自体の先行. scipy.stats.epps_singleton_2samp)
- Klindt+ 2026: LeJEPA の識別可能性定理. 候補 0 のサンプルレベル alignment が定理の設定と構造的に対応 (空間的ペアへの拡張は未証明)
- Kuang+ 2026: Rectified LpJEPA / RDMReg. JEPA 文脈での sliced 2 標本分布マッチングの先行 (arXiv:2602.01456)
