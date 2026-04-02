#!/bin/bash

# macOSビルドスクリプト
# 使用法: chmod +x scripts/build_mac.sh && ./scripts/build_mac.sh

echo "Starting macOS build for iPodding..."

# スクリプトの場所を基準にプロジェクトのルートへ移動
cd "$(dirname "$0")/.."

# アイコンの生成
python3 scripts/generate_icons.py

# 出力先ディレクトリの作成
mkdir -p build/macOS

# PyInstallerの実行
# macOSでは --windowed を使うことで .app パッケージが生成されます
# --onefile は macOS GUI アプリではトラブルが多いため、まずは標準的なビルドを試みます

pyinstaller --windowed --noconsole \
    --icon="assets/logo.png" \
    --add-data "assets/logo.png:." \
    --name "iPodding" \
    --distpath "build/macOS" \
    --workpath "temp_build_mac" \
    --specpath "temp_build_mac" \
    --clean \
    src/main.py

echo "Build process finished. Please check build/macOS/iPodding.app"
