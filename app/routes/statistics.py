"""
Statistics Blueprint

Handles statistics and line analysis pages.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

from typing import Union
from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
import pandas as pd

import grade_statistics as stats_module
from app.routes.main import get_data_service

# Create blueprint
statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/statistics')
def statistics_page() -> str:
    """Show statistics page with line analysis.

    Returns:
        Rendered statistics.html template.
    """
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))

    optional_subject = request.args.get('optional_subject', 'physics')
    total_type = request.args.get('total_type', 'scaled')
    available_subjects = stats_module.get_available_subjects(current_data)

    if optional_subject == 'physics' and not available_subjects.get('has_physics', False):
        if available_subjects.get('has_history', False):
            optional_subject = 'history'
        else:
            optional_subject = 'physics'

    all_stats = stats_module.calculate_all_subject_stats(
        current_data, total_type=total_type, optional_subject=optional_subject
    )
    class_stats = stats_module.calculate_class_all_subject_stats(
        current_data, total_type=total_type, optional_subject=optional_subject
    )
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


@statistics_bp.route('/download_statistics')
def download_statistics() -> Response:
    """Download statistics as Excel file.

    Returns:
        Excel file response.
    """
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))

    optional_subject = request.args.get('optional_subject', 'physics')
    total_type = request.args.get('total_type', 'scaled')
    class_stats = stats_module.calculate_class_all_subject_stats(
        current_data, total_type=total_type, optional_subject=optional_subject
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        class_stats.to_excel(writer, sheet_name='Class Stats', index=False)
    excel_bytes = output.getvalue()

    filename = f"statistics_{optional_subject}_{total_type}.xlsx"
    return Response(
        excel_bytes,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
