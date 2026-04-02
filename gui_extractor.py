#!/usr/bin/env python3
"""
iPod音楽エクストラクター GUI版 (Premium Edition)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import platform
import time
from pathlib import Path
from ipod_extractor import iPodExtractor
from ipod_utils import iPodManager, open_folder

class iPodExtractorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("iPodding - iPod Music Extractor")
        self.root.geometry("900x700")
        self.root.configure(bg="#f5f7f9")
        
        # テーマ設定
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # カラーパレット
        self.colors = {
            "bg": "#f5f7f9",
            "card": "#ffffff",
            "primary": "#3498db",
            "primary_hover": "#2980b9",
            "secondary": "#2c3e50",
            "success": "#2ecc71",
            "danger": "#e74c3c",
            "text": "#34495e",
            "text_light": "#7f8c8d"
        }
        
        self.setup_styles()
        
        self.extractor = None
        self.extraction_thread = None
        self.manager = iPodManager()
        
        self.setup_ui()
        
        # 起動時に自動検出を試みる
        self.root.after(500, self.auto_detect)
        
    def setup_styles(self):
        """カスタムスタイルを設定"""
        self.style.configure("Main.TFrame", background=self.colors["bg"])
        self.style.configure("Card.TFrame", background=self.colors["card"], relief="flat")
        
        # ボタン
        self.style.configure("Primary.TButton", 
                            background=self.colors["primary"], 
                            foreground="white",
                            font=("Segoe UI", 10, "bold"),
                            padding=10)
        self.style.map("Primary.TButton", 
                      background=[("active", self.colors["primary_hover"])])
        
        self.style.configure("Secondary.TButton", 
                            background=self.colors["secondary"], 
                            foreground="white",
                            font=("Segoe UI", 10),
                            padding=8)
        
        # ラベル
        self.style.configure("Header.TLabel", 
                            background=self.colors["bg"], 
                            foreground=self.colors["secondary"], 
                            font=("Segoe UI", 18, "bold"))
        
        self.style.configure("SubHeader.TLabel", 
                            background=self.colors["card"], 
                            foreground=self.colors["text"], 
                            font=("Segoe UI", 11, "bold"))
        
        self.style.configure("Normal.TLabel", 
                            background=self.colors["card"], 
                            foreground=self.colors["text"], 
                            font=("Segoe UI", 10))
        
        # 進捗バー
        self.style.configure("TProgressbar", 
                            thickness=20,
                            troughcolor="#ecf0f1",
                            background=self.colors["primary"])

    def setup_ui(self):
        """UIを構成"""
        # メインコンテナ
        container = ttk.Frame(self.root, style="Main.TFrame", padding=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        # ヘッダー
        header_frame = ttk.Frame(container, style="Main.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="iPodding", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Label(header_frame, text=" | iPod Music Extractor", style="Normal.TLabel", background=self.colors["bg"]).pack(side=tk.LEFT, padx=5, pady=(8, 0))
        
        # 設定カード
        config_card = ttk.Frame(container, style="Card.TFrame", padding=20)
        config_card.pack(fill=tk.X, pady=(0, 20))
        
        # iPodパス
        row1 = ttk.Frame(config_card, style="Card.TFrame")
        row1.pack(fill=tk.X, pady=10)
        
        ttk.Label(row1, text="iPod Location", style="SubHeader.TLabel").pack(side=tk.LEFT)
        self.ipod_path_var = tk.StringVar()
        self.ipod_path_entry = ttk.Entry(row1, textvariable=self.ipod_path_var, font=("Segoe UI", 10), width=60)
        self.ipod_path_entry.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True)
        
        btn_detect = ttk.Button(row1, text="Auto Detect", style="Secondary.TButton", command=self.auto_detect)
        btn_detect.pack(side=tk.LEFT, padx=5)
        
        btn_browse_ipod = ttk.Button(row1, text="Browse...", style="Secondary.TButton", command=self.browse_ipod)
        btn_browse_ipod.pack(side=tk.LEFT)
        
        # 出力ディレクトリ
        row2 = ttk.Frame(config_card, style="Card.TFrame")
        row2.pack(fill=tk.X, pady=10)
        
        ttk.Label(row2, text="Extraction Destination", style="SubHeader.TLabel").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Music" / "iPod_Export"))
        self.output_dir_entry = ttk.Entry(row2, textvariable=self.output_dir_var, font=("Segoe UI", 10), width=60)
        self.output_dir_entry.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True)
        
        btn_browse_out = ttk.Button(row2, text="Browse...", style="Secondary.TButton", command=self.browse_output)
        btn_browse_out.pack(side=tk.LEFT)
        row2.pack_configure(pady=(10, 0))
        
        # 操作エリア
        action_frame = ttk.Frame(container, style="Main.TFrame")
        action_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.extract_button = ttk.Button(action_frame, text="Start Extraction", style="Primary.TButton", command=self.start_extraction)
        self.extract_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(action_frame, text="Stop", style="Secondary.TButton", command=self.stop_extraction, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        self.open_button = ttk.Button(action_frame, text="Open Folder", style="Secondary.TButton", command=self.open_output_folder)
        self.open_button.pack(side=tk.RIGHT)
        
        # 進捗カード
        progress_card = ttk.Frame(container, style="Card.TFrame", padding=20)
        progress_card.pack(fill=tk.X, pady=(0, 20))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_card, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(progress_card, text="Ready to extract", style="Normal.TLabel")
        self.status_label.pack(side=tk.LEFT)
        
        self.stats_label = ttk.Label(progress_card, text="", style="Normal.TLabel", foreground=self.colors["text_light"])
        self.stats_label.pack(side=tk.RIGHT)
        
        # ログコンソール
        console_frame = ttk.Frame(container, style="Main.TFrame")
        console_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(console_frame, text="Process Logs", style="SubHeader.TLabel", background=self.colors["bg"]).pack(anchor=tk.W, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(console_frame, 
                                                bg="#1e272e", 
                                                fg="#ecf0f1", 
                                                font=("Consolas", 9),
                                                insertbackground="white",
                                                relief="flat",
                                                padding=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 読み取り専用に
        self.log_text.config(state=tk.DISABLED)

    def log(self, message):
        """ログにメッセージを追加"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
        
    def auto_detect(self):
        """iPodを自動検出"""
        self.log("Scanning for connected iPods...")
        path = self.manager.detect_ipod()
        if path:
            self.ipod_path_var.set(path)
            self.log(f"Detected iPod at: {path}")
            self.status_label.config(text=f"iPod connected at {path}")
        else:
            self.log("No iPod detected. Please connect your iPod in 'Disk Mode' or manually browse.")
            self.status_label.config(text="No iPod detected")
            
    def browse_ipod(self):
        path = filedialog.askdirectory(title="Select iPod Root Folder")
        if path:
            self.ipod_path_var.set(path)
            self.log(f"Selected iPod path: {path}")
            
    def browse_output(self):
        path = filedialog.askdirectory(title="Select Destination Folder")
        if path:
            self.output_dir_var.set(path)
            self.log(f"Selected output path: {path}")
            
    def start_extraction(self):
        ipod_path = self.ipod_path_var.get()
        output_dir = self.output_dir_var.get()
        
        if not ipod_path or not output_dir:
            messagebox.showwarning("Incomplete", "Please specify both iPod location and destination.")
            return
            
        if not os.path.exists(ipod_path):
            messagebox.showerror("Error", f"Path does not exist: {ipod_path}")
            return
            
        # UI更新
        self.extract_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        
        self.extraction_thread = threading.Thread(target=self.extraction_worker, args=(ipod_path, output_dir))
        self.extraction_thread.daemon = True
        self.extraction_thread.start()
        
    def extraction_worker(self, ipod_path, output_dir):
        try:
            self.log("Starting extraction process...")
            self.extractor = iPodExtractor(
                ipod_path, 
                output_dir,
                progress_callback=self.update_ui_progress,
                log_callback=self.log
            )
            self.extractor.setup_output_directory()
            
            self.log("Index building (this might take a moment)...")
            if not self.extractor.extract_all_music():
                self.log("Extraction failed or was cancelled.")
                return
                
            self.log("Generating playlists...")
            self.extractor.create_vlc_playlist()
            self.extractor.create_itunes_playlist()
            
            summary = self.extractor.get_summary()
            self.root.after(0, lambda: self.finish_extraction(summary))
            
        except Exception as e:
            self.log(f"CRITICAL ERROR: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"An unexpected error occurred: {e}"))
            
        finally:
            self.root.after(0, self.reset_ui)
            
    def update_ui_progress(self, current, total, message=""):
        """スレッドセーフな進捗更新"""
        def update():
            if total > 0:
                pct = (current / total) * 100
                self.progress_var.set(pct)
                self.stats_label.config(text=f"{current} / {total}")
            self.status_label.config(text=message)
        
        self.root.after(0, update)
        
    def finish_extraction(self, summary):
        self.log(f"Success! {summary['total_tracks']} tracks extracted.")
        messagebox.showinfo("Extraction Complete", 
                           f"Successfully extracted {summary['total_tracks']} tracks.\n"
                           f"Total size: {summary['total_size_mb']:.1f} MB")
        self.open_output_folder()
        
    def reset_ui(self):
        self.extract_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Ready")
        
    def stop_extraction(self):
        """抽出を中断"""
        if self.extractor:
            self.extractor.cancel()
            self.stop_button.config(state=tk.DISABLED)
        
    def open_output_folder(self):
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            open_folder(output_dir)
        else:
            messagebox.showwarning("Warning", "Destination folder does not exist yet.")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = iPodExtractorGUI()
    app.run()
