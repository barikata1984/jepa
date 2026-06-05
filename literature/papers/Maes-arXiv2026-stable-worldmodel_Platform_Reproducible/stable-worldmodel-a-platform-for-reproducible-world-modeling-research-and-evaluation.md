---
Title: "stable-worldmodel: A Platform for Reproducible World Modeling Research and Evaluation"
Authors:
  - Maes, Lucas
  - Le Lidec, Quentin
  - Facury, Luiz
  - Massaudi, Nassim
  - Chaurasia, Ayush
  - Capuano, Francesco
  - Gao, Richard
  - Gillin, Taj
  - Haramati, Dan
  - Scieur, Damien
  - LeCun, Yann
  - Balestriero, Randall
Year: 2026
Venue: arXiv
Tags:
  - "world-model"
  - "benchmark"
  - "reproducibility"
  - "model-predictive-control"
  - "open-source"
PDF: "[[papers/Maes-arXiv2026-stable-worldmodel_Platform_Reproducible/main.pdf|📃]]"
Import Date: "2026-06-05"
Read Date: 2026-06-05
Executive Summary: "ワールドモデル研究の再現性・公平比較を目的としたオープンソースプラットフォーム. Lance ベースの高速データ層, DINO-WM / PLDM / LeWM / TD-MPC2 等のベースライン実装, CEM / MPPI 等のプランナー, ~150 環境を統合. 視覚・幾何・物理の変動要因を制御した分布外汎化評価を提供し, 既存モデルが軽微な分布シフトでも大幅に劣化することを実証した."
Citekey: Maes-arXiv2026-stable-worldmodel_Platform_Reproducible
BibTeX Key: maes2026stable
DOI: ""
Relevance: 5
Repository: "https://github.com/galilai-group/stable-worldmodel"
Category: note
Template Version: v2.3
---

## Executive Summary
ワールドモデル研究の再現性・公平比較を目的としたオープンソースプラットフォーム. Lance ベースの高速データ層, DINO-WM / PLDM / LeWM / TD-MPC2 等のベースライン実装, CEM / MPPI 等のプランナー, ~150 環境を統合. 視覚・幾何・物理の変動要因を制御した分布外汎化評価を提供し, 既存モデルが軽微な分布シフトでも大幅に劣化することを実証した.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

ワールドモデル研究における 3つのボトルネック: (1) 断片化したコードベースによる再現性の欠如, (2) マルチモーダル時系列データの I/O ボトルネック, (3) 分布外汎化を含む標準化された評価プロトコルの不在, に対して統一プラットフォームを提供した (§1, §3.1).

### 提案手法のアプローチと, その根幹をなす要素は何か?

データ収集→学習→MPC 評価の全パイプラインを単一フレームワークで統合. ユーザーのモデルアーキテクチャ・学習コードには制約を課さず, データ管理・評価・制御部分のみを標準化する設計思想.

- **Lance ベースデータ層**: ランダムアクセスとスループットを両立するカラム指向 ML 最適化フォーマット. HDF5, MP4, LeRobot 形式からの変換ツール付き. Push-T で HDF5 の 3.4 倍のスループット (4815 vs 1416 samples/sec, Fig. 3)
- **制御層**: CEM, iCEM, MPPI, 勾配降下法等のプランナーを統一インターフェースで提供. 全ソルバーはエンドツーエンドでテスト・検証済みで, DINO-WM・PLDM の報告値を再現 (§3.3, §4.1)
- **モデル層**: DINO-WM, PLDM, [[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/leworldmodel-stable-end-to-end-joint-embedding-predictive-architecture-from-pixels|LeWM]], TD-MPC2, GCBC, GCIVL, GCIQL の実装を提供 (§3.3)
- **評価テストベッド**: ~150 環境 (CartPole, PushT, OGBench, Atari, MuJoCo, Craftax). 視覚 (色, テクスチャ, 遮蔽), 幾何 (サイズ, 形状), 物理 (質量, 摩擦, 重力) の変動要因を実行時に制御可能 (§3.4, Fig. 2)

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

- **DINO-WM** (Zhou+, 2024), **PLDM** (Sobal+, 2025), **[[papers/Maes-arXiv2026-LeWorldModel_Stable_End-to-End/leworldmodel-stable-end-to-end-joint-embedding-predictive-architecture-from-pixels|LeWM (Maes+, 2026)]]**: それぞれ独自のコードベースで CEM 等を再実装していた. swm はこれらを統一実装し, 公平な比較を実現
- **stable-baselines3** (Raffin+, 2021), **LeRobot** (Cadene+, 2024): モデルフリー RL やイミテーション学習のフレームワーク. ワールドモデル固有の計画・評価インフラが欠落しており, swm が補完
- **EB-JEPA** (教育目的の JEPA 実装): JEPA アーキテクチャに限定され, スケーラブルな研究コンポーネントが不足

新規性は, ワールドモデル研究に特化した初の包括的プラットフォームであり, 分布外汎化の体系的評価を可能にした点にある.

### どのように訓練・最適化したのか?

- **損失関数 / 最適化目的**: N/A (プラットフォーム論文). 各ベースラインの学習目的は原論文に準拠 (LeWM: 予測損失 + SIGReg, PLDM: JEPA + 正則化, DINO-WM: 凍結 DINOv2 + 予測損失, TD-MPC2: 報酬予測 + 価値予測)
- **データセット**: ケーススタディでは Push-T のエキスパートデータ (DINO-WM で使用されたものと同一) と OGBench-Cube を使用 (§4.1, Tab. 1). LeRobot データセットのインポートにも対応

### どのように検証したか? 指標と結果は?

**分布内計画性能** (Tab. 1, Push-T): LeWM 94%, DINO-WM 92%, PLDM 78%, GCBC 75%, TD-MPC2 12%. TD-MPC2 はオフライン設定で OOD 行動生成により大幅に劣化

**分布外頑健性** (§4.2, Fig. 5, Tab. 5b): Push-T で視覚変動 (色, サイズ, 形状) を個別に適用すると, 多くの条件で成功率が 50% 超→10–20% 台に低下. 例: LeWM の背景色変更で 50.8%→6.0%, エージェント色変更で 50.8%→12.0%. 視覚ディストラクタ (遮蔽四角形) の数に対し成功率は二次的に減衰 (Fig. 5a)

**予測誤差と成功率の非相関** (§4.2, Fig. 4): 分布外設定では予測 MSE が上昇するが, 成功・失敗の MSE 分布は大きく重複. 予測誤差の大きさよりも入力の OOD 性が計画失敗の主因

**データスループット** (Fig. 3): Lance はローカル HDF5 の 3.4 倍, S3 リモートでは HDF5 の 354 倍のスループット

### 検証結果に基づいた議論, 明らかになった課題はあるか?

- (§6) 既存ワールドモデルは軽微な分布シフトでもゼロショット汎化が不十分. 視覚・物理の頑健性向上がアーキテクチャと体系的スケーリングの両面で必要
- (§6) 現時点ではシミュレーション環境での評価に限定. sim-to-real 転移, 非同期リアルタイムインタラクション, 効率的なオンライン学習への拡張が今後の課題
- (§4.2, Fig. 4) 予測誤差はモデル選択の指標として不十分. OOD 入力が計画失敗を引き起こすメカニズムの理解が必要
- (§4.1) TD-MPC2 はオフライン設定で OOD 行動を生成し predictor を欺くため極端に低い性能. オフライン vs オンライン設定の差異がモデル比較に大きく影響する

---
## 自身の研究との関連

LeWM / LeJEPA に基づく実機ロボット研究において, swm は直接的に利用可能なインフラである. LeWM の公式実装が swm 内に含まれており, LeRobot 形式のデータインポートにも対応しているため, BridgeV2 や DROID などの実機データセットでの実験をすぐに開始できる. 分布外汎化評価は, SIGReg の低データ多様性問題 (TwoRoom 問題) をさまざまな変動要因で体系的に検証する基盤となる. また, 統一プランナー実装により CEM のパラメータ感度分析なども再現可能な形で実施できる.

---
## 追加議論

---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@article{maes2026stable,
  title={stable-worldmodel: A Platform for Reproducible World Modeling Research and Evaluation},
  author={Maes, Lucas and Le Lidec, Quentin and Facury, Luiz and Massaudi, Nassim and Chaurasia, Ayush and Capuano, Francesco and Gao, Richard and Gillin, Taj and Haramati, Dan and Scieur, Damien and LeCun, Yann and Balestriero, Randall},
  journal={arXiv preprint arXiv:2605.21800},
  year={2026}
}
```
</details>
