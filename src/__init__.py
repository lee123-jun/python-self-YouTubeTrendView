"""
YouTube 트렌드 판별기

유튜브 API를 활용한 영상 데이터 수집 및 분석 도구
"""

__version__ = "1.0.0"
__author__ = "YouTube Trend Analyzer Team"
__description__ = "YouTube Data API를 활용한 트렌드 분석 프로그램"

# 메인 모듈들
from .youtube_api import YouTubeAPI
from .data_processor import DataProcessor

__all__ = [
    'YouTubeAPI',
    'DataProcessor',
]