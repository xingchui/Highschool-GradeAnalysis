"""
Grade Analysis Service

This module provides a service layer for grade analysis operations,
encapsulating business logic and providing a clean interface for routes.
"""

from typing import Dict, List, Optional, Any, Tuple
import pandas as pd

import ranking
import grade_statistics as stats_module
import trend as trend_module


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
