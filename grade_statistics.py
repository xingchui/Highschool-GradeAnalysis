"""
Statistics Analyzer Module

This module handles calculating statistics for 985/211/yiben (one book) score lines.
Includes support for single subject score lines.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

import json
import os
import pandas as pd
from typing import Dict, List, Optional


# Default configuration
DEFAULT_CONFIG = {
    "lines": {
        "total_raw": {"985": 600.0, "211": 550.0, "yiben": 500.0},
        "total_scaled": {"985": 600.0, "211": 550.0, "yiben": 500.0},
        "chinese": {"985": 120.0, "211": 110.0, "yiben": 105.0},
        "math": {"985": 120.0, "211": 110.0, "yiben": 105.0},
        "english": {"985": 120.0, "211": 110.0, "yiben": 105.0},
        "physics": {"985": 90.0, "211": 80.0, "yiben": 70.0},
        "history": {"985": 90.0, "211": 80.0, "yiben": 70.0},
        "chemistry_raw": {"985": 90.0, "211": 80.0, "yiben": 70.0},
        "chemistry_scaled": {"985": 90.0, "211": 80.0, "yiben": 70.0},
        "biology_raw": {"985": 90.0, "211": 80.0, "yiben": 70.0},
        "biology_scaled": {"985": 90.0, "211": 80.0, "yiben": 70.0},
        "politics_raw": {"985": 90.0, "211": 80.0, "yiben": 70.0},
        "politics_scaled": {"985": 90.0, "211": 80.0, "yiben": 70.0},
        "geography_raw": {"985": 90.0, "211": 80.0, "yiben": 70.0},
        "geography_scaled": {"985": 90.0, "211": 80.0, "yiben": 70.0},
    },
    "subjects": {
        "chinese": 150.0,
        "math": 150.0,
        "english": 150.0,
        "physics": 100.0,
        "history": 100.0,
        "chemistry": 100.0,
        "biology": 100.0,
        "politics": 100.0,
        "geography": 100.0
    }
}


def load_config(config_path: str = "config.json") -> dict:
    """Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file.
        
    Returns:
        Configuration dictionary.
    """
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CONFIG


def save_config(config: dict, config_path: str = "config.json") -> None:
    """Save configuration to JSON file.
    
    Args:
        config: Configuration dictionary.
        config_path: Path to configuration file.
    """
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_line_thresholds(config: Optional[dict] = None) -> dict:
    """Get score line thresholds from configuration.
    
    Args:
        config: Configuration dictionary. If None, loads from default.
        
    Returns:
        Dictionary with line thresholds.
    """
    if config is None:
        config = load_config()
    return config.get('lines', DEFAULT_CONFIG['lines'])


def calculate_line_stats(df: pd.DataFrame, score_column: str, 
                        line_thresholds: Dict[str, float]) -> dict:
    """Calculate line statistics for a score column.
    
    Args:
        df: DataFrame containing student data.
        score_column: Column name to calculate statistics for.
        line_thresholds: Dictionary with line thresholds (e.g., {"985": 580, "211": 540}).
        
    Returns:
        Dictionary with line counts and rates.
    """
    if score_column not in df.columns:
        return {
            "total_students": 0,
            "lines": {}
        }
    
    # Remove NaN values for calculation
    valid_scores = df[score_column].dropna()
    total_students = len(valid_scores)
    
    lines = {}
    for line_name, threshold in line_thresholds.items():
        count = (valid_scores >= threshold).sum()
        rate = (count / total_students * 100) if total_students > 0 else 0
        lines[line_name] = {
            "count": int(count),
            "rate": round(rate, 2)
        }
    
    return {
        "total_students": int(total_students),
        "lines": lines
    }


# Subject column mapping in Excel (by position)
SUBJECT_COLUMN_MAP = {
    'chinese': 'chinese',
    'math': 'math', 
    'english': 'english',
    'physics': 'physics',
    'history': 'history',
    'chemistry_raw': 'chemistry_raw',
    'chemistry_scaled': 'chemistry',
    'biology_raw': 'biology_raw',
    'biology_scaled': 'biology',
    'politics_raw': 'politics_raw',
    'politics_scaled': 'politics',
    'geography_raw': 'geography_raw',
    'geography_scaled': 'geography',
}

# Subjects that have both raw and scaled versions
SUBJECTS_WITH_SCALED = ['chemistry', 'biology', 'politics', 'geography']

# Fixed subjects (no raw/scaled variant)
FIXED_SUBJECTS = ['chinese', 'math', 'english', 'physics', 'history']

# Column names for score types
TOTAL_RAW_COLUMN = 'total_raw'
TOTAL_SCALED_COLUMN = 'total_scaled'


def get_available_subjects(df: pd.DataFrame) -> dict:
    """Get available subjects in the DataFrame.
    
    Args:
        df: DataFrame containing student data.
        
    Returns:
        Dictionary with subject availability info.
    """
    available = {
        'has_physics': 'physics' in df.columns,
        'has_history': 'history' in df.columns,
        'has_chemistry_raw': 'chemistry_raw' in df.columns,
        'has_chemistry_scaled': 'chemistry' in df.columns,
        'has_biology_raw': 'biology_raw' in df.columns,
        'has_biology_scaled': 'biology' in df.columns,
        'has_politics_raw': 'politics_raw' in df.columns,
        'has_politics_scaled': 'politics' in df.columns,
        'has_geography_raw': 'geography_raw' in df.columns,
        'has_geography_scaled': 'geography' in df.columns,
        'has_total_raw': 'total_raw' in df.columns,
        'has_total_scaled': 'total_scaled' in df.columns,
        'has_chinese': 'chinese' in df.columns,
        'has_math': 'math' in df.columns,
        'has_english': 'english' in df.columns,
    }
    return available


def filter_by_optional_subject(df: pd.DataFrame, choice: str) -> pd.DataFrame:
    """Filter students by physics or history selection.
    
    Args:
        df: DataFrame containing student data.
        choice: Either 'physics' or 'history'.
        
    Returns:
        Filtered DataFrame. Returns original df if column doesn't exist.
    """
    if choice == 'physics':
        # Filter students who have physics score
        if 'physics' in df.columns:
            return df[df['physics'].notna()]
        else:
            # No physics column, return empty or all
            return df[df['physics'].notna()] if 'physics' in df.columns else df
    elif choice == 'history':
        # Filter students who have history score
        if 'history' in df.columns:
            return df[df['history'].notna()]
        else:
            # No history column, try physics as fallback or return all
            if 'physics' in df.columns:
                return df[df['physics'].notna()]
    return df


def calculate_class_line_stats(df: pd.DataFrame, score_column: str = 'total_scaled',
                              line_thresholds: Optional[Dict[str, float]] = None) -> pd.DataFrame:
    """Calculate line statistics for each class.
    
    Args:
        df: DataFrame containing student data.
        score_column: Column name to calculate statistics for.
        line_thresholds: Dictionary with line thresholds. If None, loads from config.
        
    Returns:
        DataFrame with line statistics per class.
    """
    if 'class_id' not in df.columns:
        return pd.DataFrame()  # Return empty DataFrame if no class_id column
    
    if line_thresholds is None:
        config = load_config()
        line_thresholds = config.get('lines', {}).get('total_scaled', 
            {'985': 600.0, '211': 550.0, 'yiben': 500.0})
    
    results = []
    
    for class_id in df['class_id'].dropna().unique():
        class_df = df[df['class_id'] == class_id]
        stats = calculate_line_stats(class_df, score_column, line_thresholds)
        
        results.append({
            'class_id': class_id,
            'total_students': stats['total_students'],
            '985_count': stats['lines'].get('985', {}).get('count', 0),
            '985_rate': stats['lines'].get('985', {}).get('rate', 0),
            '211_count': stats['lines'].get('211', {}).get('count', 0),
            '211_rate': stats['lines'].get('211', {}).get('rate', 0),
            'yiben_count': stats['lines'].get('yiben', {}).get('count', 0),
            'yiben_rate': stats['lines'].get('yiben', {}).get('rate', 0),
        })
    
    return pd.DataFrame(results)


def calculate_school_line_stats(df: pd.DataFrame, score_column: str = 'total_scaled',
                                 line_thresholds: Optional[Dict[str, float]] = None) -> dict:
    """Calculate line statistics for the entire school.
    
    Args:
        df: DataFrame containing student data.
        score_column: Column name to calculate statistics for.
        line_thresholds: Dictionary with line thresholds. If None, loads from config.
        
    Returns:
        Dictionary with school-level line statistics.
    """
    if line_thresholds is None:
        config = load_config()
        line_thresholds = config.get('lines', {}).get('total_scaled',
            {'985': 600.0, '211': 550.0, 'yiben': 500.0})
    
    return calculate_line_stats(df, score_column, line_thresholds)


def calculate_single_subject_line_stats(df: pd.DataFrame, 
                                       subject: str,
                                       score_type: str = 'raw',
                                       line_thresholds: Optional[Dict[str, float]] = None) -> dict:
    """Calculate line statistics for a single subject.
    
    Args:
        df: DataFrame containing student data.
        subject: Subject name (e.g., 'chinese', 'math', 'chemistry').
        score_type: 'raw' or 'scaled' for subjects that have both.
        line_thresholds: Dictionary with line thresholds. If None, loads from config.
        
    Returns:
        Dictionary with line statistics for the subject.
    """
    config = load_config()
    lines_config = config.get('lines', {})
    
    # Determine config key
    if subject in FIXED_SUBJECTS:
        config_key = subject
    elif subject in SUBJECTS_WITH_SCALED:
        config_key = f"{subject}_{score_type}"
    else:
        config_key = subject
    
    if line_thresholds is None:
        line_thresholds = lines_config.get(config_key, {'985': 90.0, '211': 80.0, 'yiben': 70.0})
    
    # Determine score column
    if subject in SUBJECTS_WITH_SCALED:
        score_column = f"{subject}_raw" if score_type == 'raw' else subject
    else:
        score_column = SUBJECT_COLUMN_MAP.get(subject, subject)
    
    # Check if column exists in dataframe
    if score_column not in df.columns:
        return {"total_students": 0, "lines": {}}
    
    return calculate_line_stats(df, score_column, line_thresholds)


def calculate_all_subject_stats(df: pd.DataFrame, 
                                total_type: str = 'scaled',
                                optional_subject: str = 'physics',
                                config: Optional[dict] = None) -> dict:
    """Calculate line statistics for all subjects.
    
    Args:
        df: DataFrame containing student data.
        total_type: 'raw' or 'scaled' for total score.
        optional_subject: 'physics' or 'history' for the 2-of-1 choice.
        config: Configuration dictionary. If None, loads from default.
        
    Returns:
        Dictionary with statistics for all subjects.
    """
    if config is None:
        config = load_config()
    
    lines_config = config.get('lines', {})
    
    # Filter by optional subject selection (physics or history)
    df_filtered = filter_by_optional_subject(df, optional_subject)
    
    # Total column based on selection
    total_column = TOTAL_SCALED_COLUMN if total_type == 'scaled' else TOTAL_RAW_COLUMN
    total_config_key = f"total_{total_type}"
    
    # Fixed subjects list (语数外 + 物理/历史二选一)
    fixed_subject_list = ['chinese', 'math', 'english', optional_subject]
    
    # Subjects that have raw/scaled (化学生物政治地理四选二)
    scaled_subjects = ['chemistry', 'biology', 'politics', 'geography']
    
    results = {
        'total': {
            'name': f'总分({total_type}分)',
            'stats': calculate_line_stats(df_filtered, total_column, 
                lines_config.get(total_config_key, {'985': 600.0, '211': 550.0, 'yiben': 500.0}))
        }
    }
    
    # Fixed subjects (Chinese, Math, English, Physics/History)
    for subject in fixed_subject_list:
        subject_thresholds = lines_config.get(subject, {'985': 120.0, '211': 110.0, 'yiben': 105.0})
        score_column = SUBJECT_COLUMN_MAP.get(subject, subject)
        
        if score_column in df_filtered.columns:
            results[subject] = {
                'name': get_subject_display_name(subject),
                'stats': calculate_line_stats(df_filtered, score_column, subject_thresholds)
            }
    
    # Subjects with raw/scaled (Chemistry, Biology, Politics, Geography)
    for subject in scaled_subjects:
        # Raw score
        raw_thresholds = lines_config.get(f"{subject}_raw", {'985': 90.0, '211': 80.0, 'yiben': 70.0})
        raw_column = f"{subject}_raw"
        if raw_column in df_filtered.columns:
            results[f"{subject}_raw"] = {
                'name': f'{get_subject_display_name(subject)}(原始分)',
                'stats': calculate_line_stats(df_filtered, raw_column, raw_thresholds)
            }
        
        # Scaled score
        scaled_thresholds = lines_config.get(f"{subject}_scaled", {'985': 90.0, '211': 80.0, 'yiben': 70.0})
        scaled_column = subject
        if scaled_column in df_filtered.columns:
            results[f"{subject}_scaled"] = {
                'name': f'{get_subject_display_name(subject)}(赋分)',
                'stats': calculate_line_stats(df_filtered, scaled_column, scaled_thresholds)
            }
    
    return results


def calculate_class_all_subject_stats(df: pd.DataFrame,
                                       total_type: str = 'scaled',
                                       optional_subject: str = 'physics',
                                       config: Optional[dict] = None) -> pd.DataFrame:
    """Calculate line statistics for all subjects per class.
    
    Args:
        df: DataFrame containing student data.
        total_type: 'raw' or 'scaled' for total score.
        optional_subject: 'physics' or 'history' for the 2-of-1 choice.
        config: Configuration dictionary. If None, loads from default.
        
    Returns:
        DataFrame with statistics for all subjects per class.
    """
    if config is None:
        config = load_config()
    
    lines_config = config.get('lines', {})
    
    # Filter by optional subject selection
    df_filtered = filter_by_optional_subject(df, optional_subject)
    
    # Total column based on selection
    total_column = TOTAL_SCALED_COLUMN if total_type == 'scaled' else TOTAL_RAW_COLUMN
    total_config_key = f"total_{total_type}"
    total_thresholds = lines_config.get(total_config_key, {'985': 600.0, '211': 550.0, 'yiben': 500.0})
    
    # Fixed subjects (Chinese, Math, English, Physics/History)
    fixed_subject_list = ['chinese', 'math', 'english', optional_subject]
    
    # Subjects with raw/scaled
    scaled_subjects = ['chemistry', 'biology', 'politics', 'geography']
    
    results = []
    
    for class_id in sorted(df_filtered['class_id'].unique()):
        class_df = df_filtered[df_filtered['class_id'] == class_id]
        
        row = {'class_id': class_id, 'total_students': len(class_df)}
        
        # Total score stats
        total_stats = calculate_line_stats(class_df, total_column, total_thresholds)
        row['total_985_count'] = total_stats['lines'].get('985', {}).get('count', 0)
        row['total_211_count'] = total_stats['lines'].get('211', {}).get('count', 0)
        row['total_yiben_count'] = total_stats['lines'].get('yiben', {}).get('count', 0)
        
        # Fixed subjects
        for subject in fixed_subject_list:
            subject_thresholds = lines_config.get(subject, {'985': 120.0, '211': 110.0, 'yiben': 105.0})
            score_column = SUBJECT_COLUMN_MAP.get(subject, subject)
            
            if score_column in class_df.columns:
                stats = calculate_line_stats(class_df, score_column, subject_thresholds)
                row[f'{subject}_985_count'] = stats['lines'].get('985', {}).get('count', 0)
                row[f'{subject}_211_count'] = stats['lines'].get('211', {}).get('count', 0)
                row[f'{subject}_yiben_count'] = stats['lines'].get('yiben', {}).get('count', 0)
        
        # Subjects with raw/scaled
        for subject in scaled_subjects:
            # Raw score
            raw_thresholds = lines_config.get(f"{subject}_raw", {'985': 90.0, '211': 80.0, 'yiben': 70.0})
            raw_column = f"{subject}_raw"
            if raw_column in class_df.columns:
                raw_stats = calculate_line_stats(class_df, raw_column, raw_thresholds)
                row[f'{subject}_raw_985_count'] = raw_stats['lines'].get('985', {}).get('count', 0)
                row[f'{subject}_raw_211_count'] = raw_stats['lines'].get('211', {}).get('count', 0)
                row[f'{subject}_raw_yiben_count'] = raw_stats['lines'].get('yiben', {}).get('count', 0)
            
            # Scaled score
            scaled_thresholds = lines_config.get(f"{subject}_scaled", {'985': 90.0, '211': 80.0, 'yiben': 70.0})
            scaled_column = subject
            if scaled_column in class_df.columns:
                scaled_stats = calculate_line_stats(class_df, scaled_column, scaled_thresholds)
                row[f'{subject}_scaled_985_count'] = scaled_stats['lines'].get('985', {}).get('count', 0)
                row[f'{subject}_scaled_211_count'] = scaled_stats['lines'].get('211', {}).get('count', 0)
                row[f'{subject}_scaled_yiben_count'] = scaled_stats['lines'].get('yiben', {}).get('count', 0)
        
        results.append(row)
    
    return pd.DataFrame(results)


def get_subject_display_name(subject: str) -> str:
    """Get display name for a subject.
    
    Args:
        subject: Subject key.
        
    Returns:
        Display name in Chinese.
    """
    display_names = {
        'chinese': '语文',
        'math': '数学',
        'english': '英语',
        'physics': '物理',
        'history': '历史',
        'chemistry': '化学',
        'biology': '生物',
        'politics': '政治',
        'geography': '地理',
    }
    return display_names.get(subject, subject)


if __name__ == "__main__":
    # Test the statistics module
    import parser
    
    file_path = r'E:\op\op8\高二期末赋分.xls'
    result = parser.parse_all_sheets(file_path)
    
    # Combine all sheets
    import pandas as pd
    combined_df = pd.concat(result.values(), ignore_index=True)
    
    # Calculate school statistics
    school_stats = calculate_school_line_stats(combined_df)
    print("School Statistics:")
    print(json.dumps(school_stats, indent=2, ensure_ascii=False))
    
    # Calculate class statistics
    class_stats = calculate_class_line_stats(combined_df)
    print("\nClass Statistics:")
    print(class_stats)
