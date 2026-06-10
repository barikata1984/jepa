# Literature Survey: 多視点自己教師あり学習によるロボット物体操作 — JEPA 式潜在 alignment・順動力学・逆動力学による復元不要アプローチ

| | |
|---|---|
| **Date** | 2026-06-09 |
| **Scope** | JEPA 系 alignment 損失, 潜在順/逆動力学, 多視点表現学習, 3D/4D ワールドモデルの交差領域. ロボット操作への応用を中心に, 復元ベースと alignment ベースの対比を軸に 51 論文を採録 |
| **Papers mapped** | 51 |
| **Hub papers (deep-read)** | 9 (既存ローカルノート 3 + 新規 6) |
| **Research Questions** | RQ1: 多視点観測から操作表現を学ぶ自己教師あり手法の分類 / RQ2: 潜在順/逆動力学の評価条件と限界 / RQ3: JEPA alignment × 多視点一貫性の探索状況と未開拓領域 / RQ4: 復元不要アプローチ vs 復元ベースの優劣条件 / RQ5: 多視点操作学習のモチベーション |

## Abstract

ロボット操作のための視覚表現学習は, 復元ベース (VAE, NeRF, 3DGS) と alignment ベース (対比学習, JEPA) の 2 つの系統に分岐しつつある. 本サーベイは 51 論文を採録し, JEPA 系 alignment 損失・潜在順動力学・潜在逆動力学・多視点一貫性の 4 つの技術軸の交差点を体系的にマッピングした. 主要な発見として, (1) JEPA 式 alignment 損失を多視点間に適用した研究は存在せず, (2) 順/逆動力学の分離事前学習が 2025–2026 年に急速に進展し, (3) 意味表現エンコーダが復元系エンコーダをロボット制御タスクで一貫して上回ることが実証されている. これらの知見は, seed 15 本からの snowballing と 8 角度の直接検索により導出された.

## Research Landscape Overview

ロボット操作のための視覚表現学習は, 2022–2023 年の R3M, VIP, MVP といった基盤表現の登場以降, 急速に多様化した. 2024 年には DreamerV3 と TD-MPC2 が潜在ワールドモデルの実用性を実証し, DINO-WM が事前学習済み意味表現上での潜在ダイナミクス予測の有効性を示した. 2025 年に入ると, JEPA 系の理論的成熟 (LeJEPA の SIGReg, Klindt+ の識別可能性証明) と, それを行動条件付きワールドモデルに応用する LeWM・V-JEPA 2-AC が登場し,"復元なし"の潜在予測パラダイムが確立された.

並行して, 多視点ロボット操作の研究も活発化している. MV-MWM (ICML 2023), ReViWo (ICLR 2025), MAD (CoRL 2025) などが, 複数カメラからの情報統合と視点頑健性を追求しているが, いずれも復元ベースまたは対比学習ベースであり, JEPA 式 alignment を多視点間に適用した例はない.

2026 年には, 順/逆動力学の分離事前学習 (DeFI), JEPA 式 VLA 事前学習 (VLA-JEPA), 物体レベル JEPA (Causal-JEPA), 3D 潜在ワールドモデル (4D Latent WM) など, 本サーベイの各軸を個別に深化させる研究が同時多発的に出現しており, これらの統合が次の frontier となっている.

## Terminology and Background

| 用語 | 同義語・変種 | 本サーベイでの範囲 |
|------|------------|-----------------|
| JEPA | Joint-Embedding Predictive Architecture | I-JEPA, V-JEPA, LeJEPA, C-JEPA 等の総称. alignment 損失 + 正則化による潜在予測 |
| alignment 損失 | invariance loss, prediction loss (in embedding space) | 2 つのビュー/時刻の埋め込み間の MSE. 復元損失 (ピクセル空間) と区別 |
| SIGReg | Sketched Isotropic Gaussian Regularization | LeJEPA の崩壊防止正則化. Epps-Pulley 検定で等方ガウスを強制 |
| 順動力学 | forward dynamics, transition model | 現在の状態と行動から次状態を潜在空間で予測 |
| 逆動力学 | inverse dynamics | 2 つの状態 (現在・未来) から行動を推定 |
| VLA | Vision-Language-Action model | 視覚・言語・行動を統合したロボット基盤モデル |
| 3DGS | 3D Gaussian Splatting | 3D シーン表現の一手法. GWM, GAF, 4D Latent WM 等で使用 |
| NeRF | Neural Radiance Field | 暗黙的 3D 表現. 本サーベイではモチベーションとして参照 |
| VIR / VDR | View-Invariant / View-Dependent Representation | ReViWo で導入された表現分離の枠組み |

## Survey Findings

### Thesis

本分野の根本的未解決問題は, **多視点観測からの操作に有用な潜在表現の獲得において, 復元を経由すべきか, 潜在空間での alignment で十分かが決着していない** ことである. 復元ベース (3DGS, VAE, 拡散モデル) は 3D 幾何の明示的な獲得を保証するが, 固有次元と潜在次元のミスマッチ, 計算コスト, ピクセル変動への過剰適合といった構造的課題を抱える ([[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics|Balestriero+ 2025]], [[papers/Nilaksh-arXiv2026-Reconstruction_Semantics_What/reconstruction-or-semantics-what-makes-a-latent-space-useful-for-robotic-world-models|Nilaksh+ 2026]]). 一方, alignment ベース (JEPA) は理論的に等方ガウス最適性が証明され, 復元なしで識別可能な表現を学習できるが, 現状では単一視点・2D パッチレベルの枠組みに留まっている ([[papers/Klindt-arXiv2026-When_LeJEPA_Learn/when-does-lejepa-learn-a-world-model|Klindt+ 2026]]). この 2 系統を多視点操作の文脈で直接比較した研究は存在しない.

### Foundation

本分野が共通して依拠する技術的基盤は以下の通りである.

1. **潜在空間での予測 (復元不要パラダイム)**: JEPA 系 (LeJEPA, V-JEPA 2, Causal-JEPA) と非 JEPA 系 (TD-MPC2, DINO-WM) の両方が, ピクセル再構成を回避して埋め込み空間で未来を予測する. LeJEPA の SIGReg は崩壊防止の理論的保証を与え ([[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics|Balestriero+ 2025]]), Klindt+ 2026 がガウス世界での線形識別可能性を証明した ([[papers/Klindt-arXiv2026-When_LeJEPA_Learn/when-does-lejepa-learn-a-world-model|Klindt+ 2026]]).

2. **順/逆動力学の分離と統合**: PIDM (Tian+ ICLR 2025) は視覚予測と逆動力学のエンドツーエンド統合でスケーラビリティを実証し, DeFI (Zhang+ ICLR 2026) は両者の分離事前学習がデータ効率と安定性を高めることを示した. JIF (Khandate+ RSS 2025) は人間デモからの同時学習, LAPA (ICLR 2025) は動画からの潜在行動抽出を実現した.

3. **事前学習済みビジョンエンコーダの活用**: DINOv2 / V-JEPA 2 系の凍結エンコーダが, ワールドモデル (DINO-WM, VLA-JEPA) やポリシー学習 (JEPA-VLA) の入力表現として広く使われている. Nilaksh+ 2026 は V-JEPA 2.1 が復元系エンコーダ (SD3 VAE, Cosmos) を一貫して上回ることを体系的に実証した.

4. **多視点情報の統合手法**: 対比学習 (Multi-View Dreaming), マスク再構成 (MV-MWM, 3D-MVP), 表現分離 (ReViWo, MAD, MVD), 3D 陽表現 (ManiVID-3D, SPA) の 4 アプローチが共存している. いずれもビュー不変な状態表現の獲得を目指すが, 学習目的関数が異なる.

### Progress

主要な進展を時系列で整理する.

1. **SFA → 対比学習 → JEPA (2002–2023)**: 遅い特徴分析 (Wiskott & Sejnowski 2002) が時間的不変性の原理を確立し, InfoNCE / CPC (van den Oord+ 2018) が対比予測符号化を体系化した. I-JEPA (Assran+ CVPR 2023) がマスク予測による JEPA を提案し, 復元なし表現学習の実用性を示した.

2. **潜在ワールドモデルの確立 (2023–2024)**: DreamerV3 (Nature 2025) と TD-MPC2 (ICLR 2024) が, 潜在空間でのダイナミクス予測がピクセル空間での復元と同等以上の制御性能を達成することを 150+ 環境で実証した.

3. **JEPA のスケーリングと理論化 (2025)**: LeJEPA が SIGReg を導入し ~50 行の実装で 60+ アーキテクチャに適用可能な安定 JEPA を実現 ([[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics|Balestriero+ 2025]]). V-JEPA 2 がビデオに拡張し, V-JEPA 2-AC が 62 時間の未ラベルロボット動画からゼロショット計画を達成した ([[papers/Assran-arXiv2025-V-JEPA_Self-Supervised_Video/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning|Assran+ 2025]]).

4. **順/逆動力学の爆発的進展 (2025–2026)**: PIDM が視覚予測 + 逆動力学のエンドツーエンド統合で CALVIN ABC-D Avg. Len. 4.28 を達成 ([[papers/Tian-ICLR2025-PIDM_Scalable_Learners/predictive-inverse-dynamics-models-are-scalable-learners-for-robotic-manipulation|Tian+ 2025]]). DeFI が分離事前学習で 4.51 に更新し, GFDM 凍結 + GIDM 更新の知見を提供 ([[papers/Zhang-ICLR2026-DeFI_Disentangled_Robot/disentangled-robot-learning-via-separate-forward-and-inverse-dynamics-pretraining|Zhang+ 2026]]). VLA-JEPA が JEPA 式漏洩防止予測で VLA 事前学習を実現し, 外乱頑健性で既存手法を上回った ([[papers/Sun-arXiv2026-VLA-JEPA_Enhancing_VLA/vla-jepa-enhancing-vision-language-action-model-with-latent-world-model|Sun+ 2026]]).

5. **3D 潜在表現の台頭 (2025–2026)**: 4D Latent WM がスパースボクセル潜在空間で 3D 構造の時間発展を直接モデル化し, 逆動力学で行動に変換するパイプラインで ManiSkill3 成功率 61.3% を達成 ([[papers/Li-ICLR2026-4D_Latent_World/4d-latent-world-model-for-robot-planning|Li+ 2026]]).

### Gap

1. **JEPA alignment × 多視点の空白**

Concept Matrix が示す通り, JEPA 式 alignment 損失と多視点一貫性を組み合わせた研究は存在しない. V-JEPA 2 は単一視点の時間マスク予測, ReViWo は復元ベースのビュー分離, MV-MWM はマスク再構成であり, いずれも JEPA の alignment 損失 (MSE in embedding + SIGReg) を複数カメラ間に適用していない. Klindt+ 2026 の識別可能性定理は"同じ潜在状態から生成された 2 つの観測"に対して成立し, 多視点カメラの設定と構造的に対応する. ただし定理は時間的ビューペアを仮定しており, カメラごとに生成関数が異なる空間的ペアへの拡張は未証明である (Seed 1 Readiness 参照). この拡張が証明されれば, 復元なしで 3D 的に一貫な操作表現を獲得する理論的基盤が得られる.

2. **順/逆動力学 + 多視点 alignment の統合**

PIDM と DeFI は順/逆動力学の統合・分離を探索したが, いずれも単一視点 (または固定カメラ配置) を前提としている. ReViWo は多視点 + ワールドモデルを扱うが, 逆動力学モジュールを持たない. 4D Latent WM は多視点 + 逆動力学だが復元ベースである. $L_{\text{align}}(\text{multi-view}) + L_{\text{fwd}} + L_{\text{inv}}$ の 3 項を潜在空間で統合した研究は皆無であり, 各構成要素は個別に実証済みだが結合は未検証である.

3. **SIGReg の次元ミスマッチ問題の多視点での増悪**

LeJEPA/LeWM で報告された固有次元と潜在次元のミスマッチ (Klindt+ 2026 §7, LeWM の TwoRoom 性能低下) は, 多視点設定でさらに深刻になりうる. 複数カメラからの冗長な視覚情報を等方ガウスに詰め込む際, 操作に必要な自由度 (物体位置・姿勢・接触状態) は少数であり, 余剰次元へのノイズ充填が加速する. Rectified LpJEPA (Kuang+ 2026) のスパース表現やVJEPA (Huang+ ICML 2026) の確率的予測が緩和策となりうるが, 多視点での検証は未実施である.

4. **物体レベル推論の操作への展開**

Causal-JEPA ([[papers/Nam-ICML2026-Causal-JEPA_Object-Level/causal-jepa-learning-world-models-through-object-level-latent-masking|Nam+ 2026]]) は物体レベルマスキングで相互作用推論を強制したが, 評価は CLEVRER (合成映像) と Push-T (2D) に限定されている. 実機の多視点カメラから物体スロットを抽出し, 物体間相互作用を潜在空間で予測する枠組みは未確立である. 遮蔽が頻発する操作シーンでは物体レベルの推論が不可欠であり, Causal-JEPA のアプローチを多視点 + 実機操作に拡張することは工学的に大きなインパクトを持つ.

### Seed

#### Seed Overview

| Seed | 前提 | アプローチ |
|------|------|----------|
| 1 | JEPA alignment は"同一潜在状態の異なる観測間の一貫性"を学ぶ. 多視点カメラは同一 3D シーンの異なる 2D 射影を生成する. 両者は構造的に対応 (定理の空間的ペアへの拡張は未証明) | 多視点間に JEPA alignment + SIGReg を適用し, 復元なしでビュー不変表現を獲得 |
| 2 | 順動力学 (LeWM) と逆動力学 (PIDM/DeFI) は個別に実証済み. 多視点 alignment は ReViWo が実証済み. 三者の統合は未検証 | L_align + L_fwd + L_inv の 3 項統合損失で, 多視点復元不要操作学習 |
| 3 | Causal-JEPA の物体レベルマスキングは合成環境で有効. 多視点は遮蔽の自然な解消手段 | Causal-JEPA を多視点に拡張し, 物体間相互作用 + 遮蔽解消を同時に学習 |

Seed 1 は Seed 2 の基盤となる表現学習モジュールであり, 先に確立すべきである. Seed 2 は Seed 1 の表現の上に順/逆動力学を構築する. Seed 3 は Seed 1–2 のパッチレベル表現を物体レベルに昇格させる独立した拡張であり, 並行して進められる. 推奨進行順序: Seed 1 → Seed 2 → Seed 3 (ただし Seed 3 は Seed 1 完了後に並行開始可能).

#### Seed 1: 多視点 JEPA Alignment — 復元なしビュー不変表現学習

##### Seed 1 — Academic Contribution

Gap 1 (JEPA alignment × 多視点の空白) を直接埋める. Klindt+ 2026 の識別可能性定理を多視点設定に拡張し,"同一 3D シーンの異なるカメラ視点"を JEPA の 2 ビューとして扱うことで, 復元なしでビュー不変表現を獲得できるかを理論的・実験的に検証する. SPA (ICLR 2025) がニューラルレンダリング (復元) で達成したビュー不変表現を, JEPA alignment (非復元) で代替できれば, 計算効率と意味表現品質の両面で優位性を主張できる.

##### Seed 1 — Required Components

1. 多視点データセット (2+ カメラのロボット操作データ)
2. JEPA alignment 損失の多視点拡張 (カメラ間 MSE in embedding)
3. SIGReg 正則化 (崩壊防止)
4. 評価プロトコル: 線形プローブ, 新規視点汎化, 下流操作タスク成功率
5. ベースライン: SPA (復元ベース), ReViWo (再構成ベース分離), MV-MWM (マスク再構成)

##### Seed 1 — Readiness Assessment

| Component | Status | Detail |
|-----------|--------|--------|
| 多視点データ | Available | DROID (76K 軌跡, マルチカメラ), BridgeV2, RoboMIND |
| JEPA alignment 損失 | Adaptable | LeJEPA の ~50 行実装が公開済み. 空間マスク → カメラ間ペアリングへの変更が必要 |
| SIGReg | Available | LeJEPA で実装・理論保証済み (Balestriero+ 2025) |
| 多視点での識別可能性理論 | New development required | Klindt+ 2026 の定理は時間的ビューペアを仮定. 空間的 (カメラ間) ビューペアへの拡張は未証明 |
| 評価プロトコル | Available | ReViWo の CIP/CSH 評価, SPA の 268 タスク評価が再利用可能 |

#### Seed 2: 多視点復元不要操作学習 — L_align + L_fwd + L_inv の統合

##### Seed 2 — Academic Contribution

Gap 2 (順/逆動力学 + 多視点 alignment の統合) を埋める. Seed 1 のビュー不変表現の上に行動条件付き順動力学予測 (LeWM 方式) と逆動力学行動抽出 (PIDM/DeFI 方式) を追加し, 3 項損失 $L = \lambda_1 L_{\text{align}} + \lambda_2 L_{\text{fwd}} + \lambda_3 L_{\text{inv}}$ による統一的な自己教師あり操作学習を実現する. DeFI の知見 (順/逆の分離事前学習が統合より安定) を多視点設定で再検証することも含む.

##### Seed 2 — Required Components

1. Seed 1 のビュー不変エンコーダ (事前学習済み or 同時学習)
2. 行動条件付き潜在 predictor (LeWM / V-JEPA 2-AC 方式)
3. 逆動力学ヘッド (PIDM 方式の [INV] トークン or DeFI 方式の GIDM)
4. 統合 vs 分離事前学習の比較実験設計
5. 評価: CALVIN, LIBERO, 実機操作 (視点変化条件含む)

##### Seed 2 — Readiness Assessment

| Component | Status | Detail |
|-----------|--------|--------|
| ビュー不変エンコーダ | Adaptable | Seed 1 の成果に依存. 代替として V-JEPA 2 凍結エンコーダ + カメラ間 alignment fine-tuning |
| 行動条件付き predictor | Available | LeWM (Maes+ 2026), V-JEPA 2-AC (Assran+ 2025) で実装済み |
| 逆動力学ヘッド | Available | PIDM (Tian+ 2025), DeFI (Zhang+ 2026) で実装済み |
| 3 項損失の balancing | New development required | $\lambda$ の探索空間, 分離 vs 統合の最適戦略は未知. DeFI の"GFDM 凍結 + GIDM 更新"の知見が出発点 |
| 多視点評価ベンチマーク | Adaptable | ReViWo の CIP/CSH 設定を CALVIN/LIBERO に移植する必要あり |

#### Seed 3: 多視点物体レベル JEPA — 遮蔽解消と相互作用推論の統合

##### Seed 3 — Academic Contribution

Gap 4 (物体レベル推論の操作への展開) を Causal-JEPA の多視点拡張として実現する. 単一カメラでは遮蔽により物体スロットの情報が欠落するが, 多視点カメラは遮蔽を自然に補完する. 多視点からの物体スロット抽出 + Causal-JEPA のマスキングによる相互作用推論を組み合わせることで, 遮蔽が頻発する密な操作シーン (例: ビンピッキング, 積み上げ) での計画精度向上が期待される.

##### Seed 3 — Required Components

1. 多視点対応の物体スロット抽出器 (SAVi / MONet の多視点拡張 or 3D 点群ベース)
2. Causal-JEPA のオブジェクトレベルマスキング + 予測目的
3. 多視点遮蔽補完メカニズム (ビュー間でのスロット情報統合)
4. 評価: 遮蔽を含む操作タスク (ビンピッキング, 積み上げ等)

##### Seed 3 — Readiness Assessment

| Component | Status | Detail |
|-----------|--------|--------|
| 物体スロット抽出 | Adaptable | Causal-JEPA は SAVi を使用. 多視点への拡張は ManiVID-3D の ViewNet が参考になる |
| オブジェクトマスキング | Available | Causal-JEPA (Nam+ 2026) で実装・理論保証済み |
| 多視点スロット統合 | New development required | 異なるカメラからの同一物体スロットの対応付けと情報統合は未解決 |
| 遮蔽評価ベンチマーク | Adaptable | ManiSkill3 の既存タスクに遮蔽条件を追加, または TVVE の仮想ビュー設定を利用 |

## Concept Matrix

| Paper | JEPA alignment | 順動力学 | 逆動力学 | 多視点/ビュー不変 | 3D/4D 表現 | 復元不要 |
|-------|:-:|:-:|:-:|:-:|:-:|:-:|
| I-JEPA 2023 | ● | | | | | ● |
| [[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics\|LeJEPA 2025]] | ● | | | | | ● |
| [[papers/Klindt-arXiv2026-When_LeJEPA_Learn/when-does-lejepa-learn-a-world-model\|Klindt+ 2026]] | ● | | | | | ● |
| [[papers/Assran-arXiv2025-V-JEPA_Self-Supervised_Video/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning\|V-JEPA 2 2025]] | ● | ● | | | | ● |
| V-JEPA 2.1 2026 | ● | ● | | | | ● |
| [[papers/Huang-ICML2026-VJEPA/vjepa-variational-joint-embedding-predictive-architectures-as-probabilistic-world-models\|VJEPA 2026]] | ● | ● | | | | ● |
| [[papers/Nam-ICML2026-Causal-JEPA_Object-Level/causal-jepa-learning-world-models-through-object-level-latent-masking\|Causal-JEPA 2026]] | ● | ● | | | | ● |
| [[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/leworldmodel-stable-end-to-end-joint-embedding-predictive-architecture-from-pixels\|LeWM 2026]] | ● | ● | | | | ● |
| [[papers/Destrade-arXiv2025-Value-guided_Action_Planning/value-guided-action-planning-with-jepa-world-models\|Destrade+ 2025]] | ● | ● | | | | ● |
| [[papers/Sun-arXiv2026-VLA-JEPA_Enhancing_VLA/vla-jepa-enhancing-vision-language-action-model-with-latent-world-model\|VLA-JEPA 2026]] | ● | ● | ○ | | | ● |
| JEPA-VLA 2026 | ● | | | | | ● |
| Rectified LpJEPA 2026 | ● | | | | | ● |
| BiJEPA 2026 | ● | | | | | ● |
| Discrete JEPA 2025 | ● | | | | | ● |
| 3D-JEPA 2024 | ● | | | | ● | ● |
| [[papers/Tian-ICLR2025-PIDM_Scalable_Learners/predictive-inverse-dynamics-models-are-scalable-learners-for-robotic-manipulation\|PIDM 2025]] | | ● | ● | | | ○ |
| LAPA 2025 | | | ● | | | ● |
| [[papers/Zhang-ICLR2026-DeFI_Disentangled_Robot/disentangled-robot-learning-via-separate-forward-and-inverse-dynamics-pretraining\|DeFI 2026]] | | ● | ● | | | ○ |
| JIF 2025 | | ● | ● | | | ● |
| Olaf-World 2026 | | ● | ● | | | ● |
| VILA 2026 | | | ● | ● | | ● |
| [[papers/Nilaksh-arXiv2026-Reconstruction_Semantics_What/reconstruction-or-semantics-what-makes-a-latent-space-useful-for-robotic-world-models\|Nilaksh+ 2026]] | ○ | ● | | | | ○ |
| MV-MWM 2023 | | ● | | ● | | |
| [[papers/ICLR2025-ReViWo_View-invariant_World/learning-view-invariant-world-models-for-visual-robotic-manipulation\|ReViWo 2025]] | | ● | | ● | | |
| MAD 2025 | | | | ● | | ○ |
| MVD 2024 | | | | ● | | ○ |
| ManiVID-3D 2025 | | | | ● | ● | |
| 3D-MVP 2024 | | | | ● | ● | |
| CL3R 2025 | | | | ● | ● | |
| Multi-View Dreaming 2022 | | ● | | ● | | ● |
| LaVA-Man 2025 | | | | | | |
| TVVE 2026 | | | | ● | ● | |
| VistaBot 2026 | | | ● | ● | ● | |
| GWM 2025 | | ● | | | ● | |
| GAF 2025 | | ● | ● | | ● | |
| [[papers/Li-ICLR2026-4D_Latent_World/4d-latent-world-model-for-robot-planning\|4D Latent WM 2026]] | | ● | ● | ● | ● | |
| Physically Embodied GS 2025 | | ● | | | ● | |
| SPA 2025 | | | | ● | ● | |
| TesserAct 2025 | | ● | ● | | ● | |
| DINO-WM 2024 | ○ | ● | | | | ● |
| DreamerV3 2025 | | ● | | | | |
| TD-MPC2 2024 | | ● | | | | ● |
| R3M 2022 | | | | | | ● |
| VIP 2023 | | | | | | ● |
| VICReg 2022 | ● | | | | | ● |
| Barlow Twins 2021 | ○ | | | | | ● |
| SFA 2002 | | | | | | ● |
| InfoNCE / CPC 2018 | | | | | | ● |
| MoDem-V2 2024 | | ● | | | | |
| Geometric Set Consistency 2022 | | | | ● | ● | |
| Multi-View Contrastive Coding 2020 | | | | ● | | ● |

**Matrix の読み方**: `●` = 手法の中核要素, `○` = 言及・部分的利用, 空欄 = 不使用. 最も疎な交差は **JEPA alignment × 多視点/ビュー不変** (該当論文なし) と **JEPA alignment × 逆動力学** (VLA-JEPA が部分的のみ).

## Quantitative Trends

### Publication Count by Year

| Year | Count |
|------|-------|
| 2026 | 18 |
| 2025 | 17 |
| 2024 | 5 |
| 2023 | 4 |
| 2022 | 3 |
| 2021 | 1 |
| 2020 | 1 |
| 2018 | 1 |
| 2002 | 1 |

### Concept Distribution

| Concept | Count | % |
|---------|-------|---|
| 復元不要 | 30 | 60% |
| 順動力学 | 24 | 48% |
| JEPA alignment | 15 | 30% |
| 多視点/ビュー不変 | 18 | 36% |
| 3D/4D 表現 | 14 | 28% |
| 逆動力学 | 13 | 26% |

### Experimental Setting Breakdown

| Setting | Count | % |
|---------|-------|---|
| Simulation only | 18 | 36% |
| Both (sim + real) | 20 | 40% |
| Real hardware only | 3 | 6% |
| Theoretical / analytical only | 9 | 18% |

### Top Venues

| Venue | Count |
|-------|-------|
| arXiv (preprint) | 20 |
| ICLR | 8 |
| ICML | 4 |
| CoRL | 3 |
| ICCV / CVPR | 3 |
| RSS | 2 |
| ICRA | 2 |
| Nature | 1 |
| Other | 7 |

## Hub Papers

| # | Citekey | Title | Year | Venue | Code | Why hub |
|---|---------|-------|------|-------|------|---------|
| 1 | [[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics\|LeJEPA]] | LeJEPA: Provable and Scalable SSL Without the Heuristics | 2025 | arXiv | [GitHub](https://github.com/galilai-group/stable-pretraining) | B+C: Cluster 1 (JEPA 理論) + Cluster 5 (基盤) を橋渡し. thesis 軸の中核 |
| 2 | [[papers/Assran-arXiv2025-V-JEPA_Self-Supervised_Video/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning\|V-JEPA 2]] | V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning | 2025 | arXiv | — | B+C: Cluster 1 + Cluster 2 を橋渡し. JEPA のロボット応用で最大規模 |
| 3 | [[papers/Nilaksh-arXiv2026-Reconstruction_Semantics_What/reconstruction-or-semantics-what-makes-a-latent-space-useful-for-robotic-world-models\|Nilaksh+ 2026]] | Reconstruction or Semantics? What Makes a Latent Space Useful for Robotic World Models | 2026 | arXiv | [HF](https://huggingface.co/Nilaksh404/semantic-wm) | C: RQ4 の主役. 復元 vs 意味表現の体系比較 |
| 4 | [[papers/Sun-arXiv2026-VLA-JEPA_Enhancing_VLA/vla-jepa-enhancing-vision-language-action-model-with-latent-world-model\|VLA-JEPA]] | VLA-JEPA: Enhancing VLA Model with Latent World Model | 2026 | arXiv | [GitHub](https://github.com/ginwind/VLA-JEPA/) | C: JEPA 式漏洩防止予測で VLA 事前学習. 復元なし + 操作の直接接続 |
| 5 | [[papers/Tian-ICLR2025-PIDM_Scalable_Learners/predictive-inverse-dynamics-models-are-scalable-learners-for-robotic-manipulation\|PIDM]] | Predictive Inverse Dynamics Models are Scalable Learners | 2025 | ICLR | [GitHub](https://github.com/OpenRobotLab/Seer/) | B+C: Cluster 2 + Cluster 3 を橋渡し. progress 軸の主役 |
| 6 | [[papers/Zhang-ICLR2026-DeFI_Disentangled_Robot/disentangled-robot-learning-via-separate-forward-and-inverse-dynamics-pretraining\|DeFI]] | Disentangled Robot Learning via Separate Fwd/Inv Dynamics Pretraining | 2026 | ICLR | [GitHub](https://github.com/WenyaoZhang/DeFI) | B: Cluster 2 + Cluster 3 を橋渡し. 分離事前学習の知見 |
| 7 | [[papers/Li-ICLR2026-4D_Latent_World/4d-latent-world-model-for-robot-planning\|4D Latent WM]] | 4D Latent World Model for Robot Planning | 2026 | ICLR | [Web](https://iclr2026-4553.github.io) | B+C: Cluster 4 + Cluster 2 を橋渡し. gap 軸の主役 |
| 8 | [[papers/ICLR2025-ReViWo_View-invariant_World/learning-view-invariant-world-models-for-visual-robotic-manipulation\|ReViWo]] | Learning View-invariant World Models for Visual Robotic Manipulation | 2025 | ICLR | — | B: Cluster 3 + Cluster 2 を橋渡し. RQ5 の主役 |
| 9 | [[papers/Nam-ICML2026-Causal-JEPA_Object-Level/causal-jepa-learning-world-models-through-object-level-latent-masking\|Causal-JEPA]] | Causal-JEPA: Learning World Models through Object-Level Latent Masking | 2026 | ICML | [GitHub](https://github.com/galilai-group/cjepa) | B+C: Cluster 1 + Cluster 2 を橋渡し. 物体レベル推論, seed 構築に直結 |

## Paper Catalogue

### JEPA 系アーキテクチャ・理論

JEPA の理論的基盤から応用展開までを包含するクラスタ. LeJEPA の SIGReg が崩壊防止の標準手法として確立し, V-JEPA 2 がビデオ・ロボットへの拡張を主導した.

1. **Assran+ 2023**,"Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture" ([arXiv](https://arxiv.org/abs/2301.08243)) — I-JEPA: 画像内マスク予測による JEPA の原型
2. **Balestriero+ 2025** *(hub — see [[papers/Balestriero-arXiv2025-LeJEPA_Provable_Scalable/lejepa-provable-and-scalable-self-supervised-learning-without-the-heuristics|deep read]])*
3. **Klindt+ 2026** *(local note — see [[papers/Klindt-arXiv2026-When_LeJEPA_Learn/when-does-lejepa-learn-a-world-model|deep read]])*
4. **Assran+ 2025** *(hub — see [[papers/Assran-arXiv2025-V-JEPA_Self-Supervised_Video/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning|deep read]])*
5. **Mur-Labadia+ 2026**,"V-JEPA 2.1: Unlocking Dense Features in Video Self-Supervised Learning" ([arXiv](https://arxiv.org/abs/2603.14482)) — Dense 特徴 + 深層自己教師あり
6. **Huang+ 2026** *(local note — see [[papers/Huang-ICML2026-VJEPA/vjepa-variational-joint-embedding-predictive-architectures-as-probabilistic-world-models|deep read]])*
7. **Nam+ 2026** *(hub — see [[papers/Nam-ICML2026-Causal-JEPA_Object-Level/causal-jepa-learning-world-models-through-object-level-latent-masking|deep read]])*
8. **Maes+ 2026** *(local note — see [[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/leworldmodel-stable-end-to-end-joint-embedding-predictive-architecture-from-pixels|deep read]])*
9. **Destrade+ 2025** *(local note — see [[papers/Destrade-arXiv2025-Value-guided_Action_Planning/value-guided-action-planning-with-jepa-world-models|deep read]])*
10. **Kuang+ 2026**,"Rectified LpJEPA" ([arXiv](https://arxiv.org/abs/2602.01456)) — スパース・最大エントロピー表現. RDMReg (sliced 2 標本分布マッチング) を導入
11. **Sun+ 2026** *(hub — see [[papers/Sun-arXiv2026-VLA-JEPA_Enhancing_VLA/vla-jepa-enhancing-vision-language-action-model-with-latent-world-model|deep read]])*
12. **Miao+ 2026**,"JEPA-VLA: Video Predictive Embedding is Needed for VLA Models" ([arXiv](https://arxiv.org/abs/2602.11832)) — V-JEPA 2 バックボーンで VLA
13. **Huang 2026**,"BiJEPA: Bi-directional JEPA for Symmetric Representation Learning" ([arXiv](https://arxiv.org/abs/2603.00049)) — 双方向予測, サイクル整合

### 潜在順/逆動力学 + 行動学習

順動力学予測と逆動力学行動抽出の組み合わせが 2025–2026 年に急速に発展した領域.

1. **Tian+ 2025** *(hub — see [[papers/Tian-ICLR2025-PIDM_Scalable_Learners/predictive-inverse-dynamics-models-are-scalable-learners-for-robotic-manipulation|deep read]])*
2. **Ye+ 2025**,"Latent Action Pretraining from Videos" ([arXiv](https://arxiv.org/abs/2410.11758)) — VQ-VAE で離散潜在行動を動画から教師なし抽出
3. **Zhang+ 2026** *(hub — see [[papers/Zhang-ICLR2026-DeFI_Disentangled_Robot/disentangled-robot-learning-via-separate-forward-and-inverse-dynamics-pretraining|deep read]])*
4. **Khandate+ 2025**,"Train Robots in a JIF" ([RSS 2025](https://arxiv.org/abs/2503.12297)) — 人間デモから順/逆動力学を同時学習, マルチモーダル
5. **arXiv 2026**,"Olaf-World: Orienting Latent Actions for Video World Modeling" ([arXiv](https://arxiv.org/abs/2602.10104)) — Seq△-REPA で潜在行動転移
6. **arXiv 2026**,"Learning to Act Robustly with View-Invariant Latent Actions (VILA)" ([arXiv](https://arxiv.org/abs/2601.02994)) — 物理動力学に根ざしたビュー不変潜在行動
7. **Nilaksh+ 2026** *(hub — see [[papers/Nilaksh-arXiv2026-Reconstruction_Semantics_What/reconstruction-or-semantics-what-makes-a-latent-space-useful-for-robotic-world-models|deep read]])*

### 多視点表現学習 + ビュー不変性

多視点カメラからの情報統合と視点変化への頑健性を追求する研究群.

1. **Seo+ 2023**,"Multi-View Masked World Models for Visual Robotic Manipulation" ([ICML 2023](https://arxiv.org/abs/2302.02408)) — 多視点マスク自己符号化 + ワールドモデル
2. **Pang+ 2025** *(hub — see [[papers/ICLR2025-ReViWo_View-invariant_World/learning-view-invariant-world-models-for-visual-robotic-manipulation|deep read]])*
3. **Almuzairee+ 2025**,"Merging and Disentangling Views in Visual RL for Robotic Manipulation" ([CoRL 2025](https://arxiv.org/abs/2505.04619)) — 多視点マージ + ビュー分離
4. **MVD 2024**,"Multi-view Disentanglement for RL with Multiple Cameras" ([RLJ 2024](https://arxiv.org/abs/2404.14064)) — 単一カメラゼロショット汎化
5. **ManiVID-3D 2025**, IEEE RA-L ([arXiv](https://arxiv.org/abs/2509.11125)) — 3D 点群ビュー不変表現
6. **Qian+ 2024**,"3D-MVP: 3D Multiview Pretraining for Robotic Manipulation" ([arXiv](https://arxiv.org/abs/2406.18158)) — 多視点マスク事前学習
7. **Cui+ 2025**,"CL3R: 3D Reconstruction and Contrastive Learning for Enhanced Robotic Manipulation" ([arXiv](https://arxiv.org/abs/2507.08262)) — 点群 MAE + 対比学習
8. **Kanazawa+ 2022**,"Multi-View Dreaming" ([Advanced Robotics 2023](https://arxiv.org/abs/2203.11024)) — 多視点対比学習 + Dreamer
9. **Zhu+ 2025**,"LaVA-Man" ([CoRL 2025](https://arxiv.org/abs/2508.19391)) — マスクゴール画像再構成. 単一視点であり多視点手法ではない (Concept Matrix 全列空欄はこのため. 本クラスタへの配置は操作表現学習としての関連による)
10. **TVVE 2026**,"Learning to See and Act: Task-Aware Virtual View Exploration" ([arXiv](https://arxiv.org/abs/2508.05186)) — 遮蔽克服
11. **VistaBot 2026**, ([arXiv](https://arxiv.org/abs/2604.21914)) — 4D 幾何 + ビデオ拡散でビュー頑健操作

### 3D/4D 表現 + ワールドモデル (復元ベース)

3DGS やボクセル表現を使ったワールドモデル. 復元ベースだが, 本サーベイの alignment ベースとの対比軸を構成する.

1. **Lu+ 2025**,"GWM: Towards Scalable Gaussian World Models for Robotic Manipulation" ([ICCV 2025](https://arxiv.org/abs/2508.17600)) — 3DGS + DiT ワールドモデル
2. **Chai+ 2025**,"GAF: Gaussian Action Field" ([arXiv](https://arxiv.org/abs/2506.14135)) — 4D Gaussian, 動的シーン + 行動推定
3. **Li+ 2026** *(hub — see [[papers/Li-ICLR2026-4D_Latent_World/4d-latent-world-model-for-robot-planning|deep read]])*
4. **Abou-Chakra+ 2025**,"Physically Embodied Gaussian Splatting" ([CoRL 2025](https://arxiv.org/abs/2406.10788)) — 3DGS + 粒子物理, リアルタイム
5. **Zhu+ 2025**,"SPA: 3D Spatial-Awareness Enables Effective Embodied Representation" ([ICLR 2025](https://arxiv.org/abs/2410.08208)) — ニューラルレンダリング事前学習
6. **Zhen+ 2025**,"TesserAct: Learning 4D Embodied World Models" ([arXiv](https://arxiv.org/abs/2504.20995)) — RGB-DN 4D ワールドモデル
7. **Zhou+ 2024**,"DINO-WM: World Models on Pre-trained Visual Features" ([arXiv](https://arxiv.org/abs/2411.04983)) — DINOv2 特徴上の潜在ワールドモデル

### 復元 vs 意味表現の基盤・理論・比較

本サーベイの分析枠組みを支える基盤的研究.

1. **Hafner+ 2025**,"Mastering Diverse Control Tasks through World Models" ([Nature](https://www.nature.com/articles/s41586-025-08744-2)) — DreamerV3, 150+ 環境
2. **Hansen+ 2024**,"TD-MPC2: Scalable, Robust World Models" ([ICLR 2024](https://arxiv.org/abs/2310.16828)) — デコーダ不要潜在 MPC
3. **Nair+ 2022**,"R3M: A Universal Visual Representation for Robot Manipulation" ([CoRL 2022](https://arxiv.org/abs/2203.12601)) — 時間対比 + 言語 alignment
4. **Ma+ 2023**,"VIP: Towards Universal Visual Reward and Representation" ([ICLR 2023](https://arxiv.org/abs/2210.00030)) — RL ベース汎用視覚報酬
5. **Bardes+ 2022**,"VICReg" ([ICLR 2022](https://arxiv.org/abs/2105.04906)) — 分散・不変性・共分散正則化
6. **Zbontar+ 2021**,"Barlow Twins" ([ICML 2021](https://arxiv.org/abs/2103.03230)) — 冗長性削減
7. **Wiskott & Sejnowski 2002**,"Slow Feature Analysis" (Neural Computation) — 不変表現の原理
8. **Hu+ 2024**,"3D-JEPA" ([arXiv](https://arxiv.org/abs/2409.15803)) — 3D 点群向け JEPA
9. **van den Oord+ 2018**,"Representation Learning with Contrastive Predictive Coding" ([arXiv](https://arxiv.org/abs/1807.03748)) — InfoNCE の基盤
10. **MoDem-V2 2024**, ([ICRA 2024](https://arxiv.org/abs/2309.14236)) — 視覚運動ワールドモデル, 実機操作
11. **Geometric Set Consistency 2022**, ([arXiv](https://arxiv.org/abs/2203.15361)) — 3D 幾何一貫性で画像表現学習
12. **Tian+ 2020**,"Contrastive Multiview Coding" ([ECCV 2020](https://arxiv.org/abs/1906.05849)) — 多視点対比学習の一般化
13. **Baek+ 2025**,"Discrete JEPA" ([ICML 2025](https://arxiv.org/abs/2506.14373)) — 離散トークン表現, 復元なし

## Survey Methodology

### Frame

- Core topic: 多視点自己教師あり学習によるロボット操作 — JEPA 式潜在 alignment + 順/逆動力学, 復元不要
- Depth: broad (target 40–60)
- Inclusion: Peer-reviewed (ICLR, ICML, NeurIPS, CoRL, RSS, ICRA, IROS, CVPR, ICCV, RA-L) + 主要 preprint; ロボット操作 or 表現学習 or ワールドモデル; 英語
- Exclusion: Navigation/autonomous driving 専用; NLP 専用; poster-only workshop papers
- Known abbreviations: JEPA, SIGReg, NeRF, 3DGS, VAE, MPC, CEM, RL, IL, VLA, MLP, ViT, MSE, EMA

### Map

| Search angle | Source(s) | Sample query | Results |
|---|---|---|---|
| Direct topic | WebSearch | "multi-view self-supervised robot manipulation" | ~12 |
| JEPA 系 | WebSearch | "JEPA world model robot planning 2024-2026" | ~15 |
| 潜在動力学 | WebSearch | "inverse dynamics latent space multi-view robot" | ~10 |
| 多視点不変性 | WebSearch | "view-invariant world model manipulation" | ~8 |
| 復元 vs alignment | WebSearch | "reconstruction-free latent dynamics robot" | ~6 |
| 3D/4D ワールドモデル | WebSearch | "3D Gaussian latent world model robot" | ~8 |
| ビュー頑健性 | WebSearch | "occlusion multi-view manipulation camera robustness" | ~5 |
| 基盤手法 | WebSearch | "VICReg Barlow Twins R3M VIP" | ~6 |
| Snowballing | seed 15 + 1-hop | — | ~80 candidates |

- Total mapped: 51 (初版は 50 と記載していたが, Paper Catalogue の実数 51 と年別集計の合計 51 に合わせて修正)
- Duplicates removed: 4
- Excluded by I/E criteria: ~26 (navigation 専用, NLP 専用, workshop-only)

### Hub Selection

- Selection criteria: B (cluster bridging + citation proxy) AND/OR C (synthesis centrality)
- Candidates considered: 51
- Final hubs: 9 (3 existing local notes + 6 new deep reads)
- PDFs successfully acquired: 6/6 new (1 required retry — 4D Latent WM initial arXiv ID mismatch)
- Citation proxy used (S2 MCP unavailable): venue tier + WebSearch hits + survey-internal citation frequency

### Verify

- Hub deep reads generated: 6 new + 3 existing = 9 total
- Hub cross-verification: completed by each subagent (self-verification against PDF)
- Synthesis trace-back: completed inline during report generation
- Reference-verify: DOI/URL spot-checked for hub papers. Full batch verification deferred (scripts unavailable in this environment)

## Abbreviation Glossary

| Abbreviation | Full Name | First Occurrence |
|---|---|---|
| JEPA | Joint-Embedding Predictive Architecture | Abstract |
| SIGReg | Sketched Isotropic Gaussian Regularization | Terminology |
| VLA | Vision-Language-Action | Terminology |
| 3DGS | 3D Gaussian Splatting | Terminology |
| NeRF | Neural Radiance Field | Terminology |
| VIR | View-Invariant Representation | Terminology |
| VDR | View-Dependent Representation | Terminology |
| MPC | Model Predictive Control | Foundation |
| CEM | Cross-Entropy Method | Foundation |
| RL | Reinforcement Learning | Foundation |
| IL | Imitation Learning | Cluster 2 |
| MLP | Multi-Layer Perceptron | PIDM |
| ViT | Vision Transformer | PIDM |
| MSE | Mean Squared Error | Thesis |
| EMA | Exponential Moving Average | I-JEPA |
| RSSM | Recurrent State Space Model | DreamerV3 |
| CPC | Contrastive Predictive Coding | Progress |
| MAE | Masked Autoencoder | MV-MWM |
| GFDM | General Forward Dynamics Model | DeFI |
| GIDM | General Inverse Dynamics Model | DeFI |
| PIDM | Predictive Inverse Dynamics Model | Hub 5 |
