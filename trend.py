"""
Trend Analysis Module

This module handles analyzing student performance trends over multiple exams.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

import pandas as pd
from typing import List, Dict, Optional
import os


# Global storage for multiple exam files
exam_data = {}
# Store file metadata
exam_metadata = {}


def load_exam_data(filepath: str, exam_name: str = None) -> pd.DataFrame:
    """Load exam data from an Excel file.
    
    Args:
        filepath: Path to the Excel file.
        exam_name: Name for this exam (e.g., 'midterm', 'final'). If None, uses filename.
        
    Returns:
        DataFrame with student data.
    """
    import parser as parser_module
    import pandas as pd
    
    if exam_name is None:
        exam_name = os.path.basename(filepath)
    
    # Use parse_all_sheets to get all sheets and concatenate
    # This matches the behavior in app.py
    result = parser_module.parse_all_sheets(filepath)
    df = pd.concat(result.values(), ignore_index=True)
    
    exam_data[exam_name] = df
    
    # Store metadata
    exam_metadata[exam_name] = {
        'filepath': filepath,
        'total_students': len(df),
        'classes': sorted(df['class_id'].dropna().unique().tolist()) if 'class_id' in df.columns else []
    }
    
    return df


def _ensure_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure rankings columns exist in DataFrame.
    
    If total_school_rank or total_class_rank are missing, calculate them.
    Uses total_scaled for ranking.
    
    Args:
        df: DataFrame with student data.
        
    Returns:
        DataFrame with ranking columns added if missing.
    """
    df = df.copy()
    
    # Check if rankings exist
    has_school_rank = 'total_school_rank' in df.columns
    has_class_rank = 'total_class_rank' in df.columns
    
    if not has_school_rank or not has_class_rank:
        # Need to calculate rankings
        if 'total_scaled' not in df.columns:
            return df  # Can't calculate without total score
        
        # Calculate school rank (by total_scaled)
        if not has_school_rank:
            df['total_school_rank'] = df['total_scaled'].rank(method='min', ascending=False).astype(int)
        
        # Calculate class rank (by total_scaled within each class)
        if not has_class_rank:
            df['total_class_rank'] = df.groupby('class_id')['total_scaled'].rank(method='min', ascending=False).astype(int)
    
    return df


def compare_two_exams(exam1_name: str, exam2_name: str, class_id: str = None, 
                       rank_type: str = 'school') -> List[Dict]:
    """Compare two exams and calculate rank changes for each student.
    
    Args:
        exam1_name: Name of first exam.
        exam2_name: Name of second exam.
        class_id: Class ID to filter (optional). If None, shows all students.
        rank_type: 'school' for school rank, 'class' for class rank.
        
    Returns:
        List of dictionaries with student info and rank changes.
    """
    if exam1_name not in exam_data or exam2_name not in exam_data:
        return []
    
    df1 = _ensure_rankings(exam_data[exam1_name])
    df2 = _ensure_rankings(exam_data[exam2_name])
    
    # Determine rank column
    if rank_type == 'school':
        rank_col = 'total_school_rank'
    else:
        rank_col = 'total_class_rank'
    
    # Merge the two dataframes on student_id
    # Use outer join to get students from both exams
    merged = pd.merge(
        df1[['student_id', 'name', 'class_id', 'total_scaled', rank_col]].rename(
            columns={'total_scaled': 'score1', rank_col: 'rank1'}
        ),
        df2[['student_id', 'name', 'class_id', 'total_scaled', rank_col]].rename(
            columns={'total_scaled': 'score2', rank_col: 'rank2'}
        ),
        on='student_id',
        how='outer',  # Changed from inner to outer to handle different class sets
        suffixes=('', '_2')
    )
    
    # Filter by class if specified
    # Check both class_id columns (from both exams)
    if class_id:
        class_id_str = str(class_id)
        # Student is in the selected class if either exam shows them in that class
        merged = merged[
            (merged['class_id'].astype(str) == class_id_str) | 
            (merged['class_id_2'].astype(str) == class_id_str)
        ]
    
    # Calculate rank change
    # rank_change = rank1 - rank2
    # If student improved (rank2 < rank1, e.g., from 10th to 5th), rank_change > 0 (positive)
    # If student declined (rank2 > rank1, e.g., from 5th to 10th), rank_change < 0 (negative)
    merged['rank_change'] = merged['rank1'] - merged['rank2']
    merged['score_change'] = merged['score2'] - merged['score1']
    
    # Convert to list of dicts
    results = []
    for _, row in merged.iterrows():
        # Use name from either exam (prefer exam1, fallback to exam2)
        name = row.get('name', '') or row.get('name_2', '')
        # Use class_id from either exam
        class_id = row.get('class_id', '') or row.get('class_id_2', '')
        
        results.append({
            'student_id': row['student_id'],
            'name': name,
            'class_id': class_id,
            'exam1_score': row['score1'] if pd.notna(row['score1']) else None,
            'exam2_score': row['score2'] if pd.notna(row['score2']) else None,
            'score_change': row['score_change'] if pd.notna(row['score_change']) else None,
            'exam1_rank': int(row['rank1']) if pd.notna(row['rank1']) else None,
            'exam2_rank': int(row['rank2']) if pd.notna(row['rank2']) else None,
            'rank_change': int(row['rank_change']) if pd.notna(row['rank_change']) else None,
        })
    
    # Sort by rank change (improvement first - larger rank_change = more improvement)
    results.sort(key=lambda x: x['rank_change'] if x['rank_change'] is not None else 0, reverse=True)
    
    return results


def get_student_trend(student_id: str = None, student_name: str = None, 
                      score_column: str = 'total_scaled',
                      rank_type: str = 'school') -> List[Dict]:
    """Get score/rank trend for a specific student across all loaded exams.
    
    Args:
        student_id: Student ID to track.
        student_name: Student name to track (alternative to student_id).
        score_column: Column to track (e.g., 'total_scaled', 'chinese').
        rank_type: 'school' for school rank, 'class' for class rank.
        
    Returns:
        List of dictionaries with exam name, score, and rank.
    """
    trend = []
    
    # Determine rank column
    if rank_type == 'school':
        rank_col = f'{score_column}_school_rank' if score_column != 'total_scaled' else 'total_school_rank'
    else:
        rank_col = f'{score_column}_class_rank' if score_column != 'total_scaled' else 'total_class_rank'
    
    # Normalize student_id to string for comparison
    student_id_str = str(student_id) if student_id else None
    
    for exam_name, df in exam_data.items():
        # Ensure rankings exist
        df = _ensure_rankings(df)
        
        # Find student by ID or name
        if student_id:
            # Convert both to string for comparison to handle int/float types
            student = df[df['student_id'].astype(str) == student_id_str]
        elif student_name:
            student = df[df['name'].astype(str).str.contains(student_name, na=False)]
        else:
            continue
        
        if len(student) > 0:
            student = student.iloc[0]
            score = student.get(score_column, None)
            
            # Calculate rank
            if score is not None and pd.notna(score):
                if rank_col in df.columns:
                    rank = int(student[rank_col]) if pd.notna(student[rank_col]) else None
                else:
                    rank = None
            else:
                score = None
                rank = None
            
            trend.append({
                'exam': exam_name,
                'exam_index': list(exam_data.keys()).index(exam_name),
                'score': float(score) if score is not None else None,
                'rank': rank,
                'student_name': student.get('name', ''),
                'class_id': student.get('class_id', ''),
            })
    
    return trend


def get_student_by_id_or_name(query: str) -> List[Dict]:
    """Search for students by ID or name across all exams.
    
    Args:
        query: Student ID or name to search.
        
    Returns:
        List of matching students with their info.
    """
    results = []
    seen_ids = set()
    
    for exam_name, df in exam_data.items():
        # Search by student_id
        matches = df[df['student_id'].astype(str).str.contains(query, na=False)]
        
        # Also search by name
        if 'name' in df.columns:
            name_matches = df[df['name'].astype(str).str.contains(query, na=False)]
            matches = pd.concat([matches, name_matches]).drop_duplicates()
        
        for _, student in matches.iterrows():
            student_id = str(student.get('student_id', ''))
            if student_id not in seen_ids:
                seen_ids.add(student_id)
                results.append({
                    'student_id': student_id,
                    'name': student.get('name', ''),
                    'class_id': student.get('class_id', ''),
                    'total_score': student.get('total_scaled', 0),
                    'school_rank': student.get('total_school_rank', 0),
                    'exam': exam_name,
                })
    
    return results


def get_class_rank_change_summary(exam1_name: str, exam2_name: str, class_id: str) -> Dict:
    """Get summary of rank changes for a class.
    
    Args:
        exam1_name: Name of first exam.
        exam2_name: Name of second exam.
        class_id: Class ID.
        
    Returns:
        Dictionary with summary statistics.
    """
    results = compare_two_exams(exam1_name, exam2_name, class_id, 'class')
    
    if not results:
        return {
            'total_students': 0,
            'improved': 0,
            'declined': 0,
            'unchanged': 0,
            'avg_rank_change': 0,
            'avg_score_change': 0,
        }
    
    # rank_change > 0 means improved (rank decreased, e.g., 10th -> 5th)
    # rank_change < 0 means declined (rank increased, e.g., 5th -> 10th)
    improved = sum(1 for r in results if r['rank_change'] and r['rank_change'] > 0)
    declined = sum(1 for r in results if r['rank_change'] and r['rank_change'] < 0)
    unchanged = sum(1 for r in results if r['rank_change'] == 0)
    
    rank_changes = [r['rank_change'] for r in results if r['rank_change'] is not None]
    score_changes = [r['score_change'] for r in results if r['score_change'] is not None]
    
    return {
        'total_students': len(results),
        'improved': improved,
        'declined': declined,
        'unchanged': unchanged,
        'avg_rank_change': sum(rank_changes) / len(rank_changes) if rank_changes else 0,
        'avg_score_change': sum(score_changes) / len(score_changes) if score_changes else 0,
    }


def clear_exam_data():
    """Clear all loaded exam data."""
    global exam_data, exam_metadata
    exam_data = {}
    exam_metadata = {}


def get_exam_list() -> List[str]:
    """Get list of loaded exam names."""
    return list(exam_data.keys())


def get_exam_metadata(exam_name: str) -> Dict:
    """Get metadata for an exam."""
    return exam_metadata.get(exam_name, {})


def get_available_classes() -> List[str]:
    """Get list of all available classes across exams."""
    classes = set()
    for df in exam_data.values():
        if 'class_id' in df.columns:
            classes.update(df['class_id'].dropna().unique().tolist())
    return sorted([str(c) for c in classes])


if __name__ == "__main__":
    # Test the trend module
    print("Trend analysis module loaded.")
    print("Use load_exam_data() to load exam files.")
