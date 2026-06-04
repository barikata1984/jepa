---
Title: "LeJEPA: Provable and Scalable Self-Supervised Learning Without the Heuristics"
Authors:
  - Balestriero, Randall
  - LeCun, Yann
Year: 2025
Venue: arXiv
Tags:
  - "self-supervised-learning"
  - "jepa"
  - "representation-learning"
  - "anti-collapse"
  - "distribution-matching"
  - "statistical-testing"
PDF: "[[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/main.pdf|📃]]"
Import Date: "2026-06-04"
Read Date: 2026-06-04
Executive Summary: "JEPA の埋め込みが従うべき最適分布が等方ガウスであることを線形・非線形プローブの両方で証明し, それを実現する SIGReg (Sketched Isotropic Gaussian Regularization) を導入. 予測損失と SIGReg の 2 項のみからなる LeJEPA は, stop-gradient, teacher-student, EMA 等のヒューリスティクスを排除しつつ, 10+ データセット, 60+ アーキテクチャ (最大 1.8B パラメータ) で安定動作. ~50 行の PyTorch 実装で済む."
Citekey: Balestriero-arXiv2025-LeJEPA_Provable_Scalable
BibTeX Key: balestriero2025lejepa
DOI:
Relevance: 5
Repository: "https://github.com/galilai-group/stable-pretraining"
Category: note
Template Version: v2.3
---

## Executive Summary

JEPA の埋め込みが従うべき最適分布が等方ガウスであることを線形・非線形プローブの両方で証明し, それを実現する SIGReg (Sketched Isotropic Gaussian Regularization) を導入. 予測損失と SIGReg の 2 項のみからなる LeJEPA は, stop-gradient, teacher-student, EMA 等のヒューリスティクスを排除しつつ, 10+ データセット, 60+ アーキテクチャ (最大 1.8B パラメータ) で安定動作. ~50 行の PyTorch 実装で済む.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

JEPA の埋め込みが理論的にどの分布に従うべきかが未解明であり, 表現崩壊を防ぐためのヒューリスティクス (stop-gradient, teacher-student ネットワーク, EMA スケジューリング, 特徴ホワイトニング等) に依存していた (§1, §2.2). 本論文は (1) 下流タスクの予測リスクを最小化する最適な埋め込み分布を理論的に同定し, (2) それを高次元で効率的に実現する正則化手法を設計し, (3) ヒューリスティクス不要でスケーラブルな JEPA を構築する, という 3 つの課題に取り組んだ.

### 提案手法のアプローチと, その根幹をなす要素は何か?

任意の下流タスクに対する予測リスクを最小化する埋め込み分布を理論的に導出し, その分布を達成する正則化項を設計, 予測損失と組み合わせて JEPA の学習目的関数とする.

- **等方ガウス最適性の証明 (§3)**: 線形プローブ (§3.1, Lemma 1-2) ではバイアスと分散の両面で等方分布が最適であることを示し, 非線形プローブ (§3.2, Thm. 1) では k-NN とカーネル法の積分二乗バイアスを最小化する唯一の分布が等方ガウスであることを証明
- **SIGReg (§4)**: Cramér-Wold 定理 (Lemma 3) に基づき, 高次元埋め込みを M 個のランダム単位方向に射影し, 各 1 次元射影に対して Epps-Pulley 特性関数検定 (§4.2.3) を適用. O(N) の時間・メモリ計算量, 有界な勾配と曲率 (Thm. 4), 次元の呪いの克服 (Thm. 5)
- **LeJEPA 損失 (§5.1)**: L = (1-λ)·予測損失 + λ·SIGReg. チューナブルなハイパラは λ のみ

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

既存手法はいずれも崩壊を根本解決せず, 回避策に依存している. SIGReg はこれらと異なり, 分布全体をガウスにマッチングすることで崩壊を理論的に排除する.

- **VICReg** [Bardes+, 2021]: SIGReg の特殊ケースとして回収できる (§5.2) — SIGReg の検定統計量を 1–2 次モーメントのみに制限すると VICReg の目的関数と一致する. しかし 1–2 次モーメントがガウスと一致しても高次モーメントが異なる分布は無数に存在し, 崩壊のショートカット解が残る (Thm. 3). SIGReg は Epps-Pulley 特性関数検定で分布全体をマッチングすることでこの穴を塞ぐ
- **I-JEPA** [Assran+, 2023]: stop-gradient と teacher-student で崩壊を回避するが, 正則化として崩壊を排除しているわけではない. SIGReg はこれらのヒューリスティクスを不要にし, 100 エポックで I-JEPA の 300 エポック相当の性能を達成 (Tab. 2)
- **DINOv2/v3**: 事前学習済み encoder の凍結で崩壊を回避するが, これもエンドツーエンド学習を放棄する回避策. 加えて自然画像 1 億枚超の事前学習に依存するため, ドメイン固有の小規模データでは転移学習に頼るしかない. SIGReg ベースの LeJEPA はハイパラ調整なしでそのまま適用でき, 小モデルの in-domain 学習が DINOv2/v3 の転移を上回る (§6.3, Fig. 12)

新規性:

1. 下流タスクの予測リスク最小化の観点から等方ガウスが最適であることの初めての証明 (Thm. 1)
2. SIGReg: 特性関数ベースの検定により, 次元の呪いを理論的に克服する分布マッチング (Thm. 5). CDF ベース (ソートが必要で並列化困難) やモーメントベース (勾配爆発) の欠点を回避
3. 上記 2 点の理論的保証が encoder の内部構造に依存しないため, 既存手法が ViT 向けにチューニングを要するのに対し, 同じ損失・同じハイパラで ResNet, ViT, ConvNeXt, MaxViT, Swin 等 60+ アーキテクチャに適用可能 (§6.1, Fig. 9)

### どのように訓練・最適化したのか?

- **損失関数**: L_LeJEPA = (1-λ)·予測損失 + λ·SIGReg (§5.1). 推奨 λ = 0.05
- **SIGReg 内部パラメータ**: Epps-Pulley 検定, 17 積分ノット, 積分区間 [-5, 5], 1024 射影方向 (射影方向は毎ステップリサンプル)
- **データセット**:
  - 主要: ImageNet-1k (~1.28M 画像, 1000 クラス)
  - 追加: ImageNet-100, ImageNet-10, Galaxy10 (11,000 画像), Food101, flowers102 (1,020 画像), DTD, Stanford Cars, CIFAR-10/100, Oxford Pets, FGVC-Aircraft
- 8 ビュー (2 グローバル 224×224 + 6 ローカル 96×96)
- AdamW, lr ∈ {5e-3, 5e-4}, wd ∈ {1e-1, 1e-2, 1e-5}, 線形ウォームアップ + コサインアニーリング
- 100 エポック (ImageNet-1k), 400 エポック (小規模データ)
- SWA (Stochastic Weight Averaging) をオプションで使用 (ViT で小幅な性能向上)

### どのように検証したか? 指標と結果は?

**評価プロトコル**: 凍結バックボーン + 線形プローブ (top-1 精度), few-shot 分類 (1/10/all-shot), 全パラメータ fine-tuning.

**主要結果**:

- ImageNet-1k 線形評価: ViT-L/14 = 75.08%, ConvNeXtV2-H = 78.5% (Tab. 1). I-JEPA ViT-H (300ep) を 100ep で上回る (Tab. 2)
- アーキテクチャ横断 (Fig. 9): 8 ファミリー 50 モデル (< 20M params) で ImageNet-10 の top-1 が 91.5–95%, すべて凍結バックボーン線形評価
- λ に対するロバスト性 (Fig. 8): λ ∈ [0.01, 0.2] で安定した性能
- バッチサイズ 128 でも競合的 (Tab. 1c): 128 → 72.20%, 1024 → 74.72%
- Galaxy10 in-domain (Fig. 12, §6.3): LeJEPA (ResNet-34 等の小モデル, 400ep in-domain 学習) が DINOv2 ViT-S/16 (LVD-142M 事前学習) と DINOv3 ViT-S/16 (LVD-1.7B 事前学習) を凍結・fine-tuning の両方で上回る
- Few-shot 転移 (Tab. 2): DTD, flowers102, food101 で I-JEPA (ViT-H, 300ep) を上回り, 訓練コスト 3 倍削減
- 学習損失と下流性能の Spearman 相関 (§6.2, Fig. 11): ~85% (スケーリング係数 α = 0.4 で ~99%). ラベル不要のモデル選択が可能

**アブレーション** (Tab. 1):

- 射影数 512–4096: 多いほど微改善, 512 でも競合的
- 積分ノット 5–41: ほぼ影響なし
- 積分区間 [-1,1]–[-5,5]: ほぼ影響なし
- Teacher-student (Tab. 4): なくても崩壊せず, SWA で小幅に改善
- レジスタートークン (Tab. 1e): 不要, あっても害なし

### 検証結果に基づいた議論, 明らかになった課題はあるか?

著者は限界に明示的には言及していない. §7 (Conclusion) は成果のまとめに留まり, limitations や future work の節は設けられていない. 本文中から読み取れる暗黙の制約として:

- (§3) 理論的結果は i.i.d. 仮定に依存しており, 時系列・ビデオ等の系列データへの直接的な拡張は議論されていない
- (§6) 検証は画像ドメイン (自然画像, 銀河画像) に限定されており, ビデオ, テキスト, ロボティクス等への適用は未検証 (ただし [[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/leworldmodel-stable-end-to-end-joint-embedding-predictive-architecture-from-pixels|LeWM]] が行動条件付きワールドモデルへの適用を示している)
- (§6.4) ImageNet-1k での最高性能 (ViT-H/14 で 79%) は DINOv2 の同規模モデルと比較してまだギャップがある可能性があるが, 著者は学習エポック数の差 (100 vs 数百) を考慮すべきとしている

---
## 自身の研究との関連

LeWM の崩壊防止メカニズムの直接的な理論的基盤. SIGReg の設計原理 (等方ガウス最適性, Epps-Pulley 検定, Cramér-Wold 定理による次元削減) を理解することで, LeWM の正則化項の挙動とチューニング指針が明確になる. また, λ のロバスト性やアーキテクチャ非依存性の知見は, ワールドモデル学習の実験設計に直接活用できる. SIGReg の ~50 行実装 (Algorithm 1) は, カスタム実装や拡張の出発点としても有用.

---
## 追加議論

### i.i.d. 仮定と系列データのギャップ

§3 の理論は i.i.d. 仮定に基づく. 系列データ (ビデオ, ロボット軌跡) への拡張は明示的に議論されていない. LeWM はこのギャップに触れずに SIGReg をステップワイズ (各時刻のバッチを独立に) 適用し, 時間依存は predictor の MSE に委ねることで暗黙的に回避している. この分離が理論的に正当化されるかは未解明だが, 実験的には機能している.

### アーキテクチャ非依存性の意味

SIGReg の損失関数は encoder の出力ベクトルの分布のみを見るため, 内部構造 (CNN か Transformer か等) に依存しない."アーキテクチャ非依存"は損失関数の設計の話であり,"どの encoder でも同等の性能が出る"とは異なる (Fig. 9 では 91.5–95% と 3.5 ポイントの幅がある). アーキテクチャの帰納バイアスは表現の質に影響するが, SIGReg 側の設計変更は不要という主張.

### 固有次元とのミスマッチ問題

LeWM の TwoRoom での性能低下は, データの固有次元 (~2) と潜在空間 (192 次元) のミスマッチに起因する (LeWM §4.2). LeJEPA 自体はこの問題を直接扱っていないが, SIGReg が"全次元を等方ガウスにせよ"と要求する以上, 固有次元が潜在次元より大幅に低い場合は構造的に不利になる. 固有次元は事前にわからないため, 潜在次元を環境ごとに合わせるのはタスク非依存の設計方針に反する — LeJEPA/SIGReg の設計に内在するジレンマ.

---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@article{balestriero2025lejepa,
  title={LeJEPA: Provable and Scalable Self-Supervised Learning Without the Heuristics},
  author={Balestriero, Randall and LeCun, Yann},
  journal={arXiv preprint arXiv:2511.08544},
  year={2025}
}
```
</details>
