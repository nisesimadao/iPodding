# <img src="assets/logo.png" width="40" vertical-align="middle" /> iPodding

iPodの音楽をPCに抽出し、VLC/iTunesプレイリストを作成するツール。
WindowsとmacOSの両方に対応し、洗練されたGUIで直感的に操作できます。

## プロジェクト構成

```
iPodding/
├── src/
│   ├── main.py              # メインエントリ（デフォルトでGUIを起動）
│   ├── gui_extractor.py      # プレミアムGUIアプリケーション
│   ├── ipod_extractor.py     # 音楽抽出コア機能（中断対応）
│   ├── ipod_parser.py       # iPodデータベースパーサー
│   └── ipod_utils.py        # OS固有・共有ユーティリティ [NEW]
├── assets/
│   ├── logo.png             # アプリケーションロゴ
│   └── logo.ico             # Windows用アイコン
├── scripts/
│   ├── build_win.sh         # Windowsビルドスクリプト
│   ├── build_mac.sh         # macOSビルドスクリプト
│   └── generate_icons.py    # アイコン生成スクリプト
├── requirements.txt      # 依存関係
└── README.md           # このファイル
```

## 特徴

- **マルチプラットフォーム**: Windows (ドライブレター検出) と macOS に完全対応。
- **プレミアムGUI**: モダンで直感的なインターフェース。
- **自動検出**: 接続されたiPod（ディスクモード）をワンクリックで検出。
- **安全な抽出**: Windowsの制限文字を考慮したファイル名サニタイズ。
- **中断機能**: 大量抽出中でも途中で安全に停止可能。
- **プレイリスト生成**: VLC (.m3u) および iTunes (.txt) 用プレイリストを自動作成。

## インストール

```bash
# 依存関係をインストール
pip install -r requirements.txt
```

## 使い方

### GUI（推奨）

1. `python main.py` を実行（引数なしで実行するとGUIが立ち上がります）
2. 「Auto Detect」ボタンをクリックしてiPodを検出
3. 出力先を確認し、「Start Extraction」をクリック
4. 完了後、「Open Folder」で抽出された曲を確認

### CUIモード

CLIでの操作も引き続き可能です：

```bash
# iPodを検出
python main.py detect

# 音楽を抽出
python main.py extract --ipod-path "E:\" --output-dir "C:\Users\Name\Music\iPod"
```

## 注意事項

- iPodは「ディスクモードとして使用」が有効になっている必要があります。
- 大量の音楽ファイルの場合、抽出に時間がかかることがあります（進捗バーで確認可能）。

## ライセンス

MIT License
