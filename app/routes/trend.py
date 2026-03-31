"""
Trend Blueprint

Handles trend analysis and exam comparison pages.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

from typing import Union
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, Response
import os

import trend as trend_module
from app.routes.main import get_data_service

# Create blueprint
trend_bp = Blueprint('trend', __name__)


@trend_bp.route('/trend')
def trend_page() -> str:
    """Show trend analysis page with exam comparison and student trends.

    Returns:
        Rendered trend.html template.
    """
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))

    # Load exams that are present in uploaded data into trend module
    for display_name in data_service.get_file_list():
        if display_name not in trend_module.get_exam_list():
            file_info = data_service.get_file_info(display_name)
            if file_info:
                actual_filename = file_info.get('saved_filename', display_name)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], actual_filename)
                if os.path.exists(filepath):
                    trend_module.load_exam_data(filepath, display_name)

    exam1 = request.args.get('exam1', '')
    exam2 = request.args.get('exam2', '')
    class_id = request.args.get('class_id', '')
    rank_type = request.args.get('rank_type', 'school')

    comparison_results = []
    summary = {}
    if exam1 and exam2 and exam1 != exam2:
        if exam1 in data_service.get_file_list() and exam2 in data_service.get_file_list():
            comparison_results = trend_module.compare_two_exams(exam1, exam2, class_id, rank_type)
            if class_id:
                summary = trend_module.get_class_rank_change_summary(exam1, exam2, class_id)

    student_query = request.args.get('student_query', '')
    student_rank_type = request.args.get('student_rank_type', 'school')
    student_trend = []

    if student_query:
        students = trend_module.get_student_by_id_or_name(student_query)
        if students:
            student_id = students[0]['student_id']
            all_trend = trend_module.get_student_trend(student_id=student_id, rank_type=student_rank_type)
            trend_exams_param = request.args.getlist('trend_exams') if request.args.get('trend_exams') else None
            if trend_exams_param:
                student_trend = [t for t in all_trend if t['exam'] in trend_exams_param]
            else:
                student_trend = all_trend

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
