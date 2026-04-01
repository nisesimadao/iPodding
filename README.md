# iPodding

iPodの音楽をPCに抽出し、VLC/iTunesプレイリストを作成するツール

## プロジェクト構成

```
iPodding/
├── main.py              # メインCLIアプリケーション
├── gui_extractor.py      # GUIアプリケーション
├── ipod_extractor.py     # 音楽抽出コア機能
├── ipod_parser.py       # iPodデータベースパーサー
├── test_enhancements.py # 機能テスト
├── requirements.txt      # 依存関係
└── README.md           # このファイル
```

## 機能

- 接続されているiPodを自動検出
- iPodの音楽をPCにコピー（本来の曲名で保存）
- VLCプレイリスト(.m3u)の自動生成
- iTunesインポート用プレイリスト(.txt)の作成
- GUIとCUIの両方に対応
- 進捗表示と詳細ログ

## インストール

```bash
# 仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

## 使い方

### CUIモード

#### iPodを検出
```bash
python main.py detect
```

#### 音楽を抽出
```bash
# 自動検出 + デフォルト出力先
python main.py extract

# iPodパスと出力先を指定
python main.py extract --ipod-path "/Volumes/ExampleiPodDriveMode" --output-dir "~/Desktop/iPod_music"
```

#### GUIを起動
```bash
python main.py gui
```

### GUIモード

1. `python main.py gui` を実行
2. iPodパスと出力先を設定（自動検出も可能）
3. 「音楽抽出開始」ボタンをクリック
4. 進捗を確認しながら抽出完了を待つ
5. 「出力フォルダを開く」で結果を確認

## 出力ファイル

抽出完了後、指定したフォルダに以下が作成されます：

- **音楽ファイル**: `001. Artist - Title.mp3` の形式
- **VLCプレイリスト**: `iPod_music.m3u` - VLCで直接再生可能
- **iTunesプレイリスト**: `iPod_music.txt` - iTunesにドラッグ＆ドロップでインポート

## 特徴

- **安全なファイル名**: 無効な文字を自動的に置換
- **メタデータ保持**: mutagenを使用して曲情報を抽出
- **進捗表示**: リアルタイムで処理状況を表示
- **エラーハンドリング**: 問題のあるファイルを最大3回リトライしてスキップ
- **重複検出**: タイトル・アーティスト・アルバムが同じ曲は重複としてスキップ
- **詳細サマリー**: 成功・失敗・重複の数を詳細に表示
- **クロスプラットフォーム**: macOSで動作確認済み

## 注意事項

- iPodは「ディスクモードとして使用」が有効になっている必要があります
- macOSでiPodに初めて接続する場合、「信頼する」を選択してください
- 大量の音楽ファイルの場合、抽出に時間がかかることがあります

## サポートされている形式

- MP3
- M4A (AAC)
- WAV
- AAC

## ライセンス

MIT License
