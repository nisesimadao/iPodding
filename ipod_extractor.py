#!/usr/bin/env python3
"""
iPod音楽エクストラクター
iPodの音楽をPCにコピーし、VLCプレイリストを作成する
"""

import os
import shutil
import urllib.parse
from pathlib import Path
from ipod_parser import iPodDatabase

class iPodExtractor:
    def __init__(self, ipod_path, output_dir, progress_callback=None, log_callback=None):
        self.ipod_path = ipod_path
        self.output_dir = Path(output_dir)
        self.database = iPodDatabase(ipod_path)
        self.copied_tracks = []
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.seen_tracks = set()  # 重複検出用
        self.failed_tracks = []   # 失敗したトラック記録
        self.is_cancelled = False # 中断フラグ
        
    def log(self, message):
        """ログを出力"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
            
    def update_progress(self, current, total, message=""):
        """進捗を更新"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
        
    def is_duplicate_track(self, track):
        """重複トラックを検出（タイトル、アーティスト、アルバムがすべて同じ）"""
        track_key = (track.title.lower().strip(), 
                    track.artist.lower().strip(), 
                    track.album.lower().strip())
        
        if track_key in self.seen_tracks:
            return True
        
        self.seen_tracks.add(track_key)
        return False
        
    def setup_output_directory(self):
        """出力ディレクトリを作成"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log(f"出力ディレクトリ: {self.output_dir}")
        
    def extract_all_music(self):
        """すべての音楽を抽出"""
        # データベース読み込み中も進捗を表示し、中断を確認するように変更
        if not self.database.load_database(
            progress_callback=self.update_progress,
            cancel_check=lambda: self.is_cancelled
        ):
            if self.is_cancelled:
                self.log("読み込み中に中断されました")
            else:
                self.log("iPodデータベースの読み取りに失敗しました")
            return False
            
        tracks = self.database.get_music_tracks()
        self.log(f"音楽トラック数: {len(tracks)}")
        
        skipped_duplicates = 0
        total_files = len(tracks)
        
        for i, track in enumerate(tracks, 1):
            try:
                # 重複チェック
                if self.is_duplicate_track(track):
                    skipped_duplicates += 1
                    self.log(f"  重複をスキップ: {track.artist} - {track.title}")
                    continue
                
                # 中断チェック
                if self.is_cancelled:
                    self.log("抽出処理が中断されました")
                    return False
                
                # トラックをコピー（リトライ機能付き）
                success = self.copy_track_with_retry(track, i)
                if success:
                    self.copied_tracks.append(track)
                
                # 進捗を更新
                self.update_progress(i, total_files, f"処理中: {i}/{total_files} - {track.title}")
                
            except Exception as e:
                self.log(f"エラー: {track.title} - {e}")
                self.failed_tracks.append(f"{track.artist} - {track.title}: {e}")
        
        # 結果サマリー
        self.log(f"\n--- 抽出結果サマリー ---")
        self.log(f"処理したトラック数: {total_files}")
        self.log(f"正常にコピー: {len(self.copied_tracks)}")
        self.log(f"重複をスキップ: {skipped_duplicates}")
        self.log(f"失敗したトラック: {len(self.failed_tracks)}")
        
        if self.failed_tracks:
            self.log(f"\n失敗したトラック一覧:")
            for failed in self.failed_tracks:
                self.log(f"  - {failed}")
                
        return True
    
    def copy_track_with_retry(self, track, index, max_retries=3):
        """リトライ機能付きトラックコピー"""
        for attempt in range(max_retries):
            try:
                success = self.copy_track(track, index)
                if success:
                    return success
                elif attempt < max_retries - 1:
                    self.log(f"  リトライ {attempt + 1}/{max_retries}: {track.title}")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    self.log(f"  リトライ {attempt + 1}/{max_retries}: {track.title} (エラー: {e})")
                else:
                    self.log(f"  コピー失敗（最大リトライ回数到達）: {track.title} - {e}")
                    self.failed_tracks.append(f"{track.artist} - {track.title}: {e}")
                    return False
        
        return False
    
    def copy_track(self, track, index):
        """トラックをコピー"""
        try:
            # ファイル存在チェック
            if not os.path.exists(track.path):
                raise FileNotFoundError(f"元ファイルが存在しません: {track.path}")
            
            # 安全なファイル名を作成
            safe_title = self.sanitize_filename(track.title)
            safe_artist = self.sanitize_filename(track.artist)
            safe_album = self.sanitize_filename(track.album)
            
            # ファイル名を生成: "001. Artist - Title.ext"
            filename = f"{index:03d}. {safe_artist} - {safe_title}.{track.file_type}"
            
            # 出力先パス
            output_path = self.output_dir / filename
            
            # ファイルをコピー
            shutil.copy2(track.path, output_path)
            self.log(f"  コピー完了: {filename}")
            
            # トラック情報を更新
            track.output_path = str(output_path)
            track.relative_path = filename
            
            return True
            
        except Exception as e:
            self.log(f"  コピー失敗: {e}")
            return False
    
    def sanitize_filename(self, filename):
        """ファイル名を安全にする"""
        # 無効な文字を置換
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # ファイル名長制限を定数化
        MAX_FILENAME_LENGTH = 100
        
        # 長すぎるファイル名を短縮
        if len(filename) > MAX_FILENAME_LENGTH:
            filename = filename[:MAX_FILENAME_LENGTH-3] + "..."
            
        return filename
    
    def create_vlc_playlist(self, playlist_name="iPod_music.m3u"):
        """VLCプレイリストを作成"""
        playlist_path = self.output_dir / playlist_name
        file_handle = None
        
        try:
            file_handle = open(playlist_path, 'w', encoding='utf-8')
            file_handle.write("#EXTM3U\n")
            
            for track in self.copied_tracks:
                # 情報行
                duration_sec = int(track.duration)
                file_handle.write(f"#EXTINF:{duration_sec},{track.artist} - {track.title}\n")
                
                # ファイルパス（相対パス）
                file_handle.write(f"{track.relative_path}\n")
                    
            self.log(f"VLCプレイリスト作成完了: {playlist_path}")
            self.log(f"トラック数: {len(self.copied_tracks)}")
            
            return str(playlist_path)
            
        except Exception as e:
            self.log(f"プレイリスト作成エラー: {e}")
            return None
        finally:
            if file_handle:
                file_handle.close()
    
    def create_itunes_playlist(self, playlist_name="iPod_music.txt"):
        """iTunesインポート用プレイリストを作成"""
        playlist_path = self.output_dir / playlist_name
        
        try:
            with open(playlist_path, 'w', encoding='utf-8') as f:
                for track in self.copied_tracks:
                    f.write(f"{track.output_path}\n")
                    
            self.log(f"iTunesプレイリスト作成完了: {playlist_path}")
            return str(playlist_path)
            
        except Exception as e:
            self.log(f"iTunesプレイリスト作成エラー: {e}")
            return None
    
    def get_summary(self):
        """抽出結果のサマリーを取得"""
        total_size = 0
        formats = {}
        
        for track in self.copied_tracks:
            # ファイルサイズ
            if os.path.exists(track.output_path):
                total_size += os.path.getsize(track.output_path)
            
            # フォーマット統計
            fmt = track.file_type.upper()
            formats[fmt] = formats.get(fmt, 0) + 1
        
        return {
            'total_tracks': len(self.copied_tracks),
            'total_size_mb': total_size / (1024 * 1024),
            'formats': formats
        }
    
    def cancel(self):
        """抽出を中断"""
        self.is_cancelled = True
        self.log("中断リクエストを受信しました...")
