#!/bin/bash

# macOSビルドスクリプト
# 使用法: chmod +x scripts/build_mac.sh && ./scripts/build_mac.sh

echo "Starting macOS build for iPodding..."

# スクリプトの場所を基準にプロジェクトのルートへ移動し、絶対パスを取得
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# アイコンの生成
python3 scripts/generate_icons.py

# 出力先ディレクトリの作成
mkdir -p build/macOS

# PyInstallerの実行
# フルパスを使用することで temp_build フォルダとの混同を防ぎます
pyinstaller --windowed --noconsole \
    --icon="$PROJECT_ROOT/assets/logo.png" \
    --add-data "$PROJECT_ROOT/assets/logo.png:." \
    --name "iPodding" \
    --distpath "$PROJECT_ROOT/build/macOS" \
    --workpath "$PROJECT_ROOT/temp_build_mac" \
    --specpath "$PROJECT_ROOT/temp_build_mac" \
    --clean \
    src/main.py

echo "Build process finished. Please check build/macOS/iPodding.app"
