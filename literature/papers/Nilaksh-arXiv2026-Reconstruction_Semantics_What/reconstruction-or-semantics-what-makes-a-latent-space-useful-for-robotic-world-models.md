---
Title: "Reconstruction or Semantics? What Makes a Latent Space Useful for Robotic World Models"
Authors:
  - Nilaksh, ""
  - Jha, Saurav
  - Zholus, Artem
  - Chandar, Sarath
Year: 2026
Venue: arXiv
Tags:
  - "world-model"
  - "latent-diffusion"
  - "robot-manipulation"
  - "representation-learning"
  - "encoder-comparison"
PDF: "[[papers/Nilaksh-arXiv2026-Reconstruction_Semantics_What/main.pdf|📃]]"
Import Date: "2026-06-05"
Read Date: 2026-06-05
Executive Summary: "BridgeV2 データセット上で, 潜在拡散ワールドモデルのエンコーダ (再構成系 3種 vs 意味系 3種) を遷移モデル・学習条件を固定して比較. 視覚的忠実度だけではワールドモデルの選択基準として不十分であり, V-JEPA 2.1, Web-DINO, SigLIP 2 などの意味表現エンコーダが行動復元性, タスク成功分類, CEM 計画, VLA ポリシー成功率で一貫して再構成系を上回ることを示した."
Citekey: Nilaksh-arXiv2026-Reconstruction_Semantics_What
BibTeX Key: nilaksh2026reconstruction
DOI: ""
Relevance: 4
Repository: "https://huggingface.co/Nilaksh404/semantic-wm"
Category: note
Template Version: v2.3
---

## Executive Summary
BridgeV2 データセット上で, 潜在拡散ワールドモデルのエンコーダ (再構成系 3種 vs 意味系 3種) を遷移モデル・学習条件を固定して比較. 視覚的忠実度だけではワールドモデルの選択基準として不十分であり, V-JEPA 2.1, Web-DINO, SigLIP 2 などの意味表現エンコーダが行動復元性, タスク成功分類, CEM 計画, VLA ポリシー成功率で一貫して再構成系を上回ることを示した.

---
## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

潜在拡散モデル (LDM) ベースのロボットワールドモデルにおいて, エンコーダが定義する潜在空間の選択 (再構成指向 vs 意味指向) がダウンストリームのロボット制御性能にどう影響するか, という問いに体系的に答えた (§1). 既存研究では視覚的忠実度のみで評価されることが多く, 行動復元性やポリシー性能への影響は未解明だった.

### 提案手法のアプローチと, その根幹をなす要素は何か?

エンコーダのみを変数とし, データセット, 履歴長, 行動条件付け, DiT 遷移モデル, オプティマイザ, 学習スケジュールを全て固定した制御実験を設計. 6種のエンコーダでそれぞれワールドモデルを学習し, 3軸の評価スイートで比較した.

- **エンコーダ 6種**: 再構成系 (SD3 VAE D=16, VA-VAE D=32, Cosmos D=16) と意味系 (V-JEPA 2.1 ViT-L D=1024, Web-DINO ViT-L D=1024, SigLIP 2 ViT-L D=1152). 意味系は S-VAE アダプタ (D→d=96) の有無も評価 (§3.1, Fig. 1)
- **3軸評価スイート**: (1) 計画・ダウンストリームポリシー性能 (CEM 行動復元, OpenVLA-7B ポリシーロールアウト, VLM 判定による成功率), (2) 視覚的忠実度 (FID, SSIM, FVD 等), (3) 潜在表現品質 (IDM 行動復元相関, 成功/失敗分類精度) (§3.2)
- **遷移モデル**: 全エンコーダ共通の DiT (時空間因果注意) + フローマッチング. 高次元意味空間には DDT ワイドヘッド + 次元依存ノイズスケジュールシフトを適用 (§2.1, §3.1)

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

- **DINO-WM** (Zhou+, 2024): DINOv2 表現上の自己回帰特徴予測ワールドモデル. 計画には使えるが拡散モデルではない. 本研究は拡散モデル内でのエンコーダ選択効果を分離した点が異なる
- **[[papers/Assran-arXiv2025-V-JEPA_Self-Supervised_Video/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning|V-JEPA 2-AC (Assran+, 2025)]]**: JEPA predictor ベースのワールドモデル. 本研究では V-JEPA 2.1 エンコーダを潜在拡散フレームワーク内で評価し, ポリシー性能で最強の結果を得た
- **RAE** (Yu+, 2024) / **S-VAE** (Zhang+, 2024): 高次元意味空間での拡散学習を可能にする技術. 本研究はこれらをロボットの行動条件付きワールドモデルに適用・統合した最初の体系的評価

新規性は, ロボットワールドモデルの潜在空間を単一のフレームワーク内で公平に比較し, 視覚品質だけでなく行動・タスク・ポリシー軸での優劣を定量化した点にある.

### どのように訓練・最適化したのか?

- **損失関数 / 最適化目的**: フローマッチング損失で DiT を学習 (§3.1). S-VAE アダプタは KL 正則化付き再構成損失で事前学習済み (凍結). エンコーダも凍結で, 遷移モデルのみ更新
- **データセット**: BridgeV2 (Walke+, 2023), WidowX 250 ロボットの ~60K デモ, 13 タスクファミリー, 7DoF エンドエフェクタ行動, 言語指示付き. 成功/失敗ラベルは SOAR (~30.5K エピソード) を利用 (§3.1). H=2 履歴フレーム, K=8 予測フレーム, 1フレームおきにサンプリング

### どのように検証したか? 指標と結果は?

**計画・ポリシー性能** (Tab. 1):
- VLA 成功率 (コンセンサス): V-JEPA 2.1 が 0.344 で最高, 再構成系は VAE 0.169, Cosmos 0.244
- CEM 行動誤差 (k=4): V-JEPA 2.1 が 0.424 で最低 (最良), VAE 0.612, Cosmos 0.661
- OOD 頑健性 (ディストラクタ): V-JEPA 2.1 0.575, VAE 0.287

**潜在表現品質** (Tab. 2):
- IDM Pearson r (k=4, WM 潜在): V-JEPA 2.1 0.840, Web-DINO 0.794, VAE 0.464
- 成功分類精度 (WM 潜在): SigLIP 2 0.823 で最高, V-JEPA 2.1 0.789

**視覚的忠実度** (Tab. 3): DiT-S では意味系が FVD, SSIM で優位. DiT-L にスケールすると VAE が FID, FVD で競合的になるが, CEM・IDM での差は残存

**スケーリング** (§4.4): DiT を大きくするとポリシー性能差は縮まるが, 行動復元の差は維持される. マルチビュー学習は CEM を改善するが視覚品質を下げうる (データ不足の影響)

### 検証結果に基づいた議論, 明らかになった課題はあるか?

- (§7) BridgeV2 の WidowX 250 に限定した結果であり, 他のエンボディメント・ドメイン・データ規模への汎化は未検証
- (§7) ポリシー評価のみ実施; ポリシー改善や sim-to-real 転移は未検証
- (§7) VLM ベースの成功判定に評価バイアスの可能性. 複数 VLM の集約と非 VLM 指標で軽減を図っている
- (§4.5) 再構成系と意味系の失敗モードが異なる: 再構成系はタスク意味を幻覚し (物体の出現・消失), 意味系は幾何・接触の精度が落ちる
- (§4.6) S-VAE アダプタは拡散の容易さを改善するが, CEM 行動誤差や OOD 頑健性では native 意味空間に劣る場合がある (制御幾何の歪み)

---
## 自身の研究との関連

LeWM / LeJEPA の研究において, ワールドモデルの潜在空間選択が行動計画性能を左右するという本論文の知見は直接的に関連する. LeWM は SIGReg で等方ガウスに正則化した潜在空間を用いるが, 本論文は意味エンコーダの潜在空間が行動復元性・タスク成功分類で優れることを示した. SIGReg の等方ガウス制約と意味エンコーダの表現構造の関係 (競合するのか補完するのか) は検討に値する. また, BridgeV2 上の評価プロトコル (3軸評価) は LeWM を実機データで評価する際の参考になる.

---
## 追加議論

---
## BibTex
<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@article{nilaksh2026reconstruction,
  title={Reconstruction or Semantics? What Makes a Latent Space Useful for Robotic World Models},
  author={Nilaksh and Jha, Saurav and Zholus, Artem and Chandar, Sarath},
  journal={arXiv preprint arXiv:2605.06388},
  year={2026}
}
```
</details>
