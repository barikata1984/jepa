---
Title: "When Does LeJEPA Learn a World Model?"
Authors:
  - Klindt, David
  - LeCun, Yann
  - Balestriero, Randall
Year: 2026
Venue: arXiv
Tags:
  - "jepa"
  - "identifiability"
  - "sigreg"
  - "world-model"
  - "representation-learning"
  - "spectral-analysis"
PDF: "[[papers/Klindt-arXiv2026-When_LeJEPA_Learn/main.pdf|📃]]"
Import Date: "2026-06-07"
Read Date: 2026-06-07
Executive Summary: LeJEPA (alignment + SIGReg による等方ガウス正則化) が, ガウス潜在変数を持つ世界において, 真の潜在変数を回転の不定性を除いて線形に復元 (linear identifiability) することを証明した. エルミート多項式によるスペクトル分解を用いて, 非線形写像がビュー間相関を厳密に低下させることを示す (定理 1). 逆方向として, この線形識別可能性を与える潜在分布がガウスに限られることを Sturm–Liouville 理論で証明した (定理 2). 近似識別可能性 (定理 3) と潜在空間計画の最適性 (定理 4) も示され, Lean 4 で形式検証されている. ただし理論はエンコーダ出力次元 = 潜在次元を仮定しており, 次元不一致時の挙動は open problem として残されている.
Citekey: Klindt-arXiv2026-When_LeJEPA_Learn
BibTeX Key: klindt2026when
DOI:
Relevance: 5
Repository: https://github.com/klindtlab/lejepa-identifiability
Category: note
Template Version: v2.3
---

## Executive Summary
LeJEPA (alignment + SIGReg による等方ガウス正則化) が, ガウス潜在変数を持つ世界において, 真の潜在変数を回転の不定性を除いて線形に復元 (linear identifiability) することを証明した. エルミート多項式によるスペクトル分解を用いて, 非線形写像がビュー間相関を厳密に低下させることを示す (定理 1). 逆方向として, この線形識別可能性を与える潜在分布がガウスに限られることを Sturm–Liouville 理論で証明した (定理 2). 近似識別可能性 (定理 3) と潜在空間計画の最適性 (定理 4) も示され, Lean 4 で形式検証されている. ただし理論はエンコーダ出力次元 = 潜在次元を仮定しており, 次元不一致時の挙動は open problem として残されている.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

LeJEPA (alignment 損失 + SIGReg 正則化) が学習する表現は, 世界の真の潜在変数を復元しているのか? 従来の JEPA は経験的に有効な表現を学習していたが, 識別可能性 (identifiability) の理論的保証は存在しなかった. 本論文は"いつ LeJEPA がワールドモデルを学習するか"に対して, 必要十分条件を与えた.

### 提案手法のアプローチと, その根幹をなす要素は何か?

ガウス潜在変数が独立・定常・加法ノイズ遷移 (Ornstein–Uhlenbeck 過程) に従う世界を仮定し, LeJEPA の学習目的 (alignment + ガウス正則化) の最適解が真の潜在変数の直交変換であることを証明する理論的フレームワークを構築した.

- **エルミート多項式によるスペクトル分解**: 任意の写像 $h$ をガウス測度上の直交基底 (エルミート多項式) で展開し, 各次数 $d$ の成分が遷移演算子で固有値 $\rho^d$ を持つことを利用する. $\rho < 1$ なので非線形成分 ($d \geq 2$) は線形成分 ($d = 1$) より厳密に減衰し, ビュー間相関が最大になるのは線形写像に限られる (式 (4): $E[h_i(z')h_i(z)] = w_1 \cdot \rho + w_2 \cdot \rho^2 + \cdots \leq \rho$, 等号は $w_1 = 1$ のときのみ)
- **ガウス性制約 (SIGReg)**: $h(z) \sim \mathcal{N}(0, I_n)$ を強制することで, 最適解の写像行列 $Q$ が直交行列に制限される ($QQ^\top = I_n$)
- **Sturm–Liouville 理論による逆方向**: 非ガウス分布では遷移演算子の第一固有関数が非線形になるため, 線形識別可能性が成立しないことを示す

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

[[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics|Balestriero+ 2025]] が SIGReg を導入し, 安定した JEPA 学習を実現した. VICReg (Bardes+ 2021) は二次モーメントの正則化, InfoNCE (van den Oord+ 2018) は暗黙的ガウス化を行う. Slow Feature Analysis (Wiskott & Sejnowski 2002, Sprekeler+ 2014) は遷移演算子の最も遅い固有関数を抽出する枠組みを提供し, 本論文のスペクトル解析の数学的基盤となっている. 非線形 ICA (Hyvarinen+ 2016, 2017, Khemakhem+ 2020) は時間的対比学習による識別可能性を示したが, JEPA アーキテクチャへの結果は存在しなかった.

新規性は, JEPA に対する初の識別可能性結果であること. alignment + ガウス正則化という特定の組み合わせが, (i) ガウス世界で線形識別可能性を保証し (定理 1), (ii) ガウスがこの保証を与える唯一の分布であること (定理 2) を, 順方向と逆方向の両方で完全に特徴づけた点. 古典的 ICA ではガウスが分離不可能な唯一の分布であったのに対し, 非線形設定では逆にガウスが識別可能性を与える唯一の分布であるという, ICA の物語の反転を示した.

### どのように訓練・最適化したのか?

- **損失関数**: $L(h) = E[\|h(z') - h(z)\|^2]$ (alignment) を $h(z) \sim \mathcal{N}(0, I_n)$ (SIGReg による正則化) の制約下で最小化. 実装上は $L = \lambda L_{\text{SIG}} + (1-\lambda) L_{\text{inv}}$ として重み付け
- **データセット**: (1) 合成 2D データ (spiral, sinusoidal shear, parabolic shear, RealNVP), (2) 合成高次元データ (RealNVP mixing, $N \in \{2, 4, \ldots, 1024\}$), (3) 一般化正規分布 (形状パラメータ $\alpha$ スイープ), (4) DMC Reacher ピクセル入力 (10K RL エピソード, OU サンプリングと RL 軌跡の 2 条件) — いずれも真の潜在変数が既知であり, 線形回帰 $R^2(h \to z)$ で識別可能性を定量評価可能な設定

### どのように検証したか? 指標と結果は?

定理ごとに対応する実験で検証:

- **定理 1 (線形識別可能性)**: 4 種の非線形混合関数 (2D) と高次元スケーリング ($N$ 最大 1024) で, SIGReg/VICReg が $R^2 > 0.999$ を達成 (Table 1). InfoNCE は高次元でカーネル幅固定のため劣化
- **定理 2 (ガウスの一意性)**: 一般化正規分布の形状パラメータ $\alpha$ をスイープし, $R^2$ が $\alpha = 2$ (ガウス) で鋭いピークを示すことを確認 (Fig. 4b). DMC Reacher で OU サンプリング ($R^2 = 0.95$) と RL 軌跡 ($R^2 < 0.5$) の対比 (Table 2)
- **定理 3 (近似識別可能性)**: 全実験の $(\varepsilon, \delta)$ から計算した理論上界が実際の復元誤差を上回ることを確認 (Fig. 4a)
- **定理 4 (最適潜在計画)**: DMC Reacher でゴール到達の制御コストが, OU エンコーダではオラクルと統計的に区別不能, RL 軌跡エンコーダでは上方バイアス (Fig. 4c,d). 制御コストが $R^2$ と単調に相関

### 検証結果に基づいた議論, 明らかになった課題はあるか?

(§7 Limitations より) 著者は 3 つの制約を明示的に議論している:

1. **潜在変数のガウス性**: 実世界の潜在変数がガウスであるかは観測からは検証不能. ただし, タスク関連の潜在変数は多数の微視変数の集約であり, 中心極限定理によりガウスに近づくという議論を提示
2. **次元不一致 ($m \neq n$)**: 定理はエンコーダ出力次元 $m$ が真の潜在次元 $n$ と一致することを仮定. $m < n$ では"どの部分空間が選択されるか, あるいは superposition が生じるかを, ガウス制約は決定しない". $m > n$ では余剰次元が崩壊するか冗長性を符号化する. これを"JEPA 設計に直接的な帰結を持つ重要な open problem"と明記
3. **有限サンプルと最適化**: 結果は母集団レベルの大域的最適解に関するもの. 定理 3 は連続的劣化を示すが, サンプルサイズや学習ダイナミクスへのスケーリングは未解決

(§8 Discussion より) 行動条件付き遷移 $\hat{p}(\hat{z}' | \hat{z}, a)$ の学習は本論文の範囲外であり, 介入的因果表現学習への接続が自然な拡張方向. データの分布に関しては, 同じ物理系でも等方的サンプリング (OU) ではガウス仮定が成立するが, 目標指向方策 (RL) では低エントロピー領域に分布が集中し識別可能性が崩壊する.

---
## 自身の研究との関連

本論文は我々の研究に対して 2 つの方向で直接的に関連する.

**理論的裏付け**: 我々の Stage 0–2 実験で観測した SIGReg ミスマッチ (固有次元 ~3–6 vs 潜在空間 192 次元, 有効ランク ~40/192) は, 本論文 §7 が明示的に open problem と指摘する"次元不一致問題"($m > n$) の具体例である. 定理 1–2 はエンコーダ出力次元 $m = n$ を仮定しており, $m \gg n$ の場合に SIGReg が余剰次元にノイズを充填して予測学習を阻害する (SIGReg/pred 比 ~170) という我々の知見は, この理論的ギャップの実験的証拠となる.

**研究の位置づけ**: 本論文は問題を理論的に同定したが解法は提示していない. [[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics|Balestriero+ 2025]] の SIGReg を [[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/leworldmodel-stable-end-to-end-joint-embedding-predictive-architecture-from-pixels|Maes+ 2026]] の LeWM に適用した場合のロボット操作データでの次元不一致問題に対し, RDMReg (Rectified LpJEPA, Kuang+ 2026) 等の代替正則化が有効かを検証することは, この open problem に対する実験的貢献となりうる.

---
## 追加議論


---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@article{klindt2026when,
  title={When Does {LeJEPA} Learn a World Model?},
  author={Klindt, David and LeCun, Yann and Balestriero, Randall},
  journal={arXiv preprint arXiv:2605.26379},
  year={2026}
}
```
</details>
