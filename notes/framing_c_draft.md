# Framing C: 多視点ロボット操作における意味表現 vs 復元表現

ステータス: たたき台 (2026-06-09)

## 研究問い

1. **多視点で復元系が意味系を逆転しうる条件はあるか?**
   Nilaksh+ 2026 は単一視点・BridgeV2 で意味表現 > 復元表現を示した. ただし多視点ではクロスビュー再構成が 3D 幾何を暗黙的に学ぶため, 復元系に構造的追い風がある. Nilaksh §4.5 自身が"意味系は幾何・接触の精度が落ちる"と報告しており, 多視点で幾何情報が増えると逆転の可能性がある.
2. **多視点統合方法 (素朴連結 vs JEPA cross-view alignment) はワールドモデルの予測・計画性能にどう影響するか?**
   サーベイ Gap 1: JEPA alignment を多視点カメラ間に適用した研究はゼロ件.
3. **Cross-view alignment は SIGReg の次元ミスマッチ問題を緩和するか?**
   Stage 0–2 で確認済みの固有次元ミスマッチ (有効ランク ~40–52/192) に対し, 多視点 alignment が追加の学習信号として機能するかを検証.

## ポジショニング

Nilaksh+ 2026 の制御実験デザイン (エンコーダのみ変数, 他は固定) を多視点に拡張する. ただし Nilaksh は拡散ワールドモデルで比較したのに対し, 我々は JEPA ワールドモデル (LeWM) 上で比較する.

- Nilaksh の"意味 > 復元"が拡散以外のワールドモデルでも成立するかを検証 (独立した貢献)
- 多視点統合の比較軸を追加 (Nilaksh にない貢献)
- SIGReg の次元ミスマッチとの関連を分析 (Stage 0–2 の知見を活用)

## 実験条件

| 条件 | エンコーダ | 多視点統合 | 損失 | 備考 |
|---|---|---|---|---|
| A. Single-view JEPA | ViT (LeWM) | なし (1 カメラ) | L_pred + SIGReg | 既存 LeWM ベースライン |
| B. Concat JEPA | ViT x N (共有) | 各ビュー独立エンコード → トークン連結 | L_pred + SIGReg (各ビュー) | ACT/PIDM 方式の素朴拡張 |
| C. Alignment JEPA | ViT x N (共有) | 各ビュー独立エンコード + cross-view alignment | L_cvt_pred + L_align + SIGReg (各ビュー) | **提案条件** |
| D. Reconstruction | ViT + Decoder | VIR/VDR 分離 (ReViWo 方式) | L_recon + L_contrastive | 復元ベースの代表 |
| E. Frozen semantic | V-JEPA 2.1 凍結 + adaptor | 各ビュー独立 → 連結 | L_pred のみ | 大規模事前学習の参照点 |

制御変数: データセット, 訓練ステップ数, predictor アーキテクチャ, CEM 計画パラメータはすべて共通.

SIGReg は全条件で各ビューの埋め込みに独立適用する (2026-06-10 改訂). 連結後の埋め込み `[z^0; z^1]` に適用すると非対角ブロック = 0, すなわちカメラ間の無相関化を強制する. 同一シーンを観測するビュー間の埋め込みは本質的に相関するため, 連結後適用は正則化が表現と恒常的に衝突し, B vs C の比較が"統合方法の差"ではなく"正則化の衝突の有無"に汚染される.

### L_align の定義

```
L_align = (1 / |P|) * sum_{(i,j) in P}  || f_theta(x_t^i) - f_theta(x_t^j) ||^2
```

- `P`: カメラペアの集合 (3 カメラなら {(0,1), (0,2), (1,2)} の 3 ペア)
- `f_theta`: 共有エンコーダ
- `x_t^i`: 時刻 t のカメラ i の画像

LeJEPA の alignment 損失 (時間的に隣接する 2 フレーム間の埋め込み MSE) と同じ形式をカメラ軸に適用. 正則化候補の比較検討は `cross_view_regularization_options.md` を参照 (候補 0 として採用).

### L_cvt_pred の定義 (2026-06-10 改訂)

条件 C の予測項は標準の同一カメラ時間予測 (L_pred) ではなく, cross-view-temporal prediction とする:

```
L_cvt_pred = || predictor(f_theta(x_t^i), a_t, cam_token[j]) - sg(f_theta(x_{t+1}^j)) ||^2
```

- カメラ i の時刻 t + 行動 → カメラ j の時刻 t+1 を予測 (i = j の場合は標準の時間予測に帰着)
- `cam_token[j]`: ターゲットビューを指定する学習可能トークン
- 時間軸とカメラ軸の予測を単一の目的に統一する. 動機と経緯は `LOGS/log_lewm_lejepa_discussion.md` (2026-06-10) を参照

### 条件 C の全損失

```
L_total = L_cvt_pred + lambda_1 * L_SIGReg + lambda_2 * L_align
```

- `cross_view_regularization_options.md` の推奨構成 (2026-06-10 改訂) と同一. L_SIGReg は各ビューの埋め込みに独立に適用 (連結後ではない)
- 条件 B に対して条件 C は 2 要素 (予測目的の L_pred → L_cvt_pred, L_align の追加) が同時に変わるため, 条件 C 内で ablation を行う: (C1) L_pred + L_align, (C2) L_cvt_pred のみ, (C3) 全部入り. C2 は"predictor がビュー変換を丸暗記するショートカット"の実証も兼ねる

## データセット

| データセット | カメラ数 | エピソード | 用途 |
|---|---|---|---|
| berkeley_autolab_ur5 | 実質 2 視点 (三人称 RGB-D, 手首) | ~1K | 主実験候補 (パイプライン疎通済み. ただし下記の制約) |
| DROID (lerobot/droid_100) | 3 (exterior x 2, wrist) | 100 ep サブセット | 主実験候補 (静的視点ペアあり) |

berkeley_autolab_ur5 は Stage 0–2 で使用済みなので, SIGReg ミスマッチの測定値 (固有次元 ~6, 有効ランク ~52/192) と直接比較できる.

**前提確認の結果 (2026-06-10)**: berkeley_autolab_ur5 は実質 2 視点. 公式ドキュメントによれば image_with_depth の RGB チャネルは image と同一 ("The first 3 channels are the same as 'image,' and the last dimension is depth"). 同一 RGB-D カメラの深度チャネルであり, 視点は (三人称, 手首) の 2 つ. ローカルデータの目視でも確認済み (LeRobot 版 image_with_depth は深度のカラーマップ動画).

影響と対応:

1. L_align のペア集合から (image, image_with_depth) を除外する. このペアは視点ではなくモダリティ (RGB vs 深度) の対応であり, cross-view alignment の検証を汚染する
2. berkeley の視点ペアは (三人称, 手首) の 1 組のみ. 手首カメラは腕と共に動くため静的視点間の alignment と性質が異なり, ビュー固有情報の差が極端
3. 静的視点ペア (exterior x 2) を持つ DROID を主実験に昇格し, berkeley を予備実験 (Stage 0–2 との接続用) に降格することを検討 → **決定待ち** (TODO 参照)

## 評価指標

Nilaksh+ 2026 の 3 軸評価を LeWM 向けに適応:

1. **予測精度**: multi-step MSE (信号/ノイズ分離), Pred/Copy 比 (Stage 2 手法)
2. **潜在表現品質**: 有効ランク, 固有次元, IDM 行動復元 Pearson r, SIGReg/pred 比
3. **計画性能**: CEM 行動復元誤差 (Nilaksh 準拠)
4. **視点頑健性**: 訓練時と異なるカメラサブセットでの性能劣化 (ReViWo の CIP 設定に準拠)

## 実装計画

| ステップ | 工数 (推定) | 内容 |
|---|---|---|
| 1. Adapter 多カメラ対応 | 1–2 日 | `primary_camera_key` → `camera_keys` リスト, `'pixels'` → `'pixels_0'`, `'pixels_1'`, ... |
| 2. World (LeWM) 多カメラ入力 | 2–3 日 | エンコーダの多ビュー入力, 連結/alignment 切り替え |
| 3. L_align + L_cvt_pred 実装 | 2 日 | cross-view MSE, cam_token 付き predictor, SIGReg は各ビュー独立適用 |
| 4. 条件 A (ベースライン) | 既存 | Stage 1 の結果を再利用 |
| 5. 条件 B–C 訓練 | 各 2–4 時間 | RTX 5090, berkeley_autolab_ur5 |
| 6. 条件 D (ReViWo) | 1–2 日 | 公式実装 (GitHub: Trevor-emt/Reviwo) を移植 |
| 7. 条件 E (凍結エンコーダ) | 1–2 日 | V-JEPA 2.1 の重みダウンロード + adaptor |
| 8. 評価スイート | 2–3 日 | Stage 2 の評価コードを多条件に汎化 |

合計: ~2–3 週間.

## リスクと緩和

| リスク | 深刻度 | 緩和策 |
|---|---|---|
| berkeley_autolab_ur5 (~1K ep) ではデータ不足で差が出ない | 中 | DROID 100 ep でも追試. 差が出なければデータ量のスケーリング曲線を報告 |
| 条件 C (alignment) と B (concat) の差が微小 | 低 | これ自体が知見."cross-view alignment は不要, 連結で十分"は実用的に価値がある |
| 条件 D (復元系) の実装が公平でない | 中 | ReViWo 公式コードを使用. パラメータ数を揃える |
| 条件 E (V-JEPA 2.1) が圧勝して他の比較が霞む | 低 | 規模の違い (1B vs 15M) を明示し, 同規模条件 (A–D) の比較を主軸にする. E は参照点 |

## 予想される貢献

結果がどう転んでも報告できる (Framing C の最大の強み):

- C > B > A → cross-view alignment が有効, 多視点 JEPA の新手法として提案
- B ≈ C > A → alignment 不要, 素朴連結で十分 (実用的知見)
- D > B, C → 復元系が多視点では優位 (Nilaksh の結論の限界を示す)
- A ≈ B → 多視点情報自体が LeWM スケールでは効かない (スケールの壁)

## 主要参考文献

- Nilaksh+ 2026:"Reconstruction or Semantics?" — 単一視点での意味 vs 復元の体系比較. 本研究の直接的な出発点
- ReViWo (Pang+ ICLR 2025): 復元ベース VIR/VDR 分離. 条件 D のベースライン. 公式実装: https://github.com/Trevor-emt/Reviwo
- Klindt+ 2026: LeJEPA の識別可能性定理. 時間的ビューペアで証明済み, 空間的 (カメラ間) は未証明
- LeWM (Maes+ 2026): JEPA ワールドモデル. 条件 A–C の基盤
- V-JEPA 2 (Assran+ 2025): 条件 E の凍結エンコーダ
