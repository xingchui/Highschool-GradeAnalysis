"""
API Routes Blueprint

Handles API endpoints for data retrieval and chart generation.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

from flask import Blueprint, jsonify, current_app, request, g
from flask_wtf.csrf import CSRFProtect
from functools import wraps
import logging
import ranking
import grade_statistics as stats_module
import charts as charts_module

# Create blueprint
api_bp = Blueprint('api', __name__)

# Exempt the entire API blueprint from CSRF protection
# This will be applied when blueprint is registered
csrf_exempt_applied = False

logger = logging.getLogger(__name__)


def require_api_key(f):
    """Decorator to require API key authentication.
    
    API key can be provided via:
    - Header: X-API-Key
    - Query parameter: api_key
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from config
        api_key = current_app.config.get('API_KEY')
        
        # If no API key configured, skip authentication (development mode)
        if not api_key:
            return f(*args, **kwargs)
        
        # Check for API key in request
        provided_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not provided_key or provided_key != api_key:
            return jsonify({'error': 'Unauthorized: Invalid or missing API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


def handle_api_error(f):
    """Decorator to handle API errors and return JSON responses."""
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {f.__name__}: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    wrapper.__name__ = f.__name__
    return wrapper


def get_data_service():
    """Get data service from session context.
    
    Returns:
        Session-bound DataService instance.
    """
    from flask import g
    return current_app.session_data_service.get_data_service()


@api_bp.route('/stats')
@require_api_key
def api_stats():
    """API endpoint for statistics data."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    school_stats = stats_module.calculate_school_line_stats(current_data)
    return jsonify(school_stats)


@api_bp.route('/rankings')
@require_api_key
def api_rankings():
    """API endpoint for rankings data."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    ranked_data = ranking.calculate_rankings(current_data, 'total_scaled')
    ranked_data = ranked_data.sort_values('total_scaled_school_rank')
    
    return jsonify(ranked_data.to_dict('records'))


# ==================== Chart API Endpoints ====================

@api_bp.route('/charts/list')
def api_chart_list():
    """API endpoint for available chart types."""
    return jsonify(charts_module.get_chart_list())


@api_bp.route('/charts/subjects')
def api_chart_subjects():
    """API endpoint for available subjects in current data."""
    from app.core import GradeAnalysisService
    
    data_service = get_data_service()
    grade_service = GradeAnalysisService(data_service)
    
    subjects = grade_service.get_subjects_list()
    pairs = grade_service.get_scatter_subjects_pairs()
    
    return jsonify({
        'subjects': subjects,
        'scatter_pairs': pairs
    })


@api_bp.route('/charts/generate', methods=['POST'])
@require_api_key
def api_chart_generate():
    """API endpoint to generate a chart."""
    from app.core import GradeAnalysisService
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        data_service = get_data_service()
        grade_service = GradeAnalysisService(data_service)
        
        chart_type = request.json.get('chart_type')
        params = request.json.get('params', {})
        
        if not chart_type:
            return jsonify({'error': 'chart_type is required'}), 400
        
        chart_html = grade_service.generate_chart(chart_type, **params)
        
        return jsonify({
            'chart_html': chart_html,
            'chart_type': chart_type
        })
    except Exception as e:
        logger.error(f"Chart generation error: {e}", exc_info=True)
        return jsonify({'error': f'图表生成失败: {str(e)}'}), 500


@api_bp.route('/charts/box')
@require_api_key
@handle_api_error
def api_chart_box():
    """API endpoint for box plot chart."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    score_column = request.args.get('score_column', 'total_scaled')
    group_column = request.args.get('group_column', 'class_id')
    
    chart_html = charts_module.create_box_plot(
        current_data, score_column, group_column
    )
    
    return jsonify({'chart_html': chart_html})


@api_bp.route('/charts/heatmap')
@require_api_key
@handle_api_error
def api_chart_heatmap():
    """API endpoint for heatmap chart."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    subjects = request.args.getlist('subjects')
    aggfunc = request.args.get('aggfunc', 'mean')
    
    chart_html = charts_module.create_heatmap(
        current_data, columns_subjects=subjects if subjects else None,
        aggfunc=aggfunc
    )
    
    return jsonify({'chart_html': chart_html})


@api_bp.route('/charts/scatter')
@require_api_key
@handle_api_error
def api_chart_scatter():
    """API endpoint for scatter plot chart."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    x_col = request.args.get('x_col', 'math')
    y_col = request.args.get('y_col', 'physics')
    show_regression = request.args.get('show_regression', 'true').lower() == 'true'
    
    chart_html = charts_module.create_scatter_with_regression(
        current_data, x_col, y_col, show_regression=show_regression
    )
    
    return jsonify({'chart_html': chart_html})


@api_bp.route('/charts/violin')
@require_api_key
@handle_api_error
def api_chart_violin():
    """API endpoint for violin plot chart."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    score_column = request.args.get('score_column', 'total_scaled')
    group_column = request.args.get('group_column', 'class_id')
    
    chart_html = charts_module.create_violin_plot(
        current_data, score_column, group_column
    )
    
    return jsonify({'chart_html': chart_html})


@api_bp.route('/charts/correlation')
@require_api_key
@handle_api_error
def api_chart_correlation():
    """API endpoint for correlation matrix chart."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    subjects = request.args.getlist('subjects')
    
    chart_html = charts_module.create_correlation_matrix(
        current_data, subject_columns=subjects if subjects else None
    )
    
    return jsonify({'chart_html': chart_html})


@api_bp.route('/charts/distribution')
@require_api_key
@handle_api_error
def api_chart_distribution():
    """API endpoint for score distribution chart."""
    from app.core import GradeAnalysisService
    
    data_service = get_data_service()
    grade_service = GradeAnalysisService(data_service)
    
    current_data = data_service.get_current_data()
    if current_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    score_column = request.args.get('score_column', 'total_scaled')
    
    # Get line config from current config
    config = grade_service.load_config()
    line_config = config.get('lines', {}).get(score_column, {})
    
    chart_html = charts_module.create_score_distribution_by_line(
        current_data, score_column, line_config=line_config
    )
    
    return jsonify({'chart_html': chart_html})
