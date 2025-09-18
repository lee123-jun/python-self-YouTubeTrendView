"""
YouTube 트렌드 기초 통계 분석 모듈
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import warnings

warnings.filterwarnings('ignore')


class StatisticalAnalyzer:
    """YouTube 데이터 기초 통계 분석 클래스"""
    
    def __init__(self):
        """통계 분석기 초기화"""
        self.setup_korean_font()
        self.data = None
        self.processed_data = None
    
    def setup_korean_font(self):
        """한글 폰트 설정"""
        try:
            # Windows의 경우 맑은 고딕 사용
            font_path = 'C:/Windows/Fonts/malgun.ttf'
            if os.path.exists(font_path):
                font_prop = fm.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = font_prop.get_name()
            else:
                # 다른 한글 폰트 시도
                plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Gulim']
            
            plt.rcParams['axes.unicode_minus'] = False
        except Exception as e:
            print(f"한글 폰트 설정 실패: {e}")
            plt.rcParams['font.family'] = ['DejaVu Sans']
    
    def load_data(self, video_data: List[Dict]) -> pd.DataFrame:
        """
        YouTube 데이터를 pandas DataFrame으로 변환
        
        Args:
            video_data: YouTube API에서 가져온 비디오 데이터 리스트
        
        Returns:
            처리된 pandas DataFrame
        """
        try:
            # DataFrame 생성
            df = pd.DataFrame(video_data)
            
            # 필수 컬럼 확인 및 생성
            required_columns = ['view_count', 'like_count', 'comment_count', 'published_at']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = 0
            
            # 데이터 타입 변환
            df['view_count'] = pd.to_numeric(df['view_count'], errors='coerce').fillna(0)
            df['like_count'] = pd.to_numeric(df['like_count'], errors='coerce').fillna(0)
            df['comment_count'] = pd.to_numeric(df['comment_count'], errors='coerce').fillna(0)
            
            # 날짜 컬럼 처리
            df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce', utc=True)
            current_time = pd.Timestamp.now(tz='UTC')
            df['days_since_published'] = (current_time - df['published_at']).dt.days
            
            # 추가 지표 계산
            df['engagement_rate'] = (df['like_count'] + df['comment_count']) / df['view_count'].replace(0, 1)
            df['like_rate'] = df['like_count'] / df['view_count'].replace(0, 1)
            df['comment_rate'] = df['comment_count'] / df['view_count'].replace(0, 1)
            
            # 영상 길이 처리 (duration이 있는 경우)
            if 'duration' in df.columns:
                df['duration_seconds'] = df['duration'].apply(self._parse_duration)
            
            self.data = df
            return df
            
        except Exception as e:
            raise Exception(f"데이터 로딩 중 오류: {str(e)}")
    
    def _parse_duration(self, duration_str: str) -> int:
        """ISO 8601 duration을 초로 변환"""
        if pd.isna(duration_str) or not duration_str:
            return 0
        
        try:
            # PT1H2M30S 형태의 문자열 파싱
            duration_str = duration_str.replace('PT', '')
            
            hours = 0
            minutes = 0
            seconds = 0
            
            if 'H' in duration_str:
                hours = int(duration_str.split('H')[0])
                duration_str = duration_str.split('H')[1]
            
            if 'M' in duration_str:
                minutes = int(duration_str.split('M')[0])
                duration_str = duration_str.split('M')[1]
            
            if 'S' in duration_str:
                seconds = int(duration_str.split('S')[0])
            
            return hours * 3600 + minutes * 60 + seconds
            
        except:
            return 0
    
    def generate_comprehensive_report(self, video_data: List[Dict]) -> Dict[str, Any]:
        """
        종합 기초 통계 분석 리포트 생성
        
        Args:
            video_data: YouTube API에서 가져온 비디오 데이터 리스트
        
        Returns:
            종합 분석 결과
        """
        try:
            # 데이터 로드
            self.data = self.load_data(video_data)
            
            if self.data.empty:
                return {"error": "분석할 데이터가 없습니다."}
            
            # 기초 통계 분석 실행
            report = {
                "basic_stats": self.basic_statistics(),
                "correlation_analysis": self.correlation_analysis(),
                "group_comparison": self.group_comparison_analysis(),
                "top_analysis": self.top_performance_analysis(),
                "summary": self.generate_summary()
            }
            
            return report
            
        except Exception as e:
            return {"error": f"분석 중 오류 발생: {str(e)}"}
    
    def basic_statistics(self) -> Dict[str, Any]:
        """기본 통계 정보"""
        try:
            stats = {}
            
            numeric_columns = ['view_count', 'like_count', 'comment_count', 'engagement_rate']
            
            for col in numeric_columns:
                if col in self.data.columns:
                    stats[col] = {
                        'mean': float(self.data[col].mean()),
                        'median': float(self.data[col].median()),
                        'std': float(self.data[col].std()),
                        'min': float(self.data[col].min()),
                        'max': float(self.data[col].max())
                    }
            
            return stats
            
        except Exception as e:
            return {"error": f"기본 통계 계산 중 오류: {str(e)}"}
    
    def correlation_analysis(self) -> Dict[str, Any]:
        """
        상관분석 - 주요 지표 간의 관계 분석
        
        Returns:
            상관분석 결과
        """
        try:
            results = {}
            
            # 주요 컬럼들 간 상관분석
            numeric_columns = ['view_count', 'like_count', 'comment_count', 'duration_seconds']
            available_columns = [col for col in numeric_columns if col in self.data.columns]
            
            if len(available_columns) < 2:
                return {"error": "상관분석을 위한 충분한 데이터가 없습니다."}
            
            # 상관계수 계산
            correlation_matrix = self.data[available_columns].corr()
            
            # 주요 상관관계 해석
            correlations = {}
            
            if 'view_count' in available_columns and 'like_count' in available_columns:
                corr_val = correlation_matrix.loc['view_count', 'like_count']
                correlations['조회수_좋아요'] = {
                    'correlation': float(corr_val),
                    'strength': self._interpret_correlation(corr_val),
                    'interpretation': self._get_correlation_interpretation('조회수', '좋아요', corr_val)
                }
            
            if 'view_count' in available_columns and 'comment_count' in available_columns:
                corr_val = correlation_matrix.loc['view_count', 'comment_count']
                correlations['조회수_댓글수'] = {
                    'correlation': float(corr_val),
                    'strength': self._interpret_correlation(corr_val),
                    'interpretation': self._get_correlation_interpretation('조회수', '댓글수', corr_val)
                }
            
            if 'view_count' in available_columns and 'duration_seconds' in available_columns:
                corr_val = correlation_matrix.loc['view_count', 'duration_seconds']
                correlations['조회수_영상길이'] = {
                    'correlation': float(corr_val),
                    'strength': self._interpret_correlation(corr_val),
                    'interpretation': self._get_correlation_interpretation('조회수', '영상길이', corr_val)
                }
            
            results['correlations'] = correlations
            results['summary'] = self._summarize_correlations(correlations)
            
            return results
            
        except Exception as e:
            return {"error": f"상관분석 중 오류: {str(e)}"}
    
    def group_comparison_analysis(self) -> Dict[str, Any]:
        """
        그룹 비교 분석 - 카테고리별 성과 비교
        
        Returns:
            그룹 비교 분석 결과
        """
        try:
            results = {}
            
            # 1. 요일별 비교
            if 'published_at' in self.data.columns:
                self.data['weekday'] = self.data['published_at'].dt.day_name()
                self.data['is_weekend'] = self.data['published_at'].dt.weekday >= 5
                
                weekend_avg = self.data[self.data['is_weekend']]['view_count'].mean()
                weekday_avg = self.data[~self.data['is_weekend']]['view_count'].mean()
                
                results['weekend_vs_weekday'] = {
                    'weekend_avg_views': int(weekend_avg) if not pd.isna(weekend_avg) else 0,
                    'weekday_avg_views': int(weekday_avg) if not pd.isna(weekday_avg) else 0,
                    'difference_ratio': float(weekend_avg / weekday_avg) if weekday_avg > 0 else 1,
                    'recommendation': '주말 업로드 권장' if weekend_avg > weekday_avg else '평일 업로드 권장'
                }
            
            # 2. 영상 길이별 비교
            if 'duration_seconds' in self.data.columns:
                self.data['length_category'] = pd.cut(
                    self.data['duration_seconds'],
                    bins=[0, 300, 900, float('inf')],
                    labels=['5분 미만', '5-15분', '15분 이상']
                )
                
                length_stats = self.data.groupby('length_category')['view_count'].agg(['mean', 'count']).reset_index()
                
                results['length_comparison'] = {
                    'categories': []
                }
                
                for _, row in length_stats.iterrows():
                    results['length_comparison']['categories'].append({
                        'category': str(row['length_category']),
                        'avg_views': int(row['mean']) if not pd.isna(row['mean']) else 0,
                        'video_count': int(row['count'])
                    })
                
                # 최적 길이 추천
                best_category = length_stats.loc[length_stats['mean'].idxmax(), 'length_category']
                results['length_comparison']['recommendation'] = f"{best_category} 영상이 가장 좋은 성과"
            
            # 3. 참여도별 비교
            if 'engagement_rate' in self.data.columns:
                self.data['engagement_level'] = pd.cut(
                    self.data['engagement_rate'],
                    bins=[0, 0.02, 0.05, float('inf')],
                    labels=['낮음', '보통', '높음']
                )
                
                engagement_stats = self.data.groupby('engagement_level')['view_count'].mean()
                
                results['engagement_comparison'] = {
                    'low_engagement_avg_views': int(engagement_stats.get('낮음', 0)),
                    'medium_engagement_avg_views': int(engagement_stats.get('보통', 0)),
                    'high_engagement_avg_views': int(engagement_stats.get('높음', 0))
                }
            
            return results
            
        except Exception as e:
            return {"error": f"그룹 비교 분석 중 오류: {str(e)}"}
    
    def top_performance_analysis(self) -> Dict[str, Any]:
        """
        상위 분석 - 상위 성과 영상들의 특징 분석
        
        Returns:
            상위 분석 결과
        """
        try:
            results = {}
            
            # 상위 10% 영상 식별
            top_10_percent = int(len(self.data) * 0.1) or 1
            top_videos = self.data.nlargest(top_10_percent, 'view_count')
            
            # 상위 영상들의 조회수 비중
            total_views = self.data['view_count'].sum()
            top_views = top_videos['view_count'].sum()
            view_share = (top_views / total_views * 100) if total_views > 0 else 0
            
            results['pareto_analysis'] = {
                'top_video_count': len(top_videos),
                'total_video_count': len(self.data),
                'top_percentage': 10,
                'view_share_percentage': float(view_share),
                'interpretation': f"상위 {len(top_videos)}개 영상이 전체 조회수의 {view_share:.1f}%를 차지"
            }
            
            # 상위 영상들의 공통 특징
            characteristics = {}
            
            # 평균 영상 길이
            if 'duration_seconds' in top_videos.columns:
                avg_duration = top_videos['duration_seconds'].mean()
                characteristics['avg_duration_minutes'] = float(avg_duration / 60) if not pd.isna(avg_duration) else 0
            
            # 평균 참여도
            if 'engagement_rate' in top_videos.columns:
                avg_engagement = top_videos['engagement_rate'].mean()
                characteristics['avg_engagement_rate'] = float(avg_engagement) if not pd.isna(avg_engagement) else 0
            
            # 주요 업로드 요일
            if 'published_at' in top_videos.columns:
                top_weekdays = top_videos['published_at'].dt.day_name().value_counts()
                characteristics['most_common_weekday'] = str(top_weekdays.index[0]) if len(top_weekdays) > 0 else "N/A"
            
            # 제목 키워드 분석 (간단히)
            if 'title' in top_videos.columns:
                # 제목에서 자주 나오는 단어들 (간단한 분석)
                all_titles = ' '.join(top_videos['title'].fillna('').astype(str))
                # 간단한 키워드 추출 (공백 기준)
                words = all_titles.split()
                word_freq = {}
                for word in words:
                    if len(word) > 1:  # 1글자 제외
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                # 상위 5개 키워드
                top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
                characteristics['common_keywords'] = [word for word, freq in top_keywords]
            
            results['top_video_characteristics'] = characteristics
            
            # 성공 패턴 요약
            success_tips = []
            if characteristics.get('avg_duration_minutes', 0) > 0:
                duration = characteristics['avg_duration_minutes']
                success_tips.append(f"성공 영상 평균 길이: {duration:.1f}분")
            
            if characteristics.get('most_common_weekday'):
                success_tips.append(f"가장 많은 성공 영상 업로드 요일: {characteristics['most_common_weekday']}")
            
            if characteristics.get('common_keywords'):
                keywords = ', '.join(characteristics['common_keywords'][:3])
                success_tips.append(f"자주 사용되는 키워드: {keywords}")
            
            results['success_patterns'] = success_tips
            
            return results
            
        except Exception as e:
            return {"error": f"상위 분석 중 오류: {str(e)}"}
    
    def _interpret_correlation(self, corr_value: float) -> str:
        """상관계수 강도 해석"""
        abs_corr = abs(corr_value)
        if abs_corr >= 0.7:
            return "강한 관계"
        elif abs_corr >= 0.3:
            return "중간 관계"
        else:
            return "약한 관계"
    
    def _get_correlation_interpretation(self, var1: str, var2: str, corr_value: float) -> str:
        """상관관계 해석 문장 생성"""
        direction = "양의" if corr_value > 0 else "음의"
        strength = self._interpret_correlation(corr_value)
        
        if corr_value > 0:
            return f"{var1}가 증가할수록 {var2}도 함께 증가하는 {strength} ({corr_value:.2f})"
        else:
            return f"{var1}가 증가할수록 {var2}는 감소하는 {strength} ({corr_value:.2f})"
    
    def _summarize_correlations(self, correlations: Dict) -> str:
        """상관분석 요약"""
        if not correlations:
            return "상관분석 결과가 없습니다."
        
        strong_relations = [k for k, v in correlations.items() if abs(v['correlation']) >= 0.7]
        weak_relations = [k for k, v in correlations.items() if abs(v['correlation']) < 0.3]
        
        summary = f"총 {len(correlations)}개 관계 분석. "
        if strong_relations:
            summary += f"강한 관계: {len(strong_relations)}개, "
        if weak_relations:
            summary += f"약한 관계: {len(weak_relations)}개"
        
        return summary
    
    def generate_summary(self) -> Dict[str, Any]:
        """전체 분석 요약"""
        try:
            summary = {
                'total_videos': len(self.data),
                'avg_views': int(self.data['view_count'].mean()) if 'view_count' in self.data.columns else 0,
                'avg_engagement': float(self.data['engagement_rate'].mean()) if 'engagement_rate' in self.data.columns else 0,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return summary
        except Exception as e:
            return {"error": f"요약 생성 중 오류: {str(e)}"}