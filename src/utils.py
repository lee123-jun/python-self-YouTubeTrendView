"""
유틸리티 함수 모듈
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional


def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """
    로깅 설정
    
    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 로그 파일 경로 (None이면 콘솔만 출력)
    
    Returns:
        설정된 로거
    """
    # 로거 생성
    logger = logging.getLogger('YouTubeTrendAnalyzer')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (옵션)
    if log_file:
        # 로그 디렉토리 생성
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def load_config(config_path: str = "config/config.json") -> Dict[str, Any]:
    """
    설정 파일 로드
    
    Args:
        config_path: 설정 파일 경로
    
    Returns:
        설정 딕셔너리
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 필수 설정값 검증
        required_keys = ['youtube_api_key']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"필수 설정값이 누락되었습니다: {key}")
        
        return config
        
    except FileNotFoundError:
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"설정 파일 형식이 올바르지 않습니다: {e}")


def save_config(config: Dict[str, Any], config_path: str = "config/config.json") -> None:
    """
    설정 파일 저장
    
    Args:
        config: 저장할 설정 딕셔너리
        config_path: 설정 파일 경로
    """
    try:
        # 디렉토리 생성
        config_dir = os.path.dirname(config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        raise Exception(f"설정 파일 저장 중 오류 발생: {e}")


def format_number(number: int) -> str:
    """
    숫자를 읽기 쉬운 형식으로 포맷
    
    Args:
        number: 포맷할 숫자
    
    Returns:
        포맷된 문자열 (예: 1,234,567 또는 1.2M)
    """
    if number >= 1000000000:  # 10억 이상
        return f"{number / 1000000000:.1f}B"
    elif number >= 1000000:  # 100만 이상
        return f"{number / 1000000:.1f}M"
    elif number >= 1000:  # 1000 이상
        return f"{number / 1000:.1f}K"
    else:
        return f"{number:,}"


def format_duration(seconds: int) -> str:
    """
    초를 시:분:초 형식으로 변환
    
    Args:
        seconds: 변환할 초
    
    Returns:
        HH:MM:SS 또는 MM:SS 형식 문자열
    """
    if seconds <= 0:
        return "00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    날짜 범위 유효성 검사
    
    Args:
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
    
    Returns:
        유효성 여부
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 시작일이 종료일보다 늦으면 안됨
        if start > end:
            return False
        
        # 미래 날짜는 안됨
        if end > datetime.now():
            return False
        
        return True
        
    except ValueError:
        return False


def create_output_filename(base_name: str, extension: str = ".csv") -> str:
    """
    출력 파일명 생성 (타임스탬프 포함)
    
    Args:
        base_name: 기본 파일명
        extension: 파일 확장자
    
    Returns:
        타임스탬프가 포함된 파일명
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"


def ensure_directory_exists(directory_path: str) -> None:
    """
    디렉토리가 존재하지 않으면 생성
    
    Args:
        directory_path: 생성할 디렉토리 경로
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def get_file_size_mb(file_path: str) -> float:
    """
    파일 크기를 MB 단위로 반환
    
    Args:
        file_path: 파일 경로
    
    Returns:
        파일 크기 (MB)
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except (OSError, FileNotFoundError):
        return 0.0


def clean_filename(filename: str) -> str:
    """
    파일명에서 불법 문자 제거
    
    Args:
        filename: 정리할 파일명
    
    Returns:
        정리된 파일명
    """
    # Windows에서 금지된 문자들
    forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    
    cleaned = filename
    for char in forbidden_chars:
        cleaned = cleaned.replace(char, '_')
    
    # 연속된 공백을 하나로
    cleaned = ' '.join(cleaned.split())
    
    # 파일명 길이 제한 (Windows 기준 255자)
    if len(cleaned) > 200:  # 확장자 여유분 고려
        cleaned = cleaned[:200] + "..."
    
    return cleaned.strip()


def calculate_engagement_rate(likes: int, views: int) -> float:
    """
    참여율 계산 (좋아요 / 조회수 * 100)
    
    Args:
        likes: 좋아요 수
        views: 조회수
    
    Returns:
        참여율 (%)
    """
    if views <= 0:
        return 0.0
    
    return (likes / views) * 100


def get_video_category(duration_seconds: int, tags: list) -> str:
    """
    영상 카테고리 분류
    
    Args:
        duration_seconds: 영상 길이 (초)
        tags: 태그 리스트
    
    Returns:
        카테고리 문자열
    """
    # 숏폼 체크
    if duration_seconds <= 60:
        return "숏폼"
    
    # 태그 기반 카테고리 분류
    if tags:
        tags_lower = [tag.lower() for tag in tags]
        
        music_keywords = ['music', '음악', 'song', 'cover', '노래']
        if any(keyword in ' '.join(tags_lower) for keyword in music_keywords):
            return "음악"
        
        game_keywords = ['game', '게임', 'gaming', 'play']
        if any(keyword in ' '.join(tags_lower) for keyword in game_keywords):
            return "게임"
        
        food_keywords = ['food', '음식', '먹방', 'eating', 'mukbang']
        if any(keyword in ' '.join(tags_lower) for keyword in food_keywords):
            return "음식"
        
        vlog_keywords = ['vlog', '브이로그', 'daily', '일상']
        if any(keyword in ' '.join(tags_lower) for keyword in vlog_keywords):
            return "브이로그"
    
    # 길이 기반 분류
    if duration_seconds <= 240:  # 4분 이하
        return "숏폼"
    elif duration_seconds <= 1200:  # 20분 이하
        return "미디엄폼"
    else:
        return "롱폼"


def export_search_history(search_data: list, filename: str = None) -> str:
    """
    검색 기록을 JSON 파일로 내보내기
    
    Args:
        search_data: 검색 데이터 리스트
        filename: 저장할 파일명
    
    Returns:
        저장된 파일 경로
    """
    if filename is None:
        filename = create_output_filename("search_history", ".json")
    
    ensure_directory_exists("output")
    filepath = os.path.join("output", filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(search_data, f, indent=2, ensure_ascii=False, default=str)
        
        return filepath
        
    except Exception as e:
        raise Exception(f"검색 기록 내보내기 중 오류 발생: {e}")


def import_search_history(filepath: str) -> list:
    """
    검색 기록을 JSON 파일에서 가져오기
    
    Args:
        filepath: JSON 파일 경로
    
    Returns:
        검색 데이터 리스트
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except Exception as e:
        raise Exception(f"검색 기록 가져오기 중 오류 발생: {e}")


# 전역 로거 인스턴스
logger = setup_logging("INFO")