---
Title: "V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning"
Authors:
  - Assran, Mahmoud
  - Bardes, Adrien
  - Fan, David
  - Garrido, Quentin
  - Howes, Russell
  - Komeili, Mojtaba
  - Muckley, Matthew
  - Rizvi, Ammar
  - Roberts, Claire
  - Sinha, Koustuv
  - Zholus, Artem
  - Arnaud, Sergio
  - Gejji, Abha
  - Martin, Ada
  - Hogan, Francois Robert
  - Dugas, Daniel
  - Bojanowski, Piotr
  - Khalidov, Vasil
  - Labatut, Patrick
  - Massa, Francisco
  - Szafraniec, Marc
  - Krishnakumar, Kapil
  - Li, Yong
  - Ma, Xiaodong
  - Chandar, Sarath
  - Meier, Franziska
  - LeCun, Yann
  - Rabbat, Michael
  - Ballas, Nicolas
Year: 2025
Venue: arXiv
Tags:
  - "self-supervised-learning"
  - "world-model"
  - "video-understanding"
  - "robot-manipulation"
  - "jepa"
  - "model-predictive-control"
PDF: "[[papers/Assran-arXiv2025-V-JEPA_Self-Supervised_Video/main.pdf|📃]]"
Import Date: "2026-06-05"
Read Date: 2026-06-05
Executive Summary: "100万時間超のインターネット動画で自己教師あり事前学習した JEPA 動画エンコーダ (最大 1B パラメータ) を, わずか 62時間のロボットインタラクションデータで行動条件付きワールドモデル V-JEPA 2-AC に拡張. 凍結エンコーダ上に 300M パラメータの自己回帰 predictor を学習し, CEM による潜在空間 MPC で Franka 実機のゼロショット把持・ピックアンドプレースを実現した. 動画理解・行動予測タスクでも 8B クラス SOTA を達成し, 言語監督なしの動画エンコーダの汎用性を示した."
Citekey: Assran-arXiv2025-V-JEPA_Self-Supervised_Video
BibTeX Key: assran2025vjepa
DOI: ""
Relevance: 5
Repository: "https://github.com/facebookresearch/vjepa2"
Category: note
Template Version: v2.3
---

## Executive Summary
100万時間超のインターネット動画で自己教師あり事前学習した JEPA 動画エンコーダ (最大 1B パラメータ) を, わずか 62時間のロボットインタラクションデータで行動条件付きワールドモデル V-JEPA 2-AC に拡張. 凍結エンコーダ上に 300M パラメータの自己回帰 predictor を学習し, CEM による潜在空間 MPC で Franka 実機のゼロショット把持・ピックアンドプレースを実現した. 動画理解・行動予測タスクでも 8B クラス SOTA を達成し, 言語監督なしの動画エンコーダの汎用性を示した.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

インターネット規模の動画データから自己教師あり学習で獲得した表現を, 少量のロボットインタラクションデータと組み合わせることで, 新規環境でゼロショットに計画・行動できるワールドモデルを構築できるか, という問いに取り組んだ (§1). 既存の行動条件付き動画生成モデルは計画能力の実証が不十分であり, インタラクションデータのみで学習するワールドモデルはデータの疎さに制約されていた.

### 提案手法のアプローチと, その根幹をなす要素は何か?

2段階の学習パイプラインで構成される. 第1段階では 100万時間超の動画 (VideoMix22M) 上でマスクノイズ除去目的関数 (mask denoising: マスクをノイズとみなし表現空間で復元する, V-JEPA 目的関数) により動画エンコーダを自己教師あり事前学習し, 第2段階では凍結したエンコーダ上に行動条件付き predictor を少量のロボットデータで学習する.

- **マスクノイズ除去事前学習 (mask denoising)**: 動画をパッチ列に変換し, 一部のパッチをマスク (欠損) させ, 残りから表現空間でマスク部分を復元する. L1 損失 (§2.1, 式 1)
- **スケーリング**: データ規模 (2M→22M 動画), モデル規模 (ViT-L 300M→ViT-g 1B), 長時間学習 (90K→252K イテレーション), 段階的解像度向上 (256→384, 16→64 フレーム) の 4軸で拡張 (§2.2, Fig. 3)
- **行動条件付き predictor (V-JEPA 2-AC)**: 凍結エンコーダの特徴マップ上に 300M パラメータのブロック因果注意トランスフォーマーを配置. エンドエフェクタの状態・行動と特徴マップを時間的にインターリーブし, 次フレームの表現を自己回帰的に予測 (§3.1, 式 2–4)
- **CEM による潜在空間 MPC**: ゴール画像の表現との L1 距離をエネルギー関数とし, CEM で行動系列を最適化. 1ステップ実行後に再計画する後退ホライゾン制御 (§3.2, 式 5)

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

- **V-JEPA** ([[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable|Bardes+, 2024]]): 提案手法の事前学習の基盤. V-JEPA 2 はデータ・モデル・解像度・学習期間の 4軸スケーリングと 3D-RoPE の導入で大幅に拡張した
- **Octo** (Octo Model Team+, 2024): Open X-Embodiment 1M+ 軌跡で事前学習した VLA モデル. DROID で微調整しても把持成功率が低く (Cup 15%, Box 0%), V-JEPA 2-AC が全タスクで上回る (Tab. 2)
- **Cosmos** (Agarwal+, 2025): 20M時間の動画で学習した潜在拡散ベースの動画生成モデル. MPC に使うと 1行動あたり 4分を要し, V-JEPA 2-AC の 16秒と比べ 15倍遅い上に性能も劣る (Tab. 3)
- **DINO-WM / Sobal+ (2025)**: JEPA 表現上にワールドモデルを構築しシミュレーション環境で計画タスクをゼロショットで解く先行研究. V-JEPA 2 は同様の原理を実機ロボットの操作タスクへスケールさせた点で差別化される (§8)

新規性の核心は, 言語監督なしの自己教師あり動画エンコーダが, 少量のインタラクションデータだけで実機ゼロショット計画を可能にすることを初めて実証した点にある.

### どのように訓練・最適化したのか?

- **損失関数 / 最適化目的**:
  - 事前学習: マスクノイズ除去 L1 損失, `||P_phi(Delta_y, E_theta(x)) - sg(E_bar_theta(y))||_1` (式 1). EMA + stop-gradient で崩壊を防止
  - 行動条件付き学習: teacher-forcing 損失 (1ステップ先予測, 式 2) + rollout 損失 (2ステップ先自己回帰予測, 式 3) の和 (式 4). いずれも L1 損失
  - 計画時: ゴール表現との L1 距離をエネルギー関数として CEM で最小化 (式 5)

- **データセット**:
  - 事前学習: VideoMix22M (SSv2 168K, Kinetics 733K, HowTo100M 1.1M, YT1B 19M 動画 + ImageNet 1M 画像. Tab. 1). YT1B にはクラスタベースのキュレーションを適用
  - 行動条件付き学習: DROID データセット (Khazatsky+, 2024) から 62時間未満. Franka Panda のテレオペレーション動画. 4 fps, 256×256, 16フレームクリップ. 行動はエンドエフェクタ状態の差分 (7次元)
  - MLLM アライメント: 88.5M の画像・動画テキストペア (§7.4)

### どのように検証したか? 指標と結果は?

4つの軸で評価:

1. **動画分類 (理解)**: 凍結エンコーダ + 4層 attentive プローブ. 6タスク平均 88.2% (ViT-g384). SSv2 77.3% で同一プロトコルの次点 V-JEPA ViT-H 74.3 を上回る. K400 87.3%, IN1K 85.1% (Tab. 4)
2. **行動予測**: EK100 行動予測で recall@5 = 39.7 (ViT-g384). 従来最高 PlausiVL (8B) の 27.6 から +12.1 ポイント, 相対 44% 改善 (Tab. 5)
3. **動画質問応答**: LLaMA 3.1 8B との統合で PerceptionTest 84.0, MVP 44.5, TempCompass 76.9, TemporalBench 36.7, TOMATO 40.3. 8B クラスで複数ベンチマーク SOTA (Tab. 8)
4. **ロボット計画**: Franka Panda 2台 (異なるラボ) でゼロショット評価 (各10試行). Reach 100%, Grasp (Cup 65%, Box 25%), Pick-and-Place (Cup 80%, Box 65%). Octo, Cosmos を全タスクで上回る (Tab. 2, 3). 計画時間: RTX 4090 で 800サンプル×10反復, 1行動あたり 16秒

### 検証結果に基づいた議論, 明らかになった課題はあるか?

- (§4.3 Sensitivity to camera positioning) カメラ位置に対する感度が高い. ロボットのベースがカメラに映らない場合, 行動座標軸の推定が不定になり世界モデルにエラーが生じる. 実験ではカメラ位置を手動で調整
- (§4.3 Long horizon planning) 自己回帰予測の誤差蓄積により長期計画が困難. 探索空間も指数的に増大. 現状の pick-and-place は人間が中間サブゴール画像と切り替えタイミングを手動指定しており, サブゴールを自律生成する機構はない
- (§4.3 Image goals) ゴールが画像指定に限定されており, 言語によるゴール指定は未対応
- (§6 Limitations) EK100 行動予測では, 文脈動画の終了から行動開始までの時間差 (anticipation time) がデフォルトの 1秒を超えると精度が低下. 評価もキッチン環境に限定されており, 他環境への汎化は未検証
- (§9 Future work) 階層的モデルによる複数の時空間スケールでの予測, 言語ゴールとの統合, 1B 以上へのさらなるモデルスケーリングが今後の課題として挙げられている

---
## 自身の研究との関連

LeWM / LeJEPA の研究方向と直接的に関連する. V-JEPA 2-AC は JEPA ベースのワールドモデルで実機ゼロショット制御を実証した最初の大規模システムであり, LeWM (15M パラメータ, エンドツーエンド学習, SIGReg) とは対照的なアプローチを取る: 1B パラメータの事前学習済みエンコーダを凍結し, 300M の predictor のみをロボットデータで学習する. この規模差 (15M vs 1.3B) が研究上の問いになる: 小規模モデルでも SIGReg のような正則化で同等の実機性能が出るのか, あるいはインターネット規模の事前学習が本質的に必要なのか. 実機ベースラインとして DROID データセット (62h, Franka Panda) を使用しており, 今後の比較実験に直接活用できる.

---
## 追加議論

### DINO-WM との差: なぜ V-JEPA 2 は実機にスケールできたか

DINO-WM (Zhou+, 2024) も"凍結エンコーダ + 学習済み predictor"という同じ原理だが, シミュレーション環境での計画に留まっている. V-JEPA 2 が実機に到達できた要因は主に 2つ. 第一に, DINO-WM の DINOv2 は画像エンコーダ (静止画で学習) であるのに対し, V-JEPA 2 は 100万時間超の動画で学習した動画エンコーダであり, 時間方向のダイナミクス (物体の動き, 状態遷移) が表現に組み込まれている. 未知の実環境でも状態変化の予測が成り立ちやすい. 第二に, DINO-WM はシミュレータの行動データのみで predictor を学習するが, V-JEPA 2-AC は DROID (実機テレオペ 62h) で学習しており, 実機固有のノイズ・遅延・幾何を含むデータで行動-状態対応を獲得している.

---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@article{assran2025vjepa,
  title={V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning},
  author={Assran, Mahmoud and Bardes, Adrien and Fan, David and Garrido, Quentin and Howes, Russell and Komeili, Mojtaba and Muckley, Matthew and Rizvi, Ammar and Roberts, Claire and Sinha, Koustuv and Zholus, Artem and Arnaud, Sergio and Gejji, Abha and Martin, Ada and Hogan, Francois Robert and Dugas, Daniel and Bojanowski, Piotr and Khalidov, Vasil and Labatut, Patrick and Massa, Francisco and Szafraniec, Marc and Krishnakumar, Kapil and Li, Yong and Ma, Xiaodong and Chandar, Sarath and Meier, Franziska and LeCun, Yann and Rabbat, Michael and Ballas, Nicolas},
  journal={arXiv preprint arXiv:2506.09985},
  year={2025}
}
```
</details>
