---
Title: "Learning View-invariant World Models for Visual Robotic Manipulation"
Authors:
  - Pang, Jing-Cheng
  - Tang, Nan
  - Li, Kaiyuan
  - Tang, Yuting
  - Cai, Xin-Qiang
  - Zhang, Zhen-Yu
  - Niu, Gang
  - Sugiyama, Masashi
  - Yu, Yang
Year: 2025
Venue: ICLR
Tags:
  - "view-invariant"
  - "world-model"
  - "multi-view"
  - "robot-manipulation"
  - "representation-learning"
PDF: "[[papers/ICLR2025-ReViWo_View-invariant_World/main.pdf|📃]]"
Import Date: "2026-06-09"
Read Date: 2026-06-09
Executive Summary: 視点変化によるカメラ位置の揺れや変化に対して脆弱なロボット操作ポリシーの問題を解決するため, 視覚観測を view-invariant representation (VIR) と view-dependent representation (VDR) に分解するオートエンコーダフレームワーク ReViWo を提案する. VIR 抽出には Vision Transformer ベースの 2 つのエンコーダ (VIE・VDE) を用い, マルチビュー画像から VIR を学習した上で, その VIR を状態として世界モデルとオフライン RL ポリシーを訓練する. Meta-world・PandaGym・実機 ALOHA ロボットでの評価において, ReViWo はカメラ設置位置変化 (CIP) ・カメラ振動 (CSH) の両シナリオでベースライン手法を大きく上回り, 視点外乱に対する頑健な操作を実現した. 限界として学習時の視点ラベルへの依存と, 小規模データセット・シンプルな世界モデル構造が挙げられる.
Citekey: ICLR2025-ReViWo_View-invariant_World
BibTeX Key: reviwo2025
DOI: ""
Relevance: 5
Repository: none
Category: note
Template Version: v2.3
---

## Executive Summary

視点変化によるカメラ位置の揺れや変化に対して脆弱なロボット操作ポリシーの問題を解決するため, 視覚観測を view-invariant representation (VIR) と view-dependent representation (VDR) に分解するオートエンコーダフレームワーク ReViWo を提案する. VIR 抽出には Vision Transformer ベースの 2 つのエンコーダ (VIE・VDE) を用い, マルチビュー画像から VIR を学習した上で, その VIR を状態として世界モデルとオフライン RL ポリシーを訓練する. Meta-world・PandaGym・実機 ALOHA ロボットでの評価において, ReViWo はカメラ設置位置変化 (CIP) ・カメラ振動 (CSH) の両シナリオでベースライン手法を大きく上回り, 視点外乱に対する頑健な操作を実現した. 限界として学習時の視点ラベルへの依存と, 小規模データセット・シンプルな世界モデル構造が挙げられる.

---

## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

ロボット操作ポリシーは視覚入力に依存するが, 展開時にカメラ位置が訓練時と異なると性能が大きく劣化する. この"視点外乱 (viewpoint disturbance)"の問題は, 学習された表現が視点不変なタスク状態と視点依存な照明・背景等の情報を混在してエンコードすることに起因する. 本論文は, 視覚観測からタスクに不変な情報のみを抽出し, 視点変化に頑健なポリシーを学習する方法を問う.

### 提案手法のアプローチと, その根幹をなす要素は何か?

視覚観測を VIR と VDR に明示的に分離するオートエンコーダを学習し, その VIR を状態空間として世界モデルとポリシーを構築するという 2 段階のフレームワーク ReViWo を提案する.

- **View-invariant Encoder (VIE)**: ViT ベースのエンコーダ. 入力画像からタスク状態に依存し視点に不変な潜在表現 $z_s$ を抽出する.
- **View-dependent Encoder (VDE)**: VIE と同一アーキテクチャ. 視点固有の情報 (照明・角度・背景等) を捉える潜在表現 $z_v$ を抽出する.
- **Decoder**: $z_s$ と $z_v$ を結合し, 任意の視点から目標画像を再構成する Transformer ベースのデコーダ. 異なるソース画像から得た $z_s$ と $z_v$ を組み合わせた再構成損失により, 両エンコーダが異なる情報を担うよう強制する.
- **マルチビューデータと視点ラベル**: シミュレータで複数固定カメラから収集した, 視点ラベル付きマルチビューデータセット $\mathcal{O}$. 学習の根幹となる教師信号を提供する.
- **世界モデルとオフライン RL**: 学習済み VIR を状態として, COMBO アルゴリズムにより世界モデルとポリシーをオフライン制御データ $\mathcal{D}$ から訓練する.

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

最も直接的な先行研究は **MVWM** (Seo et al., 2023) であり, マスクされたマルチビューオートエンコーダで視点頑健な表現を学習し世界モデルへ活用する手法である. しかし MVWM は単一エンコーダで全視覚情報を混在してエンコードするため, 視点変化による表現の変動が残存する. **RoboUniView** (Liu et al., 2024) は 3D マルチビュー画像から統一表現を学習するが, カメラキャリブレーションと全視点が類似内容を持つことを前提とする.

ReViWo の新規性は以下の点にある. 第一に, 観測を VIR と VDR に明示的に分解するという"観測分解 (observation decomposition)"のアイデアを, 再構成損失によって原理的に実現した点. 第二に, Open X-Embodiment データ (O'Neill et al., 2024) のような視点ラベルなしデータを重み付き損失で同時活用することで, 訓練データの多様性を高める点.

### どのように訓練・最適化したのか?

**損失関数 / 最適化目的:**

オートエンコーダは以下の複合損失で学習する (式 (3)):

$$\mathcal{L}_{AE}(\phi) = \mathbb{E}_{o_{s_1}^{v_1}, o_{s_m}^{v_2}, o_{s_n}^{v_m} \sim \mathcal{O}} \left[ -\log p_\phi(o_{s_n}^{v_m} | q_\phi^S(o_{s_i}^{v_1}); q_\phi^V(o_{s_m}^{v_2})) \right] + \lambda_1 \mathcal{L}_{VQ} + \lambda_2 \mathcal{L}_{Contrastive}(\phi)$$

- 第 1 項 (画像再構成損失): 一方の画像から $z_s$, 別の画像から $z_v$ を取得しターゲット画像を再構成することで, 状態情報と視点情報の分離を強制する.
- $\mathcal{L}_{VQ}$: VQ-VAE のコードブック損失 (commitment loss + quantization loss). 潜在空間を離散化し情報を凝縮する.
- $\mathcal{L}_{Contrastive}$: コントラスト損失. $z_s$ を同一状態・異なる視点間で一致させ, $z_v$ を同一視点・異なる状態間で一致させることで分解を促進する.

世界モデルは式 (4) の最大尤度目的で学習する:

$$\mathcal{L}_{WM}(\theta) = \mathbb{E}_{(s_t, a_t, s_{t+1}) \sim \mathcal{D}} \left[ -\log \mathcal{M}_\theta(q_\phi^S(s_{t+1}) | q_\phi^S(s_t), a_t) \right]$$

**データセット:**

| データセット | 役割 | 規模 |
|---|---|---|
| Meta-world マルチビューデータ | VIE 学習 | 51 軌跡 × 20 視点 = 1,020 シーケンス (112,040 観測) |
| PandaGym マルチビューデータ | VIE 学習 | 30 軌跡 × 20 視点 = 600 シーケンス (30k 観測) |
| Open X-Embodiment (Routing Primitive) | VIE 補助学習 (視点ラベルなし) | 101 軌跡, 10,064 観測 |
| Meta-world オフライン制御データ | 世界モデル・ポリシー学習 | 400 軌跡 (単一固定視点) |
| PandaGym オフライン制御データ | 世界モデル・ポリシー学習 | 100 軌跡 (単一固定視点) |
| 実機 ALOHA データ | 実世界評価用 VIE・ポリシー学習 | 128 軌跡 (3 カメラ) |

観測は $128 \times 128$ ピクセルの画像. 訓練は 25,000 勾配ステップ, OfflineRL-kit (Sun, 2023) を使用. ハードウェア: AMD EPYC 9654 (64 コア) + NVIDIA GeForce RTX 4090 × 4.

### どのように検証したか? 指標と結果は?

**評価環境:** Meta-world (Door Open, Drawer Open, Window Close), PandaGym (Reach, Coffee Button, Faucet Open, Dial Turn), 実機 ALOHA (ボトル把持・配置 3 段階タスク).

**視点外乱の種類:**

- **CIP (Camera Installation Position)**: アジマス角を Meta-world で 10°, PandaGym で 90° オフセット.
- **CSH (Camera SHaking)**: アジマス角を連続的に動的変化させる.

**ベースライン:** MVWM (Seo et al., 2023), COMBO (Yu et al., 2021), BC, CQL (Kumar et al., 2020).

**評価指標:** 直近 2 チェックポイントの平均成功率 (30 エピソード評価, 4 シード).

**主要結果:**

- Meta-world・PandaGym の全タスクにおいて, CIP・CSH 両条件下で ReViWo がベースラインを上回る. 例: COMBO は Door Open で CIP 時 $23.3 \to 0$, CSH 時も大幅低下するが, ReViWo は頑健を維持.
- 実機 ALOHA (Tab. 1): ReViWo-BC は CIP 条件下でも Stage 1: 100%, Stage 2: 60%, Stage 3: 50% を達成. ACT (Zhao et al., 2023) は CIP 時 Stage 2・Stage 3 がともに 0%.
- データ量実験 (Fig. 5): 10 視点・90° 範囲 (10V+90D) で十分な性能が得られ, 20 視点・180° 範囲 (20V+180D) でさらに改善. アジマスオフセット 15° 以内では両設定が同等.
- Open X-Embodiment 統合 (Tab. 2): Door Open CIP で $22.8 \to 42.2$, Drawer Open CIP で $30.6 \to 55.0$ と大幅改善.
- 世界モデルの寄与 (Tab. 3): Drawer Open の CIP で w/ WM: 30.6, w/o WM: 28.3; Window Close の訓練視点で w/ WM: 98.9, w/o WM: 97.2 と一貫した改善.
- t-SNE 分析 (Fig. 6): VIR (ReViWo) は同一状態の異なる視点表現が近接クラスタを形成するのに対し, MVWM と VAE は視点間で大きく分散する.

### 検証結果に基づいた議論, 明らかになった課題はあるか?

(§5 Conclusion and Limitation より) 著者が明示的に述べた限界と future work は以下の通り.

- **視点ラベルへの依存**: 現在の VIR 学習には固定カメラで収集した視点ラベル付きマルチビューデータが必要. 実用上ラベル取得は可能だが, ラベルなしデータを活用できるよう制約する手法 (情報ボトルネック (Tishby & Slonim, 2000) や VDR のマスキング等) の探索が課題として挙げられている.
- **実験規模の制限**: データセット規模とモデルサイズが小規模. CLIP (Radford et al., 2021) 等の事前学習モデルや, より大量の Open X-Embodiment データを活用したスケールアップが future work として挙げられている.
- **世界モデルの表現力**: 現状は単純な多層パーセプトロン構造. より複雑な動力学を持つタスクへの適用には, 再帰型状態空間モデル (Hafner et al., 2019) 等のより強力な構造が有益であると述べられている.
- **Door Open CSH でのパフォーマンス低下**: Open X-Embodiment の多様で非構造的なデータが動的条件下での汎化を妨げる可能性があることが言及されている.

---

## 自身の研究との関連

VIR/VDR の分解は, 触覚・固有受容センサと視覚を組み合わせたマルチモーダルロボット学習において, センサモダリティ間の不変表現を抽出する設計に応用できる. オフライン RL + 世界モデルの組み合わせ (COMBO) は, 実機データ収集が限られる触覚ベースの操作タスクでも有効な枠組みとなりうる. 一方, 本論文は視覚のみを扱い触覚センサの統合は未検討であり, 相補的な研究対象となる. また VIR の t-SNE 分析で示された"状態クラスタリング"の質は, 本研究プロジェクトの潜在空間診断手法 (信号/ノイズ比, 固有次元推定) で定量評価できる観点である. [[papers/Nilaksh-arXiv2026-Reconstruction_Semantics_What/reconstruction-or-semantics-what-makes-a-latent-space-useful-for-robotic-world-models|Nilaksh+ 2026]] は再構成ベース表現のロボット世界モデルへの有用性を問う論文であり, ReViWo と直接比較対象となる関連研究である.

---

## 追加議論

---

## BibTex

<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@inproceedings{reviwo2025,
  title     = {Learning View-invariant World Models for Visual Robotic Manipulation},
  author    = {Pang, Jing-Cheng and Tang, Nan and Li, Kaiyuan and Tang, Yuting and Cai, Xin-Qiang and Zhang, Zhen-Yu and Niu, Gang and Sugiyama, Masashi and Yu, Yang},
  booktitle = {International Conference on Learning Representations},
  year      = {2025},
  url       = {https://openreview.net/forum?id=ReViWo}
}
```

</details>
