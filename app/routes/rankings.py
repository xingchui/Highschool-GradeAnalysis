"""
Rankings Blueprint

Handles student ranking and detail pages.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

from typing import Union
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response

import ranking
from app.routes.main import get_data_service

# Create blueprint
rankings_bp = Blueprint('rankings', __name__)


@rankings_bp.route('/rankings')
def rankings_page() -> str:
    """Show all student rankings with pagination.

    Returns:
        Rendered rankings.html template.
    """
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))
    ranked_data = ranking.calculate_rankings(current_data, 'total_scaled')
    ranked_data = ranked_data.sort_values('total_scaled_school_rank')
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


@rankings_bp.route('/student/<student_id>')
def student_detail(student_id: str) -> Union[str, Response]:
    """Show detailed information for a specific student.

    Args:
        student_id: The unique identifier of the student.

    Returns:
        Rendered student.html template or redirect if not found.
    """
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    if current_data is None:
        flash('请先上传文件', 'warning')
        return redirect(url_for('main.index'))

    ranked_data = ranking.calculate_rankings(current_data, 'total_scaled')
    student = ranking.get_student_rank(ranked_data, student_id)
    if student is None:
        flash(f'未找到学生 {student_id}', 'error')
        return redirect(url_for('rankings.rankings_page'))
    return render_template('student.html', student=student)
