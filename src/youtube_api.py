"""
YouTube Data API v3를 활용한 데이터 수집 모듈
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeAPI:
    """YouTube Data API v3 연동 클래스"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        YouTube API 클래스 초기화
        
        Args:
            config_path: 설정 파일 경로
        """
        self.config = self._load_config(config_path)
        self.api_key = self.config.get("youtube_api_key", "")
        self.youtube = None
        
        if not self.api_key or self.api_key == "YOUR_YOUTUBE_API_KEY_HERE":
            print("⚠️ YouTube API 키가 설정되지 않았습니다. GUI에서 API 키를 설정해주세요.")
            # API 키가 없어도 프로그램은 계속 실행되도록 함
        else:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                print("✅ YouTube API가 성공적으로 초기화되었습니다.")
            except Exception as e:
                print(f"❌ YouTube API 초기화 실패: {e}")
                self.youtube = None
    
    def _load_config(self, config_path: str) -> Dict:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"설정 파일 형식이 올바르지 않습니다: {config_path}")
    
    def search_videos(self, 
                     query: str,
                     max_results: int = 50,
                     published_after: Optional[str] = None,
                     published_before: Optional[str] = None,
                     video_duration: str = "any",
                     order: str = "relevance",
                     region_code: Optional[str] = None,
                     age_group: str = "전체") -> List[Dict]:
        """
        YouTube 영상 검색
        
        Args:
            query: 검색어
            max_results: 최대 결과 수 (1-100)
            published_after: 검색 시작일 (YYYY-MM-DD 형식)
            published_before: 검색 종료일 (YYYY-MM-DD 형식)
            video_duration: 영상 길이 ('short', 'medium', 'long', 'any')
            order: 정렬 방식 ('relevance', 'date', 'rating', 'viewCount', 'title')
            region_code: 국가 코드 (예: 'KR', 'US', 'JP' 등)
            age_group: 연령층 필터
        
        Returns:
            검색된 영상 정보 리스트
        """
        # API 키가 설정되지 않은 경우
        if not self.youtube or not self.api_key:
            raise ValueError("YouTube API 키가 설정되지 않았습니다. 먼저 API 키를 설정해주세요.")
        
        try:
            all_videos = []
            next_page_token = None
            per_page_limit = 50  # YouTube API 제한: 한 번에 최대 50개
            
            # 연령층에 따른 safe search 설정
            safe_search = self._get_safe_search_for_age(age_group)
            
            # 검색어에 연령층 키워드 추가
            enhanced_query = self._enhance_query_for_age(query, age_group)
            
            while len(all_videos) < max_results:
                # 이번 요청에서 가져올 결과 수
                remaining = max_results - len(all_videos)
                current_max = min(per_page_limit, remaining)
                
                # 검색 매개변수 설정
                search_params = {
                    'part': 'id,snippet',
                    'q': enhanced_query,
                    'type': 'video',
                    'maxResults': current_max,
                    'order': order,
                    'videoDuration': video_duration,
                    'safeSearch': safe_search
                }
                
                # 페이지 토큰 추가 (두 번째 페이지부터)
                if next_page_token:
                    search_params['pageToken'] = next_page_token
                
                # 국가 코드 추가 (선택된 경우)
                if region_code:
                    search_params['regionCode'] = region_code
                
                # 날짜 필터 추가
                if published_after:
                    search_params['publishedAfter'] = self._format_date_for_api(published_after)
                if published_before:
                    search_params['publishedBefore'] = self._format_date_for_api(published_before)
                
                # API 호출
                search_response = self.youtube.search().list(**search_params).execute()
                
                if 'items' not in search_response or not search_response['items']:
                    break
                
                video_ids = []
                video_info = []
                
                # 비디오 ID 수집
                for item in search_response['items']:
                    video_ids.append(item['id']['videoId'])
                    video_info.append({
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt'],
                        'channel_title': item['snippet']['channelTitle'],
                        'thumbnail_url': item['snippet']['thumbnails']['default']['url']
                    })
                
                # 상세 정보 가져오기 (조회수, 좋아요 등)
                if video_ids:
                    detailed_info = self._get_video_details(video_ids)
                    
                    # 정보 병합
                    for i, video in enumerate(video_info):
                        if i < len(detailed_info):
                            video.update(detailed_info[i])
                
                all_videos.extend(video_info)
                
                # 다음 페이지 토큰 확인
                next_page_token = search_response.get('nextPageToken')
                if not next_page_token:
                    break
            
            # 연령층 필터링 (키워드 기반 후처리)
            filtered_videos = self._filter_videos_by_age(all_videos, age_group)
            
            return filtered_videos[:max_results]
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            raise Exception(f"YouTube API 오류: {error_details['error']['message']}")
        except Exception as e:
            raise Exception(f"영상 검색 중 오류 발생: {str(e)}")
    
    def _get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """
        영상 상세 정보 가져오기 (조회수, 좋아요, 댓글 수 등)
        
        Args:
            video_ids: 영상 ID 리스트
        
        Returns:
            영상 상세 정보 리스트
        """
        try:
            # 한 번에 최대 50개까지 처리 가능
            video_details = []
            
            for i in range(0, len(video_ids), 50):
                batch_ids = video_ids[i:i+50]
                
                details_response = self.youtube.videos().list(
                    part='statistics,contentDetails,snippet',
                    id=','.join(batch_ids)
                ).execute()
                
                for item in details_response['items']:
                    stats = item['statistics']
                    content_details = item['contentDetails']
                    snippet = item['snippet']
                    
                    detail_info = {
                        'view_count': int(stats.get('viewCount', 0)),
                        'like_count': int(stats.get('likeCount', 0)),
                        'comment_count': int(stats.get('commentCount', 0)),
                        'duration': content_details.get('duration', ''),
                        'tags': snippet.get('tags', [])
                    }
                    
                    video_details.append(detail_info)
            
            return video_details
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            raise Exception(f"YouTube API 상세정보 오류: {error_details['error']['message']}")
        except Exception as e:
            raise Exception(f"영상 상세정보 조회 중 오류 발생: {str(e)}")
    
    def _format_date_for_api(self, date_str: str) -> str:
        """
        날짜를 API 형식으로 변환
        
        Args:
            date_str: YYYY-MM-DD 형식의 날짜 문자열
        
        Returns:
            RFC 3339 형식의 날짜 문자열
        """
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%Y-%m-%dT00:00:00Z')
        except ValueError:
            raise ValueError(f"날짜 형식이 올바르지 않습니다: {date_str} (YYYY-MM-DD 형식이어야 함)")
    
    def get_trending_videos(self, region_code: str = "KR", max_results: int = 50) -> List[Dict]:
        """
        인기 급상승 영상 가져오기
        
        Args:
            region_code: 지역 코드 (KR, US 등)
            max_results: 최대 결과 수
        
        Returns:
            인기 급상승 영상 정보 리스트
        """
        # API 키가 설정되지 않은 경우
        if not self.youtube or not self.api_key:
            raise ValueError("YouTube API 키가 설정되지 않았습니다. 먼저 API 키를 설정해주세요.")
        
        try:
            trending_response = self.youtube.videos().list(
                part='id,snippet,statistics,contentDetails',
                chart='mostPopular',
                regionCode=region_code,
                maxResults=min(max_results, 50)
            ).execute()
            
            trending_videos = []
            
            for item in trending_response['items']:
                stats = item['statistics']
                snippet = item['snippet']
                content_details = item['contentDetails']
                
                video_info = {
                    'video_id': item['id'],
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'published_at': snippet['publishedAt'],
                    'channel_title': snippet['channelTitle'],
                    'thumbnail_url': snippet['thumbnails']['default']['url'],
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'comment_count': int(stats.get('commentCount', 0)),
                    'duration': content_details.get('duration', ''),
                    'tags': snippet.get('tags', [])
                }
                
                trending_videos.append(video_info)
            
            return trending_videos
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            raise Exception(f"YouTube API 트렌딩 오류: {error_details['error']['message']}")
        except Exception as e:
            raise Exception(f"트렌딩 영상 조회 중 오류 발생: {str(e)}")
    
    def parse_duration(self, duration: str) -> int:
        """
        YouTube API duration을 초 단위로 변환
        
        Args:
            duration: PT#M#S 형식의 duration 문자열
        
        Returns:
            총 초 수
        """
        import re
        
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def is_short_form(self, duration: str) -> bool:
        """
        숏폼 영상인지 확인 (60초 이하)
        
        Args:
            duration: PT#M#S 형식의 duration 문자열
        
        Returns:
            숏폼 여부
        """
        return self.parse_duration(duration) <= 60
    
    def format_duration(self, duration: str) -> str:
        """
        Duration을 사람이 읽기 쉬운 형식으로 변환
        
        Args:
            duration: PT#M#S 형식의 duration 문자열
        
        Returns:
            HH:MM:SS 또는 MM:SS 형식의 문자열
        """
        total_seconds = self.parse_duration(duration)
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def _get_safe_search_for_age(self, age_group: str) -> str:
        """연령층에 따른 safe search 설정"""
        if age_group in ["어린이 (7세 이하)", "청소년 (8-17세)"]:
            return "strict"
        elif age_group == "청년 (18-24세)":
            return "moderate"
        else:
            return "none"
    
    def _enhance_query_for_age(self, query: str, age_group: str) -> str:
        """연령층에 맞는 검색어 향상"""
        age_keywords = {
            "어린이 (7세 이하)": ["어린이", "키즈", "유아", "아이", "동화"],
            "청소년 (8-17세)": ["청소년", "학생", "10대", "중학생", "고등학생"],
            "청년 (18-24세)": ["대학생", "청년", "20대", "취업", "연애"],
            "성인 (25-34세)": ["직장", "회사원", "30대", "결혼", "육아"],
            "중년 (35-54세)": ["중년", "40대", "50대", "가족", "자녀교육"],
            "장년 (55세 이상)": ["시니어", "은퇴", "건강", "노년", "실버"]
        }
        
        if age_group != "전체" and age_group in age_keywords:
            # 원본 쿼리에 연령층 키워드를 자연스럽게 추가
            keywords = age_keywords[age_group]
            # 첫 번째 키워드만 추가하여 검색 결과를 너무 제한하지 않음
            return f"{query} {keywords[0]}"
        
        return query
    
    def _filter_videos_by_age(self, videos: List[Dict], age_group: str) -> List[Dict]:
        """연령층에 따른 비디오 필터링 (후처리)"""
        if age_group == "전체":
            return videos
        
        age_filter_keywords = {
            "어린이 (7세 이하)": {
                "include": ["어린이", "키즈", "유아", "아이", "동화", "만화", "애니메이션", "놀이"],
                "exclude": ["성인", "19금", "술", "담배", "폭력"]
            },
            "청소년 (8-17세)": {
                "include": ["청소년", "학생", "10대", "중학교", "고등학교", "공부", "게임"],
                "exclude": ["성인", "19금", "술", "담배"]
            },
            "청년 (18-24세)": {
                "include": ["대학생", "청년", "20대", "취업", "연애", "패션", "뷰티"],
                "exclude": ["어린이", "키즈"]
            },
            "성인 (25-34세)": {
                "include": ["직장", "회사원", "30대", "결혼", "육아", "부동산", "투자"],
                "exclude": ["어린이", "키즈"]
            },
            "중년 (35-54세)": {
                "include": ["중년", "40대", "50대", "가족", "자녀교육", "건강", "재테크"],
                "exclude": ["어린이", "키즈", "10대"]
            },
            "장년 (55세 이상)": {
                "include": ["시니어", "은퇴", "건강", "노년", "실버", "운동", "여행"],
                "exclude": ["어린이", "키즈", "10대", "20대"]
            }
        }
        
        if age_group not in age_filter_keywords:
            return videos
        
        filter_config = age_filter_keywords[age_group]
        include_keywords = filter_config["include"]
        exclude_keywords = filter_config["exclude"]
        
        filtered_videos = []
        for video in videos:
            title = video.get('title', '').lower()
            description = video.get('description', '').lower()
            content = f"{title} {description}"
            
            # 제외 키워드 확인
            if any(keyword in content for keyword in exclude_keywords):
                continue
            
            # 포함 키워드 확인 (너무 엄격하지 않게)
            if any(keyword in content for keyword in include_keywords) or len(include_keywords) == 0:
                filtered_videos.append(video)
            else:
                # 키워드가 없어도 안전한 콘텐츠라면 포함
                filtered_videos.append(video)
        
        return filtered_videos