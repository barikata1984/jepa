---
Title: "Inference via Interpolation: Contrastive Representations Provably Enable Planning and Inference"
Authors:
  - Eysenbach, Benjamin
  - Myers, Vivek
  - Salakhutdinov, Ruslan
  - Levine, Sergey
Year: 2024
Venue: NeurIPS
Tags:
  - "contrastive-learning"
  - "gauss-markov-chain"
  - "planning"
  - "representation-learning"
  - "probabilistic-inference"
  - "time-series"
PDF: "[[papers/Eysenbach-NeurIPS2024-Inference_Interpolation/main.pdf|📃]]"
Import Date: "2026-06-08"
Read Date: 2026-06-08
Executive Summary: "時系列データに対する正則化付き対比学習が, 周辺分布が等方ガウスとなる表現を獲得し, その結果として表現列が Gauss-Markov 連鎖に従うことを証明. これにより, 将来状態の予測や中間経由点の推定 (計画) が低次元行列の逆行列計算に帰着され, 特殊ケースでは初期表現と最終表現の線形補間と等価になる. 2D スパイラル・迷路・39/46 次元ロボット操作タスクで理論を数値的に検証し, 対比表現による計画が VIP や PCA ベースラインを大幅に上回ることを示した."
Citekey: Eysenbach-NeurIPS2024-Inference_Interpolation
BibTeX Key: eysenbach2024inference
DOI: "10.48550/arXiv.2403.04082"
Relevance: 5
Repository: "https://github.com/vivekmyers/contrastive_planning"
Category: note
Template Version: v2.3
---

## Executive Summary

時系列データに対する正則化付き対比学習が, 周辺分布が等方ガウスとなる表現を獲得し, その結果として表現列が Gauss-Markov 連鎖に従うことを証明. これにより, 将来状態の予測や中間経由点の推定 (計画) が低次元行列の逆行列計算に帰着され, 特殊ケースでは初期表現と最終表現の線形補間と等価になる. 2D スパイラル・迷路・39/46 次元ロボット操作タスクで理論を数値的に検証し, 対比表現による計画が VIP や PCA ベースラインを大幅に上回ることを示した.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

高次元の時系列データにおいて,"将来何が起こるか" (予測) および "初期状態と最終状態の間をどのような状態で通過するか" (計画・補間) という確率的推論を, 生成モデルに頼らず判別的手法 (対比学習) のみで閉形式に解けるか, という問いに答えた (§1). 従来, これらの推論は高次元空間で反復的な最適化や生成を必要としたが, 本論文は対比表現上では行列逆演算のみで実行可能であることを理論的に証明した.

### 提案手法のアプローチと, その根幹をなす要素は何か?

時系列データから正の対を生成し, 正則化付き symmetrized infoNCE で表現を学習する. 学習された表現の周辺分布が等方ガウスであること (仮定 1) と, 表現が確率比をエンコードすること (仮定 2) を組み合わせ, 表現列が Gauss-Markov 連鎖をなすことを証明する. この構造により, 任意の条件付き分布がガウスの閉形式で得られる.

- **二重エンコーダのパラメトリゼーション (§4.1)**: 状態内容をエンコードする $\psi(\cdot)$ と, 多ステップ予測を担う線形射影 $\phi(x) = A\psi(x)$ の 2 つを学習. 行列 $A$ が時間的非対称性を捕捉する
- **等方ガウス周辺分布の仮定と正当化 (§3.1, Appendix A.1)**: 表現の期待 L2 ノルム制約 (式 3) の下で infoNCE の uniformity 項を最大化すると, 最大エントロピー分布として等方ガウスが出現する
- **Lemma 1 — 予測分布 (§4.2)**: 将来の表現 $\psi_{t^+}$ の条件付き分布が $\mathcal{N}(\frac{c}{c+1}A\psi_0, \frac{c}{c+1}I)$ となることを証明. 予測が表現の線形関数
- **Lemma 2 — 経由点事後分布 (§4.3)**: 初期・最終表現が与えられたとき, 中間経由点表現の事後分布がガウスとなり, その平均と共分散が $A$, $c$ の閉形式で記述される
- **Lemma 3 — 多段計画 (§4.4)**: $n$ 個の中間状態の同時分布が三重対角精度行列を持つガウスとなり, 各経由点の周辺分布が行列逆演算で得られる

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

Arora+ (2016) の単語埋め込みにおけるガウス性仮定とランダムウォーク解析, Wang & Isola (2020) の infoNCE の alignment/uniformity 分解, Eysenbach+ (2022) のゴール条件付き RL としての対比学習が主要な基盤. Sequential VAE (Zhao+ 2017) は再構成損失による生成的推論を行うが計算コストが高い.

本論文の新規性は, 対比学習 (判別的手法) が Gauss-Markov 連鎖という生成的グラフィカルモデルの構造を暗黙的に獲得することを理論的に証明した点にある. これにより, 再構成を一切行わず, 表現空間上の行列演算のみで予測・計画が閉形式に解ける. 先行研究は主に単語埋め込みのアナロジー解法を説明する目的だったが, 本論文は高次元時系列の推論ツールとしての応用を示した.

### どのように訓練・最適化したのか?

- **損失関数 / 最適化目的**: symmetrized infoNCE (式 2) に期待 L2 ノルム制約 (式 3) を追加. 制約は正則化項 $\lambda \mathbb{E}[\|\psi(x)\|_2^2]$ として付加し, 重み $\lambda$ を双対勾配降下法で動的に調整 (§3). 正の対は割引状態占有測度 $p_{t^+}(x_{t^+} | x)$ からサンプリング
- **データセット**: (1) 2D スパイラル軌跡の合成データ (§5.1), (2) 2D 迷路環境 (D4RL 由来, §5.2), (3) door-human-v0 (39 次元, D4RL, §5.3), (4) hammer-human-v0 (46 次元, D4RL, §5.3). 学習・検証のスプリット詳細は明示されていないが, 計画の評価には検証セット上の軌跡を使用

### どのように検証したか? 指標と結果は?

**合成データ (§5.1)**: 2D スパイラルデータで予測・逆推論・経由点推論を可視化. 対比表現が非線形構造を正しく捉え, 時間的に隣接しないがユークリッド距離では近い状態に低い尤度を付与.

**迷路計画 (§5.2)**: 比例制御器でゴール到達率を評価. ベースラインは VIP, PCA, 計画なしの 3 手法. 最困難ゴール (初期 L2 距離 > 8) で成功率が計画なし 18% → 対比表現による計画 84% (4.5 倍向上, Fig. 5). VIP と PCA は計画なしと大差なし.

**高次元タスク (§5.3)**: door-human-v0 (39 次元) と hammer-human-v0 (46 次元) で, 検証軌跡の初期・最終観測から 5 つの中間経由点を線形補間 (式 7) で推定. 経由点の MSE で評価 (最近傍検索で表現を観測に変換). 対比表現による計画が PCA・VIP・補間なしを大幅に下回る MSE を達成 (Fig. 6, Fig. 8). 誤差棒は検証セット 500 軌跡の標準偏差.

### 検証結果に基づいた議論, 明らかになった課題はあるか?

(§6 Limitations より) 解析は §3.1 の 2 つの仮定 (周辺分布のガウス性, 表現が確率比を完全にエンコードすること) に依存しており, これらの近似誤差が推論結果にどのように伝播するかは未解明. 十分に表現力のある関数近似器があれば常にこれらの仮定を満たせるかどうかも open question として残されている.

---
## 自身の研究との関連

本論文の Gauss-Markov 連鎖の結果は, LeWM ([[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/leworldmodel-stable-end-to-end-joint-embedding-predictive-architecture-from-pixels|Maes+ 2026]]) が SIGReg ([[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics|Balestriero+ 2025]]) で強制する等方ガウス潜在分布と直接的に接続する. SIGReg が表現の周辺分布をガウスにする以上, 本論文の理論が示すように, 潜在表現列は Gauss-Markov 連鎖をなし, 計画が行列逆演算に帰着される可能性がある.

我々の研究で観測されている次元不一致問題 (内在次元 ~6 vs 潜在次元 192) は, SIGReg が全 192 次元を等方ガウスに膨張させることで情報が薄く広がる現象と解釈できる. 本論文の枠組みでは, 表現のノルム制約パラメータ $c$ が小さい (強い正則化) と予測分布の平均が原点に縮退する (Example 3, §4.3). SIGReg の強い正則化が同様の効果を生み, 計画に有用な信号を希釈している可能性がある.

逆に, SIGReg のガウス構造を"バグではなく機能"として活用する方向を支持する結果でもある. Gauss-Markov 構造が成立するなら, CEM のようなサンプリングベース最適化ではなく, Lemma 2–3 の閉形式解による計画が可能になる. [[papers/Klindt-arXiv2026-When_LeJEPA_Learn/when-does-lejepa-learn-a-world-model|Klindt+ 2026]] が示す線形識別可能性の結果と合わせると, SIGReg + 線形予測器の組み合わせで, 潜在空間上の解析的計画が理論的に正当化される.

---
## 追加議論


---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@inproceedings{eysenbach2024inference,
  title     = {Inference via Interpolation: Contrastive Representations Provably Enable Planning and Inference},
  author    = {Eysenbach, Benjamin and Myers, Vivek and Salakhutdinov, Ruslan and Levine, Sergey},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {37},
  year      = {2024}
}
```
</details>
