---
marp: true
theme: default
size: 16:9
html: true
style: |
  section {
    padding: 20px 30px;
    font-family: 'Helvetica Neue', Arial, sans-serif;
  }
  h1 {
    color: #2c3e50;
    border-bottom: 3px solid #1E88E5;
    padding-bottom: 6px;
    margin-bottom: 12px;
    font-size: 1.5em;
    text-align: center;
  }
  .pipeline {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin: 20px auto 0;
  }
  .layer {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
  }
  .box {
    border-radius: 6px;
    color: white;
    font-weight: bold;
    font-size: 13px;
    text-align: center;
    padding: 8px 6px 6px;
    width: 88px;
    min-height: 48px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  .box .dim {
    font-size: 9px;
    font-weight: normal;
    opacity: 0.85;
    margin-top: 3px;
  }
  .arrow {
    font-size: 18px;
    color: #888;
    margin: 0 2px;
    line-height: 48px;
  }
  .desc {
    font-size: 9px;
    color: #555;
    text-align: center;
    line-height: 1.4;
    width: 100px;
    margin-top: 6px;
  }
  .desc .dtitle {
    font-weight: bold;
    font-size: 9.5px;
    color: #333;
  }
  .bg-input { background: #43A047; }
  .bg-conv { background: #1E88E5; }
  .bg-conv-late { background: #1565C0; }
  .bg-fc { background: #8E24AA; }
  .bg-out { background: #E53935; }
  .legend {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-top: 14px;
    font-size: 10px;
    color: #555;
  }
  .legend-item {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .legend-chip {
    width: 14px;
    height: 10px;
    border-radius: 2px;
    display: inline-block;
  }
---

# AlexNet アーキテクチャ

<div class="pipeline">
  <div class="layer">
    <div class="box bg-input">Input<span class="dim">227×227×3</span></div>
    <div class="desc"><span class="dtitle">入力画像</span><br>ImageNet 227×227 RGB</div>
  </div>
  <div class="arrow">→</div>
  <div class="layer">
    <div class="box bg-conv">Conv1<span class="dim">55×55×96</span></div>
    <div class="desc"><span class="dtitle">第 1 畳み込み</span><br>96 フィルタ, 11×11<br>stride 4, ReLU<br>LRN → MaxPool</div>
  </div>
  <div class="arrow">→</div>
  <div class="layer">
    <div class="box bg-conv">Conv2<span class="dim">27×27×256</span></div>
    <div class="desc"><span class="dtitle">第 2 畳み込み</span><br>256 フィルタ, 5×5<br>pad 2, ReLU<br>LRN → MaxPool</div>
  </div>
  <div class="arrow">→</div>
  <div class="layer">
    <div class="box bg-conv">Conv3<span class="dim">13×13×384</span></div>
    <div class="desc"><span class="dtitle">第 3 畳み込み</span><br>384 フィルタ, 3×3<br>pad 1, ReLU</div>
  </div>
  <div class="arrow">→</div>
  <div class="layer">
    <div class="box bg-conv">Conv4<span class="dim">13×13×384</span></div>
    <div class="desc"><span class="dtitle">第 4 畳み込み</span><br>384 フィルタ, 3×3<br>pad 1, ReLU</div>
  </div>
  <div class="arrow">→</div>
  <div class="layer">
    <div class="box bg-conv-late">Conv5<span class="dim">6×6×256</span></div>
    <div class="desc"><span class="dtitle">第 5 畳み込み</span><br>256 フィルタ, 3×3<br>pad 1, ReLU<br>MaxPool → Flatten</div>
  </div>
  <div class="arrow">→</div>
  <div class="layer">
    <div class="box bg-fc">FC6<span class="dim">4096</span></div>
    <div class="desc"><span class="dtitle">全結合層 1</span><br>4096 ユニット<br>ReLU + Dropout(0.5)</div>
  </div>
  <div class="arrow">→</div>
  <div class="layer">
    <div class="box bg-fc">FC7<span class="dim">4096</span></div>
    <div class="desc"><span class="dtitle">全結合層 2</span><br>4096 ユニット<br>ReLU + Dropout(0.5)</div>
  </div>
  <div class="arrow">→</div>
  <div class="layer">
    <div class="box bg-out">FC8<span class="dim">1000</span></div>
    <div class="desc"><span class="dtitle">出力層</span><br>1000 クラス<br>Softmax</div>
  </div>
</div>

<div class="legend">
  <div class="legend-item"><span class="legend-chip bg-input"></span>入力</div>
  <div class="legend-item"><span class="legend-chip bg-conv"></span>畳み込み層</div>
  <div class="legend-item"><span class="legend-chip bg-conv-late"></span>畳み込み層 (後段)</div>
  <div class="legend-item"><span class="legend-chip bg-fc"></span>全結合層</div>
  <div class="legend-item"><span class="legend-chip bg-out"></span>出力層</div>
</div>
