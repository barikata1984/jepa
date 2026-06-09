# Devcontainer 環境変更ログ

## 2026-06-09: Marp (Markdown スライド) 環境追加

- **目的**: NN パイプライン図の視覚的なやり取り用ツールとして Marp を導入
- **Dockerfile**: Node.js 22 + `@marp-team/marp-cli` v4.4.0 のインストールレイヤーを追加
- **devcontainer.json**: `marp-team.marp-vscode` 拡張を追加, `markdown.marp.enableHtml: true` 設定を追加
- **テスト結果**: AlexNet アーキテクチャ図を CSS + HTML div ベースで作成し, VS Code Marp プレビューでの描画を確認. インライン SVG は Marp プレビューのサンドボックス制約でレンダリングされないため, CSS + div ベースが実用的
- **成果物**: `alexnet_architecture.md` (テスト用, プロジェクトルート)
