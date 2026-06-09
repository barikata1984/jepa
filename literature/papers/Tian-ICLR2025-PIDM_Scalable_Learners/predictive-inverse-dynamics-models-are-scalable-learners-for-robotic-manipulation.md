---
Title: "Predictive Inverse Dynamics Models are Scalable Learners for Robotic Manipulation"
Authors: [Yang Tian, Sizhe Yang, Jia Zeng, Ping Wang, Dahua Lin, Hao Dong, Jiangmiao Pang]
Year: 2025
Venue: ICLR
Tags: ["inverse-dynamics", "forward-prediction", "robot-manipulation", "scalable", "imitation-learning"]
PDF: "[[papers/Tian-ICLR2025-PIDM_Scalable_Learners/main.pdf|📃]]"
Import Date: "2026-06-09"
Read Date: 2026-06-09
Executive Summary: ロボット操作における大規模なスケーラブルな方策学習に向けて, 視覚予測と逆ダイナミクスをエンドツーエンドで統合した Predictive Inverse Dynamics Models (PIDM) パラダイムを提案する. Transformer ベースの実装 Seer は, 未来の視覚状態を条件として逆ダイナミクスモジュールが行動を推定するループを閉じることで, シミュレーション・実環境の両方で従来の最先端手法を大幅に上回る性能を達成した.
Citekey: Tian-ICLR2025-PIDM_Scalable_Learners
BibTeX Key: tian2025pidm
DOI: ""
Relevance: 4
Repository: https://github.com/OpenRobotLab/Seer/
Category: note
Template Version: v2.3
---

## Executive Summary

ロボット操作における大規模なスケーラブルな方策学習に向けて, 視覚予測と逆ダイナミクスをエンドツーエンドで統合した Predictive Inverse Dynamics Models (PIDM) パラダイムを提案する. Transformer ベースの実装 Seer は, 未来の視覚状態を条件として逆ダイナミクスモジュールが行動を推定するループを閉じることで, シミュレーション・実環境の両方で従来の最先端手法を大幅に上回る性能を達成した.

## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

ロボット操作における大規模かつ汎化性の高い方策学習には,"行動"中心アプローチ (大規模ロボットデータからの行動模倣) と"視覚"中心アプローチ (視覚表現・生成モデルの事前学習) の 2 系統が存在する. しかし既存の 2 段階 PIDM 手法では, 視覚予測モジュールと逆ダイナミクスモジュールが分離されており, 視覚と行動の相乗効果を訓練時に十分に活用できない. 本論文は, 両者をエンドツーエンドで最適化することで, スケーラブルな操作方策学習を実現できるかという問いに答える.

### 提案手法のアプローチと, その根幹をなす要素は何か?

PIDM は"条件付き視覚予見 (conditional visual foresight)"と"逆ダイナミクス予測 (inverse dynamics prediction)"をエンドツーエンドで結合するパラダイムである. 具体的な実装 Seer は以下の 3 要素から構成される.

第一に, マルチモーダルエンコーダ. MAE 事前学習済み ViT-B で画像を符号化し, Perceiver Resampler でトークン数を圧縮する. 言語は CLIP ViT-B/32 テキストエンコーダで符号化し, ロボット状態は MLP でトークン化する. これらを GPT-2 スタイルの 24 層 Transformer バックボーンで処理する.

第二に, Foresight Token [FRS] と Action Token [INV]. [FRS] は未来の RGB 画像を再構成する潜在表現を生成し, [INV] は [FRS] の出力を一方向アテンションで参照しながら行動系列を推定する. この単方向アテンションマスクにより, [INV] は過去・未来の予測情報を深く統合できる.

第三に, エンドツーエンド訓練. 損失関数は視覚予見損失 L_fore (MSE, ピクセルレベル) と逆ダイナミクス損失 L_inv (Smooth-L1 + Binary Cross Entropy) の重み付き和であり, 事前学習とファインチューニングで同一目標関数を使用する.

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

行動中心の先行研究として RT-1, Octo, OpenVLA が挙げられる. これらは大規模ロボットデータから直接行動を模倣するが, 視覚情報の豊かな時間的構造を十分に活用しない. 視覚中心の先行研究として R3M, MVP, MPI がある. これらは表現学習や生成モデルを活用するが, 行動との閉ループを訓練時に形成しない.

2 段階 PIDM として Gen2act, This&That, CLOVER, GR-1 が近い. これらは視覚生成モデルが目標を設定し, 逆ダイナミクス方策が行動を生成するという 2 段階の構成を採る. 本手法の新規性は, この 2 段階を単一のエンドツーエンド訓練に統合した点にある. 潜在空間上で視覚予見と逆ダイナミクスを結合し, 大規模ロボットデータを用いた事前学習が両目標で同時に機能するため, 下流タスクへの転移効率が高い.

### どのように訓練・最適化したのか?

事前学習とファインチューニングで目標関数は共通で, L = α L_fore + L_inv (α = 0.5) を用いる. 最適化器は AdamW, 学習率コサイン減衰スケジュールを採用する. 事前学習の学習率は 1e-4, バッチサイズは 640 (シミュレーション) または 2048 (実環境), ファインチューニングは学習率 1e-3, バッチサイズ 512 である.

視覚エンコーダと言語エンコーダ (計 251M パラメータ) は凍結し, バックボーン・デコーダ等 65M パラメータを訓練する. Seer-Large は 315M パラメータが訓練可能である. LIBERO・実環境実験では DROID データセット (76K 成功軌道) で事前学習し, CALVIN では公式プレイデータを使用する. 言語アノテーションが欠如したデータには, 将来のロボット状態トークンを言語代替のゴールとして用いる設計により対応する.

推論時は, 3 ステップ分の行動チャンクを出力し, 最初のステップのみ実行するか時間的アンサンブルを適用する.

### どのように検証したか? 指標と結果は?

シミュレーション評価として LIBERO-LONG (10 タスク, 各 20 ロールアウト平均成功率) と CALVIN ABC-D (34 タスク, 5 連続タスクを 1000 シーケンスで評価した Avg. Len.) の 2 ベンチマークを用いる.

LIBERO-LONG では Seer が平均成功率 87.7% を達成し, 次点の MPI (77.3%) を 10.4 ポイント上回る. 事前学習なし版 (78.7%) との比較で 9% の絶対改善を示す. CALVIN ABC-D では Seer-Large が Avg. Len. 4.28 を達成し, 従来最高の CLOVER (3.53) を 0.75 上回り, 新たな最先端を確立する. 標準版 Seer は 3.98 である.

実環境評価では Franka Research 3 ロボットで 6 タスクを実施し, Flip White Bowl / Stack Cups / Wipe Board / Pick, Place, Close の 4 汎化タスクで平均成功率 78.4% (スコア 39.5) を達成する. 事前学習なし版 (60.0% / 32.8) と比較して大幅に向上し, MVP (55.0% / 29.8) や MPI (48.4% / 29.3), OpenVLA (16.7% / 11.0) を上回る. 汎化実験では新規物体・背景変化・照明変動のいずれの条件下でも事前学習版が一貫して改善を示す.

データ効率実験では, ファインチューニングデータの 10% のみを使用した場合でも, 事前学習版がスクラッチ訓練版に対して LIBERO で 187%, CALVIN で 150% の相対改善を達成する. スケーラビリティ実験では 65M, 107M, 316M パラメータの全スケールで事前学習の効果が確認され, モデル規模の増加とともに性能が単調に向上する.

### 検証結果に基づいた議論, 明らかになった課題はあるか?

アブレーション研究により, ファインチューニング段階での L_fore と L_inv の両方が必要であることが確認されている. L_fore のみではなく両者を組み合わせることで最大性能が得られ, 視覚期待を行動予測に活用する戦略の有効性が裏付けられる. 事前学習段階でも同様に, 視覚予見と逆ダイナミクスの統合が単一目標のみの場合より有効である.

クロスエンボディメント実験では, DROID (Franka ロボット特化) と OXE (マルチロボット) の比較において, OXE 事前学習版は汎化タスクでは小幅改善に留まり, 精密タスクでは若干の性能低下を示す. これはカメラ構成 (アイオンハンドカメラ比率の低さ) とクロス行動コントローラのギャップに起因すると分析されている.

制約として, 評価対象タスクが 6 種類に限られており, 高精度・接触豊富なタスクの網羅性が不足している. また, 異なるロボット機体への汎化能力の検証が不十分であり, クロスエンボディメント能力の体系的評価が今後の課題として残る.

## BibTex

<details>
<summary>BibTeX</summary>

```bibtex
@inproceedings{tian2025pidm,
  title     = {Predictive Inverse Dynamics Models are Scalable Learners for Robotic Manipulation},
  author    = {Yang Tian and Sizhe Yang and Jia Zeng and Ping Wang and Dahua Lin and Hao Dong and Jiangmiao Pang},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2025},
  url       = {https://arxiv.org/abs/2412.15109},
}
```

</details>
