import os
import platform
import string

class iPodManager:
    def __init__(self):
        self.ipod_path = None
    
    def detect_ipod(self):
        """接続されているiPodを検出"""
        try:
            system = platform.system()
            possible_paths = []
            
            if system == "Darwin": # macOS
                possible_paths = ["/Volumes/iPod", "/Volumes/iPod touch", "/Volumes/iPhone"]
                volumes_path = "/Volumes"
                if os.path.exists(volumes_path):
                    for item in os.listdir(volumes_path):
                        possible_paths.append(os.path.join(volumes_path, item))
                        
            elif system == "Windows": # Windows
                # AからZまでのドライブをチェック
                drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
                possible_paths = drives
                
            else: # Linux etc.
                possible_paths = ["/media/iPod", "/mnt/iPod"]
                try:
                    user_media = f"/media/{os.getlogin()}"
                    if os.path.exists(user_media):
                        for item in os.listdir(user_media):
                            possible_paths.append(os.path.join(user_media, item))
                except:
                    pass

            for path in possible_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    # iPodかどうかを確認するための隠しフォルダをチェック
                    itunes_path = os.path.join(path, "iPod_Control", "iTunes")
                    if os.path.exists(itunes_path):
                        return path
            
            return None
        except Exception as e:
            print(f"iPod検出エラー: {e}")
            return None

def open_folder(path):
    """OS標準の方法でフォルダを開く"""
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            import subprocess
            subprocess.run(["open", path])
        else:
            import subprocess
            subprocess.run(["xdg-open", path])
        return True
    except Exception as e:
        print(f"フォルダ起動エラー: {e}")
        return False
