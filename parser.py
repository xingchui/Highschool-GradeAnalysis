"""
Excel Parser Module

This module handles parsing of Excel files containing student grade data.
Supports both .xls and .xlsx formats.
"""

import pandas as pd
import os
from typing import Optional, Dict


def detect_excel_format(df: pd.DataFrame) -> str:
    """Detect the Excel format based on column structure.
    
    Args:
        df: Raw DataFrame from Excel.
        
    Returns:
        Format type: 'new' (61 cols, 理科) or 'liberal' (54 cols, 文科) or 'old' (32 cols)
    """
    col_count = len(df.columns)
    if col_count >= 60:
        return 'new'  # 理科 61 columns
    elif col_count >= 50:
        return 'liberal'  # 文科 54 columns
    return 'old'


def parse_excel(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Parse an Excel file and return a cleaned DataFrame.
    
    Args:
        file_path: Path to the Excel file (.xls or .xlsx).
        sheet_name: Name of the sheet to parse. If None, reads all sheets.
        
    Returns:
        DataFrame with cleaned student data.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file format is not supported.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.xls':
        return _parse_xls(file_path, sheet_name)
    elif file_ext in ['.xlsx', '.xlsm']:
        return _parse_xlsx(file_path, sheet_name)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")


def _parse_xls(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Parse an .xls file (BIFF format)."""
    # Use xlrd engine for .xls files
    xls = pd.ExcelFile(file_path, engine='xlrd')
    
    if sheet_name is None:
        sheet_name = xls.sheet_names[0]
    
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=1, engine='xlrd')
    return _clean_dataframe(df)


def _parse_xlsx(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Parse an .xlsx file (Office Open XML format)."""
    # Use openpyxl engine for .xlsx files
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    
    if sheet_name is None:
        sheet_name = xls.sheet_names[0]
    
    # First read to detect format (check if it has 2-row header)
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine='openpyxl')
    fmt = detect_excel_format(df_raw)
    
    # Liberal format has 2-row headers, use header=None
    if fmt == 'liberal':
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine='openpyxl')
    else:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=1, engine='openpyxl')
    
    return _clean_dataframe(df)


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize the DataFrame."""
    # Detect format
    fmt = detect_excel_format(df)
    
    if fmt == 'new':
        return _clean_new_format(df)
    elif fmt == 'liberal':
        return _clean_liberal_format(df)
    else:
        return _clean_old_format(df)


def _clean_new_format(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the new format Excel (61 columns).
    
    Column structure:
    0: 学校, 1: 学号, 2: 考号, 3: 座位号, 4: 学籍号
    5: 班级, 6: 姓名, 7: 选考科目, 8: 外语类型
    9-15: 总分 (原始分, 赋分, 全体排名, 区县排名, 年级排名, 班级排名, 档次)
    16-21: 语文 (得分, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    22-27: 数学 (得分, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    28-33: 英语 (得分, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    34-39: 物理 (得分, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    40-46: 化学 (原始分, 赋分, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    47-53: 生物 (原始分, 赋分, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    54-60: 地理 (原始分, 赋分, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    """
    # Define column mapping for new format
    column_names = {
        0: 'school',
        1: 'student_id',
        2: 'exam_id',
        3: 'seat_number',
        4: 'enrollment_id',
        5: 'class_id',
        6: 'name',
        7: 'optional_subject',  # 选考科目
        8: 'foreign_lang_type',  # 外语类型
        # Total scores
        9: 'total_raw',
        10: 'total_scaled',
        11: 'total_all_rank',
        12: 'total_district_rank',
        13: 'total_school_rank',
        14: 'total_class_rank',
        15: 'total_level',
        # Chinese
        16: 'chinese',
        17: 'chinese_exam_rank',
        18: 'chinese_district_rank',
        19: 'chinese_school_rank',
        20: 'chinese_class_rank',
        21: 'chinese_level',
        # Math
        22: 'math',
        23: 'math_exam_rank',
        24: 'math_district_rank',
        25: 'math_school_rank',
        26: 'math_class_rank',
        27: 'math_level',
        # English
        28: 'english',
        29: 'english_exam_rank',
        30: 'english_district_rank',
        31: 'english_school_rank',
        32: 'english_class_rank',
        33: 'english_level',
        # Physics
        34: 'physics',
        35: 'physics_exam_rank',
        36: 'physics_district_rank',
        37: 'physics_school_rank',
        38: 'physics_class_rank',
        39: 'physics_level',
        # Chemistry
        40: 'chemistry_raw',
        41: 'chemistry',
        42: 'chemistry_exam_rank',
        43: 'chemistry_district_rank',
        44: 'chemistry_school_rank',
        45: 'chemistry_class_rank',
        46: 'chemistry_level',
        # Biology
        47: 'biology_raw',
        48: 'biology',
        49: 'biology_exam_rank',
        50: 'biology_district_rank',
        51: 'biology_school_rank',
        52: 'biology_class_rank',
        53: 'biology_level',
        # Geography
        54: 'geography_raw',
        55: 'geography',
        56: 'geography_exam_rank',
        57: 'geography_district_rank',
        58: 'geography_school_rank',
        59: 'geography_class_rank',
        60: 'geography_level',
    }
    
    # Rename columns
    new_columns = {}
    for i, col in enumerate(df.columns):
        if i in column_names:
            new_columns[col] = column_names[i]
    
    df = df.rename(columns=new_columns)
    
    # Remove rows with NaN in critical columns
    df = df.dropna(subset=['name', 'class_id'])
    
    # Convert numeric columns
    numeric_cols = [
        'class_id', 'total_raw', 'total_scaled', 'total_school_rank', 'total_class_rank',
        'chinese', 'chinese_school_rank', 'chinese_class_rank',
        'math', 'math_school_rank', 'math_class_rank',
        'english', 'english_school_rank', 'english_class_rank',
        'physics', 'physics_school_rank', 'physics_class_rank',
        'chemistry_raw', 'chemistry', 'chemistry_school_rank', 'chemistry_class_rank',
        'biology_raw', 'biology', 'biology_school_rank', 'biology_class_rank',
        'geography_raw', 'geography', 'geography_school_rank', 'geography_class_rank',
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def _clean_liberal_format(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the liberal arts format Excel (54 columns, 文科).
    
    Column structure:
    0: 学校, 1: 学号, 2: 考号, 3: 座位号, 4: 学籍号
    5: 班级, 6: 姓名, 7: 选考科目, 8: 外语类型
    9-15: 总分 (原始分, 赋分, 全体排名, 区县排名, 年级排名, 班级排名, 档次)
    16-21: 语文 (分数, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    22-27: 数学 (分数, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    28-33: 英语 (分数, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    34-40: 政治 (原始分, 赋分, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    41-46: 历史 (分数, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    47-53: 地理 (原始分, 赋分, 联考排名, 区县排名, 年级排名, 班级排名, 档次)
    """
    # Skip the first two rows (headers)
    df = df.iloc[2:].copy()
    df = df.reset_index(drop=True)
    
    # Define column mapping for liberal arts format
    column_names = {
        0: 'school',
        1: 'student_id',
        2: 'exam_id',
        3: 'seat_number',
        4: 'enrollment_id',
        5: 'class_id',
        6: 'name',  # 姓名
        7: 'optional_subject',  # 选考科目
        8: 'foreign_lang_type',  # 外语类型
        # Total scores
        9: 'total_raw',
        10: 'total_scaled',
        11: 'total_all_rank',
        12: 'total_district_rank',
        13: 'total_school_rank',
        14: 'total_class_rank',
        15: 'total_level',
        # Chinese
        16: 'chinese',
        17: 'chinese_exam_rank',
        18: 'chinese_district_rank',
        19: 'chinese_school_rank',
        20: 'chinese_class_rank',
        21: 'chinese_level',
        # Math
        22: 'math',
        23: 'math_exam_rank',
        24: 'math_district_rank',
        25: 'math_school_rank',
        26: 'math_class_rank',
        27: 'math_level',
        # English
        28: 'english',
        29: 'english_exam_rank',
        30: 'english_district_rank',
        31: 'english_school_rank',
        32: 'english_class_rank',
        33: 'english_level',
        # Politics (政治) - with raw and scaled
        34: 'politics_raw',
        35: 'politics',
        36: 'politics_exam_rank',
        37: 'politics_district_rank',
        38: 'politics_school_rank',
        39: 'politics_class_rank',
        40: 'politics_level',
        # History (历史)
        41: 'history',
        42: 'history_exam_rank',
        43: 'history_district_rank',
        44: 'history_school_rank',
        45: 'history_class_rank',
        46: 'history_level',
        # Geography (with raw and scaled)
        47: 'geography_raw',
        48: 'geography',
        49: 'geography_exam_rank',
        50: 'geography_district_rank',
        51: 'geography_school_rank',
        52: 'geography_class_rank',
        53: 'geography_level',
    }
    
    # Rename columns
    df = df.rename(columns=column_names)
    
    # Keep only necessary columns
    keep_cols = [
        'school', 'student_id', 'exam_id', 'class_id', 'name',
        'optional_subject', 'foreign_lang_type',
        'total_raw', 'total_scaled',
        'total_school_rank', 'total_class_rank',
        'chinese', 'chinese_school_rank', 'chinese_class_rank',
        'math', 'math_school_rank', 'math_class_rank',
        'english', 'english_school_rank', 'english_class_rank',
        'politics_raw', 'politics', 'politics_school_rank', 'politics_class_rank',
        'history', 'history_school_rank', 'history_class_rank',
        'geography_raw', 'geography', 'geography_school_rank', 'geography_class_rank',
    ]
    
    # Filter to existing columns
    keep_cols = [c for c in keep_cols if c in df.columns]
    df = df[keep_cols]
    
    # Convert numeric columns
    numeric_cols = [
        'total_raw', 'total_scaled', 'total_school_rank', 'total_class_rank',
        'chinese', 'chinese_school_rank', 'chinese_class_rank',
        'math', 'math_school_rank', 'math_class_rank',
        'english', 'english_school_rank', 'english_class_rank',
        'politics_raw', 'politics', 'politics_school_rank', 'politics_class_rank',
        'history', 'history_school_rank', 'history_class_rank',
        'geography_raw', 'geography', 'geography_school_rank', 'geography_class_rank',
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def _clean_old_format(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the old format Excel (32 columns)."""
    # Define column mapping for old format
    column_names = [
        'name', 'class_id', 'student_id', 'exam_id',
        'total_raw', 'total_scaled',
        'chinese_school_rank', 'chinese_class_rank', 'chinese',
        'english_school_rank', 'english_class_rank', 'english',
        'math_school_rank', 'math_class_rank', 'math',
        'physics_school_rank', 'physics_class_rank', 'physics',
        'chemistry_school_rank', 'chemistry_class_rank', 'chemistry_raw', 'chemistry',
        'biology_school_rank', 'biology_class_rank', 'biology_raw', 'biology',
    ]
    
    # Only rename columns that exist
    num_cols = min(len(column_names), len(df.columns))
    new_column_names = list(df.columns[:num_cols])
    for i in range(num_cols):
        new_column_names[i] = column_names[i]
    
    df.columns = new_column_names + list(df.columns[num_cols:])
    
    # Remove rows with NaN in critical columns
    df = df.dropna(subset=['name', 'class_id'])
    
    # Convert numeric columns
    for i, col in enumerate(df.columns):
        if i >= 4:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def parse_all_sheets(file_path: str) -> dict[str, pd.DataFrame]:
    """Parse all sheets in an Excel file.
    
    Args:
        file_path: Path to the Excel file.
        
    Returns:
        Dictionary with sheet names as keys and DataFrames as values.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine engine based on file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    engine = 'xlrd' if file_ext == '.xls' else 'openpyxl'
    
    xls = pd.ExcelFile(file_path, engine=engine)
    result = {}
    
    for sheet_name in xls.sheet_names:
        df = parse_excel(file_path, sheet_name)
        result[sheet_name] = df
    
    return result


def get_student_by_id(df: pd.DataFrame, student_id: str) -> Optional[pd.Series]:
    """Get a student's data by student ID.
    
    Args:
        df: DataFrame containing student data.
        student_id: Student ID to search for.
        
    Returns:
        Series containing student data, or None if not found.
    """
    matches = df[df['student_id'] == student_id]
    if len(matches) > 0:
        return matches.iloc[0]
    return None


def get_students_by_class(df: pd.DataFrame, class_id: int) -> pd.DataFrame:
    """Get all students in a specific class.
    
    Args:
        df: DataFrame containing student data.
        class_id: Class ID to filter by.
        
    Returns:
        DataFrame containing students in the specified class.
    """
    return df[df['class_id'] == class_id]


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"Parsing file: {file_path}")
        
        try:
            df = parse_excel(file_path)
            print(f"Loaded {len(df)} students")
            print(f"Columns: {list(df.columns)}")
            print(df.head())
        except Exception as e:
            print(f"Error: {e}")
