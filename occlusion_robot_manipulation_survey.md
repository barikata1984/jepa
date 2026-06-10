# ロボット物体操作学習におけるオクルージョン対策 — 調査まとめ

> 本ドキュメントは、ロボットの物体操作学習におけるオクルージョン(遮蔽)対策手法の調査、
> マルチビュー観察 vs アクティブパーセプションの動向比較、公開データセット、
> および stable-worldmodel パイプラインへの接続に関する議論のまとめである。
> (調査日: 2026年6月10日。文献情報はウェブ検索結果に基づく)

---

## 1. オクルージョン対策手法の分類

対策手法は大きく5系統に整理できる。

### 1.1 マルチモーダルセンシング(触覚・聴覚)

視覚が遮られた状況を別モダリティで補うアプローチ。

- **視触覚マニピュレーション**: 高解像度触覚センサは遮蔽物体の操作に有効だが、コストと複雑さが普及の障壁 [1]。
- **音響の活用**: グリッパに取り付けたマイクで接触情報を取得し、視覚+音響の模倣学習を行う。LSTM で観測履歴を符号化し部分観測性に対処(Play it by Ear)[2]。
- **触覚なしの代替**: マルチモーダル融合の二重化と表現正規化により、触覚なしで遮蔽下のサンプル効率と頑健性を高める RL 手法 [1]。

### 1.2 アクティブパーセプション / Next-Best-View (NBV) 計画

カメラ視点を能動的に動かして遮蔽を解消する系統。研究が最も厚い。

- **Multi-View Picking (MVP)**: 把持へのリーチング動作中に eye-in-hand カメラの情報量の多い視点を選択。把持姿勢推定のエントロピーを制御に直接利用し、クラッタで約80%の把持成功率(単一視点比 +12%以上)[3]。
- **アフォーダンス駆動 NBV**: 形状再構成の情報利得ではなく、把持アフォーダンス自体を視点選択基準にする(ACE-NBV 等)[4]。
- **Neural Graspness Field**: NeRF ベースのリアルタイムマッピングを拡張し、graspness の不整合最小化で視点計画 [5]。
- **VLM/VLA との統合(2025〜2026 の新潮流)**:
  - GraspView: 候補視点を点群からレンダリングし VLM でスコアリングする render-and-score 戦略 [6]。
  - ActiveVLA: VLA モデルに遮蔽考慮の視点計画を統合 [7]。
  - SaPaVe: 視野切れには視点調整、物理的遮蔽には容器を開ける等の能動操作を要求するベンチマーク [8]。

### 1.3 形状補完・アモーダル補完(見えない部分の推定)

- **3D 形状補完の古典**: 単一視点の 2.5D 点群を 3D CNN で補完して把持計画(Varley et al.)。44万超の 3D サンプルのデータセットも公開 [9]。
- **拡散モデルによる補完**: 単一視点深度からカテゴリレベル 3D 形状補完。補完なし比で把持成功率 +23% [10]。
- **アモーダルセグメンテーション**: 遮蔽部分を含む物体全体のマスク推定。未知物体への階層的遮蔽モデリング(UOAIS)[11]、サーベイ [12]。
- **ベンチマーク**: TARGO — 遮蔽下ターゲット指向把持の評価。TARGO-Net は遮蔽物を除去せず直接ターゲットを再構成・把持 [13]。
- **ダイナミクスモデルでの対応**: ACID — 部分 RGB-D を 3D 特徴場に符号化し占有確率予測で遮蔽に対処(変形物体)[14]。

### 1.4 インタラクティブパーセプション(環境への物理的働きかけ)

- **push-grasp 協調**: 把持・プッシュ等の行動プリミティブを生成器-評価器で選択(GE-Grasp)[15]。
- **VLM 連携**: 言語指示でターゲット特定後、プッシュで再配置して把持成功率を向上(Ground4Act)[16]。
- **対話的形状推定**: ピクセル単位の不確実性に基づき、推定精度とインタラクションコストのトレードオフを最適化 [17]。

### 1.5 学習アルゴリズム・表現側の工夫

- 観測履歴を考慮した diffusion ポリシー(FlowBotHD)[18]、パーティクルフィルタ等の確率推論(古典)[18]。
- 遮蔽物・環境制約・ロボット形態まで考慮した「環境認識アフォーダンス」学習 [19]。

---

## 2. 固定マルチビュー vs アクティブパーセプション

**結論**: 疎な固定マルチカメラ(外部 + 手首)は今も事実上の標準。NeRF/3DGS 的な
「密な多視点撮影」は研究系統として存在するがコスト要因としてスパース化が進行中で、
その延長で「ロボット自身が視点を動かす」アクティブビジョンが直近のトレンド。

### 2.1 固定マルチビューの現状

- 外部視点 + 手首カメラの複数視点は相補的情報を提供し操作性能を大きく向上させる [20]。ALOHA / DROID 等の標準構成。
- ただし密な多視点は実用上の制約が大きい: 3DGS はオフライン最適化が必要で明示的ジオメトリを欠き [21]、マルチビュー構成は同期・帯域・外部キャリブレーションの複雑さを増幅 [22]。操作中の動的シーンとも相性が悪い。

### 2.2 NeRF / 3DGS 系の研究(スパース化へ)

- GaussianGrasper: 限られた RGB-D 視点から特徴場を構築し衝突のない把持候補を生成 [23]。
- ManiGaussian: ガウス点が操作とともに動く動的 GS で、静的再構成の限界に対処 [24]。
- SparseGrasp: DUSt3R でスパース視点から初期化し、Render-and-Compare でシーン高速更新 [25]。
- SparseGrasper: わずか3枚の RGB から 3D ガウス言語場を構築(密多視点要求からの脱却)[26]。
- 方向性: 「密な多視点撮影」は目的ではなく削減すべきコストとして扱われている。

### 2.3 アクティブビジョンのトレンド(2024〜)

- 手首カメラの視点は知覚目的ではなく操作要求に拘束され、遮蔽下で情報を捉え損ねる(Vision in Action)[27]。
- Observe Then Act: タスク目標に基づき第三者カメラを再配置する NBV ポリシー + 操作ポリシーの直列接続 [28]。
- ActiveUMI: VR ヘッドセットで操作者の頭部運動を追跡し、ポリシー自身が視点を能動制御 [29]。

### 2.4 両者の融合

- **ObAct**: 双腕の一方(observer)が3枚の画像から 3DGS を構築 → 仮想探索で最適視点を発見 → 移動、他方(actor)がその観測でポリシー実行。静的カメラ比で遮蔽下の behavior cloning が +143% [30]。3DGS は「事前データ」ではなく「視点計画のための内部表現」へ。
- 逆方向: 外部カメラ1台から拡散モデルで手首視点を合成し、物理カメラなしで二視点推論 [31]。WristWorld は 4D 世界モデルで手首視点を生成 [32]。

---

## 3. 公開マルチビューデータセット

### 3.1 キャリブ済みマルチビューの大規模実機データセット

| データセット | 視点構成 | 規模 | 公開形態 |
|---|---|---|---|
| **RH20T** [33] | グローバルカメラ 8〜10台 + 手先 1〜2台(全カメラ基部座標系にキャリブ済・時間同期)。RGB / 深度 / IR / 力覚 / 音声 | 11万+ シーケンス、約20TB | rh20t.github.io |
| **DROID** [34] | 手首1 + 外部ステレオ2(計3ストリーム、キャリブ付)。1,417 視点をカバー | 76k 軌道 / 350時間 / 564シーン | CC-BY 4.0、droid-dataset.github.io、HuggingFace(2025年に36kエピソードの改良キャリブ追加) |
| **AgiBot World** [35] | 統一エンボディメント・カメラ構成(全視点動画 + PNG深度) | 100万+ 双腕軌道(Alpha は 92,214 軌道 / 約8.5TB) | HuggingFace、LeRobot 変換スクリプト公式提供 |
| **AgiBot World 2026** [36] | G2 ロボット、実環境100% + デジタルツイン(GenieSim) | — | HuggingFace、LeRobot v2.1 構造 |
| **Open X-Embodiment** [37] | 21機関・22エンボディメント(カメラ構成はデータセットごとに不均一) | 240万軌道 | 公開(キャリブ情報の有無はサブセット依存) |

### 3.2 手法論文のコード公開

- 3DGS 系(GaussianGrasper / ManiGaussian / Splat-MOVER 等)は論文・コード・プロジェクトページが公開されており、Awesome-3D-Gaussian-Splatting-in-Robotics [38] にキュレーションされている。
- Varley らの形状補完データセット(44万 3D サンプル)はオープンソース [9]。TARGO ベンチマーク公開 [13]。
- ObAct はプロジェクトページ(obact.github.io)から動画・コードを辿れる [30]。

### 3.3 注意点

「NeRF/3DGS 品質の密多視点 × 実機操作 × 大規模」を全て満たす公開データセットは未だ存在しない。
現実的な選択肢: (a) RH20T の 8〜10 視点キャリブ済データ、(b) DROID + 改良キャリブ + スパースビュー再構成(DUSt3R / VGGT 系)、(c) シミュレータ(RLBench 等)での任意視点レンダリング。

---

## 4. stable-worldmodel (swm) パイプラインへの接続

### 4.1 swm のデータ層

- swm は Lance ベースの高性能データレイヤを持ち、**MP4 / HDF5 / LeRobot データセットのネイティブサポートと変換ツール**を提供 [39]。
- 制約条件は「LeRobot 形式にできるもの、または HDF5/MP4 で持っているもの」。**DROID 一択ではない**。

### 4.2 データセット選択肢

| 選択肢 | 変換の手間 | 備考 |
|---|---|---|
| DROID | ほぼゼロ(LeRobot 公式版あり) | 改良キャリブで 3D 系世界モデルにも使いやすい。PointWorld [40] が外部2カメラから 3D シーンフロー復元の前例 |
| AgiBot World | 小(公式変換スクリプト) | 統一カメラ構成・深度付き・100万軌道。2026版は最初から LeRobot v2.1。実写+シミュ対データが世界モデル評価に好適 |
| OXE / RoboMIND / LIBERO | 小〜中 | Any4LeRobot [41] が LeRobot 形式への変換とバージョン間変換(v1.6〜v3.0)をサポート |
| RH20T | 中(自前変換が必要) | 多視点条件付き世界モデル・視点不変表現の学習には最有力 |
| swm 内蔵環境 | ゼロ | 色・形状・物理特性まで完全カスタマイズ可能 [42]。遮蔽あり/なしの統制実験に好適 |

### 4.3 推奨ワークフロー

1. swm 内蔵環境(PushT 等)で遮蔽を統制した in-silico 実験を設計
2. 手軽な実データとして DROID(LeRobot 公式版)で検証
3. スケール・統一構成が必要なら AgiBot World
4. 密多視点・深度・力覚を使う遮蔽研究なら RH20T を自前変換

※ swm は 2026 年公開の若いライブラリのため、各データセットローダの対応状況は
公式ドキュメント(https://galilai-group.github.io/stable-worldmodel/)で要確認。

---

## 文献リスト

※ 書誌情報は調査時点のウェブ検索結果に基づく。会議名・年は arXiv 掲載情報等から推定したものを含むため、引用時は原典を確認のこと。

[1] "Sample-efficient and occlusion-robust reinforcement learning for robotic manipulation via multimodal fusion dualization and representation normalization." *Neural Networks*, 2025. https://www.sciencedirect.com/science/article/abs/pii/S0893608025000814

[2] M. Du, O. Y. Lee, S. Nair, C. Finn. "Play it by Ear: Learning Skills amidst Occlusion through Audio-Visual Imitation Learning." *RSS*, 2022. arXiv:2205.14850. https://arxiv.org/abs/2205.14850

[3] D. Morrison, P. Corke, J. Leitner. "Multi-View Picking: Next-best-view Reaching for Improved Grasping in Clutter." *ICRA*, 2019. arXiv:1809.08564. https://arxiv.org/abs/1809.08564

[4] X. Zhang et al. "Affordance-Driven Next-Best-View Planning for Robotic Grasping (ACE-NBV)." *CoRL*, 2023. arXiv:2309.09556. https://arxiv.org/abs/2309.09556

[5] H. Ma et al. "Active Perception for Grasp Detection via Neural Graspness Field." *NeurIPS*, 2024. https://proceedings.neurips.cc/paper_files/paper/2024/file/4364fef031fdf7bfd9d1c9c56b287084-Paper-Conference.pdf

[6] "GraspView: Active Perception Scoring and Best-View Optimization for Robotic Grasping in Cluttered Environments." 2025. arXiv:2511.04199. https://arxiv.org/abs/2511.04199

[7] "ActiveVLA: Injecting Active Perception into Vision-Language-Action Models for Precise 3D Robotic Manipulation." 2026. arXiv:2601.08325. https://arxiv.org/abs/2601.08325

[8] "SaPaVe: Towards Active Perception and Manipulation in Vision-Language-Action Models for Robotics." 2026. arXiv:2603.12193. https://arxiv.org/abs/2603.12193

[9] J. Varley, C. DeChant, A. Richardson, J. Ruales, P. Allen. "Shape Completion Enabled Robotic Grasping." *IROS*, 2017. arXiv:1609.08546. https://arxiv.org/abs/1609.08546

[10] A. Kashyap, Y. Yang, H. Andreasson, T. Stoyanov. "Single-View Shape Completion for Robotic Grasping in Clutter." 2025. arXiv:2512.16449. コード: https://amm.aass.oru.se/shape-completion-grasping/

[11] S. Back et al. "Unseen Object Amodal Instance Segmentation via Hierarchical Occlusion Modeling." *ICRA*, 2022. arXiv:2109.11103. https://arxiv.org/abs/2109.11103

[12] "Image Amodal Completion: A Survey." 2022. arXiv:2207.02062. https://arxiv.org/abs/2207.02062

[13] "TARGO: Benchmarking Target-driven Object Grasping under Occlusions." 2024. arXiv:2407.06168. https://arxiv.org/abs/2407.06168

[14] "A review of learning-based dynamics models for robotic manipulation." *Science Robotics*, 2025. https://www.science.org/doi/10.1126/scirobotics.adt1497 (ACID への言及を含むレビュー)

[15] Z. Liu et al. "GE-Grasp: Efficient Target-Oriented Grasping in Dense Clutter." *IROS*, 2022. https://ziweiwangthu.github.io/data/GE-Grasp.pdf

[16] "Ground4Act: Leveraging visual-language model for collaborative pushing and grasping in clutter." *Image and Vision Computing*, 2024. https://www.sciencedirect.com/science/article/pii/S0262885624003858

[17] "Interactive shape estimation for densely cluttered objects." *Pattern Recognition Letters*, 2025. https://www.sciencedirect.com/science/article/abs/pii/S0167865525000686

[18] "FlowBotHD: History-Aware Diffuser Handling Ambiguities in Articulated Objects Manipulation." *CoRL*, 2024. arXiv:2410.07078. https://arxiv.org/abs/2410.07078

[19] "Learning Environment-Aware Affordance for 3D Articulated Object Manipulation under Occlusions." *NeurIPS*, 2023. arXiv:2309.07510. https://arxiv.org/abs/2309.07510

[20] "Imagination at Inference: Synthesizing In-Hand Views for Robust Visuomotor Policy Inference." 2025. arXiv:2509.15717. https://arxiv.org/abs/2509.15717

[21] "3D Gaussian Splatting for Robotics: Scene Reconstruction, Navigation and Grasp Planning." RoboCloud Hub, 2025. https://robocloud-dashboard.vercel.app/learn/blog/gaussian-splatting-robotics

[22] "ROI-Driven Foveated Attention for Unified Egocentric Representations in Vision-Language-Action Systems." 2026. arXiv:2603.20668. https://arxiv.org/abs/2603.20668

[23] "GaussianGrasper: 3D Language Gaussian Splatting for Open-vocabulary Robotic Grasping." *IEEE RA-L*, 2024. プロジェクト: https://mrsecant.github.io/GaussianGrasper/

[24] G. Lu et al. "ManiGaussian: Dynamic Gaussian Splatting for Multi-task Robotic Manipulation." *ECCV*, 2024. arXiv:2403.08321. https://arxiv.org/abs/2403.08321

[25] "SparseGrasp: Robotic Grasping via 3D Semantic Gaussian Splatting from Sparse Multi-View RGB Images." 2024. arXiv:2412.02140. https://arxiv.org/abs/2412.02140

[26] "Sparse-View 3-D Language Gaussian Splatting for Zero-Shot Robotic Grasping (SparseGrasper)." *IEEE*, 2026. https://ieeexplore.ieee.org/document/11363633

[27] "Vision in Action: Learning Active Perception from Human Demonstrations." 2025. arXiv:2506.15666. https://arxiv.org/abs/2506.15666

[28] "Observe Then Act: Asynchronous Active Vision-Action Model for Robotic Manipulation." 2025. https://www.researchgate.net/publication/388948168

[29] "ActiveUMI: Robotic Manipulation with Active Perception from Robot-Free Human Demonstrations." 2025. arXiv:2510.01607. https://arxiv.org/abs/2510.01607

[30] "Observer-Actor (ObAct): Active Vision Imitation Learning with 3D Gaussian Splatting." 2025. arXiv:2511.18140. プロジェクト: https://obact.github.io

[31] (同 [20] Imagination at Inference)

[32] "WristWorld: Generating Wrist-Views via 4D World Models for Robotic Manipulation." 2025. arXiv:2510.07313. https://arxiv.org/abs/2510.07313

[33] H.-S. Fang et al. "RH20T: A Comprehensive Robotic Dataset for Learning Diverse Skills in One-Shot." *ICRA*, 2024. arXiv:2307.00595. https://rh20t.github.io/

[34] A. Khazatsky et al. "DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset." *RSS*, 2024. arXiv:2403.12945. https://droid-dataset.github.io/ (CC-BY 4.0)

[35] AgiBot World Team. "AgiBot World." *IROS 2025 Best Paper Award Finalist / IEEE T-RO 2026*. GitHub: https://github.com/OpenDriveLab/AgiBot-World / HuggingFace: https://huggingface.co/datasets/agibot-world/AgiBotWorld-Beta

[36] "AgiBot World 2026." HuggingFace, 2026. https://huggingface.co/datasets/agibot-world/AgiBotWorld2026

[37] Open X-Embodiment Collaboration. "Open X-Embodiment: Robotic Learning Datasets and RT-X Models." *ICRA*, 2024. https://robotics-transformer-x.github.io/

[38] "Awesome-3D-Gaussian-Splatting-in-Robotics." GitHub キュレーションリスト. https://github.com/zstsandy/Awesome-3D-Gaussian-Splatting-in-Robotics

[39] "stable-worldmodel: A Platform for Reproducible World Modeling Research and Evaluation." 2026. arXiv:2605.21800. https://arxiv.org/abs/2605.21800 / ドキュメント: https://galilai-group.github.io/stable-worldmodel/ (関連: stable-worldmodel-v1, arXiv:2602.08968)

[40] "PointWorld: Scaling 3D World Models for In-The-Wild Robotic Manipulation." 2026. arXiv:2601.03782. https://arxiv.org/abs/2601.03782

[41] "Any4LeRobot / Any4LeRobotGUI." GitHub. https://github.com/omniedgeio/Any4LeRobotGUI (OpenX / AgiBot-World / RoboMIND / LIBERO → LeRobot 変換)

[42] Stable World-Model 公式ドキュメント. https://galilai-group.github.io/stable-worldmodel/
