"""
API Routes Blueprint

Handles API endpoints for data retrieval.
"""

from flask import Blueprint, jsonify, current_app
import ranking
import grade_statistics as stats_module

# Create blueprint
api_bp = Blueprint('api', __name__)


def get_data_service():
    """Get data service from app context.
    
    Returns:
        DataService instance.
    """
    return current_app.data_service


@api_bp.route('/stats')
def api_stats():
    """API endpoint for statistics data."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    school_stats = stats_module.calculate_school_line_stats(current_data)
    return jsonify(school_stats)


@api_bp.route('/rankings')
def api_rankings():
    """API endpoint for rankings data."""
    data_service = get_data_service()
    current_data = data_service.get_current_data()
    
    if current_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    ranked_data = ranking.calculate_rankings(current_data, 'total_scaled')
    ranked_data = ranked_data.sort_values('total_scaled_school_rank')
    
    return jsonify(ranked_data.to_dict('records'))
