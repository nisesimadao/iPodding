#!/bin/bash

# Windowsビルドスクリプト
# 使用法: ./build_win.sh

echo "Starting Windows build for iPodding..."

# アイコンの生成
python scripts/generate_icons.py

# 出力先ディレクトリの作成
mkdir -p build/Windows

# PyInstallerの実行
# --onefile: 1つの実行ファイルにまとめる
# --noconsole: 実行時にコンソールを表示しない (GUIアプリ向け)
# --icon: アプリケーションアイコンを指定
# --add-data: 静的アセットを含める (logo.png)
# --distpath: ビルド成果物の出力先

pyinstaller --noconsole --onefile \
    --icon="assets/logo.ico" \
    --add-data "assets/logo.png;." \
    --name "iPodding" \
    --distpath "build/Windows" \
    --workpath "temp_build" \
    --specpath "temp_build" \
    src/main.py

echo "Build complete! Check build/Windows directory."
