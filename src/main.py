#!/usr/bin/env python3
"""
iPodding - iPod音楽・ポッドキャスト管理ツール
"""

import os
import sys
import click
from rich.console import Console
from pathlib import Path
import platform
import shutil
from ipod_extractor import iPodExtractor
from ipod_utils import iPodManager

console = Console()

    # iPodManagerはipod_utilsからインポートされるため、このクラス定義は不要です

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """iPodding - iPod音楽管理ツール"""
    if ctx.invoked_subcommand is None:
        # サブコマンドが指定されていない場合はGUIを起動
        ctx.invoke(gui)

@cli.command()
def detect():
    """接続されているiPodを検出"""
    manager = iPodManager()
    ipod_path = manager.detect_ipod()
    
    if ipod_path:
        console.print(f"[green]iPodを検出しました: {ipod_path}[/green]")
    else:
        console.print("[red]iPodが見つかりません[/red]")

@cli.command()
@click.option('--ipod-path', help='iPodのマウントパスを指定')
@click.option('--output-dir', help='出力先ディレクトリを指定')
def extract(ipod_path, output_dir):
    """iPodの音楽をPCに抽出"""
    manager = iPodManager()
    
    if not ipod_path:
        ipod_path = manager.detect_ipod()
        if not ipod_path:
            console.print("[red]iPodが見つかりません。--ipod-pathオプションでパスを指定してください[/red]")
            return
    
    if not output_dir:
        output_dir = str(Path.home() / "Music" / "iPod_Export")
    
    console.print(f"[blue]iPodパス: {ipod_path}[/blue]")
    console.print(f"[blue]出力先: {output_dir}[/blue]")
    
    try:
        # 進捗表示用のコールバック
        def progress_callback(current, total, message=""):
            if total > 0:
                progress_percent = (current / total) * 100
                console.print(f"[yellow]進捗: {progress_percent:.1f}% - {message}[/yellow]")
            else:
                console.print(f"[yellow]{message}[/yellow]")
        
        # エクストラクターを作成
        extractor = iPodExtractor(
            ipod_path, 
            output_dir,
            progress_callback=progress_callback
        )
        extractor.setup_output_directory()
        
        # 音楽を抽出
        console.print("[yellow]iPodから音楽を抽出中...[/yellow]")
        if not extractor.extract_all_music():
            console.print("[red]抽出に失敗しました[/red]")
            return
        
        # プレイリストを作成
        console.print("[yellow]プレイリストを作成中...[/yellow]")
        vlc_playlist = extractor.create_vlc_playlist()
        itunes_playlist = extractor.create_itunes_playlist()
        
        # サマリーを表示
        summary = extractor.get_summary()
        console.print(f"\n[green]✅ 抽出完了![/green]")
        console.print(f"合計トラック数: {summary['total_tracks']}")
        console.print(f"合計サイズ: {summary['total_size_mb']:.1f} MB")
        console.print(f"フォーマット: {summary['formats']}")
        
        if vlc_playlist:
            console.print(f"VLCプレイリスト: {vlc_playlist}")
        if itunes_playlist:
            console.print(f"iTunesプレイリスト: {itunes_playlist}")
            
    except FileNotFoundError as e:
        console.print(f"[red]ファイルが見つかりません: {e}[/red]")
    except PermissionError as e:
        console.print(f"[red]アクセス権限エラー: {e}[/red]")
    except Exception as e:
        console.print(f"[red]予期せぬエラー: {e}[/red]")

@cli.command()
def gui():
    """GUIを起動"""
    try:
        from gui_extractor import iPodExtractorGUI
        app = iPodExtractorGUI()
        app.run()
    except ImportError as e:
        console.print(f"[red]GUIモジュールのインポートに失敗しました: {e}[/red]")
        console.print("[yellow]tkinterがインストールされているか確認してください[/yellow]")

if __name__ == "__main__":
    cli()
