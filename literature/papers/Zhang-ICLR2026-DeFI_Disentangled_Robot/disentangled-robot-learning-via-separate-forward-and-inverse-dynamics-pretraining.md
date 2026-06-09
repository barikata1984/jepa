---
Title: "Disentangled Robot Learning via Separate Forward and Inverse Dynamics Pretraining"
Authors:
  - Zhang, Wenyao
  - Zhang, Bozhou
  - Qi, Zekun
  - Zeng, Wenjun
  - Jin, Xin
  - Zhang, Li
Year: 2026
Venue: ICLR
Tags:
  - "forward-dynamics"
  - "inverse-dynamics"
  - "disentangled"
  - "pretraining"
  - "robot-manipulation"
  - "vla"
PDF: "[[papers/Zhang-ICLR2026-DeFI_Disentangled_Robot/main.pdf|📃]]"
Import Date: "2026-06-09"
Read Date: 2026-06-09
Executive Summary: "VLA モデルが抱える 2D 映像予測と 3D 行動予測の目標競合, および大規模動作なし動画の活用困難という課題に対し, 順ダイナミクスと逆ダイナミクスの事前学習を分離する DeFI フレームワークを提案. General Forward Dynamics Model (GFDM) は映像生成目標で人間・ロボット混合動画から前向きダイナミクスを習得し, General Inverse Dynamics Model (GIDM) は自己教師あり学習で未ラベル動画から潜在行動を推定する. 両モデルをファインチューニング時にエンドツーエンドで結合することで, CALVIN ABC-D で平均タスク長 4.51, SimplerEnv-Fractal で 51.2% 成功率, 実機 Franka での 81.3% 成功率を達成し, 先行手法を大幅に上回る."
Citekey: Zhang-ICLR2026-DeFI_Disentangled_Robot
BibTeX Key: zhang2026defi
DOI: ""
Relevance: 4
Repository: "https://github.com/WenyaoZhang/DeFI"
Category: note
Template Version: v2.3
---

## Executive Summary
VLA モデルが抱える 2D 映像予測と 3D 行動予測の目標競合, および大規模動作なし動画の活用困難という課題に対し, 順ダイナミクスと逆ダイナミクスの事前学習を分離する DeFI フレームワークを提案. General Forward Dynamics Model (GFDM) は映像生成目標で人間・ロボット混合動画から前向きダイナミクスを習得し, General Inverse Dynamics Model (GIDM) は自己教師あり学習で未ラベル動画から潜在行動を推定する. 両モデルをファインチューニング時にエンドツーエンドで結合することで, CALVIN ABC-D で平均タスク長 4.51, SimplerEnv-Fractal で 51.2% 成功率, 実機 Franka での 81.3% 成功率を達成し, 先行手法を大幅に上回る.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

VLA モデルは 2D 映像予測 (前向きダイナミクス) と 3D 行動予測 (逆ダイナミクス) を同一ネットワークで同時に学習しようとするため, 二つの目標が互いに競合し学習が不安定になる (§1). また, 視覚と行動を結合した学習方式では, 大規模な動作なし人間・ウェブ動画を活用できず, スケールアップが難しい. 本論文はこの 2 点, すなわち"目標競合"と"大規模動作なし動画の活用困難"を同時に解決することを目指した.

### 提案手法のアプローチと, その根幹をなす要素は何か?

DeFI は事前学習を 2 系統に分離し, ファインチューニング時に結合するという 2 段階の枠組みをとる.

**Stage I — 分離事前学習 (Decoupled Pretraining):**

- **GFDM (General Forward Dynamics Model)**: Stable Video Diffusion (SVD) ベースの映像生成モデルを, 人間動画 (Something-Something v2, Ego4D 等) とロボット動画 (CALVIN, Open X-Embodiments 等) の混合データで事前学習. 現在の観測フレームとタスク指示 (CLIP テキスト埋め込み) を条件として, 水平線 H+1 フレームの将来映像潜在表現を予測する (Eq. 1–3). 推論時は 1 ステップノイズ除去に制限し, 将来の潜在埋め込みを効率的に取得する.
- **GIDM (General Inverse Dynamics Model)**: 連続 2 フレームの DINOv2 特徴 (e_t, e_{t+n}) とタスク指示を入力とし, 潜在行動を推定する Spatial-Temporal Transformer + VQ-VAE 構造. VQ-VAE の離散化ボトルネックが将来状態の漏れ込みを防ぎ, 意味ある行動表現の学習を促す. 目標は将来フレームの DINO 特徴予測 (MSE 損失) であり, 行動ラベルは一切不要 (§3.2).

**Stage II — 結合ファインチューニング (Coupled Finetuning):**
GFDM を凍結したまま, 軽量 MLP でその出力を GIDM の入力空間に投影. GIDM と 30M DiT-B ベースの拡散行動アダプタをエンドツーエンドで更新する (§3.3). GFDM を凍結することで, 大規模事前学習が与えた長期ダイナミクス表現が崩れず, 安定した逆ダイナミクス学習の基盤となる.

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

- **UniVLA / LAPA (Ye+, 2024)**: 人間動画から潜在行動ラベルを抽出し, VLA の事前学習に利用. 本論文はこのアプローチが逆ダイナミクス学習を軽視している点を批判し, 逆ダイナミクスにも同等の事前学習リソースを充てる必要があることを示した (§2.2, Table 1 の UniVLA との比較).
- **VPP (Hu+, 2024)**: 映像予測モデルを順ダイナミクス基盤として活用しつつ, 逆ダイナミクスを簡易モデルで補う. 本論文の GIDM の方が強い逆ダイナミクス事前学習を持つため, CALVIN で VPP を上回る (§4.2).
- **SuSIE / CLOVER (Black+, 2023; Bu+, 2024)**: 映像生成の予測映像を直接ポリシー入力とする. 本論文は行動推定そのものの精度も重要であることを示し, 逆ダイナミクスモデルの強化が性能改善の鍵と主張する.

新規性は, 前向き・逆向きダイナミクスを独立した専用データソース・専用目的関数でそれぞれ事前学習し, かつ動作なし動画で逆ダイナミクスまで大規模に学習するレシピを確立した点にある.

### どのように訓練・最適化したのか?

**GFDM 事前学習:**
- アーキテクチャ: SVD + CLIP テキストエンコーダ (凍結). Video VAE で 2D/3D エンコード, 時間注意付き U-Net/Transformer デノイザーを latent diffusion 目標で学習 (Eq. 1–3).
- データ: Something-Something v2, Ego4D などの人間動画と CALVIN, Open X-Embodiments などのロボット動画の混合.
- 推論時は 1 ステップノイズ除去に固定 (計算効率のため).

**GIDM 事前学習:**
- アーキテクチャ: DINOv2 エンコーダ (凍結) + 因果マスク付き時空間 Transformer + VQ-VAE コードブック + Spatial Transformer デコーダ.
- 学習可能なクエリ q_a ∈ R^{N×d} を DINO 特徴・T5 指示埋め込みと連結し, 未来フレームの DINO 特徴を予測 (MSE 損失).
- データ: Ego4D および Open X-Embodiments (動作ラベル不使用).

**結合ファインチューニング:**
- GFDM は凍結; GIDM + 行動アダプタ (30M DiT-B) のみ更新.
- 小規模ロボットデモデータで実施 (CALVIN では全データの 60% で先行最高性能を超える).
- 推論: GFDM が 1 ステップで将来潜在を生成 → MLP 投影 → GIDM が潜在行動を推定 → 行動アダプタが実行可能コマンドを生成 (§3.4).

### どのように検証したか? 指標と結果は?

**CALVIN ABC-D (シミュレーション, 長期ホライズン操作):**
- 指標: 1000 ロールアウトでの連続タスク平均成功数 (Avg. Len., 最大 5).
- マルチビュー設定: DeFI **4.51** (先行最高 VPP 4.33 を +0.18 上回る). 1〜5 タスクの逐次成功率も全ステップで最高 (97.9 / 94.2 / 90.7 / 87.0 / 81.2 %).
- サードビュー設定: DeFI **4.05** (UniVLA 3.80 を上回る).
- データ効率: 学習データ 10% でも VPP 比 18% 相対改善; 60% で当時最高性能を超える.

**SimplerEnv-Fractal (Google Robot, 多様な照明・視点):**
- 指標: 3 タスクの平均成功率 (Visual Matching / Variant Aggregation).
- DeFI: Visual Matching **51.2%**, Variant Aggregation **45.4%** (OpenVLA 27.7% / 39.8% を大幅上回る).

**実機 Franka Panda (8 タスク, 15 種以上の物体):**
- 指標: 各タスク成功率と 8 タスク平均.
- DeFI 平均 **81.3%** (Diffusion Policy 48.2%, Octo 34.4%, OpenVLA 43.8% を超える). 複雑な Cut & Stack, Pour Water タスクで特に優位.

**アブレーション (§4.5):**
- 分離事前学習なし → Avg. Len. 3.28 (GFDM のみ) / 4.16 (GIDM のみ) → 全あり 4.51: 両モジュールの寄与を確認.
- 人間動画なし → Avg. Len. 4.19 (GFDM なし) → 4.51: 人間動画が +0.32 の改善.
- VQ-VAE 離散化 vs ガウス混合・単純ビニング・連続: VQ-VAE が最高 (Table 8).
- GIDM アーキテクチャ比較: MLP (3.42), Transformer (4.22) に対し GIDM 4.51 が最高 (Table 7).
- ファインチューニング組み合わせ: アダプタのみ (4.33), FDM+アダプタ (4.35), GIDM+アダプタ (4.51), 全部更新 (4.40): GFDM 凍結が有効 (Table 9).

### 検証結果に基づいた議論, 明らかになった課題はあるか?

- **ドメインシフト問題 (§4.3)**: SimplerEnv-Fractal でタスクによって性能が低下するケースがある. GFDM が Fractal データセットで事前学習され凍結されているため, 実世界画像のみを予測しようとする傾向があり, そのズレが GIDM に伝播して誤った行動を生成する.
- **計算コスト**: 1 ステップ GFDM 推論でも約 150 ms を要し, 5 ステップでは 250 ms に増加 (Table 6). リアルタイム制御への適用にはさらなる高速化が必要.
- **DINO ベース生成モデル**: GFDM として DINO ベースモデルを試したが, SVD ベースより収束が速い一方で既存の映像生成フレームワークとの親和性が低く, 最終性能は SVD ベースに劣った (§4.5, Q3). より強力な DINO (Zhou+, 2024) や潜在埋め込み予測モデルとの組み合わせは今後の探索課題.
- **事前学習データの異質性**: 人間動画とロボット動画は外観・動作様式が大きく異なる. GFDM と GIDM がそれぞれ異なるデータを吸収できる一方, ファインチューニング時の分布不一致が残存する可能性がある.

---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@inproceedings{zhang2026defi,
  title={Disentangled Robot Learning via Separate Forward and Inverse Dynamics Pretraining},
  author={Zhang, Wenyao and Zhang, Bozhou and Qi, Zekun and Zeng, Wenjun and Jin, Xin and Zhang, Li},
  booktitle={International Conference on Learning Representations},
  year={2026}
}
```
</details>
