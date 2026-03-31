"""
Grade Analysis Service

This module provides a service layer for grade analysis operations,
encapsulating business logic and providing a clean interface for routes.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

from typing import Dict, List, Optional, Any, Tuple
import pandas as pd

import ranking
import grade_statistics as stats_module
import trend as trend_module
import charts as charts_module


class GradeAnalysisService:
    """Service class for grade analysis operations.
    
    This class encapsulates business logic for ranking, statistics,
    and trend analysis, providing a clean interface for route handlers.
    """
    
    def __init__(self, data_service):
        """Initialize the grade analysis service.
        
        Args:
            data_service: DataService instance for data access.
        """
        self.data_service = data_service
    
    # ==================== Ranking Methods ====================
    
    def calculate_rankings(self, score_column: str = 'total_scaled') -> Optional[pd.DataFrame]:
        """Calculate rankings for current data.
        
        Args:
            score_column: Column to use for ranking calculation.
            
        Returns:
            DataFrame with rankings or None if no data.
        """
        current_data = self.data_service.get_current_data()
        if current_data is None:
            return None
        
        return ranking.calculate_rankings(current_data, score_column)
    
    def get_top_students(self, score_column: str = 'total_scaled', 
                         top_n: int = 20) -> Optional[List[Dict]]:
        """Get top N students by score.
        
        Args:
            score_column: Column to use for ranking.
            top_n: Number of top students to return.
            
        Returns:
            List of student dictionaries or None if no data.
        """
        ranked_data = self.calculate_rankings(score_column)
        if ranked_data is None:
            return None
        
        top_students = ranking.get_top_students(ranked_data, score_column, top_n)
        return top_students.to_dict('records')
    
    def get_student_rank(self, student_id: str) -> Optional[Dict]:
        """Get ranking information for a specific student.
        
        Args:
            student_id: Student ID to look up.
            
        Returns:
            Student dictionary or None if not found.
        """
        ranked_data = self.calculate_rankings()
        if ranked_data is None:
            return None
        
        return ranking.get_student_rank(ranked_data, student_id)
    
    def get_all_rankings(self, page: int = 1, per_page: int = 50) -> Tuple[List[Dict], int]:
        """Get paginated rankings for all students.
        
        Args:
            page: Page number (1-indexed).
            per_page: Number of students per page.
            
        Returns:
            Tuple of (students list, total pages).
        """
        ranked_data = self.calculate_rankings()
        if ranked_data is None:
            return [], 0
        
        ranked_data = ranked_data.sort_values('total_scaled_school_rank')
        
        start = (page - 1) * per_page
        end = start + per_page
        total_pages = (len(ranked_data) + per_page - 1) // per_page
        
        students = ranked_data.iloc[start:end].to_dict('records')
        return students, total_pages
    
    # ==================== Statistics Methods ====================
    
    def get_school_statistics(self) -> Optional[Dict]:
        """Get school-level statistics.
        
        Returns:
            School statistics dictionary or None if no data.
        """
        current_data = self.data_service.get_current_data()
        if current_data is None:
            return None
        
        return stats_module.calculate_school_line_stats(current_data)
    
    def get_class_statistics(self) -> Optional[pd.DataFrame]:
        """Get class-level statistics.
        
        Returns:
            DataFrame with class statistics or None if no data.
        """
        current_data = self.data_service.get_current_data()
        if current_data is None:
            return None
        
        return stats_module.calculate_class_line_stats(current_data)
    
    def get_subject_statistics(self, optional_subject: str = 'physics',
                               total_type: str = 'scaled') -> Optional[Dict]:
        """Get all subject statistics.
        
        Args:
            optional_subject: Optional subject (physics/history).
            total_type: Total type ('raw' or 'scaled').
            
        Returns:
            Statistics dictionary or None if no data.
        """
        current_data = self.data_service.get_current_data()
        if current_data is None:
            return None
        
        return stats_module.calculate_all_subject_stats(
            current_data,
            total_type=total_type,
            optional_subject=optional_subject
        )
    
    def get_class_subject_statistics(self, optional_subject: str = 'physics',
                                     total_type: str = 'scaled') -> Optional[pd.DataFrame]:
        """Get class-level subject statistics.
        
        Args:
            optional_subject: Optional subject (physics/history).
            total_type: Total type ('raw' or 'scaled').
            
        Returns:
            DataFrame with class statistics or None if no data.
        """
        current_data = self.data_service.get_current_data()
        if current_data is None:
            return None
        
        return stats_module.calculate_class_all_subject_stats(
            current_data,
            total_type=total_type,
            optional_subject=optional_subject
        )
    
    def get_available_subjects(self) -> Dict[str, bool]:
        """Get available subjects in current data.
        
        Returns:
            Dictionary indicating which subjects are available.
        """
        current_data = self.data_service.get_current_data()
        if current_data is None:
            return {'has_physics': False, 'has_history': False}
        
        return stats_module.get_available_subjects(current_data)
    
    # ==================== Configuration Methods ====================
    
    def load_config(self) -> Dict:
        """Load current configuration.
        
        Returns:
            Configuration dictionary.
        """
        return stats_module.load_config()
    
    def save_config(self, config: Dict) -> None:
        """Save configuration.
        
        Args:
            config: Configuration dictionary to save.
        """
        stats_module.save_config(config)
    
    # ==================== Trend Methods ====================
    
    def load_exam_for_trend(self, display_name: str) -> bool:
        """Load a file into the trend analysis module.
        
        Args:
            display_name: Display name of the file.
            
        Returns:
            True if loaded successfully, False otherwise.
        """
        import os
        from flask import current_app
        
        file_info = self.data_service.get_file_info(display_name)
        if not file_info:
            return False
        
        if display_name in trend_module.get_exam_list():
            return True  # Already loaded
        
        actual_filename = file_info.get('saved_filename', display_name)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], actual_filename)
        
        if os.path.exists(filepath):
            trend_module.load_exam_data(filepath, display_name)
            return True
        
        return False
    
    def load_all_exams_for_trend(self) -> None:
        """Load all files into trend analysis module."""
        for display_name in self.data_service.get_file_list():
            self.load_exam_for_trend(display_name)
    
    def compare_exams(self, exam1: str, exam2: str, 
                      class_id: str = None, rank_type: str = 'school') -> List[Dict]:
        """Compare two exams.
        
        Args:
            exam1: First exam name.
            exam2: Second exam name.
            class_id: Optional class ID filter.
            rank_type: 'school' or 'class' rank type.
            
        Returns:
            List of comparison results.
        """
        self.load_all_exams_for_trend()
        return trend_module.compare_two_exams(exam1, exam2, class_id, rank_type)
    
    def get_class_summary(self, exam1: str, exam2: str, class_id: str) -> Dict:
        """Get class rank change summary.
        
        Args:
            exam1: First exam name.
            exam2: Second exam name.
            class_id: Class ID.
            
        Returns:
            Summary dictionary.
        """
        self.load_all_exams_for_trend()
        return trend_module.get_class_rank_change_summary(exam1, exam2, class_id)
    
    def get_student_trend(self, student_id: str = None, student_name: str = None,
                          score_column: str = 'total_scaled',
                          rank_type: str = 'school',
                          filter_exams: List[str] = None) -> List[Dict]:
        """Get trend data for a student.
        
        Args:
            student_id: Student ID.
            student_name: Student name (alternative to ID).
            score_column: Column to track.
            rank_type: 'school' or 'class' rank.
            filter_exams: Optional list of exams to include.
            
        Returns:
            List of trend data points.
        """
        self.load_all_exams_for_trend()
        
        all_trend = trend_module.get_student_trend(
            student_id=student_id,
            student_name=student_name,
            score_column=score_column,
            rank_type=rank_type
        )
        
        if filter_exams:
            return [t for t in all_trend if t['exam'] in filter_exams]
        
        return all_trend
    
    def search_students(self, query: str) -> List[Dict]:
        """Search for students by ID or name.
        
        Args:
            query: Search query.
            
        Returns:
            List of matching students.
        """
        self.load_all_exams_for_trend()
        return trend_module.get_student_by_id_or_name(query)
    
    def get_available_classes(self) -> List[str]:
        """Get list of available classes across all exams.
        
        Returns:
            Sorted list of class IDs.
        """
        self.load_all_exams_for_trend()
        return trend_module.get_available_classes()
    
    def get_exam_list(self) -> List[str]:
        """Get list of loaded exam names.
        
        Returns:
            List of exam names.
        """
        return trend_module.get_exam_list()

    # ==================== Chart Methods ====================
    
    def get_chart_list(self) -> List[Dict[str, str]]:
        """Get list of available chart types.
        
        Returns:
            List of chart type info dicts.
        """
        return charts_module.get_chart_list()
    
    def generate_chart(self, chart_type: str, **kwargs) -> str:
        """Generate a chart based on type and parameters.
        
        Args:
            chart_type: Type of chart to generate.
            **kwargs: Additional parameters for the chart.
            
        Returns:
            HTML string of the chart.
        """
        current_data = self.data_service.get_current_data()
        if current_data is None:
            return "<p>无数据可用</p>"
        
        chart_generators = {
            'box': self._generate_box_chart,
            'heatmap': self._generate_heatmap_chart,
            'scatter': self._generate_scatter_chart,
            'violin': self._generate_violin_chart,
            'correlation': self._generate_correlation_chart,
            'distribution': self._generate_distribution_chart,
            'rank_change': self._generate_rank_change_chart,
            'trend': self._generate_trend_chart,
            'radar': self._generate_radar_chart,
        }
        
        generator = chart_generators.get(chart_type)
        if generator:
            return generator(current_data, **kwargs)
        
        return "<p>未知的图表类型</p>"
    
    def _generate_box_chart(self, df: pd.DataFrame, **kwargs) -> str:
        """Generate box plot."""
        score_column = kwargs.get('score_column', 'total_scaled')
        group_column = kwargs.get('group_column', 'class_id')
        return charts_module.create_box_plot(df, score_column, group_column)
    
    def _generate_heatmap_chart(self, df: pd.DataFrame, **kwargs) -> str:
        """Generate heatmap chart."""
        subjects = kwargs.get('subjects', None)
        aggfunc = kwargs.get('aggfunc', 'mean')
        return charts_module.create_heatmap(df, columns_subjects=subjects, aggfunc=aggfunc)
    
    def _generate_scatter_chart(self, df: pd.DataFrame, **kwargs) -> str:
        """Generate scatter plot with regression."""
        x_col = kwargs.get('x_col', 'math')
        y_col = kwargs.get('y_col', 'physics')
        show_regression = kwargs.get('show_regression', True)
        return charts_module.create_scatter_with_regression(
            df, x_col, y_col, show_regression=show_regression
        )
    
    def _generate_violin_chart(self, df: pd.DataFrame, **kwargs) -> str:
        """Generate violin plot."""
        score_column = kwargs.get('score_column', 'total_scaled')
        group_column = kwargs.get('group_column', 'class_id')
        return charts_module.create_violin_plot(df, score_column, group_column)
    
    def _generate_correlation_chart(self, df: pd.DataFrame, **kwargs) -> str:
        """Generate correlation matrix."""
        subjects = kwargs.get('subjects', None)
        return charts_module.create_correlation_matrix(df, subject_columns=subjects)
    
    def _generate_distribution_chart(self, df: pd.DataFrame, **kwargs) -> str:
        """Generate distribution chart with line overlays."""
        score_column = kwargs.get('score_column', 'total_scaled')
        line_config = kwargs.get('line_config', None)
        return charts_module.create_score_distribution_by_line(
            df, score_column, line_config=line_config
        )
    
    def _generate_rank_change_chart(self, df: pd.DataFrame, **kwargs) -> str:
        """Generate rank change chart."""
        comparison_data = kwargs.get('comparison_data', [])
        return charts_module.create_class_rank_change_chart(comparison_data)
    
    def _generate_trend_chart(self, df: pd.DataFrame, **kwargs) -> str:
        """Generate score trend distribution chart.
        
        For single exam data, shows score distribution as a line chart.
        For multiple exams, shows score trends across exams.
        """
        score_column = kwargs.get('score_column', 'total_scaled')
        exam_name = kwargs.get('exam_name', '当前考试')
        
        # Create trend data from score distribution bins
        if score_column not in df.columns:
            return "<p>数据不可用</p>"
        
        scores = df[score_column].dropna()
        if scores.empty:
            return "<p>无有效数据</p>"
        
        # Create bins for score distribution
        import numpy as np
        bins = np.linspace(scores.min(), scores.max(), 20)
        hist, _ = np.histogram(scores, bins=bins)
        
        # Format as trend data (score ranges vs count)
        trend_data = []
        for i in range(len(bins) - 1):
            trend_data.append({
                'exam': f'{int(bins[i])}-{int(bins[i+1])}',
                'score': int(hist[i]),
                'rank': None
            })
        
        return charts_module.create_score_trend_chart(
            trend_data, 
            subject_name=f"{score_column} 分数段分布"
        )
    
    def _generate_radar_chart(self, df: pd.DataFrame, **kwargs) -> str:
        """Generate radar chart for subject comparison.
        
        Shows average scores per subject as a radar chart.
        """
        # Get available subjects
        subjects = self.get_subjects_list()
        
        # Filter to only subject scores (not ranks or totals)
        subject_cols = [s for s in subjects if s not in ['total_raw', 'total_scaled']]
        
        if not subject_cols:
            return "<p>无学科数据</p>"
        
        # Calculate average scores for each subject
        student_data = {}
        for col in subject_cols:
            avg_score = df[col].mean()
            if not pd.isna(avg_score):
                student_data[col] = round(float(avg_score), 2)
        
        if not student_data:
            return "<p>无有效数据</p>"
        
        return charts_module.create_subject_radar_chart(student_data)
    
    def get_subjects_list(self) -> List[str]:
        """Get list of available subjects in current data.
        
        Returns:
            List of subject column names.
        """
        current_data = self.data_service.get_current_data()
        if current_data is None:
            return []
        
        # Common subject columns
        subject_cols = ['chinese', 'math', 'english', 'physics', 
                       'chemistry', 'biology', 'history', 'geography',
                       'politics', 'total_raw', 'total_scaled']
        
        return [col for col in subject_cols if col in current_data.columns]
    
    def get_scatter_subjects_pairs(self) -> List[Dict[str, str]]:
        """Get suggested subject pairs for scatter plot.
        
        Returns:
            List of dicts with x_col and y_col for scatter plots.
        """
        subjects = self.get_subjects_list()
        pairs = []
        
        # Common meaningful pairs
        suggested_pairs = [
            ('math', 'physics'),
            ('chinese', 'english'),
            ('total_scaled', 'physics'),
            ('math', 'chemistry'),
        ]
        
        for x, y in suggested_pairs:
            if x in subjects and y in subjects:
                pairs.append({'x_col': x, 'y_col': y, 'label': f'{x} vs {y}'})
        
        return pairs
