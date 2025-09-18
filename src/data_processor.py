"""
YouTube 데이터 처리 및 분석 모듈
"""

import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Optional, Any
import os


class DataProcessor:
    """YouTube 데이터 처리 클래스"""
    
    def __init__(self):
        """데이터 처리 클래스 초기화"""
        self.df = None
    
    def process_youtube_data(self, video_data: List[Dict]) -> pd.DataFrame:
        """
        YouTube API에서 받은 데이터를 DataFrame으로 변환
        
        Args:
            video_data: YouTube API에서 받은 영상 데이터 리스트
        
        Returns:
            처리된 DataFrame
        """
        if not video_data:
            return pd.DataFrame()
        
        processed_data = []
        
        for video in video_data:
            # 기본 정보 추출
            processed_video = {
                'video_id': video.get('video_id', ''),
                'title': self._clean_text(video.get('title', '')),
                'channel_title': self._clean_text(video.get('channel_title', '')),
                'published_at': self._parse_published_date(video.get('published_at', '')),
                'view_count': video.get('view_count', 0),
                'like_count': video.get('like_count', 0),
                'comment_count': video.get('comment_count', 0),
                'duration_seconds': self._parse_duration_to_seconds(video.get('duration', '')),
                'duration_formatted': self._format_duration(video.get('duration', '')),
                'is_short_form': self._is_short_form(video.get('duration', '')),
                'tags': self._format_tags(video.get('tags', [])),
                'tags_count': len(video.get('tags', [])),
                'description_length': len(video.get('description', '')),
                'thumbnail_url': video.get('thumbnail_url', ''),
                'video_url': f"https://www.youtube.com/watch?v={video.get('video_id', '')}"
            }
            
            # 추가 분석 지표 계산
            processed_video.update(self._calculate_engagement_metrics(processed_video))
            
            processed_data.append(processed_video)
        
        # DataFrame 생성
        self.df = pd.DataFrame(processed_data)
        
        # 데이터 타입 최적화
        self._optimize_dtypes()
        
        return self.df
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정리 (특수문자 제거 등)"""
        if not isinstance(text, str):
            return ""
        
        # HTML 엔티티 디코딩
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&quot;', '"').replace('&#39;', "'")
        
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _parse_published_date(self, date_str: str) -> Optional[datetime]:
        """게시일 파싱"""
        if not date_str:
            return None
        
        try:
            # ISO 8601 형식 파싱
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                # 대체 형식 시도
                return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                return None
    
    def _parse_duration_to_seconds(self, duration: str) -> int:
        """YouTube duration을 초 단위로 변환"""
        if not duration:
            return 0
        
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def _format_duration(self, duration: str) -> str:
        """Duration을 읽기 쉬운 형식으로 변환"""
        total_seconds = self._parse_duration_to_seconds(duration)
        
        if total_seconds == 0:
            return "00:00"
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def _is_short_form(self, duration: str) -> bool:
        """숏폼 영상 여부 확인 (60초 이하)"""
        return self._parse_duration_to_seconds(duration) <= 60
    
    def _format_tags(self, tags: List[str]) -> str:
        """태그 리스트를 문자열로 변환"""
        if not tags:
            return ""
        
        # 태그 개수 제한 (처음 10개만)
        limited_tags = tags[:10]
        return ", ".join(limited_tags)
    
    def _calculate_engagement_metrics(self, video_data: Dict) -> Dict:
        """참여도 지표 계산"""
        view_count = video_data.get('view_count', 0)
        like_count = video_data.get('like_count', 0)
        comment_count = video_data.get('comment_count', 0)
        
        metrics = {}
        
        # 조회수 대비 좋아요 비율 (%)
        if view_count > 0:
            metrics['like_rate'] = round((like_count / view_count) * 100, 3)
        else:
            metrics['like_rate'] = 0.0
        
        # 조회수 대비 댓글 비율 (%)
        if view_count > 0:
            metrics['comment_rate'] = round((comment_count / view_count) * 100, 3)
        else:
            metrics['comment_rate'] = 0.0
        
        # 참여도 점수 (좋아요 + 댓글 수)
        metrics['engagement_score'] = like_count + comment_count
        
        # 조회수 등급
        metrics['view_tier'] = self._get_view_tier(view_count)
        
        return metrics
    
    def _get_view_tier(self, view_count: int) -> str:
        """조회수 기반 등급 분류"""
        if view_count >= 10000000:  # 1천만 이상
            return "메가히트"
        elif view_count >= 1000000:  # 100만 이상
            return "히트"
        elif view_count >= 100000:  # 10만 이상
            return "인기"
        elif view_count >= 10000:  # 1만 이상
            return "보통"
        else:
            return "신규"
    
    def _optimize_dtypes(self):
        """DataFrame 데이터 타입 최적화"""
        if self.df is None or self.df.empty:
            return
        
        # 정수형 최적화
        int_columns = ['view_count', 'like_count', 'comment_count', 
                      'duration_seconds', 'tags_count', 'description_length', 'engagement_score']
        
        for col in int_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0).astype('int64')
        
        # 실수형 최적화
        float_columns = ['like_rate', 'comment_rate']
        for col in float_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0.0).astype('float64')
        
        # 범주형 최적화
        category_columns = ['view_tier']
        for col in category_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype('category')
    
    def sort_data(self, column: str, ascending: bool = True) -> pd.DataFrame:
        """
        데이터 정렬
        
        Args:
            column: 정렬할 컬럼명
            ascending: 오름차순 여부
        
        Returns:
            정렬된 DataFrame
        """
        if self.df is None or self.df.empty:
            return pd.DataFrame()
        
        if column not in self.df.columns:
            raise ValueError(f"컬럼 '{column}'이 존재하지 않습니다.")
        
        self.df = self.df.sort_values(by=column, ascending=ascending).reset_index(drop=True)
        return self.df
    
    def filter_data(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        데이터 필터링
        
        Args:
            filters: 필터 조건 딕셔너리
                - keyword: 제목에서 검색할 키워드
                - min_views: 최소 조회수
                - max_views: 최대 조회수
                - min_likes: 최소 좋아요
                - max_likes: 최대 좋아요
                - short_form_only: 숏폼만 보기
                - long_form_only: 롱폼만 보기
                - date_from: 시작 날짜
                - date_to: 종료 날짜
        
        Returns:
            필터링된 DataFrame
        """
        if self.df is None or self.df.empty:
            return pd.DataFrame()
        
        filtered_df = self.df.copy()
        
        # 키워드 필터
        if filters.get('keyword'):
            keyword = filters['keyword'].lower()
            filtered_df = filtered_df[
                filtered_df['title'].str.lower().str.contains(keyword, na=False) |
                filtered_df['tags'].str.lower().str.contains(keyword, na=False)
            ]
        
        # 조회수 필터
        if filters.get('min_views') is not None:
            filtered_df = filtered_df[filtered_df['view_count'] >= filters['min_views']]
        if filters.get('max_views') is not None:
            filtered_df = filtered_df[filtered_df['view_count'] <= filters['max_views']]
        
        # 좋아요 필터
        if filters.get('min_likes') is not None:
            filtered_df = filtered_df[filtered_df['like_count'] >= filters['min_likes']]
        if filters.get('max_likes') is not None:
            filtered_df = filtered_df[filtered_df['like_count'] <= filters['max_likes']]
        
        # 영상 길이 필터
        if filters.get('short_form_only'):
            filtered_df = filtered_df[filtered_df['is_short_form'] == True]
        elif filters.get('long_form_only'):
            filtered_df = filtered_df[filtered_df['is_short_form'] == False]
        
        # 날짜 필터
        if filters.get('date_from') and 'published_at' in filtered_df.columns:
            date_from = pd.to_datetime(filters['date_from'])
            filtered_df = filtered_df[filtered_df['published_at'] >= date_from]
        if filters.get('date_to') and 'published_at' in filtered_df.columns:
            date_to = pd.to_datetime(filters['date_to'])
            filtered_df = filtered_df[filtered_df['published_at'] <= date_to]
        
        return filtered_df.reset_index(drop=True)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """데이터 요약 통계"""
        if self.df is None or self.df.empty:
            return {}
        
        stats = {
            'total_videos': len(self.df),
            'short_form_count': self.df['is_short_form'].sum(),
            'long_form_count': len(self.df) - self.df['is_short_form'].sum(),
            'avg_views': self.df['view_count'].mean(),
            'median_views': self.df['view_count'].median(),
            'max_views': self.df['view_count'].max(),
            'min_views': self.df['view_count'].min(),
            'avg_likes': self.df['like_count'].mean(),
            'avg_comments': self.df['comment_count'].mean(),
            'avg_like_rate': self.df['like_rate'].mean(),
            'avg_comment_rate': self.df['comment_rate'].mean(),
            'avg_duration': self.df['duration_seconds'].mean()
        }
        
        # 수치 반올림
        for key, value in stats.items():
            if isinstance(value, float):
                stats[key] = round(value, 2)
        
        return stats
    
    def export_to_csv(self, filename: str = None) -> str:
        """
        CSV 파일로 내보내기
        
        Args:
            filename: 저장할 파일명 (None이면 자동 생성)
        
        Returns:
            저장된 파일 경로
        """
        if self.df is None or self.df.empty:
            raise ValueError("내보낼 데이터가 없습니다.")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_data_{timestamp}.csv"
        
        # output 디렉토리 확인
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filepath = os.path.join(output_dir, filename)
        
        # UTF-8 BOM으로 저장 (엑셀에서 한글 깨짐 방지)
        self.df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    def export_to_excel(self, filename: str = None) -> str:
        """
        Excel 파일로 내보내기
        
        Args:
            filename: 저장할 파일명 (None이면 자동 생성)
        
        Returns:
            저장된 파일 경로
        """
        if self.df is None or self.df.empty:
            raise ValueError("내보낼 데이터가 없습니다.")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_data_{timestamp}.xlsx"
        
        # output 디렉토리 확인
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filepath = os.path.join(output_dir, filename)
        
        # Excel 파일로 저장
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # 메인 데이터
            self.df.to_excel(writer, sheet_name='YouTube_Data', index=False)
            
            # 요약 통계
            stats_df = pd.DataFrame(list(self.get_summary_stats().items()), 
                                  columns=['항목', '값'])
            stats_df.to_excel(writer, sheet_name='Summary_Stats', index=False)
        
        return filepath
    
    def get_top_performers(self, metric: str = 'view_count', top_n: int = 10) -> pd.DataFrame:
        """
        상위 성과 영상 추출
        
        Args:
            metric: 기준 지표 (view_count, like_count, comment_count, engagement_score 등)
            top_n: 상위 n개
        
        Returns:
            상위 성과 영상 DataFrame
        """
        if self.df is None or self.df.empty:
            return pd.DataFrame()
        
        if metric not in self.df.columns:
            raise ValueError(f"지표 '{metric}'이 존재하지 않습니다.")
        
        return self.df.nlargest(top_n, metric).reset_index(drop=True)