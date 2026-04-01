#!/usr/bin/env python3
"""
エラーハンドリングと重複検出のテスト
"""

import os
import tempfile
from ipod_extractor import iPodExtractor
from ipod_parser import iPodTrack

def create_test_tracks():
    """テスト用のトラックデータを作成"""
    tracks = []
    
    # 通常のトラック
    track1 = iPodTrack({
        'id': 'test1',
        'title': 'Test Song 1',
        'artist': 'Test Artist',
        'album': 'Test Album',
        'genre': 'Pop',
        'duration': 180,
        'playcount': 0,
        'rating': 0,
        'file_type': 'mp3',
        'ipod_path': '/fake/path/test1.mp3'
    })
    tracks.append(track1)
    
    # 重複トラック（同じタイトル、アーティスト、アルバム）
    track2 = iPodTrack({
        'id': 'test2',
        'title': 'Test Song 1',  # 同じタイトル
        'artist': 'Test Artist',  # 同じアーティスト
        'album': 'Test Album',   # 同じアルバム
        'genre': 'Pop',
        'duration': 180,
        'playcount': 0,
        'rating': 0,
        'file_type': 'mp3',
        'ipod_path': '/fake/path/test2.mp3'
    })
    tracks.append(track2)
    
    # 異なるトラック（同じタイトルだけ）
    track3 = iPodTrack({
        'id': 'test3',
        'title': 'Test Song 1',  # 同じタイトル
        'artist': 'Different Artist',  # 異なるアーティスト
        'album': 'Test Album',
        'genre': 'Pop',
        'duration': 180,
        'playcount': 0,
        'rating': 0,
        'file_type': 'mp3',
        'ipod_path': '/fake/path/test3.mp3'
    })
    tracks.append(track3)
    
    return tracks

def test_duplicate_detection():
    """重複検出をテスト"""
    print("=== 重複検出テスト ===")
    
    # 一時的な出力ディレクトリを作成
    with tempfile.TemporaryDirectory() as temp_dir:
        extractor = iPodExtractor("/fake/ipod", temp_dir)
        
        # テストトラックを作成
        tracks = create_test_tracks()
        
        # 重複チェック
        for i, track in enumerate(tracks):
            is_duplicate = extractor.is_duplicate_track(track)
            status = "重複" if is_duplicate else "新規"
            print(f"  トラック{i+1}: {track.artist} - {track.title} -> {status}")

def test_error_handling():
    """エラーハンドリングをテスト"""
    print("\n=== エラーハンドリングテスト ===")
    
    # 存在しないファイルパスを持つトラック
    error_track = iPodTrack({
        'id': 'error1',
        'title': 'Error Test Song',
        'artist': 'Error Artist',
        'album': 'Error Album',
        'genre': 'Pop',
        'duration': 180,
        'playcount': 0,
        'rating': 0,
        'file_type': 'mp3',
        'ipod_path': '/nonexistent/path/error.mp3'
    })
    
    # 一時的な出力ディレクトリを作成
    with tempfile.TemporaryDirectory() as temp_dir:
        extractor = iPodExtractor("/fake/ipod", temp_dir)
        
        # リトライ機能をテスト
        print("  存在しないファイルのコピーをテスト...")
        result = extractor.copy_track_with_retry(error_track, 1)
        
        if not result:
            print("  ✓ エラー処理が正常に動作しました")
            if extractor.failed_tracks:
                print(f"  ✓ 失敗したトラックが記録されました: {extractor.failed_tracks[0]}")
        else:
            print("  ✗ エラー処理に問題があります")

def test_summary_output():
    """サマリー出力をテスト"""
    print("\n=== サマリー出力テスト ===")
    
    # 一時的な出力ディレクトリを作成
    with tempfile.TemporaryDirectory() as temp_dir:
        extractor = iPodExtractor("/fake/ipod", temp_dir)
        
        # テストデータを設定
        extractor.copied_tracks = create_test_tracks()[:2]  # 2曲成功
        extractor.failed_tracks = ["Test Artist - Error Song: File not found"]  # 1曲失敗
        
        # サマリーを表示
        print("  抽出結果サマリー:")
        print(f"    正常にコピー: {len(extractor.copied_tracks)}")
        print(f"    失敗したトラック: {len(extractor.failed_tracks)}")
        
        if extractor.failed_tracks:
            print("    失敗したトラック一覧:")
            for failed in extractor.failed_tracks:
                print(f"      - {failed}")

if __name__ == "__main__":
    test_duplicate_detection()
    test_error_handling() 
    test_summary_output()
    print("\n=== テスト完了 ===")
