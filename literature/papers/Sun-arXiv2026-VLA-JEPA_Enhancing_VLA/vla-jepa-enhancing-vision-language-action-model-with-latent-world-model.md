---
Title: "VLA-JEPA: Enhancing Vision-Language-Action Model with Latent World Model"
Authors:
  - Sun, Jingwen
  - Zhang, Wenyao
  - Qi, Zekun
  - Ren, Shaojie
  - Liu, Zezhi
  - Zhu, Hanxin
  - Sun, Guangzhong
  - Jin, Xin
  - Chen, Zhibo
Year: 2026
Venue: arXiv
Tags:
  - "jepa"
  - "vla"
  - "world-model"
  - "robot-manipulation"
  - "self-supervised"
  - "latent-prediction"
PDF: "[[papers/Sun-arXiv2026-VLA-JEPA_Enhancing_VLA/main.pdf|📃]]"
Import Date: "2026-06-09"
Read Date: 2026-06-09
Executive Summary: "インターネット規模の人間動画から VLA ポリシーを事前学習する際, 既存の潜在行動目的は画素変動に引きずられ行動関連の状態遷移を捉えられないという問題に取り組む. 提案する VLA-JEPA は JEPA 方式の漏洩なし状態予測 (leakage-free state prediction) を核とし, ターゲットエンコーダ (V-JEPA2) が未来フレームの潜在表現を生成する一方, 学習器側には現在観測のみを与えることで情報漏洩ショートカットを排除する. VLM バックボーン (Qwen3-VL) が出力する潜在行動トークンを条件として自己回帰型潜在世界モデルが次状態を予測し, ロボットデータではフロー整合行動ヘッドを追加して連続軌道を生成する. LIBERO・LIBERO-Plus・SimplerEnv・実世界 Franka ロボットで既存の潜在行動 VLA を一貫して上回り, 特に外乱頑健性で顕著な改善を示す一方, 細粒度テキスト追従性は今後の課題として残る."
Citekey: Sun-arXiv2026-VLA-JEPA_Enhancing_VLA
BibTeX Key: sun2026vlajepa
DOI: ""
Relevance: 4
Repository: https://github.com/ginwind/VLA-JEPA/
Category: note
Template Version: v2.3
---

## Executive Summary

インターネット規模の人間動画から VLA ポリシーを事前学習する際, 既存の潜在行動目的は画素変動に引きずられ行動関連の状態遷移を捉えられないという問題に取り組む. 提案する VLA-JEPA は JEPA 方式の漏洩なし状態予測 (leakage-free state prediction) を核とし, ターゲットエンコーダ (V-JEPA2) が未来フレームの潜在表現を生成する一方, 学習器側には現在観測のみを与えることで情報漏洩ショートカットを排除する. VLM バックボーン (Qwen3-VL) が出力する潜在行動トークンを条件として自己回帰型潜在世界モデルが次状態を予測し, ロボットデータではフロー整合行動ヘッドを追加して連続軌道を生成する. LIBERO・LIBERO-Plus・SimplerEnv・実世界 Franka ロボットで既存の潜在行動 VLA を一貫して上回り, 特に外乱頑健性で顕著な改善を示す一方, 細粒度テキスト追従性は今後の課題として残る.

---

## Summary

### この論文が答えた問い, あるいは解決した課題は何か?

人間動画を用いた VLA 事前学習において, 既存の潜在行動手法が"行動の意味"ではなく"画素の変化"を学んでしまうという根本的な問題を解決する. 論文は失敗の原因を 4 点に整理している. 第一に, 画素レベル目的がカメラ動作・照明・背景クラッタ等の外見変動に特化した表現を学ぶこと. 第二に, 実世界動画ではカメラ動作が行動起因の変化より支配的なノイズとなること. 第三に, 現在・未来フレームを同一モジュールに同時入力する設計が"未来をそのまま転写する"ショートカットを生じさせること. 第四に, これを防ぐための多段階パイプラインが複雑かつ不安定であること. これらに対し, 行動関連の状態遷移意味論を潜在空間で直接学べる単一の事前学習枠組みを示す.

### 提案手法のアプローチと, その根幹をなす要素は何か?

VLA-JEPA は, 人間動画とロボットデータの両方で同一の潜在世界モデル目的を用いて VLM を共同事前学習し, その後フロー整合行動ヘッドで精調整するという 2 段階のシンプルな枠組みである. 核心は"未来フレームを学習器の入力から完全に遮断し, ターゲットとしてのみ使う"漏洩なし設計にあり, これにより画素ショートカットと情報漏洩を同時に回避する.

不可欠な構成要素:

- **漏洩なし状態予測 (leakage-free state prediction)**: ターゲット側に凍結 V-JEPA2 エンコーダを用いて未来フレームの潜在表現を生成し, 学習器 (VLM 側) には現在観測のみを与える. 未来情報は監督信号として一方向にのみ流れる.
- **潜在行動トークン**: VLM (Qwen3-VL) に挿入された学習可能トークン `<latent_i>` が状態遷移のダイナミクスを潜在表現に集約する. ロボットデータには `<action>` トークンも追加される.
- **自己回帰型潜在世界モデル**: 現在の世界状態表現と潜在行動表現を条件に, 次のフレーム列の状態を予測するトランスフォーマーベース世界モデル. 時間因果的アテンション機構を用いる.
- **世界状態エンコーダ (multi-view V-JEPA2)**: 複数視点の映像フレームを連結して統一世界状態表現を構築する単視点エンコーダ. 事前学習中は凍結する.
- **フロー整合行動ヘッド**: ロボットデータ精調整時に連続行動軌道を生成する条件付きフロー整合モジュール. 潜在行動表現 $z_a$ を条件信号として用いる.

### 特に参考とした既存研究と, それらと比した提案手法の新規性は何か?

参考とした主要先行研究:

- **JEPA / V-JEPA2** [[papers/Assran-arXiv2025-V-JEPA_Self-Supervised_Video/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning|Assran+ 2025]]: 潜在空間アライメントにより画素再構成を排除するという設計思想の出発点. VLA-JEPA はこの原理をロボット制御の事前学習に拡張する.
- **LAPA** (Ye et al. 2024): 動画から潜在行動を事前学習する代表的な手法. 画素差分ベースの圧縮で情報漏洩が生じる点が批判対象.
- **UniVLA** (Bu et al. 2025): タスク関連テキスト誘導で漏洩を部分的に緩和するが, テキストへの過依存が操作無関係背景に注意を向けさせる問題が残る.
- **villa-x** (Chen et al. 2025): 光学フロー・オブジェクト中心制約で潜在行動空間を制御するが, 手工芸的制約が新環境での汎化を阻む.

提案手法の新規性は 3 点ある. 第一に, 未来フレームを入力から完全に除外する漏洩なし設計により, 補助モジュールや光学フロー等の事前知識なしに行動中心表現を獲得できる. 第二に, 人間動画とロボットデータを同一の世界モデル目的で統合的に学習し, 多段階パイプラインを 2 段階 (事前学習 + 精調整) に簡略化した. 第三に, 潜在行動トークンが学習後も再定義されないため, 精調整時に表現の一貫性が保たれる.

### どのように訓練・最適化したのか?

**損失関数 / 最適化目的:**

事前学習 (人間動画・ロボットデータ共通) では世界モデル損失を使用する:

$$\mathcal{L}_{\mathrm{WM}} = \sum_{k=1}^{T} \mathbb{E}_{s_{t_k} \sim F(\cdot)} [\hat{s}_{t_k} - s_{t_k}]$$

ここで $s_{t_k}$ は V-JEPA2 による真の世界状態表現, $\hat{s}_{t_k}$ は世界モデルによる予測, $T$ は動画予測ホライズン (消失 KL 項により ELBO は再構成損失に帰着する).

ロボットデータ精調整では世界モデル損失にフロー整合損失を加えた結合目的を使用する:

$$\mathcal{L} = \mathcal{L}_{\mathrm{FM}} + \beta \mathcal{L}_{\mathrm{WM}}$$

フロー整合損失は:

$$\mathcal{L}_{\mathrm{FM}} = \mathbb{E}_{a_{0:H}, \epsilon, t} \bigl[ \|v_\theta(a_t, t \mid z_a) - (a_{0:H} - \epsilon)\|_2^2 \bigr]$$

$\beta$ は調整可能なハイパーパラメータ. $K$ (潜在行動トークンの繰り返し数) も調整可能.

**データセット:**

- 事前学習 (潜在行動): Something-Something-v2 (22 万本の人間動画) + Open X-Embodiment (OXE) サブセット
- 事前学習 (アクション): Droid データセット (7.6 万軌道の高品質ロボットデモ)
- LIBERO / LIBERO-Plus 精調整: LIBERO データセット (シミュレーション収集の約 2,000 エキスパートデモ)
- SimplerEnv 精調整: Fractal データセット + BridgeV2 データセット (2 種のロボット本体に対応)
- 実世界実験: Franka Research 3 アームで収集した 100 件の人間デモ (3 タスク)

全実験は 8 枚の NVIDIA A100 GPU で実施.

### どのように検証したか? 指標と結果は?

**検証プロトコル:**

3 つのシミュレーションベンチマークと 1 つの実世界環境で評価した. シミュレーション評価はスイートごとに 50 エピソードずつ実施し成功率を算出. 比較手法は最新の潜在行動 VLA (LAPA, UniVLA, villa-x, CoT-VLA, WorldVLA 等) と, ロボットデータのみで学習した VLA ($\pi_0$, $\pi_{0.5}$, OpenVLA-OFT 等) を含む.

**主要な定量的結果:**

- **LIBERO** (Table 1): VLA-JEPA は Avg 97.2% で, $\pi_{0.5}$ (96.9%) および OpenVLA-OFT (97.1%) と同水準の最高性能を達成. 人間動画を省いたアブレーション (w/o human videos) は 96.1%.
- **SimplerEnv** (Table 2): Google Robot で Avg 65.2% (最高), WidowX Robot で Avg 57.3% (LAPA と並んで最高). villa-x (大規模ロボット+人間動画で学習) と比べ, 1% 未満のデータ量で同等以上の結果.
- **LIBERO-Plus** (Table 3): 7 つの外乱次元中 5 つで最高性能, Avg 79.5%. Language (+85.4%), Light (+95.6%), Background (+93.6%) で特に顕著な優位性を示す.
- **実世界 Franka ロボット** (Figure 4): インドメイン成功率 0.70 (最高), オブジェクト配置 OOD で 0.47 (最高), タスク OOD では 0.20 ($\pi_{0.5}$ の 0.17 に次ぐ 2 位).
- **未来ホライズン感度** (Table 4): $T=8$ で LIBERO Avg 96.1% (最高).

### 検証結果に基づいた議論, 明らかになった課題はあるか?

(§4.4 Real-world Experiments より) 実世界展開において, VLA-JEPA は $\pi_{0.5}$ と比べて姿勢制御の精度で劣ることが観察された. 具体的には $\pi_{0.5}$ がターゲット物体への接触指示を精確に遵守する一方, VLA-JEPA は細粒度のテキスト指示に対する推論力が不足しており, 指示と一致しない物体を把持するケースが生じる.

(§4.4 末尾) 一方で VLA-JEPA は繰り返し把持 (grasp retry) のスキルを自発的に獲得しており, これは人間動画に豊富に含まれる再試行行動から学習したと著者は解釈している.

(§5 Conclusion より) 著者は, 人間動画事前学習パラダイムはロボットデータやテキストベース推論データを追加することで自然に拡張可能であり, 汎化性と頑健性をさらに向上できると述べているが, 明示的な limitation セクションは設けていない. ロボット安全制約の逸脱は $\pi_{0.5}$ の問題として言及されているが, VLA-JEPA 自身の限界として記述されたものではない.

---

## 自身の研究との関連

VLA-JEPA の漏洩なし設計は, 潜在行動が"未来状態の縮退した圧縮"に陥るという問題に対する構造的な解答を与えており, 自身の研究で JEPA 系潜在表現の信号 / ノイズ比を診断する際の対照条件として有用である. 特に, 世界状態エンコーダとして凍結 V-JEPA2 を用いることで外見ノイズを抑制しつつ行動関連情報を保持できるという知見は, 操作タスク向けの潜在空間設計に直接応用できる. 一方, VLA-JEPA はマニピュレーション向けにエンドエフェクタ軌道を生成する設計であり, より低レベルのセンサモータ制御や触覚フィードバックとの統合は検討外であるため, 本研究との差分として位置づけられる.

---

## 追加議論

---

## BibTex

<details>
<summary> Click to show/noshow the BibTex data </summary>

```bibtex
@article{sun2026vlajepa,
  title   = {VLA-JEPA: Enhancing Vision-Language-Action Model with Latent World Model},
  author  = {Sun, Jingwen and Zhang, Wenyao and Qi, Zekun and Ren, Shaojie and
             Liu, Zezhi and Zhu, Hanxin and Sun, Guangzhong and Jin, Xin and
             Chen, Zhibo},
  journal = {arXiv preprint arXiv:2602.10098},
  year    = {2026}
}
```

</details>
