#!/bin/bash

# macOSビルドスクリプト
# 使用法: chmod +x build_mac.sh && ./build_mac.sh

echo "Starting macOS build for iPodding..."

# アイコンの生成
python3 scripts/generate_icons.py

# 出力先ディレクトリの作成
mkdir -p build/macOS

# PyInstallerの実行
# --windowed: macOS向けのアプリパッケージ (.app) を生成
# --icon: アイコンファイルを指定 (macOSは本来 .icns が望ましいですが、.png も試みます)
# --add-data: アセットを含める (macOSは ":" で区切る)

pyinstaller --windowed --noconsole --onefile \
    --icon="assets/logo.png" \
    --add-data "assets/logo.png:." \
    --name "iPodding" \
    --distpath "build/macOS" \
    --workpath "temp_build_mac" \
    --specpath "temp_build_mac" \
    src/main.py

echo "Build complete! Check build/macOS directory."
