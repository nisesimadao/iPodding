#!/usr/bin/env python3
"""
iPod iTunesDBパーサー
ファイルシステムベースでiPodの音楽ファイルを直接読み込む
"""

import os
import mutagen

class iPodTrack:
    def __init__(self, track_data):
        self.id = track_data.get('id', 0)
        self.title = track_data.get('title', 'Unknown')
        self.artist = track_data.get('artist', 'Unknown Artist')
        self.album = track_data.get('album', 'Unknown Album')
        self.genre = track_data.get('genre', 'Unknown')
        self.duration = track_data.get('duration', 0)
        self.play_count = track_data.get('playcount', 0)
        self.rating = track_data.get('rating', 0)
        self.file_type = track_data.get('file_type', '')
        self.path = track_data.get('ipod_path', '')

class iPodDatabase:
    def __init__(self, ipod_path):
        self.ipod_path = ipod_path
        self.itunes_path = os.path.join(ipod_path, "iPod_Control", "iTunes")
        self.music_path = os.path.join(ipod_path, "iPod_Control", "Music")
        self.tracks = []
        self.progress_callback = None
        self.cancel_check = None
        
    def load_database(self, progress_callback=None, cancel_check=None):
        """iPodの音楽ファイルを読み込む"""
        self.progress_callback = progress_callback
        self.cancel_check = cancel_check
        
        if not os.path.exists(self.music_path):
            raise FileNotFoundError(f"音楽フォルダが見つかりません: {self.music_path}")
        
        try:
            self.load_tracks_from_filesystem()
            return True
            
        except Exception as e:
            print(f"トラック読み込みエラー: {e}")
            return False
    
    def extract_metadata(self, file_path):
        """オーディオファイルからメタデータを抽出"""
        try:
            # macOSの隠しファイルをスキップ
            if os.path.basename(file_path).startswith('._'):
                return None
                
            audio = mutagen.File(file_path)
            if audio is None:
                return None
            
            # 共通のメタデータを取得
            title = "Unknown"
            artist = "Unknown Artist"
            album = "Unknown Album"
            genre = "Unknown"
            duration = 0
            
            if hasattr(audio, 'tags') and audio.tags:
                # M4A/AACの場合
                if hasattr(audio.tags, 'get'):
                    title = self._safe_get_tag(audio.tags, '\xa9nam', 'Unknown')
                    artist = self._safe_get_tag(audio.tags, '\xa9ART', 'Unknown Artist')
                    album = self._safe_get_tag(audio.tags, '\xa9alb', 'Unknown Album')
                    genre = self._safe_get_tag(audio.tags, '\xa9gen', 'Unknown')
                else:
                    # MP3の場合
                    title = self._safe_get_tag(audio.tags, 'TIT2', 'Unknown')
                    artist = self._safe_get_tag(audio.tags, 'TPE1', 'Unknown Artist')
                    album = self._safe_get_tag(audio.tags, 'TALB', 'Unknown Album')
                    genre = self._safe_get_tag(audio.tags, 'TCON', 'Unknown')
            
            if hasattr(audio, 'info'):
                duration = getattr(audio.info, 'length', 0)
            
            # ファイル名からIDを生成
            file_id = os.path.basename(file_path).split('.')[0]
            
            return {
                'id': file_id,
                'title': title,
                'artist': artist,
                'album': album,
                'genre': genre,
                'duration': duration,
                'playcount': 0,
                'rating': 0,
                'file_type': os.path.splitext(file_path)[1][1:],
                'ipod_path': file_path
            }
        except Exception as e:
            # エラーを表示して処理を継続
            print(f"メタデータ抽出エラー {os.path.basename(file_path)}: {e}")
            return None
    
    def _safe_get_tag(self, tags, tag_key, default_value):
        """安全なタグ取得"""
        try:
            tag_value = tags.get(tag_key, [default_value])
            if tag_value and len(tag_value) > 0:
                return str(tag_value[0])
            return default_value
        except (IndexError, AttributeError, TypeError):
            return default_value
    
    def load_tracks_from_filesystem(self):
        """ファイルシステムからトラック情報を取得"""
        if not os.path.exists(self.music_path):
            print(f"音楽フォルダが見つかりません: {self.music_path}")
            return
        
        # すべてのフォルダをスキャン
        folders = [f for f in os.listdir(self.music_path) if os.path.isdir(os.path.join(self.music_path, f))]
        msg = f"スキャン中: {len(folders)} フォルダ..."
        if self.progress_callback:
            self.progress_callback(0, len(folders), msg)
        else:
            print(msg)
        
        total_files = 0
        for i, folder in enumerate(folders):
            # 中断チェック
            if self.cancel_check and self.cancel_check():
                return
                
            folder_path = os.path.join(self.music_path, folder)
            files = os.listdir(folder_path)
            for file in files:
                if file.endswith(('.mp3', '.m4a', '.wav', '.aac')) and not file.startswith('._'):
                    file_path = os.path.join(folder_path, file)
                    track_data = self.extract_metadata(file_path)
                    if track_data:
                        self.tracks.append(iPodTrack(track_data))
                        total_files += 1
            
            # 進捗表示
            progress_pct = ((i + 1) / len(folders)) * 100
            msg = f"進捗: {progress_pct:.1f}% - 処理中: {i+1}/{len(folders)} フォルダ完了"
            if self.progress_callback:
                self.progress_callback(i + 1, len(folders), msg)
            else:
                print(f"\r{msg}", end="", flush=True)
        
        final_msg = f"合計 {total_files} 件の音楽ファイルを検出しました"
        if self.progress_callback:
            self.progress_callback(len(folders), len(folders), final_msg)
        else:
            print(f"\n{final_msg}")
    
    def get_tracks(self):
        """すべてのトラックを取得"""
        return self.tracks
    
    def get_music_tracks(self):
        """音楽トラックのみを取得"""
        return [track for track in self.tracks 
                if track.genre.lower() not in ['podcast', 'ポッドキャスト']]
    
    def get_podcast_tracks(self):
        """ポッドキャストトラックのみを取得"""
        return [track for track in self.tracks 
                if track.genre.lower() in ['podcast', 'ポッドキャスト']]
