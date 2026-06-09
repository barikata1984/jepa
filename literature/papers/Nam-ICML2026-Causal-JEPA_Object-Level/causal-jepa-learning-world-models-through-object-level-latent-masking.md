---
Title: "Causal-JEPA: Learning World Models through Object-Level Latent Masking"
Authors:
  - Nam, Heejeong
  - Le Lidec, Quentin
  - Maes, Lucas
  - LeCun, Yann
  - Balestriero, Randall
Year: 2026
Venue: ICML
Tags: ["jepa", "object-centric", "causal", "world-model", "latent-masking", "planning"]
PDF: "[[papers/Nam-ICML2026-Causal-JEPA_Object-Level/main.pdf|📃]]"
Import Date: "2026-06-09"
Read Date: 2026-06-09
Executive Summary: オブジェクト中心の world model において, 既存手法は object-centric 表現を学習するものの, オブジェクト間の相互依存ダイナミクスを訓練目的から必然化できていない. C-JEPA はオブジェクトスロットの潜在表現を時系列にわたってマスクし, マスクされたオブジェクトの状態を周囲オブジェクトとの相互作用から復元するよう強制することで, 相互作用依存性を学習目的に組み込む因果的帰納バイアスを導入する. ViT スタイルの masked transformer predictor を用いて CLEVRER での視覚的質問応答と Push-T でのモデル予測制御を評価し, 反実仮想推論で約 20% の絶対的向上と, パッチベース手法の 1% 以下のトークン数で同等の制御性能を達成した.
Citekey: Nam-ICML2026-Causal-JEPA_Object-Level
BibTeX Key: nam2026causal
DOI: ""
Relevance: 4
Repository: https://github.com/galilai-group/cjepa
Category: note
Template Version: v2.3
---

## Executive Summary

オブジェクト中心の world model において, 既存手法は object-centric 表現を学習するものの, オブジェクト間の相互依存ダイナミクスを訓練目的から必然化できていない. C-JEPA はオブジェクトスロットの潜在表現を時系列にわたってマスクし, マスクされたオブジェクトの状態を周囲オブジェクトとの相互作用から復元するよう強制することで, 相互作用依存性を学習目的に組み込む因果的帰納バイアスを導入する. ViT スタイルの masked transformer predictor を用いて CLEVRER での視覚的質問応答と Push-T でのモデル予測制御を評価し, 反実仮想推論で約 20% の絶対的向上と, パッチベース手法の 1% 以下のトークン数で同等の制御性能を達成した.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

object-centric world model はオブジェクトを区別できるが, それだけでは相互作用依存のダイナミクスを捉えるには不十分である. 訓練目的を設計しなければ, モデルは各オブジェクトの自己ダイナミクスや偶発的な相関に依存したショートカット解を学んでしまう. 本論文は"相互作用推論を訓練目的それ自体によって機能的に必要にする"という問いに取り組み, 再構成損失もタスク固有の教師信号も用いずに相互作用依存の予測を学ぶ手法を提案する.

### 提案手法のアプローチと, その根幹をなす要素は何か?

オブジェクトスロットの潜在系列をマスクし, マスクされたオブジェクトの状態を残存スロットと補助変数のみから予測する joint masked-history & forward-prediction 目的を採用する. これにより, マスクされたオブジェクトの自己履歴への近道を封じ, 相互作用推論を最小化条件として強制する.

必要不可欠な構成要素は以下の通りである.

- **Object-Level Masking**: マスク対象のオブジェクト $i$ の潜在表現を, 時間窓 $T$ 全体にわたってマスクトークン $\tilde{z}_\tau^i = \phi(z_{t_0}^i) + e_\tau$ に置換する. 最初の時刻の表現のみを identity anchor として保持し, 残りの履歴を遮断することで, temporal interpolation や self-dynamics によるショートカットを防ぐ.
- **ViT スタイル masked transformer predictor**: 双方向アテンションをもつ masked transformer が, 履歴窓と将来地平の両方にわたってマスクされたオブジェクトトークンを復元・予測する. これにより, 並列に相互作用依存の文脈から欠損スロットを推論する.
- **Masked latent prediction loss** $\mathcal{L}_\text{mask}$: 履歴再構成項 $\mathcal{L}_\text{history}$ と将来予測項 $\mathcal{L}_\text{future}$ を合わせた MSE 目的で, 予測スロットと frozen object-centric encoder が生成するターゲットスロットの $\ell_2$ 距離を最小化する (式 5).
- **Auxiliary Variables の分離モデリング**: アクションや固有感覚信号を独立した補助ノードとして predictor に入力し, 潜在への連結 (concatenation) ではなく分離エンコードで条件付けする.

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

JEPA ファミリー (I-JEPA, [[papers/Assran-arXiv2025-V-JEPA_Self-Supervised_Video/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning|Assran+ 2025]]) はパッチレベルのマスク予測を採用するが, オブジェクト粒度の相互作用推論を強制しない. DINO-WM (Zhou et al., 2025) はパッチベースの world model で高い制御性能を示すが, 大量のトークンを要する. SlotFormer (Wu et al., 2023) はオブジェクトスロットの自己回帰ロールアウトを行うが, 相互作用の明示的な強制はない. SPARTAN (Lei et al., 2025) は sparse attention によって相互作用選択性を誘導するが, 学習目的自体には組み込まない.

C-JEPA の新規性は, (1) オブジェクトスロット全体の時系列をマスクする"オブジェクトレベルマスキング"を世界モデルの帰納バイアスとして初めて定式化したこと, (2) 再構成損失・タスク固有監督なしにこの目的だけで相互作用依存予測を達成したこと, (3) 影響近傍 (influence neighborhood) の概念とその形式的解析 (Theorem 1, Corollary 1) を通じて, マスキングが因果的帰納バイアスをもたらすことを理論的に示したことにある. [[papers/Maes-arXiv2026-stable-worldmodel_Platform_Reproducible/stable-worldmodel-a-platform-for-reproducible-world-modeling-research-and-evaluation|Maes+ 2026]] の `stable-worldmodel` フレームワーク上に実装されている.

### どのように訓練・最適化したのか?

- **損失関数 / 最適化目的**: マスクされたオブジェクトトークンに対する MSE ベースの masked latent prediction loss (式 5):

$$\mathcal{L}_\text{mask} = \mathbb{E}\left[\sum_{\tau \in \mathcal{T}} \sum_{i=1}^{N} \mathbf{1}[\tilde{z}_\tau^i \neq z_\tau^i] \|\hat{z}_\tau^i - z_\tau^i\|_2^2\right]$$

  これは履歴再構成項 ($\tau \leq t$, マスクオブジェクトのみ) と将来予測項 ($\tau > t$, 全オブジェクト) に分解される (式 6). ターゲットは frozen object-centric encoder からの表現. encoder 自体は訓練しない.

- **データセット**:
  - CLEVRER (Yi et al., 2020): 解像度 $480 \times 320$, 訓練 10,000 動画・検証 5,000 動画・テスト 5,000 動画, 128 フレーム/動画. 訓練時はストライド 2 で 6 フレームのクリップ, 検証時は 10 フレームのクリップ.
  - Push-T (Chi et al., 2025): 解像度 $224 \times 224$, 訓練 18,410 軌跡・検証 21 軌跡. ストライド 5 で 6 フレームのクリップ.

- **Predictor**: 6 層・16 ヘッド・ヘッド次元 64・MLP 隠れ次元 2048 の Transformer. スロット次元 128.
- **Optimizer**: Adam, 学習率 $5 \times 10^{-4}$, バッチサイズ 256, 30 エポック.
- **Object-centric encoder**: VideoSAUR (Zadaianchuk et al., 2023; frozen DINOv2 ViT-S/14 バックボーン, 196 パッチトークン/フレーム, 次元 384 → 128 次元スロット, Slot Attention 2 回反復, 100k ステップ事前学習) を主要エンコーダとして使用. SAVi (Kipf et al., 2022) も比較実験で使用.

### どのように検証したか? 指標と結果は?

**視覚的質問応答 (§5.1, CLEVRER)**: ALOE (Ding et al., 2021) を用いて 128 フレーム入力を 160 フレームにロールアウトし, 質問応答精度を評価. 指標は平均精度 (per question %) と反実仮想精度 (per question %).

Table 1 (VideoSAUR エンコーダ, $|\mathcal{M}| = 4$): C-JEPA は平均精度 89.40% (OC-JEPA 82.79% 比 +6.61%), 反実仮想精度 per question 68.81% (OC-JEPA 47.68% 比 +21.13%) を達成.

Table 1 (SAVi エンコーダ, $|\mathcal{M}| = 2$): C-JEPA は平均精度 83.88% (OC-JEPA 77.28% 比 +6.60%), 反実仮想精度 per question 60.19% (OC-JEPA 41.10% 比 +19.09%).

Table 2 (reconstruction なし設定): C-JEPA は再構成損失なしで最高性能 (全平均 83.88%, 反実仮想 60.19%) を達成. SlotFormer は再構成なしで大幅に性能低下 (79.44% → 44.94%), OCVP-Seq は軽微な低下 (83.11% → 80.09%).

**モデル予測制御 (§5.2, Push-T)**: Cross-Entropy Method による MPC で計画成功率を評価. トークン数 $6 \times 128$ でパッチベース手法 ($196 \times 384$) の 1.02% のトークン数を使用.

Table 3: C-JEPA 成功率 88.67% (OC-JEPA 76.00% 比 +12.67%, DINO-WM 60.67% 比 +28.00%). DINO-WM は $196 \times 384$ トークンで 91.33% を達成するが, C-JEPA は 8 倍以上高速な計画 (673 秒 vs 5,763 秒 on L40s GPU, 50 軌跡評価) を実現.

### 検証結果に基づいた議論, 明らかになった課題はあるか?

(§7 Conclusion より) 著者は以下の限界を明示的に述べている.

第一に, 性能は object-centric encoder の品質に依存し, これが性能の上限を制約する.

第二に, 影響近傍 (influence neighborhood) を形式的に定義したが, 明示的な時系列因果グラフをもつデータセットでの直接検証は行っておらず, 今後の課題として挙げられている.

第三に, 強力な事前学習済みバックボーンを表現崩壊なしに end-to-end で洗練することは今後の有望な方向として挙げられている (Đukić et al., 2025 への言及あり).

第四に, より複雑な相互作用を含む環境での評価も今後の課題として挙げられている.

なお §6 の理論的分析では, C-JEPA がクレームする"因果性"は, 厳密な因果識別可能性の主張ではなく, 時間方向に有向な予測依存性 (temporally directed predictive dependencies) の意味でのものと著者自身が明示している.

---
## 自身の研究との関連

object-level masking による相互作用依存性の強制という考え方は, ロボット操作の world model 構築においても有用である. 物体と手・ツール間の接触ダイナミクスは相互作用依存性が高く, 自己ダイナミクスへのショートカットが問題になりやすいため, C-JEPA の訓練目的は直接適用候補となる. また, Push-T 上での MPC 評価における大幅な計算効率向上 (パッチベース比 8 倍高速) は, リアルタイム制御への応用可能性を示す. 一方, C-JEPA は frozen encoder を前提としており, encoder 品質が限界となる点は実環境への適用時に課題となりうる.

---
## 追加議論

---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@inproceedings{nam2026causal,
  title     = {Causal-{JEPA}: Learning World Models through Object-Level Latent Masking},
  author    = {Nam, Heejeong and Le Lidec, Quentin and Maes, Lucas and LeCun, Yann and Balestriero, Randall},
  booktitle = {Proceedings of the 43rd International Conference on Machine Learning},
  series    = {Proceedings of Machine Learning Research},
  volume    = {306},
  year      = {2026},
  publisher = {PMLR},
  address   = {Seoul, South Korea},
  url       = {https://arxiv.org/abs/2602.11389},
}
```
</details>
