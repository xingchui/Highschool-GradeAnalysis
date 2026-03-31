"""
Main Routes Blueprint

Handles page rendering and core application routes.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

from typing import Union
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from werkzeug.utils import secure_filename
import os
import uuid
import pandas as pd
from io import BytesIO

import parser
import ranking
import grade_statistics as stats_module
import charts as charts_module
from app.core import GradeAnalysisService
from app.utils import allowed_file
from report_service import ReportDataService
from report_pdf import generate_pdf_report
from report_excel import generate_excel_report_bytes

# Create blueprint
main_bp = Blueprint('main', __name__)


def get_data_service():
    """Get data service from session context.

    Returns:
        Session-bound DataService instance.
    """
    return current_app.session_data_service.get_data_service()


@main_bp.route('/')
def index() -> str:
    """Home page - show upload form.

    Returns:
        Rendered index.html template.
    """
    return render_template('index.html')


@main_bp.route('/upload', methods=['POST'])
def upload_file() -> Union[str, Response]:
    """Handle file upload - supports multiple files.

    Returns:
        Redirect to dashboard on success, index on failure.
    """
    data_service = get_data_service()

    if 'files' in request.files:
        files = request.files.getlist('files')
    elif 'file' in request.files and request.files['file'].filename:
        files = [request.files['file']]
    else:
        flash('未选择文件', 'error')
        return redirect(url_for('main.index'))

    files = [f for f in files if f and f.filename]
    if not files:
        flash('未选择文件', 'error')
        return redirect(url_for('main.index'))

    success_count = 0
    error_files = []
    loaded_files_info = []

    for file in files:
        original_filename = file.filename
        if not allowed_file(original_filename):
            error_files.append(f'{original_filename} (无效格式)')
            continue
        try:
            file_ext = original_filename.rsplit('.', 1)[1].lower()
            safe_name = secure_filename(original_filename)
            if not safe_name or safe_name == '_':
                safe_name = f"grade_{uuid.uuid4().hex[:8]}"
            unique_id = uuid.uuid4().hex[:8]
            filename = f"{safe_name}_{unique_id}.{file_ext}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            result = parser.parse_all_sheets(filepath)
            if isinstance(result, dict):
                df = pd.concat(result.values(), ignore_index=True)
            elif isinstance(result, list):
                df = pd.concat(result, ignore_index=True)
            elif isinstance(result, pd.DataFrame):
                df = result
            else:
                raise ValueError(f'Unknown parser return type: {type(result)}')
            display_name = original_filename
            data_service.load_file(display_name, df, filename)
            loaded_files_info.append((display_name, len(df)))
            success_count += 1
        except Exception as e:
            error_files.append(f'{original_filename} ({str(e)})')

    if loaded_files_info:
        data_service.set_current_file(loaded_files_info[0][0])

    if success_count > 0:
        if success_count == 1:
            flash(f'成功加载 {loaded_files_info[0][1]} 名学生数据', 'success')
        else:
            total_students = sum(info[1] for info in loaded_files_info)
            flash(f'成功加载 {success_count} 个文件，共 {total_students} 名学生数据', 'success')

    if error_files:
        flash(f'以下文件加载失败: {"; ".join(error_files)}', 'warning')

    if success_count > 0:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.index'))


@main_bp.route('/dashboard')
def dashboard() -> str:
    """Show dashboard with rankings and statistics.

    Returns:
        Rendered dashboard.html template.
    """
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))
    ranked_data = ranking.calculate_rankings(current_data, 'total_scaled')
    top_students = ranking.get_top_students(ranked_data, 'total_scaled', 20)
    school_stats = stats_module.calculate_school_line_stats(current_data)
    class_stats = stats_module.calculate_class_line_stats(current_data)
    return render_template('dashboard.html',
                           top_students=top_students.to_dict('records'),
                           school_stats=school_stats,
                           class_stats=class_stats.to_dict('records'),
                           filename=data_service.get_current_filename(),
                           total_students=len(current_data),
                           loaded_files=data_service.get_file_list())


@main_bp.route('/select_file/<filename>')
def select_file(filename: str) -> Response:
    """Select a file as the current active file.

    Args:
        filename: Display name of the file to select.

    Returns:
        Redirect to dashboard or referrer.
    """
    data_service = get_data_service()
    data_service.set_current_file(filename)
    flash(f'已切换到 {filename}', 'success')
    return redirect(request.referrer or url_for('main.dashboard'))


@main_bp.route('/analysis')
def analysis_page() -> str:
    """Show advanced chart analysis page.

    Returns:
        Rendered analysis.html template.
    """
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))
    grade_service = GradeAnalysisService(data_service)
    chart_list = charts_module.get_chart_list()
    ranked_data = ranking.calculate_rankings(current_data, 'total_scaled')
    top_students = ranking.get_top_students(ranked_data, 'total_scaled', 10)
    class_stats = stats_module.calculate_class_line_stats(current_data)
    top_students_chart = charts_module.create_top_students_chart(current_data, 'total_scaled', 10)
    line_rate_chart = charts_module.create_line_passing_rate_chart(class_stats.to_dict('records'))
    return render_template('analysis.html', chart_list=chart_list, top_students_chart=top_students_chart,
                           line_rate_chart=line_rate_chart, filename=data_service.get_current_filename(),
                           loaded_files=data_service.get_file_list())


@main_bp.route('/about')
def about() -> str:
    """Show about page.

    Returns:
        Rendered about.html template.
    """
    return render_template('about.html')


@main_bp.route('/report/download_pdf')
def download_report_pdf() -> Union[str, Response]:
    """Download complete report as PDF.

    Returns:
        PDF file response or redirect on error.
    """
    import tempfile
    data_service = get_data_service()
    current_data = data_service.get_current_data()

    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))

    optional_subject = request.args.get('optional_subject', 'physics')
    total_type = request.args.get('total_type', 'scaled')

    report_service = ReportDataService(data_service, filename=data_service.get_current_filename())
    report_data = report_service.get_report_data({
        'optional_subject': optional_subject,
        'total_type': total_type,
        'top_n': 20
    })

    chart_images = report_service.get_chart_images()

    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            temp_path = tmp.name

        generate_pdf_report(report_data, temp_path, chart_images)

        with open(temp_path, 'rb') as f:
            pdf_content = f.read()

        os.unlink(temp_path)

        filename = f"report_{data_service.get_current_filename().replace('.xls', '').replace('.xlsx', '')}.pdf"

        return Response(
            pdf_content,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        flash(f'PDF生成失败: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/report/download_excel')
def download_report_excel() -> Union[str, Response]:
    """Download enhanced report as Excel.

    Returns:
        Excel file response or redirect on error.
    """
    data_service = get_data_service()
    current_data = data_service.get_current_data()

    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))

    optional_subject = request.args.get('optional_subject', 'physics')
    total_type = request.args.get('total_type', 'scaled')

    report_service = ReportDataService(data_service, filename=data_service.get_current_filename())
    report_data = report_service.get_report_data({
        'optional_subject': optional_subject,
        'total_type': total_type,
        'top_n': 20
    })

    try:
        excel_content = generate_excel_report_bytes(report_data)
        filename = f"report_{data_service.get_current_filename().replace('.xls', '').replace('.xlsx', '')}.xlsx"

        return Response(
            excel_content,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        flash(f'Excel生成失败: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))
