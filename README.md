# <img src="assets/logo.png" width="42" alt="iPodding logo" /> iPodding

[![CI](https://github.com/nisesimadao/iPodding/actions/workflows/ci.yml/badge.svg)](https://github.com/nisesimadao/iPodding/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/nisesimadao/iPodding)](https://github.com/nisesimadao/iPodding/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**iPodの音楽をPCへ取り出し、VLC / iTunes向けプレイリストまでまとめて作るデスクトップツール。** Windows と macOS に対応し、GUIとCLIの両方から使えます。

## ダウンロード

ビルド済みアプリは [Releases](https://github.com/nisesimadao/iPodding/releases/latest) から取得できます。

- **Windows**: `iPodding-Windows.exe`
- **macOS**: `iPodding-macOS.zip`

## 主な機能

- 接続された iPod（ディスクモード）の自動検出
- 曲・アーティスト・アルバム情報を使った整理付き抽出
- Windowsで使えない文字を考慮した安全なファイル名処理
- 大量抽出中の中断と失敗トラックの記録
- VLC (`.m3u`) / iTunes (`.txt`) プレイリスト生成
- Windows / macOS 対応
- GUI / CLI 両対応

## ソースから実行

Python 3.10+ を推奨します。

```bash
git clone https://github.com/nisesimadao/iPodding.git
cd iPodding
python -m pip install -r requirements.txt
python src/main.py
```

### CLI

```bash
# iPodを検出
python src/main.py detect

# 音楽を抽出
python src/main.py extract --ipod-path "E:\\" --output-dir "C:\\Users\\Name\\Music\\iPod"
```

## iPod側の準備

iPodding は、PCからストレージとして見える **ディスクモードの iPod** を対象にしています。iPodがFinder / エクスプローラーから参照できる状態にしてから起動してください。

## プロジェクト構成

```text
src/
  main.py           CLI / GUI エントリポイント
  gui_extractor.py  GUI
  ipod_extractor.py 抽出・コピー・プレイリスト生成
  ipod_parser.py    iPodデータベース解析
  ipod_utils.py     OS別の検出・ユーティリティ
scripts/            Windows / macOS ビルドスクリプト
assets/             アプリアイコン
```

## テスト

```bash
python test_enhancements.py
python -m compileall -q src
```

GitHub Actions でも Windows / macOS 互換の基本ロジックとPython構文を継続チェックします。

## ビルド

PyInstaller を利用します。ビルド成果物はGit管理せず、配布物は GitHub Releases に置く方針です。

```bash
# macOS / Linux shell
bash scripts/build_mac.sh

# Windowsでは Git Bash 等から
bash scripts/build_win.sh
```

## License

[MIT](LICENSE)
