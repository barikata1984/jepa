---
Title: "Latent Geometry Beyond Search: Amortizing Planning in World Models"
Authors:
  - Nguyen, Hoang
  - Xu, Xiaohao
  - Huang, Xiaonan
Year: 2026
Venue: arXiv
Tags:
  - "world-models"
  - "inverse-dynamics"
  - "latent-planning"
  - "jepa"
  - "amortized-inference"
  - "goal-conditioned-control"
PDF: "[[papers/Nguyen-arXiv2026-Latent_Geometry_Beyond/main.pdf|📃]]"
Import Date: "2026-06-08"
Read Date: 2026-06-08
Executive Summary: "LeWM の潜在空間が SIGReg 正則化により十分に構造化されている場合, CEM 等の反復的テスト時探索を, 軽量な Goal-Conditioned Inverse Dynamics Model (GC-IDM) による単一フォワードパスに置き換えられることを実証. ~1.5M パラメータの MLP が, 凍結 LeWM 埋め込み上で現在の潜在状態・目標潜在状態・残りホライズンから直接行動を予測し, 4 環境 8 設定中 7 設定で CEM と同等以上の成功率を達成しつつ, 計画コストを 100–130 倍削減."
Citekey: Nguyen-arXiv2026-Latent_Geometry_Beyond
BibTeX Key: nguyen2026latent
DOI:
Relevance: 5
Repository: "none"
Category: note
Template Version: v2.3
---

## Executive Summary

LeWM の潜在空間が SIGReg 正則化により十分に構造化されている場合, CEM 等の反復的テスト時探索を, 軽量な Goal-Conditioned Inverse Dynamics Model (GC-IDM) による単一フォワードパスに置き換えられることを実証. ~1.5M パラメータの MLP が, 凍結 LeWM 埋め込み上で現在の潜在状態・目標潜在状態・残りホライズンから直接行動を予測し, 4 環境 8 設定中 7 設定で CEM と同等以上の成功率を達成しつつ, 計画コストを 100–130 倍削減.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

JEPA ベースのワールドモデル ([[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/leworldmodel-stable-end-to-end-joint-embedding-predictive-architecture-from-pixels|Maes+ 2026]]) において, 動的予測は高速だが行動選択には CEM による 9,000 ロールアウト (45,000 predictor フォワードパス) のオンライン探索が必要であり, これが推論コストの支配項となっていた (§1,"planning tax"). 本論文は, SIGReg で正則化された潜在幾何が十分に滑らかかつ行動感度の高い構造を持つとき, 計画問題をオンライン探索から学習済み逆写像による推論へ完全に移行できるかという問いに答えた.

### 提案手法のアプローチと, その根幹をなす要素は何か?

事前学習済み LeWM の凍結エンコーダが生成する潜在空間上で, 目標条件付き逆ダイナミクスモデル (GC-IDM) を教師あり回帰で学習する. テスト時には反復探索を一切行わず, 現在の観測を毎ステップ再エンコードし, 目標埋め込みと残りホライズンとともに GC-IDM に入力して 1 回のフォワードパスで行動を予測するクローズドループ制御を行う (Algorithm 1, §4.1).

- **GC-IDM アーキテクチャ**: 3 層 MLP (隠れ次元 512, LayerNorm, GELU, dropout 10%, ~1.5M パラメータ). 入力は $z_t \| z_g$ の連結. 残りホライズン $h_t$ は正規化後に正弦波エンコーディング (64 次元) を経て AdaLN-Zero 変調 (式 6) により MLP 出力を変調する (§4.2)
- **凍結埋め込み上の教師あり学習**: LeWM の学習に使用した同一のオフラインデモデータセットから, ランダムなホライズン $h \in [1, H_{\max}]$ で $(z_t, z_{t+h}, a_t)$ のタプルを構成し, MSE 回帰 (式 7) で学習. 追加の環境インタラクションは不要 (§4.2)
- **毎ステップ再エンコード**: テスト時に各ステップで現在の観測を凍結エンコーダで再エンコードし, 真の現在状態から行動を決定. オープンループの軌道コミットを排除し, 単一ステップ誤差の蓄積を防止 (§4.2, Appendix A の式 9)

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

[[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/leworldmodel-stable-end-to-end-joint-embedding-predictive-architecture-from-pixels|Maes+ 2026]] (LeWM) がワールドモデルのバックボーンを提供し, [[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics|Balestriero & LeCun 2025]] (LeJEPA/SIGReg) がその正則化基盤を与えた. GLAMOR (Paster+ 2021) は画素から再帰的逆ダイナミクスモデルを学習し行動系列を予測する先行研究だが, マルチステップ行動にコミットする点が異なる. Seer (Tian+ 2025) や Latent Diffusion Planning (Xie+ 2025) は将来状態を予測してから行動を復号する二段階方式を採用する.

本論文の新規性は, JEPA ワールドモデルの凍結潜在空間上で目標条件付き逆ダイナミクスを直接学習し, テスト時の反復探索を完全に排除した点にある. 単一ステップ予測 + 毎ステップ再エンコードによるクローズドループ設計, および残りホライズンの AdaLN-Zero 変調が, 先行する逆ダイナミクス手法との主な差別化要素である.

### どのように訓練・最適化したのか?

- **損失関数 / 最適化目的**: GC-IDM の損失は $\mathcal{L}_{\text{gc-idm}}(\psi) = \mathbb{E}_{(t,h) \sim D} \| \text{gc-idm}_\psi(z_t, z_{t+h}, h) - a_t \|_2^2$ (式 7). 凍結エンコーダ出力に対する MSE 回帰. 勾配は GC-IDM パラメータ $\psi$ のみに流れる
- **データセット**: LeWM の学習に使用されたオフラインデモデータセットをそのまま再利用. 4 環境: Two-Room (2D ナビゲーション), Push-T (接触操作), OGBench-Cube (3D 物体操作), Reacher (連続リーチング). 各環境の行動次元は 2–5. 学習は AdamW (lr = $10^{-3}$, weight decay = $10^{-4}$), バッチサイズ 1024, 50 エポック, cosine annealing, gradient clipping (norm 1.0). 各環境で単一 GPU 約 20 分 (§4.2, Appendix F)

### どのように検証したか? 指標と結果は?

凍結 LeWM チェックポイント上で GC-IDM と CEM を同一条件で比較. 評価プロトコルは n=50 (LeWM 論文準拠) と n=200 (低分散) の 2 種. 3 シード (42, 123, 456) の平均 ± 標準偏差を報告.

**主要結果 (Table 1)**: GC-IDM は 8 設定中 7 設定で CEM と同等以上の成功率を達成. Two-Room: 100% vs 84%, Reacher: 99.7% vs 70.3%, OGBench-Cube: 98.7% vs 67.0% (いずれも n=200). Push-T のみ n=50 で CEM が僅かに優位 (84.7% vs 89.3%) だが n=200 では逆転 (84.2% vs 82.5%). 計画コストは 100–130 倍削減 (1 plan call あたり ~0.4 ms vs ~42 ms).

**ソルバーファミリ比較 (Table G, Figure 4)**: CEM, iCEM, MPPI, GradientSolver の全てに対し, GC-IDM は全環境で最高成功率を達成. 最良サンプリングベースラインとの差は Two-Room +12.5 pp, Push-T +1.7 pp, Cube +28.2 pp, Reacher +29.4 pp.

**アブレーション**: ホライズン監視の除去で平均 42 pp 低下 (Table F). ノイズ注入は不要 (Table E). 目標距離ロバスト性 (Table 2), データ効率 (Table D), アーキテクチャ感度 (Table H), 評価バジェット (Table J), ホールドアウト検証 (Table K) を網羅.

**軌道品質 (Table 4)**: GC-IDM は CEM と比較して 15–36 倍滑らかな行動 (action jerk) を生成し, 4 環境中 3 環境で潜在空間単調性 (latent monotonicity) が優位.

### 検証結果に基づいた議論, 明らかになった課題はあるか?

(§6 Conclusion and Future Work, Appendix G) 著者は以下の限界と将来課題を明示的に述べている:

- Push-T のような長い接触系列を要するタスクでは, 局所的逆復元が困難になり GC-IDM の優位性が低下する. これは逆ダイナミクスの本質的限界であり, GC-IDM を高速提案として使い CEM を補正器として併用するハイブリッド方式が自然な拡張として挙げられている
- 単一のワールドモデルバックボーン (LeWM) のみで検証しており, DINO-WM のように空間パッチ特徴を生成する JEPA への適用にはアーキテクチャ変更が必要
- 行動空間は 2–5 自由度に限定. LIBERO (7 DoF) 等のより高次元な行動空間への拡張は未検証
- (§6) 正則化子自体の役割の解明 (等方 vs 非等方潜在空間の比較) が今後の課題として挙げられている
- コードは受理後に公開予定で, 現時点では未公開

---
## 自身の研究との関連

本論文は我々の研究と極めて密接に関連している. 我々は LeWM と SIGReg の次元不一致問題を研究しているが, 本論文は SIGReg が生成する潜在幾何の構造を活用して CEM を完全に置き換える方向に進んでいる. 特に以下の点が重要である:

- **SIGReg の潜在幾何が計画を簡素化する**: 本論文の中心的洞察は, SIGReg による等方ガウス正則化が潜在空間を十分に滑らかにし, オンライン探索を不要にするというものである. [[papers/Klindt-arXiv2026-When_LeJEPA_Learn/when-does-lejepa-learn-a-world-model|Klindt+ 2026]] が示した線形識別可能性 (エンコーダ出力次元 = 潜在次元の場合) と組み合わせると, SIGReg が理論的に保証する幾何構造が, 本論文で経験的に示された逆ダイナミクスの学習容易性を説明する理論的基盤となりうる
- **次元不一致問題との接点**: Klindt+ 2026 がオープン問題として残した次元不一致時の挙動は, GC-IDM の有効性にも影響する可能性がある. エンコーダ出力次元と真の潜在次元が不一致の場合, 潜在幾何の等方性が崩れ, 逆ダイナミクスの条件数 (式 17) が悪化する可能性がある. 我々の SIGReg 次元不一致研究の結果は, GC-IDM の適用可能範囲を理論的に特定する手がかりとなる
- **CEM 代替としての実用的意義**: LeWM のボトルネックが CEM にあるという定量的証拠 (45,000 predictor 呼び出し / plan call) は, 我々が LeWM を実ロボット環境に適用する際の設計指針として直接有用

---
## 追加議論


---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@article{nguyen2026latent,
  title={Latent Geometry Beyond Search: Amortizing Planning in World Models},
  author={Nguyen, Hoang and Xu, Xiaohao and Huang, Xiaonan},
  journal={arXiv preprint arXiv:2605.08732},
  year={2026}
}
```
</details>
