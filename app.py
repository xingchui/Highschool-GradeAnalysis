"""
Flask Web Application for Grade Analysis

Main application file that handles routes and serves HTML templates.
"""

import os
import json
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, Response
from werkzeug.utils import secure_filename

# Import local modules
import parser
import ranking
import grade_statistics as stats_module
import trend as trend_module
from io import BytesIO

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'grade-analysis-secret-key'

# Configuration
UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variable to store loaded data
# Store multiple files: {filename: DataFrame}
loaded_files = {}
# Map display name to actual file path (for trend analysis)
file_paths = {}
# Current selected file key
current_file_key = None


def get_current_data():
    """Get the currently selected data."""
    global loaded_files, current_file_key
    if current_file_key and current_file_key in loaded_files:
        return loaded_files[current_file_key]
    # Fallback to first file if available
    if loaded_files:
        first_key = list(loaded_files.keys())[0]
        return loaded_files[first_key]
    return None


def get_current_filename():
    """Get the currently selected filename."""
    global current_file_key
    return current_file_key


def set_current_file(filename):
    """Set the current file as selected."""
    global current_file_key
    if filename in loaded_files:
        current_file_key = filename


def allowed_file(filename):
    """Check if file extension is allowed."""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page - show upload form."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    global current_data, current_filename
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    # Get original filename first to check extension
    original_filename = file.filename
    
    if file and allowed_file(original_filename):
        # Generate a safe filename but keep extension
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        safe_name = secure_filename(original_filename)
        # If secure_filename removes everything, generate a random name
        if not safe_name or safe_name == '_':
            import uuid
            safe_name = f"grade_{uuid.uuid4().hex[:8]}"
        
        # Generate unique filename to allow multiple uploads with same name
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{safe_name}_{unique_id}.{file_ext}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Parse Excel file
            result = parser.parse_all_sheets(filepath)
            df = pd.concat(result.values(), ignore_index=True)
            
            # Use original filename as key for display
            display_name = original_filename
            loaded_files[display_name] = df
            # Store the actual file path for trend analysis
            file_paths[display_name] = filename
            set_current_file(display_name)
            
            flash(f'Successfully loaded {len(df)} students from {original_filename}', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error parsing file: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload .xls or .xlsx files.', 'error')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """Show dashboard with rankings and statistics."""
    current_data = get_current_data()
    
    if current_data is None:
        flash('Please upload a file first', 'warning')
        return redirect(url_for('index'))
    
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
                         filename=get_current_filename(),
                         total_students=len(current_data),
                         loaded_files=list(loaded_files.keys()))


@app.route('/rankings')
def rankings_page():
    """Show all student rankings."""
    current_data = get_current_data()
    
    if current_data is None:
        flash('Please upload a file first', 'warning')
        return redirect(url_for('index'))
    
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
                         filename=get_current_filename(),
                         loaded_files=list(loaded_files.keys()))


@app.route('/statistics')
def statistics_page():
    """Show statistics page with line analysis."""
    current_data = get_current_data()
    
    if current_data is None:
        flash('Please upload a file first', 'warning')
        return redirect(url_for('index'))
    
    # Get selection parameters
    optional_subject = request.args.get('optional_subject', 'physics')
    total_type = request.args.get('total_type', 'scaled')
    
    # Get available subjects in the data
    available_subjects = stats_module.get_available_subjects(current_data)
    
    # Determine the actual optional subject based on available data
    # If user selects physics but no physics column, try history, else use whatever exists
    if optional_subject == 'physics' and not available_subjects.get('has_physics', False):
        if available_subjects.get('has_history', False):
            optional_subject = 'history'
        else:
            # No physics or history, try to determine from data
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
                         filename=get_current_filename(),
                         optional_subject=optional_subject,
                         total_type=total_type,
                         available_subjects=available_subjects,
                         loaded_files=list(loaded_files.keys()))


def get_float(value, default):
    """Convert string to float, return default if empty or invalid."""
    try:
        result = float(value) if value else default
        return result if result else default
    except (ValueError, TypeError):
        return default


@app.route('/config', methods=['GET', 'POST'])
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
        flash('Configuration saved successfully', 'success')
        return redirect(url_for('statistics_page'))
    
    config = stats_module.load_config()
    return render_template('config.html', config=config)


@app.route('/student/<student_id>')
def student_detail(student_id):
    """Show detailed information for a specific student."""
    current_data = get_current_data()
    
    if current_data is None:
        flash('Please upload a file first', 'warning')
        return redirect(url_for('index'))
    
    ranked_data = ranking.calculate_rankings(current_data, 'total_scaled')
    student = ranking.get_student_rank(ranked_data, student_id)
    
    if student is None:
        flash(f'Student {student_id} not found', 'error')
        return redirect(url_for('rankings_page'))
    
    return render_template('student.html', student=student)


@app.route('/trend')
def trend_page():
    """Show trend analysis page."""
    current_data = get_current_data()
    
    # Get parameters for two-exam comparison
    exam1 = request.args.get('exam1', '')
    exam2 = request.args.get('exam2', '')
    class_id = request.args.get('class_id', '')
    rank_type = request.args.get('rank_type', 'school')
    
    # Get parameters for student trend
    student_query = request.args.get('student_query', '')
    student_rank_type = request.args.get('student_rank_type', 'school')
    
    # Load exam data into trend module
    for display_name in loaded_files.keys():
        if display_name not in trend_module.get_exam_list():
            # Use the actual saved filename (with UUID)
            actual_filename = file_paths.get(display_name, display_name)
            filepath = os.path.join(UPLOAD_FOLDER, actual_filename)
            if os.path.exists(filepath):
                trend_module.load_exam_data(filepath, display_name)
    
    # Get comparison results if both exams selected
    comparison_results = []
    summary = {}
    if exam1 and exam2 and exam1 != exam2 and exam1 in loaded_files and exam2 in loaded_files:
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
                         loaded_files=list(loaded_files.keys()),
                         current_file=get_current_filename(),
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


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics data."""
    current_data = get_current_data()
    
    if current_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    school_stats = stats_module.calculate_school_line_stats(current_data)
    return jsonify(school_stats)


@app.route('/api/rankings')
def api_rankings():
    """API endpoint for rankings data."""
    current_data = get_current_data()
    
    if current_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    ranked_data = ranking.calculate_rankings(current_data, 'total_scaled')
    ranked_data = ranked_data.sort_values('total_scaled_school_rank')
    
    return jsonify(ranked_data.to_dict('records'))


@app.route('/download_statistics')
def download_statistics():
    """Download statistics as Excel file."""
    current_data = get_current_data()
    
    if current_data is None:
        flash('Please upload a file first', 'warning')
        return redirect(url_for('index'))
    
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


@app.route('/select_file/<filename>')
def select_file(filename):
    """Select which file to use as current."""
    set_current_file(filename)
    flash(f'Switched to {filename}', 'success')
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/about')
def about():
    """Show about page."""
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
