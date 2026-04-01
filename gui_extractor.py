#!/usr/bin/env python3
"""
iPod音楽エクストラクター GUI版
Tkinterベースのグラフィカルインターフェース
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import subprocess
from pathlib import Path
from ipod_extractor import iPodExtractor

class iPodExtractorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("iPodding - iPod音楽エクストラクター")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.extractor = None
        self.extraction_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """UIを設定"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 設定セクション
        settings_frame = ttk.LabelFrame(main_frame, text="設定", padding="10")
        settings_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # iPodパス
        ttk.Label(settings_frame, text="iPodパス:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ipod_path_var = tk.StringVar(value="")  # 空文字列に変更
        self.ipod_path_entry = ttk.Entry(settings_frame, textvariable=self.ipod_path_var, width=50)
        self.ipod_path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(settings_frame, text="参照", command=self.browse_ipod).grid(row=0, column=2)
        
        # 出力ディレクトリ
        ttk.Label(settings_frame, text="出力先:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Music" / "iPod_Export"))
        self.output_dir_entry = ttk.Entry(settings_frame, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(settings_frame, text="参照", command=self.browse_output).grid(row=1, column=2)
        
        # 設定列の重み
        settings_frame.columnconfigure(1, weight=1)
        
        # 操作ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.extract_button = ttk.Button(button_frame, text="音楽抽出開始", command=self.start_extraction)
        self.extract_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_extraction, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.open_button = ttk.Button(button_frame, text="出力フォルダを開く", command=self.open_output_folder)
        self.open_button.grid(row=0, column=2, padx=5)
        
        # 進捗バー
        progress_frame = ttk.LabelFrame(main_frame, text="進捗", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="準備完了")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        progress_frame.columnconfigure(0, weight=1)
        
        # ログ出力
        log_frame = ttk.LabelFrame(main_frame, text="ログ", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # メインウィンドウの重み
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 初期ログ
        self.log("iPodding - iPod音楽エクストラクター")
        self.log("準備完了")
        
    def log(self, message):
        """ログにメッセージを追加"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def browse_ipod(self):
        """iPodフォルダを選択"""
        path = filedialog.askdirectory(title="iPodフォルダを選択")
        if path:
            self.ipod_path_var.set(path)
            
    def browse_output(self):
        """出力フォルダを選択"""
        path = filedialog.askdirectory(title="出力フォルダを選択")
        if path:
            self.output_dir_var.set(path)
            
    def start_extraction(self):
        """抽出処理を開始"""
        ipod_path = self.ipod_path_var.get()
        output_dir = self.output_dir_var.get()
        
        if not ipod_path or not output_dir:
            messagebox.showerror("エラー", "iPodパスと出力先を指定してください")
            return
            
        if not os.path.exists(ipod_path):
            messagebox.showerror("エラー", f"iPodパスが存在しません: {ipod_path}")
            return
            
        # UI状態を更新
        self.extract_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_label.config(text="抽出中...")
        
        # 抽出処理をスレッドで実行
        self.extraction_thread = threading.Thread(target=self.extraction_worker, args=(ipod_path, output_dir))
        self.extraction_thread.daemon = True
        self.extraction_thread.start()
        
    def extraction_worker(self, ipod_path, output_dir):
        """抽出処理ワーカー"""
        try:
            self.log("抽出処理を開始します...")
            
            # エクストラクターを作成（コールバック関数を渡す）
            self.extractor = iPodExtractor(
                ipod_path, 
                output_dir,
                progress_callback=self.update_progress,
                log_callback=self.log
            )
            self.extractor.setup_output_directory()
            
            # 音楽を抽出
            self.log("iPodから音楽を読み込み中...")
            if not self.extractor.extract_all_music():
                self.log("抽出に失敗しました")
                return
                
            # プレイリストを作成
            self.log("VLCプレイリストを作成中...")
            vlc_playlist = self.extractor.create_vlc_playlist()
            
            self.log("iTunesプレイリストを作成中...")
            itunes_playlist = self.extractor.create_itunes_playlist()
            
            # サマリーを表示
            summary = self.extractor.get_summary()
            self.log(f"\n抽出完了!")
            self.log(f"合計トラック数: {summary['total_tracks']}")
            self.log(f"合計サイズ: {summary['total_size_mb']:.1f} MB")
            self.log(f"フォーマット: {summary['formats']}")
            
            if vlc_playlist:
                self.log(f"VLCプレイリスト: {vlc_playlist}")
            if itunes_playlist:
                self.log(f"iTunesプレイリスト: {itunes_playlist}")
                
            # 進捗を100%に
            self.progress_var.set(100)
            self.status_label.config(text="抽出完了")
            
            messagebox.showinfo("完了", f"{summary['total_tracks']}曲の抽出が完了しました!")
            
        except Exception as e:
            self.log(f"エラーが発生しました: {e}")
            messagebox.showerror("エラー", f"抽出中にエラーが発生しました: {e}")
            
        finally:
            # UI状態を復元
            self.extract_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
    def update_progress(self, current, total, message=""):
        """進捗バーを更新（スレッドセーフ）"""
        def update_ui():
            if total > 0:
                progress_percent = (current / total) * 100
                self.progress_var.set(progress_percent)
            self.status_label.config(text=message)
            self.root.update_idletasks()
        
        # UIスレッドで実行
        self.root.after(0, update_ui)
            
    def stop_extraction(self):
        """抽出処理を停止"""
        if self.extraction_thread and self.extraction_thread.is_alive():
            self.log("抽出を停止します...")
            # スレッドの停止は難しいので、UIだけ無効化
            self.status_label.config(text="停止中...")
            
    def open_output_folder(self):
        """出力フォルダを開く"""
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            try:
                subprocess.run(['open', output_dir], check=True)
            except subprocess.CalledProcessError as e:
                self.log(f"フォルダを開けませんでした: {e}")
        else:
            messagebox.showerror("エラー", "出力フォルダが存在しません")
            
    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()

if __name__ == "__main__":
    app = iPodExtractorGUI()
    app.run()
