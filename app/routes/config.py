"""
Config Blueprint

Handles configuration settings pages.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

from typing import Union
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response

import grade_statistics as stats_module
from app.utils import get_float

# Create blueprint
config_bp = Blueprint('config', __name__)


@config_bp.route('/config', methods=['GET', 'POST'])
def config_page() -> Union[str, Response]:
    """Handle configuration settings.

    GET: Display configuration form.
    POST: Save configuration changes.

    Returns:
        Rendered config.html template or redirect after save.
    """
    if request.method == 'POST':
        config = stats_module.load_config()

        # Update all line configurations
        config['lines']['total_raw'] = {
            '985': get_float(request.form.get('total_raw_985'), 600),
            '211': get_float(request.form.get('total_raw_211'), 550),
            'yiben': get_float(request.form.get('total_raw_yiben'), 500)
        }
        config['lines']['total_scaled'] = {
            '985': get_float(request.form.get('total_scaled_985'), 600),
            '211': get_float(request.form.get('total_scaled_211'), 550),
            'yiben': get_float(request.form.get('total_scaled_yiben'), 500)
        }
        config['lines']['chinese'] = {
            '985': get_float(request.form.get('chinese_985'), 120),
            '211': get_float(request.form.get('chinese_211'), 110),
            'yiben': get_float(request.form.get('chinese_yiben'), 105)
        }
        config['lines']['math'] = {
            '985': get_float(request.form.get('math_985'), 120),
            '211': get_float(request.form.get('math_211'), 110),
            'yiben': get_float(request.form.get('math_yiben'), 105)
        }
        config['lines']['english'] = {
            '985': get_float(request.form.get('english_985'), 120),
            '211': get_float(request.form.get('english_211'), 110),
            'yiben': get_float(request.form.get('english_yiben'), 105)
        }
        config['lines']['physics'] = {
            '985': get_float(request.form.get('physics_985'), 90),
            '211': get_float(request.form.get('physics_211'), 80),
            'yiben': get_float(request.form.get('physics_yiben'), 70)
        }
        config['lines']['history'] = {
            '985': get_float(request.form.get('history_985'), 90),
            '211': get_float(request.form.get('history_211'), 80),
            'yiben': get_float(request.form.get('history_yiben'), 70)
        }
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
        return redirect(url_for('statistics.statistics_page'))

    config = stats_module.load_config()
    return render_template('config.html', config=config)
