---
Title: "VJEPA: Variational Joint Embedding Predictive Architectures as Probabilistic World Models"
Authors:
  - Huang, Yongchao
Year: 2026
Venue: ICML
Tags:
  - "joint-embedding-predictive-architecture"
  - "variational-inference"
  - "world-model"
  - "collapse-avoidance"
  - "bayesian-filtering"
  - "latent-dynamics"
PDF: "[[papers/Huang-ICML2026-VJEPA/main.pdf|📃]]"
Import Date: "2026-06-08"
Read Date: 2026-06-08
Executive Summary: 決定論的 JEPA の回帰損失が等方ガウス尤度と等価である点に着目し, 予測分布を明示的に学習する変分定式化 VJEPA を導入する. ターゲットエンコーダからの推論分布に対する負の対数尤度と KL 正則化を組み合わせた目的関数により, 観測再構成なしで潜在空間の予測的相互情報量の下界を最大化し, 表現崩壊の回避を目的関数レベルで保証する. さらに Product of Experts でダイナミクス専門家と制約事前分布を分離する BJEPA に拡張し, ゼロショットタスク転移を可能にする. "Noisy TV" 線形系実験で, 生成モデルが高分散外乱に汚染される一方, VJEPA/BJEPA は信号回復 R2 > 0.84 を維持した.
Citekey: Huang-ICML2026-VJEPA
BibTeX Key: huang2026vjepa
DOI: ""
Relevance: 4
Repository: "https://github.com/YongchaoHuang/VJEPA"
Category: note
Template Version: v2.3
---

## Executive Summary
決定論的 JEPA の回帰損失が等方ガウス尤度と等価である点に着目し, 予測分布を明示的に学習する変分定式化 VJEPA を導入する. ターゲットエンコーダからの推論分布に対する負の対数尤度と KL 正則化を組み合わせた目的関数により, 観測再構成なしで潜在空間の予測的相互情報量の下界を最大化し, 表現崩壊の回避を目的関数レベルで保証する. さらに Product of Experts でダイナミクス専門家と制約事前分布を分離する BJEPA に拡張し, ゼロショットタスク転移を可能にする."Noisy TV" 線形系実験で, 生成モデルが高分散外乱に汚染される一方, VJEPA/BJEPA は信号回復 R2 > 0.84 を維持した.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

既存の JEPA は決定論的回帰目的で訓練されるため, (1) 潜在予測の確率的意味論が暗黙的で不明瞭であり, (2) 確率的環境における将来の不確実性を表現できず, (3) 学習された表現が最適制御の十分情報状態となる条件が未定式化であった. 本論文はこれらを統一的に解決する確率的定式化を与え, さらに JEPA の逐次予測が観測の自己回帰尤度分解を必要としないことを理論的に示した.

### 提案手法のアプローチと, その根幹をなす要素は何か?

JEPA の MSE 損失が固定分散の等方ガウス尤度と等価であるという観察 (§3, Eq. 6) から出発し, 点推定を分布予測に置き換える変分拡張を行う. コンテキストエンコーダが履歴を潜在状態に圧縮し, 確率的予測器が将来の潜在表現の分布を出力する. 訓練は EMA ターゲットエンコーダが提供する推論分布からのサンプルに対して行われる.

- **確率的予測モデル** $p_\phi(Z_T | Z_C, \xi_T)$: 決定論的予測器の代わりに, 将来の潜在表現に対する条件付き分布を学習する (§4.1, Eq. 7).
- **変分目的関数**: ターゲットエンコーダの推論分布 $q_{\theta'}(Z_T | x_T)$ に対する負の対数尤度と, 固定事前分布への KL 正則化の和 (§4.3, Eq. 11). 崩壊回避は KL 項と予測的ミスマッチの相互作用から目的関数レベルで保証される (Theorem 1, §4.7).
- **EMA ターゲットエンコーダによる推論分布**: JEPA と同様に EMA で更新されるターゲットエンコーダが, 表現空間における"事後分布"を定義する (§4.2, Eq. 10).
- **時間インデックス化による潜在状態空間モデル**: コンテキスト・ターゲットを時間的に構成すると, VJEPA は潜在遷移モデル $p_\phi(Z_{t+\Delta} | Z_t, \xi_{t+\Delta})$ を誘導し, 信念伝播・フィルタリングを観測尤度なしで実現する (§5).

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

主要な先行研究として, I-JEPA/V-JEPA [[papers/Assran-arXiv2025-V-JEPA_Self-Supervised_Video/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning|Assran+ 2025]] (決定論的 JEPA の画像・動画拡張), PlaNet/Dreamer (観測再構成を伴う潜在ダイナミクスモデル), Predictive State Representations (PSR) (予測的統計量としての状態表現), Active Inference (変分自由エネルギー最小化) を挙げている.

新規性は以下の点にある:

1. **JEPA に対する初の変分定式化**: 既存 JEPA は全て決定論的回帰目的であり, 確率的拡張は存在しなかった. VJEPA は予測分布を明示的にモデル化し, 不確実性推定・マルチモーダル予測を可能にした.
2. **崩壊回避の目的関数レベルの保証**: SIGReg や VICReg のような補助正則化ではなく, 変分目的関数そのものが崩壊と大域最適性の非両立を保証する (Theorem 1). これは [[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics|Balestriero+ 2025]] の SIGReg や [[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/leworldmodel-stable-end-to-end-joint-embedding-predictive-architecture-from-pixels|Maes+ 2026]] のアプローチとは異なる代替的メカニズムである.
3. **逐次モデリングと自己回帰の分離**: 時間的予測構造を導入しても観測レベルの自己回帰尤度分解が不要であることを定式化した.
4. **BJEPA による Product of Experts 分離**: ダイナミクス(尤度専門家)と制約(事前分布専門家)をモジュラーに分離し, ゼロショットタスク転移と潜在ベイズフィルタリングを統一的に実現した.

### どのように訓練・最適化したのか?

- **損失関数 / 最適化目的**: VJEPA 目的関数 (Eq. 11): $\mathcal{L}_{\text{VJEPA}} = \mathbb{E}_{Z_T \sim q_{\theta'}}[-\log p_\phi(Z_T | Z_C, \xi_T)] + \beta \cdot \text{KL}(q_{\theta'}(Z_T | x_T) \| p(Z_T))$. 第1項は予測尤度, 第2項は固定事前分布 $\mathcal{N}(0, I)$ への KL 正則化. BJEPA はこれに構造的事前分布への KL 項 $\gamma \cdot \text{KL}(p_{\text{like}} \| p_{\text{struct}})$ を加える (Eq. 33). コンテキストエンコーダ $\theta$ と予測器 $\phi$ は勾配降下で, ターゲットエンコーダ $\theta'$ は EMA (Eq. 3) で更新.
- **データセット**:"Noisy TV" 線形ガウス系 (§9). 観測次元 $D_x = 20$, 真の状態次元 $D_s = 4$. 信号は安定回転行列による線形ダイナミクス, 外乱は "sticky" ランダムウォーク. 外乱スケール $\sigma \in [0, 8]$ (9 段階). 連続訓練軌道 $T_{\text{train}} = 6000$ ステップ, テスト軌道 $T_{\text{test}} = 2000$ ステップ (Appendix J).

### どのように検証したか? 指標と結果は?

"Noisy TV" 線形系で 5 モデル (VAE, AR, JEPA, VJEPA, BJEPA) を比較. 全モデルの潜在次元は $D_z = 4$, 線形変換のみ使用. 評価は線形プローブによる決定係数 $R^2$ (信号回復・ノイズ回復) で行い, 訓練データとテストデータの両方で測定 (Table 4, §9.3).

主要な定量的結果 (テストセット $R^2$, 外乱スケール $\sigma = 8.0$, SNR = $-2.2$ dB):
- VAE: 信号 $R^2 = 0.499$, ノイズ $R^2 = 0.620$ (ノイズを優先的にエンコード)
- AR: 信号 $R^2 = 0.578$, ノイズ $R^2 = 0.449$
- JEPA: 信号 $R^2 = 0.930$, ノイズ $R^2 = 0.183$
- VJEPA: 信号 $R^2 = 0.870$, ノイズ $R^2 = 0.251$
- BJEPA: 信号 $R^2 = 0.841$, ノイズ $R^2 = 0.238$

JEPA 系は全ノイズスケールで $R^2 > 0.84$ を維持. 生成モデル (VAE, AR) はノイズ増加に伴い線形に劣化し, 高分散外乱に表現容量を割り当てた. 定性的にも, VAE/AR の再構成は高周波ノイズを追跡する一方, VJEPA/BJEPA は真の信号を忠実に追跡した (Fig. 4).

### 検証結果に基づいた議論, 明らかになった課題はあるか?

(§10.4 Limitations and Future Directions より) 著者は以下の制約を明示的に述べている:

1. **予測分布の表現力**: ガウス仮定による単峰性の制約. マルチモーダルな分岐 (例: 障害物回避の左右選択) では, 単峰ガウスがモードを平均化して不正確な信念を生む可能性がある. ガウス混合モデルや潜在拡散ヘッドへの拡張を今後の方向として挙げている.
2. **最適化ダイナミクス**: VJEPA の $\beta$ および BJEPA の $\gamma$ による予測損失と KL 正則化のバランスが重要. 正則化が強すぎると表現崩壊, 弱すぎると分散推定のキャリブレーション不良が起こる. 適応的バランス機構の開発を将来課題として挙げている.
3. (暗黙的制約) 実験は解析的に扱いやすい線形ガウス系に限定されており, 高次元ビジョンタスクやロボット制御タスクでの大規模実証は行われていない.

---
## 自身の研究との関連

本論文は, 我々が研究する LeWM の SIGReg 正則化とその問題点に対し, 理論的に異なる代替フレームワークを提供する. VJEPA の崩壊回避は SIGReg のような明示的なスペクトル正則化ではなく, 変分目的関数の構造そのものから導かれる (Theorem 1). これは SIGReg の既知の問題 (ハイパーパラメータ感度, 勾配干渉等) を回避する可能性がある一方, ガウス仮定の制約や $\beta$ チューニングの必要性という別種の課題を持つ.

BJEPA の Product of Experts による尤度と事前分布の分離は, LeWM のアクション条件付き予測に構造的事前知識を注入する方法として参考になる. 特に, ダイナミクス学習とタスク仕様を分離する設計は, ロボット操作における汎化性の観点で有用な設計原理である.

情報理論的分析 (§7) で示された VJEPA と Predictive Information Bottleneck の関係, および外乱不変性の形式的保証 (Proposition 1) は, 我々のノイズ環境下での表現学習の理論的根拠として直接参照できる.

---
## 追加議論


---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@inproceedings{huang2026vjepa,
  title     = {{VJEPA}: Variational Joint Embedding Predictive Architectures as Probabilistic World Models},
  author    = {Huang, Yongchao},
  booktitle = {Proceedings of the 43rd International Conference on Machine Learning (ICML)},
  year      = {2026},
  note      = {Poster. arXiv:2601.14354}
}
```
</details>
