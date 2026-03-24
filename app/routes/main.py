"""
Main Routes Blueprint

Handles page rendering and core application routes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from werkzeug.utils import secure_filename
import os
import uuid
import pandas as pd
from io import BytesIO

import parser
import ranking
import grade_statistics as stats_module
import trend as trend_module

# Create blueprint
main_bp = Blueprint('main', __name__)


def get_data_service():
    """Get data service from app context.
    
    Returns:
        DataService instance.
    """
    return current_app.data_service


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed.
    
    Args:
        filename: Name of the file to check.
        
    Returns:
        True if extension is allowed, False otherwise.
    """
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@main_bp.route('/')
def index():
    """Home page - show upload form."""
    return render_template('index.html')


@main_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    data_service = get_data_service()
    
    if 'file' not in request.files:
        flash('未选择文件', 'error')
        return redirect(url_for('main.index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('未选择文件', 'error')
        return redirect(url_for('main.index'))
    
    # Get original filename first to check extension
    original_filename = file.filename
    
    if file and allowed_file(original_filename):
        # Generate a safe filename but keep extension
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        safe_name = secure_filename(original_filename)
        
        # If secure_filename removes everything, generate a random name
        if not safe_name or safe_name == '_':
            safe_name = f"grade_{uuid.uuid4().hex[:8]}"
        
        # Generate unique filename to allow multiple uploads with same name
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{safe_name}_{unique_id}.{file_ext}"
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Parse Excel file
            result = parser.parse_all_sheets(filepath)
            df = pd.concat(result.values(), ignore_index=True)
            
            # Store data in data service (session-bound)
            display_name = original_filename
            data_service.load_file(display_name, df, filename)
            data_service.set_current_file(display_name)
            
            flash(f'成功加载 {len(df)} 名学生数据来自 {original_filename}', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            flash(f'解析文件出错: {str(e)}', 'error')
            return redirect(url_for('main.index'))
    
    flash('无效的文件类型，请上传 .xls 或 .xlsx 文件', 'error')
    return redirect(url_for('main.index'))


@main_bp.route('/dashboard')
def dashboard():
    """Show dashboard with rankings and statistics."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))
    
    # Calculate rankings
    ranked_data = ranking.calculate_rankings(current_data, 'total_scaled')
    
    # Get top students
    top_students = ranking.get_top_students(ranked_data, 'total_scaled', 20)
    
    # Get school statistics
    school_stats = stats_module.calculate_school_line_stats(current_data)
    
    # Get class statistics
    class_stats = stats_module.calculate_class_line_stats(current_data)
    
    return render_template('dashboard.html',
                         top_students=top_students.to_dict('records'),
                         school_stats=school_stats,
                         class_stats=class_stats.to_dict('records'),
                         filename=data_service.get_current_filename(),
                         total_students=len(current_data),
                         loaded_files=data_service.get_file_list())


@main_bp.route('/rankings')
def rankings_page():
    """Show all student rankings."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))
    
    # Calculate rankings
    ranked_data = ranking.calculate_rankings(current_data, 'total_scaled')
    ranked_data = ranked_data.sort_values('total_scaled_school_rank')
    
    # Get page number
    page = request.args.get('page', 1, type=int)
    per_page = 50
    start = (page - 1) * per_page
    end = start + per_page
    
    total_pages = (len(ranked_data) + per_page - 1) // per_page
    
    return render_template('rankings.html',
                         students=ranked_data.iloc[start:end].to_dict('records'),
                         page=page,
                         total_pages=total_pages,
                         filename=data_service.get_current_filename(),
                         loaded_files=data_service.get_file_list())


@main_bp.route('/statistics')
def statistics_page():
    """Show statistics page with line analysis."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))
    
    # Get selection parameters
    optional_subject = request.args.get('optional_subject', 'physics')
    total_type = request.args.get('total_type', 'scaled')
    
    # Get available subjects in the data
    available_subjects = stats_module.get_available_subjects(current_data)
    
    # Determine the actual optional subject based on available data
    if optional_subject == 'physics' and not available_subjects.get('has_physics', False):
        if available_subjects.get('has_history', False):
            optional_subject = 'history'
        else:
            optional_subject = 'physics'  # Keep selection, filter will handle gracefully
    
    # Get all statistics with selection
    all_stats = stats_module.calculate_all_subject_stats(
        current_data, 
        total_type=total_type,
        optional_subject=optional_subject
    )
    
    # Get class statistics for all subjects
    class_stats = stats_module.calculate_class_all_subject_stats(
        current_data,
        total_type=total_type,
        optional_subject=optional_subject
    )
    
    # Get configuration
    config = stats_module.load_config()
    
    return render_template('statistics.html',
                         school_stats=all_stats,
                         class_stats=class_stats.to_dict('records'),
                         config=config,
                         filename=data_service.get_current_filename(),
                         optional_subject=optional_subject,
                         total_type=total_type,
                         available_subjects=available_subjects,
                         loaded_files=data_service.get_file_list())


def get_float(value, default):
    """Convert string to float, return default if empty or invalid."""
    try:
        result = float(value) if value else default
        return result if result else default
    except (ValueError, TypeError):
        return default


@main_bp.route('/config', methods=['GET', 'POST'])
def config_page():
    """Handle configuration settings."""
    if request.method == 'POST':
        # Update configuration
        config = stats_module.load_config()
        
        # Update total_raw lines
        config['lines']['total_raw'] = {
            '985': get_float(request.form.get('total_raw_985'), 600),
            '211': get_float(request.form.get('total_raw_211'), 550),
            'yiben': get_float(request.form.get('total_raw_yiben'), 500)
        }
        
        # Update total_scaled lines
        config['lines']['total_scaled'] = {
            '985': get_float(request.form.get('total_scaled_985'), 600),
            '211': get_float(request.form.get('total_scaled_211'), 550),
            'yiben': get_float(request.form.get('total_scaled_yiben'), 500)
        }
        
        # Update Chinese lines
        config['lines']['chinese'] = {
            '985': get_float(request.form.get('chinese_985'), 120),
            '211': get_float(request.form.get('chinese_211'), 110),
            'yiben': get_float(request.form.get('chinese_yiben'), 105)
        }
        
        # Update Math lines
        config['lines']['math'] = {
            '985': get_float(request.form.get('math_985'), 120),
            '211': get_float(request.form.get('math_211'), 110),
            'yiben': get_float(request.form.get('math_yiben'), 105)
        }
        
        # Update English lines
        config['lines']['english'] = {
            '985': get_float(request.form.get('english_985'), 120),
            '211': get_float(request.form.get('english_211'), 110),
            'yiben': get_float(request.form.get('english_yiben'), 105)
        }
        
        # Update Physics lines
        config['lines']['physics'] = {
            '985': get_float(request.form.get('physics_985'), 90),
            '211': get_float(request.form.get('physics_211'), 80),
            'yiben': get_float(request.form.get('physics_yiben'), 70)
        }
        
        # Update History lines
        config['lines']['history'] = {
            '985': get_float(request.form.get('history_985'), 90),
            '211': get_float(request.form.get('history_211'), 80),
            'yiben': get_float(request.form.get('history_yiben'), 70)
        }
        
        # Update Chemistry raw/scaled lines
        config['lines']['chemistry_raw'] = {
            '985': get_float(request.form.get('chemistry_raw_985'), 90),
            '211': get_float(request.form.get('chemistry_raw_211'), 80),
            'yiben': get_float(request.form.get('chemistry_raw_yiben'), 70)
        }
        config['lines']['chemistry_scaled'] = {
            '985': get_float(request.form.get('chemistry_scaled_985'), 90),
            '211': get_float(request.form.get('chemistry_scaled_211'), 80),
            'yiben': get_float(request.form.get('chemistry_scaled_yiben'), 70)
        }
        
        # Update Biology raw/scaled lines
        config['lines']['biology_raw'] = {
            '985': get_float(request.form.get('biology_raw_985'), 90),
            '211': get_float(request.form.get('biology_raw_211'), 80),
            'yiben': get_float(request.form.get('biology_raw_yiben'), 70)
        }
        config['lines']['biology_scaled'] = {
            '985': get_float(request.form.get('biology_scaled_985'), 90),
            '211': get_float(request.form.get('biology_scaled_211'), 80),
            'yiben': get_float(request.form.get('biology_scaled_yiben'), 70)
        }
        
        # Update Politics raw/scaled lines
        config['lines']['politics_raw'] = {
            '985': get_float(request.form.get('politics_raw_985'), 90),
            '211': get_float(request.form.get('politics_raw_211'), 80),
            'yiben': get_float(request.form.get('politics_raw_yiben'), 70)
        }
        config['lines']['politics_scaled'] = {
            '985': get_float(request.form.get('politics_scaled_985'), 90),
            '211': get_float(request.form.get('politics_scaled_211'), 80),
            'yiben': get_float(request.form.get('politics_scaled_yiben'), 70)
        }
        
        # Update Geography raw/scaled lines
        config['lines']['geography_raw'] = {
            '985': get_float(request.form.get('geography_raw_985'), 90),
            '211': get_float(request.form.get('geography_raw_211'), 80),
            'yiben': get_float(request.form.get('geography_raw_yiben'), 70)
        }
        config['lines']['geography_scaled'] = {
            '985': get_float(request.form.get('geography_scaled_985'), 90),
            '211': get_float(request.form.get('geography_scaled_211'), 80),
            'yiben': get_float(request.form.get('geography_scaled_yiben'), 70)
        }
        
        stats_module.save_config(config)
        flash('配置保存成功', 'success')
        return redirect(url_for('main.statistics_page'))
    
    config = stats_module.load_config()
    return render_template('config.html', config=config)


@main_bp.route('/student/<student_id>')
def student_detail(student_id):
    """Show detailed information for a specific student."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))
    
    ranked_data = ranking.calculate_rankings(current_data, 'total_scaled')
    student = ranking.get_student_rank(ranked_data, student_id)
    
    if student is None:
        flash(f'未找到学生 {student_id}', 'error')
        return redirect(url_for('main.rankings_page'))
    
    return render_template('student.html', student=student)


@main_bp.route('/trend')
def trend_page():
    """Show trend analysis page."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    # Get parameters for two-exam comparison
    exam1 = request.args.get('exam1', '')
    exam2 = request.args.get('exam2', '')
    class_id = request.args.get('class_id', '')
    rank_type = request.args.get('rank_type', 'school')
    
    # Get parameters for student trend
    student_query = request.args.get('student_query', '')
    student_rank_type = request.args.get('student_rank_type', 'school')
    
    # Load exam data into trend module from data service
    for display_name in data_service.get_file_list():
        if display_name not in trend_module.get_exam_list():
            # Use the actual saved filename (with UUID)
            file_info = data_service.get_file_info(display_name)
            if file_info:
                actual_filename = file_info.get('saved_filename', display_name)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], actual_filename)
                if os.path.exists(filepath):
                    trend_module.load_exam_data(filepath, display_name)
    
    # Get comparison results if both exams selected
    comparison_results = []
    summary = {}
    if exam1 and exam2 and exam1 != exam2:
        file_list = data_service.get_file_list()
        if exam1 in file_list and exam2 in file_list:
            comparison_results = trend_module.compare_two_exams(exam1, exam2, class_id, rank_type)
            if class_id:
                summary = trend_module.get_class_rank_change_summary(exam1, exam2, class_id)
    
    # Get student trend if query provided
    student_trend = []
    if student_query:
        students = trend_module.get_student_by_id_or_name(student_query)
        if students:
            # Get trend for first match
            student_id = students[0]['student_id']
            # Get trend for all exams
            all_trend = trend_module.get_student_trend(student_id=student_id, rank_type=student_rank_type)
            
            # Filter by selected exams if provided
            trend_exams_param = request.args.getlist('trend_exams') if request.args.get('trend_exams') else None
            if trend_exams_param:
                student_trend = [t for t in all_trend if t['exam'] in trend_exams_param]
            else:
                student_trend = all_trend
    
    # Get available classes
    available_classes = trend_module.get_available_classes() if exam1 and exam2 else []
    
    return render_template('trend.html', 
                         loaded_files=data_service.get_file_list(),
                         current_file=data_service.get_current_filename(),
                         exam1=exam1,
                         exam2=exam2,
                         class_id=class_id,
                         rank_type=rank_type,
                         comparison_results=comparison_results,
                         summary=summary,
                         student_query=student_query,
                         student_rank_type=student_rank_type,
                         student_trend=student_trend,
                         available_classes=available_classes)


@main_bp.route('/download_statistics')
def download_statistics():
    """Download statistics as Excel file."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))
    
    # Get selection parameters
    optional_subject = request.args.get('optional_subject', 'physics')
    total_type = request.args.get('total_type', 'scaled')
    
    # Get class statistics
    class_stats = stats_module.calculate_class_all_subject_stats(
        current_data,
        total_type=total_type,
        optional_subject=optional_subject
    )
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        class_stats.to_excel(writer, sheet_name='Class Stats', index=False)
    
    output.seek(0)
    
    # Generate filename with ASCII only
    filename = f"statistics_{optional_subject}_{total_type}.xlsx"
    
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@main_bp.route('/select_file/<filename>')
def select_file(filename):
    """Select which file to use as current."""
    data_service = get_data_service()
    data_service.set_current_file(filename)
    flash(f'已切换到 {filename}', 'success')
    return redirect(request.referrer or url_for('main.dashboard'))


@main_bp.route('/about')
def about():
    """Show about page."""
    return render_template('about.html')
