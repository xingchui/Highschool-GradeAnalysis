"""
Excel Parser Module

This module handles parsing of Excel files containing student grade data.
Supports both .xls and .xlsx formats.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

import pandas as pd
import os
import re
from typing import Optional, Dict


# Column keyword patterns for new format (61+ cols) header matching.
# Used by _clean_new_format() to dynamically detect column positions.
_NEW_FORMAT_PATTERNS = {
    'school': ['学校'],
    'student_id': ['学号'],
    'exam_id': ['考号'],
    'seat_number': ['座位号'],
    'enrollment_id': ['学籍号'],
    'class_id': ['班级'],
    'name': ['姓名'],
    'optional_subject': ['选考科目', '选科'],
    'foreign_lang_type': ['外语类型', '小语种'],
    # Total scores - only specific patterns (broad patterns like '总分' cause false matches)
    'total_raw': ['总分(物理)-分数', '总分-分数', '总分(原始分)-分数'],
    'total_scaled': ['总分(物理)(赋分)-分数', '总分(赋分)-分数'],
    'total_all_rank': ['总分(物理)(赋分)-方向全体名次', '总分(物理)-方向全体名次', '总分(赋分)-方向全体名次', '总分-方向全体名次'],
    'total_district_rank': ['总分(物理)(赋分)-方向偃师区名次', '总分(物理)-方向偃师区名次', '总分(赋分)-方向偃师区名次', '总分-方向偃师区名次'],
    'total_school_rank': ['总分(物理)(赋分)-方向校名次', '总分(物理)-方向校名次', '总分(赋分)-方向校名次', '总分-方向校名次'],
    'total_class_rank': ['总分(物理)(赋分)-方向班名次', '总分(物理)-方向班名次', '总分(赋分)-方向班名次', '总分-方向班名次'],
    'total_level': ['总分(物理)(赋分)-等级', '总分(物理)-等级', '总分(赋分)-等级', '总分-等级', '档次'],
    # Chinese - only specific patterns
    'chinese': ['语文-分数'],
    'chinese_exam_rank': ['语文-方向全体名次'],
    'chinese_district_rank': ['语文-方向偃师区名次'],
    'chinese_school_rank': ['语文-方向校名次'],
    'chinese_class_rank': ['语文-方向班名次'],
    'chinese_level': ['语文-等级'],
    # Math
    'math': ['数学-分数'],
    'math_exam_rank': ['数学-方向全体名次'],
    'math_district_rank': ['数学-方向偃师区名次'],
    'math_school_rank': ['数学-方向校名次'],
    'math_class_rank': ['数学-方向班名次'],
    'math_level': ['数学-等级'],
    # English
    'english': ['英语-分数'],
    'english_exam_rank': ['英语-方向全体名次'],
    'english_district_rank': ['英语-方向偃师区名次'],
    'english_school_rank': ['英语-方向校名次'],
    'english_class_rank': ['英语-方向班名次'],
    'english_level': ['英语-等级'],
    # Physics
    'physics': ['物理-分数'],
    'physics_exam_rank': ['物理-方向全体名次'],
    'physics_district_rank': ['物理-方向偃师区名次'],
    'physics_school_rank': ['物理-方向校名次'],
    'physics_class_rank': ['物理-方向班名次'],
    'physics_level': ['物理-等级'],
    # Chemistry - convention: {subject}=赋分, {subject}_raw=原始分
    'chemistry': ['化学(赋分)-分数'],
    'chemistry_raw': ['化学-分数'],
    'chemistry_exam_rank': ['化学(赋分)-方向全体名次', '化学-方向全体名次'],
    'chemistry_district_rank': ['化学(赋分)-方向偃师区名次', '化学-方向偃师区名次'],
    'chemistry_school_rank': ['化学(赋分)-方向校名次', '化学-方向校名次'],
    'chemistry_class_rank': ['化学(赋分)-方向班名次', '化学-方向班名次'],
    'chemistry_level': ['化学(赋分)-等级', '化学-等级'],
    # Biology
    'biology': ['生物(赋分)-分数'],
    'biology_raw': ['生物-分数'],
    'biology_exam_rank': ['生物(赋分)-方向全体名次', '生物-方向全体名次'],
    'biology_district_rank': ['生物(赋分)-方向偃师区名次', '生物-方向偃师区名次'],
    'biology_school_rank': ['生物(赋分)-方向校名次', '生物-方向校名次'],
    'biology_class_rank': ['生物(赋分)-方向班名次', '生物-方向班名次'],
    'biology_level': ['生物(赋分)-等级', '生物-等级'],
    # Geography
    'geography': ['地理(赋分)-分数'],
    'geography_raw': ['地理-分数'],
    'geography_exam_rank': ['地理(赋分)-方向全体名次', '地理-方向全体名次'],
    'geography_district_rank': ['地理(赋分)-方向偃师区名次', '地理-方向偃师区名次'],
    'geography_school_rank': ['地理(赋分)-方向校名次', '地理-方向校名次'],
    'geography_class_rank': ['地理(赋分)-方向班名次', '地理-方向班名次'],
    'geography_level': ['地理(赋分)-等级', '地理-等级'],
    # Politics
    'politics': ['政治(赋分)-分数'],
    'politics_raw': ['政治-分数'],
    'politics_exam_rank': ['政治(赋分)-方向全体名次', '政治-方向全体名次'],
    'politics_district_rank': ['政治(赋分)-方向偃师区名次', '政治-方向偃师区名次'],
    'politics_school_rank': ['政治(赋分)-方向校名次', '政治-方向校名次'],
    'politics_class_rank': ['政治(赋分)-方向班名次', '政治-方向班名次'],
    'politics_level': ['政治(赋分)-等级', '政治-等级'],
}


def detect_excel_format(df: pd.DataFrame) -> str:
    """Detect the Excel format based on column structure.
    
    Args:
        df: Raw DataFrame from Excel.
        
    Returns:
        Format type: 'new' (61 cols), 'liberal' (50-59 cols),
                     'print' (38-45 cols, 打印版), or 'old' (32 cols)
    """
    col_count = len(df.columns)
    if col_count >= 60:
        return 'new'
    elif col_count >= 50:
        return 'liberal'
    elif 38 <= col_count <= 45:
        # Check if it looks like print format (has 班级/考号/姓名 in row 0)
        row0 = [str(x) for x in df.iloc[0]]
        if '班级' in ' '.join(row0) and '考号' in ' '.join(row0):
            return 'print'
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


def _find_header_rows(df_raw: pd.DataFrame):
    """Find the header rows (may be 1 or 2 rows) by looking for key column names.
    
    For files like qzwlmc.xlsx, headers span TWO rows that need merging.
    Row 1: 学校, 班级, 学号, 姓名, 总分(物理)(赋分), 语文, 数学, ...
    Row 2: (empty), (empty), (empty), (empty), (empty), 分数, 全体名次, 校名次, 班名次, ...
    
    Args:
        df_raw: Raw DataFrame read with header=None.
        
    Returns:
        List of row indices to merge as header.
    """
    header_rows = []
    header_keywords = ['班级', '姓名', '学校', '考号', 'student_id', 'class_id', 'name', '分数', '名次']
    
    for i, row in df_raw.iterrows():
        row_str = ' '.join(str(x) for x in row if pd.notna(x))
        if any(keyword in row_str for keyword in header_keywords):
            header_rows.append(i)
            if len(header_rows) >= 2:  # Max 2 header rows
                break
    
    if not header_rows:
        return [1]  # Default
    
    return header_rows


def _parse_xlsx(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Parse an .xlsx file (Office Open XML format)."""
    # Use openpyxl engine for .xlsx files
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    
    if sheet_name is None:
        sheet_name = xls.sheet_names[0]
    
    # Read once without header for format detection
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine='openpyxl')
    
    # Detect format to decide header handling
    fmt = detect_excel_format(df_raw)
    
    if fmt == 'liberal':
        # Liberal arts format: 2-row header, data starts at row 2 (0-indexed)
        df = df_raw
    elif fmt == 'print':
        # Print format: single header row, data starts at row 1
        df = df_raw
    elif fmt == 'new':
        # New format: detect and merge two-row headers
        header_rows = _find_header_rows(df_raw)
        
        if len(header_rows) >= 2:
            # Re-read with merged headers
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_rows, engine='openpyxl')
            
            # Merge MultiIndex columns into single-level header
            if isinstance(df.columns, pd.MultiIndex):
                merged_cols = []
                for col in df.columns:
                    part1 = str(col[0]).strip() if pd.notna(col[0]) else ''
                    part2 = str(col[1]).strip() if pd.notna(col[1]) else ''
                    
                    if part1 and part2:
                        if 'Unnamed' in part2:
                            merged_cols.append(part1)
                        elif 'Unnamed' in part1:
                            merged_cols.append(part2)
                        else:
                            merged_cols.append(f"{part1}-{part2}")
                    elif part1:
                        merged_cols.append(part1)
                    elif part2:
                        merged_cols.append(part2)
                    else:
                        merged_cols.append('')
                
                df.columns = merged_cols
        else:
            header_row = header_rows[0]
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row, engine='openpyxl')
    else:
        # Old format: single header row
        header_rows = _find_header_rows(df_raw)
        header_row = header_rows[0]
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row, engine='openpyxl')
    
    return _clean_dataframe(df)


def _clean_class_id(series: pd.Series) -> pd.Series:
    """Clean class_id values: strip '.0' suffix from numeric conversion."""
    def _clean_value(x):
        if pd.isna(x):
            return None
        s = str(x)
        # Only strip trailing '.0', not all occurrences
        if s.endswith('.0'):
            s = s[:-2]
        if s.isdigit():
            return s
        return str(x) if pd.notna(x) else None
    return series.apply(_clean_value)


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize the DataFrame."""
    fmt = detect_excel_format(df)
    
    if fmt == 'new':
        df = _clean_new_format(df)
    elif fmt == 'liberal':
        df = _clean_liberal_format(df)
    elif fmt == 'print':
        df = _clean_print_format(df)
    else:
        df = _clean_old_format(df)
    
    # Add _scaled aliases for consistent column naming across all formats
    _add_scaled_aliases(df)
    # Ensure student_id exists for trend analysis
    _ensure_student_id(df)
    return df


def _add_scaled_aliases(df: pd.DataFrame) -> pd.DataFrame:
    """Add _scaled alias columns for all subjects that have raw/scaled distinction.
    
    Convention: {subject} = 赋分 (scaled score), {subject}_raw = 原始分 (raw score)
    This adds {subject}_scaled as an alias for {subject} for backward compatibility.
    
    Returns:
        The modified DataFrame (for chaining consistency).
    """
    for subject in ['chemistry', 'biology', 'geography', 'politics']:
        if subject in df.columns and subject + '_scaled' not in df.columns:
            df[subject + '_scaled'] = df[subject]
    return df


def _ensure_student_id(df: pd.DataFrame) -> None:
    """Ensure student_id column exists.
    
    Priority: 学号 > 考号 > 复合标识(name+class_id)
    
    If student_id (学号) is missing but exam_id (考号) exists,
    use exam_id as student_id. This handles files like qzwlmc.xlsx
    that only have 考号.
    """
    if 'student_id' not in df.columns:
        if 'exam_id' in df.columns:
            # Use exam_id (考号) as student_id
            df['student_id'] = df['exam_id'].astype(str).str.strip()
        elif 'name' in df.columns and 'class_id' in df.columns:
            # Last resort: composite ID
            df['student_id'] = df['class_id'].astype(str) + '_' + df['name'].astype(str)
        elif 'name' in df.columns:
            df['student_id'] = df['name'].astype(str)
        else:
            # Absolute fallback: generate sequential IDs
            df['student_id'] = [f'student_{i}' for i in range(len(df))]


def _clean_new_format(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the new format Excel (61 columns).
    
    Dynamically detects column positions by header names instead of fixed positions.
    Supports different column orders in Excel files.
    """
    # Build mapping: column_index -> new_name
    # Use list to preserve order and handle duplicates
    column_mapping = {}  # col_idx -> new_name
    target_assigned = set()  # Track which targets have been assigned (to avoid duplicates)
    
    for col_idx, col_name in enumerate(df.columns):
        col_str = str(col_name).strip()
        
        # Skip empty or NaN columns
        if not col_str or col_str.lower() in ['nan', 'none', '']:
            continue
        
        # Try to match with patterns - prioritize exact matches
        matched_target = None
        best_match_type = 0  # 0=none, 1=contains, 2=exact
        
        for target_col, patterns in _NEW_FORMAT_PATTERNS.items():
            if target_col in target_assigned:
                continue  # Skip already-assigned targets
            
            for pattern in patterns:
                if '*' in pattern:
                    if re.search(pattern, col_str, re.IGNORECASE):
                        matched_target = target_col
                        best_match_type = 2  # Regex = high priority
                        break
                elif pattern == col_str:
                    # Exact match = highest priority
                    matched_target = target_col
                    best_match_type = 3
                    break
                elif pattern in col_str or col_str in pattern:
                    # Substring match = lower priority
                    if best_match_type < 2:
                        matched_target = target_col
                        best_match_type = 1
        
        if matched_target:
            column_mapping[col_idx] = matched_target
            target_assigned.add(matched_target)
    
    # Rename columns
    rename_dict = {}
    for idx, new_name in column_mapping.items():
        if idx < len(df.columns):
            old_name = df.columns[idx]
            rename_dict[old_name] = new_name
    
    if rename_dict:
        df = df.rename(columns=rename_dict)
    
    # Drop all "Unnamed" columns that weren't mapped
    unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col) or str(col).startswith('Unnamed')]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)
    
    # Remove rows with NaN in critical columns
    if 'name' in df.columns and 'class_id' in df.columns:
        df = df.dropna(subset=['name', 'class_id'])
    
    # Convert numeric columns (excluding class_id which is string)
    numeric_cols = [
        'total_raw', 'total_scaled', 'total_school_rank', 'total_class_rank',
        'chinese', 'chinese_school_rank', 'chinese_class_rank',
        'math', 'math_school_rank', 'math_class_rank',
        'english', 'english_school_rank', 'english_class_rank',
        'physics', 'physics_school_rank', 'physics_class_rank',
        'chemistry_raw', 'chemistry', 'chemistry_scaled', 'chemistry_school_rank', 'chemistry_class_rank',
        'biology_raw', 'biology', 'biology_scaled', 'biology_school_rank', 'biology_class_rank',
        'geography_raw', 'geography', 'geography_scaled', 'geography_school_rank', 'geography_class_rank',
        'politics_raw', 'politics', 'politics_scaled', 'politics_school_rank', 'politics_class_rank',
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            # Ensure we're working with a Series, not DataFrame (handle duplicate column names)
            if isinstance(df[col], pd.DataFrame):
                # Take the first column if there are duplicates
                df[col] = pd.to_numeric(df[col].iloc[:, 0], errors='coerce')
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Ensure class_id is string type (remove '.0' suffix from numeric conversion)
    if 'class_id' in df.columns:
        df['class_id'] = _clean_class_id(df['class_id'])
    
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
    """Clean the old format Excel (32 columns).
    
    Column structure:
    0: name, 1: class_id, 2: student_id, 3: exam_id
    4-5: total_raw, total_scaled
    6-7: total_school_rank, total_class_rank
    8-10: chinese (score, school_rank, class_rank)
    11-13: math (score, school_rank, class_rank)
    14-16: english (score, school_rank, class_rank)
    17-19: physics (score, school_rank, class_rank)
    20-23: chemistry (raw, scaled, school_rank, class_rank)
    24-27: biology (raw, scaled, school_rank, class_rank)
    28-31: history/liberal arts subject (raw, scaled, school_rank, class_rank) - often 0 for science students
    """
    column_names = [
        'name', 'class_id', 'student_id', 'exam_id',
        'total_raw', 'total_scaled',
        'total_school_rank', 'total_class_rank',
        'chinese', 'chinese_school_rank', 'chinese_class_rank',
        'math', 'math_school_rank', 'math_class_rank',
        'english', 'english_school_rank', 'english_class_rank',
        'physics', 'physics_school_rank', 'physics_class_rank',
        'chemistry_raw', 'chemistry', 'chemistry_school_rank', 'chemistry_class_rank',
        'biology_raw', 'biology', 'biology_school_rank', 'biology_class_rank',
        'history_raw', 'history', 'history_school_rank', 'history_class_rank',
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


def _clean_print_format(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the print format Excel (41 columns, 总分(物理)_学生成绩打印版.xlsx).
    
    Single header row with positional columns.
    Column structure:
    0: 班级, 1: 考号, 2: 姓名
    3-5: 总分(物理)(赋分) (分数, 班名, 校名)
    6-8: 总分(物理) 原始分 (分数, 班名, 校名)
    9-11: 语文 (分数, 班名, 校名)
    12-14: 数学 (分数, 班名, 校名)
    15-17: 英语 (分数, 班名, 校名)
    18-20: 物理 (分数, 班名, 校名)
    21-23: 化学(赋分) (分数, 班名, 校名)
    24-26: 化学 原始分 (分数, 班名, 校名)
    27-29: 生物(赋分) (分数, 班名, 校名)
    30-32: 生物 原始分 (分数, 班名, 校名)
    33-35: 地理(赋分) (分数, 班名, 校名)
    36-38: 地理 原始分 (分数, 班名, 校名)
    39: 语书 (语文书写得分)
    40: 英书 (英语书写得分)
    
    '班名'/'校名' are ambiguous - they follow the nearest subject column.
    """
    # Skip header row, data starts at row 1
    df = df.iloc[1:].copy()
    df = df.reset_index(drop=True)
    
    # Direct positional mapping
    column_names = [
        'class_id',
        'exam_id',
        'name',
        # Total scaled (赋分)
        'total_scaled', 'total_class_rank', 'total_school_rank',
        # Total raw (原始分)
        'total_raw', 'total_raw_class_rank', 'total_raw_school_rank',
        # Chinese
        'chinese', 'chinese_class_rank', 'chinese_school_rank',
        # Math
        'math', 'math_class_rank', 'math_school_rank',
        # English
        'english', 'english_class_rank', 'english_school_rank',
        # Physics
        'physics', 'physics_class_rank', 'physics_school_rank',
        # Chemistry scaled
        'chemistry', 'chemistry_class_rank', 'chemistry_school_rank',
        # Chemistry raw
        'chemistry_raw', 'chemistry_raw_class_rank', 'chemistry_raw_school_rank',
        # Biology scaled
        'biology', 'biology_class_rank', 'biology_school_rank',
        # Biology raw
        'biology_raw', 'biology_raw_class_rank', 'biology_raw_school_rank',
        # Geography scaled
        'geography', 'geography_class_rank', 'geography_school_rank',
        # Geography raw
        'geography_raw', 'geography_raw_class_rank', 'geography_raw_school_rank',
        # Writing scores
        'chinese_writing',
        'english_writing',
    ]
    
    # Rename columns by position
    num_cols = min(len(column_names), len(df.columns))
    new_column_names = list(df.columns[:num_cols])
    for i in range(num_cols):
        new_column_names[i] = column_names[i]
    df.columns = new_column_names + list(df.columns[num_cols:])
    
    # Drop any remaining extra columns (beyond 41)
    extra_cols = [c for c in df.columns if c not in column_names]
    if extra_cols:
        df = df.drop(columns=extra_cols)
    
    # Remove rows with NaN in critical columns
    df = df.dropna(subset=['name', 'class_id'])
    
    # Convert numeric columns
    numeric_cols = [
        'total_raw', 'total_scaled', 'total_class_rank', 'total_school_rank',
        'total_raw_class_rank', 'total_raw_school_rank',
        'chinese', 'chinese_class_rank', 'chinese_school_rank',
        'math', 'math_class_rank', 'math_school_rank',
        'english', 'english_class_rank', 'english_school_rank',
        'physics', 'physics_class_rank', 'physics_school_rank',
        'chemistry', 'chemistry_class_rank', 'chemistry_school_rank',
        'chemistry_raw', 'chemistry_raw_class_rank', 'chemistry_raw_school_rank',
        'biology', 'biology_class_rank', 'biology_school_rank',
        'biology_raw', 'biology_raw_class_rank', 'biology_raw_school_rank',
        'geography', 'geography_class_rank', 'geography_school_rank',
        'geography_raw', 'geography_raw_class_rank', 'geography_raw_school_rank',
        'chinese_writing',
        'english_writing',
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Ensure class_id is string
    if 'class_id' in df.columns:
        df['class_id'] = _clean_class_id(df['class_id'])
    
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
