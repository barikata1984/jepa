---
Title: "On Epistemics in Expected Free Energy for Linear Gaussian State Space Models"
Authors:
  - Koudahl, Magnus T.
  - Kouw, Wouter M.
  - de Vries, Bert
Year: 2021
Venue: Entropy
Tags:
  - "active-inference"
  - "expected-free-energy"
  - "epistemic-value"
  - "linear-gaussian-state-space-model"
  - "exploration-exploitation"
  - "mutual-information"
PDF: "[[papers/Koudahl-Entropy2021-Epistemics_Expected_Free/main.pdf|📃]]"
Import Date: "2026-06-08"
Read Date: 2026-06-08
Executive Summary: "線形ガウス状態空間モデル (LGDS) において, Active Inference の Expected Free Energy (EFE) 最小化がエピステミックな探索行動を生まないことを証明した. EFE を相互情報量とクロスエントロピーに分解し, 道具的価値項との結合時にエントロピー項が相殺され, 残るのは観測ノイズのみに依存する定数 (ambiguity) と KL 制御項だけであることを示した. 加法的制御では純粋なエピステミック項も状態遷移から独立する一方, 乗法的制御 (遷移行列の切替) では探索が再出現する."
Citekey: Koudahl-Entropy2021-Epistemics_Expected_Free
BibTeX Key: koudahl2021on
DOI: 10.3390/e23121565
Relevance: 3
Repository: "https://github.com/biaslab/efe_lgds"
Category: note
Template Version: v2.3
---

## Executive Summary
線形ガウス状態空間モデル (LGDS) において, Active Inference の Expected Free Energy (EFE) 最小化がエピステミックな探索行動を生まないことを証明した. EFE を相互情報量とクロスエントロピーに分解し, 道具的価値項との結合時にエントロピー項が相殺され, 残るのは観測ノイズのみに依存する定数 (ambiguity) と KL 制御項だけであることを示した. 加法的制御では純粋なエピステミック項も状態遷移から独立する一方, 乗法的制御 (遷移行列の切替) では探索が再出現する.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

LGDS に Active Inference (AIF) を適用した場合, EFE の最小化がエピステミック駆動 (探索行動) をもたらすか否か, という問いに答えた. AIF の文献では EFE が探索と利用のトレードオフを自動的にもたらすと広く仮定されていたが, LGDS という重要かつ広範なモデルクラスにおいてこの仮定が成立するかは未検証であった.

### 提案手法のアプローチと, その根幹をなす要素は何か?

EFE を相互情報量 (MI) 項とクロスエントロピー項に分解し (式 34c), それぞれを LGDS の場合に閉形式で導出した上で, 両者を結合した際に何が起こるかを解析した. 手法の核心は, エピステミック項 (負の MI) と道具的価値項 (クロスエントロピー) を別々に導出し, 再結合時のエントロピー $H[x_k|u_k]$ の相殺を明示的に示す点にある.

- EFE を MI とクロスエントロピーに分解する枠組み (式 34c): $G(u_k) \geq \text{cross-entropy} - \text{MI}$
- LGDS における MI の閉形式表現 (式 36): $I[x_k, z_k] = \frac{1}{2} \log |I + \Sigma_x^{-1} A \Sigma_{z_k} A^T|$
- 加法的制御と乗法的制御の 2 つのモデル構造 (式 2–6) の明示的な区別
- 道具的価値項を KL ダイバージェンス + エントロピーに分解 (式 41)
- 結合時の ambiguity 項の定数性の証明 (式 45): $H[x_k|z_k, u_k] = \frac{1}{2}(n\log 2\pi + \log|\Sigma_x| + n)$

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

Friston et al. [8] による EFE の定式化と, Sajid et al. [1] および Friston et al. [2] による離散モデルでの探索・利用の分析を主な先行研究とする. また Solopchuk [35] が加法的制御の線形ダイナミクスでエピステミック項の非依存性を示していた.

新規性は以下の 3 点:
1. LGDS における EFE 全体が KL 制御 + 定数に退化し, エピステミック駆動が消失することの厳密な証明 (§5.5)
2. エピステミック項を単独で考えた場合でも, 加法的制御では状態遷移とエピステミック価値が分離すること (§5.3), 一方で乗法的制御では探索が維持されること (§5.4) の対比分析
3. 連続状態空間・線形ガウスモデルでの EFE の完全な導出 (従来は離散モデルが主流)

### どのように訓練・最適化したのか?

- **損失関数 / 最適化目的**: N/A: 学習を伴うモデルではなく, 解析的な理論研究である. 実験では EFE (式 30–31) や MI (式 36) を閉形式で計算し, 制御信号の選択に用いた.
- **データセット**: N/A: 合成的な設定 (2次元の LGDS) のみを使用. 既定のパラメータ (式 46–52) による数値検証.

### どのように検証したか? 指標と結果は?

3 つの数値実験で解析的な主張を検証した:

1. **加法的制御での純粋エピステミクス** (§6.1, Table 1): 4 つのパラメータ設定 $\Theta_{1:4}$ で MI を計算. 平均の変化は MI に影響せず ($\Theta_1$ と $\Theta_2$ が同値 $-1.386$), 分散の変化のみが影響 ($\Theta_3$ と $\Theta_4$ が同値 $-1.609$). 式 38b の予測と一致.

2. **乗法的制御での純粋エピステミクス** (§6.2, Table 2): 遷移行列の大きさ (0.1 から 100 まで 4 桁) に対する MI を計算. 大きな遷移ほど負の MI が低下 ($-0.698$ から $-9.211$). 式 40 の予測と一致.

3. **完全 EFE** (§6.3, Tables 3–4): 加法・乗法の両方で, ambiguity 項が一定値 $2.84$ であることを確認. EFE が KL + 定数に分解されることを実証. 乗法的制御 (Table 3) でもエピステミック項と道具的項が正確に相殺.

### 検証結果に基づいた議論, 明らかになった課題はあるか?

(§7 Discussion より) 線形観測モデルへの強い依存が明確な制約として挙げられている. MI の閉形式が得られるのは線形ガウスの場合に限られ, 近似が必要な非線形モデルでは本解析が直接適用できない.

(§7 Discussion より) Extended Kalman Filter のように共分散行列を近似する特殊ケースでは本解析が適用可能であり, 非線形ガウス状態空間モデルへの拡張が今後の研究として示唆されている.

(§8 Conclusions より) 乗法的制御 (遷移行列選択) が古典的な Hidden Markov Model の構造に類似しており, 離散モデルの最近の進展を連続状態空間に適用することが将来の方向として述べられている.

---
## 自身の研究との関連

LeWM では SIGReg により潜在分布を等方ガウスに制約している. 本論文の中心的な結果, すなわち線形ガウス SSM では EFE のエピステミック駆動が消失するという知見は, ガウス潜在構造がプランニングにおける探索をどの程度支援できるかに関して重要な示唆を与える. 具体的には, 潜在空間がガウス的であること自体はエピステミックな探索を保証せず, 探索を実現するには遷移ダイナミクスの構造 (乗法的制御のような非加法的な制御信号) が必要となる. LeWM の潜在世界モデルが加法的遷移に近い構造を持つ場合, EFE ベースのプランニングを導入しても探索が生じない可能性がある. ただし LeWM は非線形モデルであるため, 本論文の結果が直接適用される訳ではなく, 非線形性がエピステミック駆動を回復させる可能性がある点は留意すべきである. 関連度は 3: 直接的な手法の借用ではないが, ガウス潜在空間と探索の関係を理解する理論的基盤として参考になる.

---
## 追加議論


---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@article{koudahl2021on,
  title     = {On Epistemics in Expected Free Energy for Linear Gaussian State Space Models},
  author    = {Koudahl, Magnus T. and Kouw, Wouter M. and de Vries, Bert},
  journal   = {Entropy},
  volume    = {23},
  number    = {12},
  pages     = {1565},
  year      = {2021},
  publisher = {MDPI},
  doi       = {10.3390/e23121565}
}
```
</details>
