"""
Ranking Engine Module

This module handles calculating rankings for students at both school and class levels.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

import pandas as pd
from typing import List, Optional


# Score columns to rank
SCORE_COLUMNS = {
    'total_raw': '总分(原始分)',
    'total_scaled': '总分(赋分)',
    'chinese': '语文',
    'math': '数学',
    'english': '英语',
    'physics': '物理',
    'chemistry': '化学',
    'biology': '生物',
}


def calculate_rankings(df: pd.DataFrame, score_column: str = 'total_scaled') -> pd.DataFrame:
    """Calculate rankings for all students.
    
    Args:
        df: DataFrame containing student data.
        score_column: Column name to rank by.
        
    Returns:
        DataFrame with ranking columns added.
    """
    df = df.copy()
    
    # Calculate school-level ranking
    if score_column in df.columns:
        df[f'{score_column}_school_rank'] = df[score_column].rank(ascending=False, method='min')
    
    # Calculate class-level ranking
    if 'class_id' in df.columns:
        df[f'{score_column}_class_rank'] = df.groupby('class_id')[score_column].rank(
            ascending=False, method='min'
        )
    
    return df


def calculate_all_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate rankings for all score columns.
    
    Args:
        df: DataFrame containing student data.
        
    Returns:
        DataFrame with all ranking columns added.
    """
    df = df.copy()
    
    for score_col in SCORE_COLUMNS.keys():
        if score_col in df.columns:
            df = calculate_rankings(df, score_col)
    
    return df


def get_top_students(df: pd.DataFrame, score_column: str = 'total_scaled', 
                     n: int = 10, by_class: bool = False) -> pd.DataFrame:
    """Get top N students by score.
    
    Args:
        df: DataFrame containing student data.
        score_column: Column to rank by.
        n: Number of students to return.
        by_class: If True, get top N per class.
        
    Returns:
        DataFrame with top N students, or empty DataFrame if column missing.
    """
    if score_column not in df.columns:
        return pd.DataFrame()  # Return empty DataFrame if column missing
    
    if by_class and 'class_id' in df.columns:
        return df.groupby('class_id').apply(
            lambda x: x.nlargest(n, score_column)
        ).reset_index(drop=True)
    else:
        return df.nlargest(n, score_column)


def get_class_rankings(df: pd.DataFrame, class_id: int) -> pd.DataFrame:
    """Get rankings for a specific class.
    
    Args:
        df: DataFrame containing student data.
        class_id: Class ID to filter by.
        
    Returns:
        DataFrame with students in the specified class, ranked by total score.
        Returns empty DataFrame if required columns missing.
    """
    if 'class_id' not in df.columns or 'total_scaled' not in df.columns:
        return pd.DataFrame()
    
    class_df = df[df['class_id'] == class_id].copy()
    class_df = calculate_rankings(class_df, 'total_scaled')
    
    rank_col = 'total_scaled_school_rank'
    if rank_col not in class_df.columns:
        return class_df
    
    return class_df.sort_values(rank_col)


def get_school_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Get rankings for the entire school.
    
    Args:
        df: DataFrame containing student data.
        
    Returns:
        DataFrame with all students, ranked by total score.
    """
    df = calculate_rankings(df, 'total_scaled')
    return df.sort_values('total_scaled_school_rank')


def get_student_rank(df: pd.DataFrame, student_id: str) -> Optional[dict]:
    """Get ranking information for a specific student.
    
    Args:
        df: DataFrame containing student data with rankings.
        student_id: Student ID to look up.
        
    Returns:
        Dictionary with ranking information, or None if not found.
    """
    student = df[df['student_id'] == student_id]
    
    if len(student) == 0:
        return None
    
    student = student.iloc[0]
    
    result = {
        'student_id': student_id,
        'name': student.get('name', ''),
        'class_id': student.get('class_id', ''),
        'total_score': student.get('total_scaled', 0),
    }
    
    # Add school rank for each subject
    for col in SCORE_COLUMNS.keys():
        if col in df.columns:
            rank_col = f'{col}_school_rank'
            if rank_col in student.index:
                result[f'{col}_school_rank'] = student.get(rank_col, 0)
    
    return result


if __name__ == "__main__":
    # Test the ranking module
    import parser
    
    file_path = r'E:\op\op8\高二期末赋分.xls'
    df = parser.parse_excel(file_path)
    
    # Add score columns if they don't exist (for testing)
    if 'total_scaled' not in df.columns:
        # Try to find the column
        for col in df.columns:
            if '赋分' in str(col) and '总分' in str(col):
                df['total_scaled'] = df[col]
                break
    
    ranked_df = calculate_rankings(df, 'total_scaled')
    print("Top 10 students:")
    print(get_top_students(ranked_df, 'total_scaled', 10)[['name', 'class_id', 'total_scaled', 'total_scaled_school_rank', 'total_scaled_class_rank']])
