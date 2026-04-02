#!/bin/bash

# Windowsビルドスクリプト
# 使用法: ./build_win.sh

echo "Starting Windows build for iPodding..."

# スクリプトの場所を基準にプロジェクトのルートへ移動し、絶対パスを取得
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# アイコンの生成
python scripts/generate_icons.py

# 出力先ディレクトリの作成
mkdir -p build/Windows

# PyInstallerの実行
# フルパスを使用することで temp_build フォルダとの混同を防ぎます
# Windowsでは --add-data の区切りにセミコロン (;) を使用します

pyinstaller --noconsole --onefile \
    --icon="$PROJECT_ROOT/assets/logo.ico" \
    --add-data "$PROJECT_ROOT/assets/logo.png;." \
    --name "iPodding" \
    --distpath "$PROJECT_ROOT/build/Windows" \
    --workpath "$PROJECT_ROOT/temp_build" \
    --specpath "$PROJECT_ROOT/temp_build" \
    src/main.py

echo "Build complete! Check build/Windows directory."
