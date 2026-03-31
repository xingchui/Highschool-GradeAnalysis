"""
Charts Module

This module generates interactive charts using Plotly.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import json


def create_score_trend_chart(trend_data: List[Dict], subject_name: str = "总分") -> str:
    """Create a line chart showing score trends.
    
    Args:
        trend_data: List of dictionaries with 'exam', 'score', and 'rank' keys.
        subject_name: Name of the subject being charted.
        
    Returns:
        HTML string of the chart.
    """
    if not trend_data:
        return "<p>No data available</p>"
    
    exams = [d['exam'] for d in trend_data]
    scores = [d['score'] for d in trend_data]
    ranks = [d['rank'] for d in trend_data if d.get('rank')]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add score line
    fig.add_trace(
        go.Scatter(x=exams, y=scores, name="分数", mode="lines+markers"),
        secondary_y=False
    )
    
    # Add rank line if available
    if ranks:
        fig.add_trace(
            go.Scatter(x=exams, y=ranks, name="排名", mode="lines+markers"),
            secondary_y=True
        )
    
    fig.update_layout(
        title=f"{subject_name}趋势图",
        xaxis_title="考试",
        yaxis_title="分数",
        hovermode="x unified"
    )
    
    fig.update_yaxes(title_text="分数", secondary_y=False)
    if ranks:
        fig.update_yaxes(title_text="排名", secondary_y=True, autorange="reversed")
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_class_comparison_chart(df: pd.DataFrame, class_ids: List[int], 
                                  score_column: str = 'total_scaled') -> str:
    """Create a bar chart comparing classes.
    
    Args:
        df: DataFrame with student data.
        class_ids: List of class IDs to compare.
        score_column: Column to compare.
        
    Returns:
        HTML string of the chart.
    """
    class_stats = []
    
    for class_id in class_ids:
        class_df = df[df['class_id'] == class_id]
        
        if score_column in class_df.columns:
            avg_score = class_df[score_column].mean()
            max_score = class_df[score_column].max()
            min_score = class_df[score_column].min()
            
            class_stats.append({
                'class': str(class_id),
                '平均分': round(avg_score, 2),
                '最高分': max_score,
                '最低分': min_score
            })
    
    fig = go.Figure(data=[
        go.Bar(name='平均分', x=[c['class'] for c in class_stats], y=[c['平均分'] for c in class_stats]),
        go.Bar(name='最高分', x=[c['class'] for c in class_stats], y=[c['最高分'] for c in class_stats]),
        go.Bar(name='最低分', x=[c['class'] for c in class_stats], y=[c['最低分'] for c in class_stats])
    ])
    
    fig.update_layout(
        barmode='group',
        title="班级成绩对比",
        xaxis_title="班级",
        yaxis_title="分数"
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_score_distribution_chart(df: pd.DataFrame, score_column: str = 'total_scaled',
                                   title: str = "成绩分布") -> str:
    """Create a histogram showing score distribution.
    
    Args:
        df: DataFrame with student data.
        score_column: Column to analyze.
        title: Chart title.
        
    Returns:
        HTML string of the chart.
    """
    if score_column not in df.columns:
        return "<p>No data available</p>"
    
    scores = df[score_column].dropna()
    
    fig = px.histogram(
        scores, 
        nbins=20,
        title=title,
        labels={'value': '分数', 'count': '人数'}
    )
    
    fig.update_layout(
        xaxis_title="分数",
        yaxis_title="人数",
        bargap=0.1
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_line_passing_rate_chart(class_stats: List[Dict]) -> str:
    """Create a chart showing line passing rates by class.
    
    Args:
        class_stats: List of dictionaries with class statistics.
        
    Returns:
        HTML string of the chart.
    """
    classes = [str(c['class_id']) for c in class_stats]
    rates_985 = [c.get('985_rate', 0) for c in class_stats]
    rates_211 = [c.get('211_rate', 0) for c in class_stats]
    rates_yiben = [c.get('yiben_rate', 0) for c in class_stats]
    
    fig = go.Figure(data=[
        go.Bar(name='985上线率', x=classes, y=rates_985),
        go.Bar(name='211上线率', x=classes, y=rates_211),
        go.Bar(name='一本上线率', x=classes, y=rates_yiben)
    ])
    
    fig.update_layout(
        barmode='group',
        title="班级上线率对比",
        xaxis_title="班级",
        yaxis_title="上线率 (%)"
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_subject_radar_chart(student_data: Dict, average_data: Optional[Dict] = None) -> str:
    """Create a radar chart for subject comparison.
    
    Args:
        student_data: Dictionary with subject scores.
        average_data: Dictionary with average scores (optional).
        
    Returns:
        HTML string of the chart.
    """
    subjects = list(student_data.keys())
    scores = list(student_data.values())
    
    fig = go.Figure()
    
    # Add student data
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=subjects,
        fill='toself',
        name='学生成绩'
    ))
    
    # Add average data if available
    if average_data:
        avg_scores = list(average_data.values())
        fig.add_trace(go.Scatterpolar(
            r=avg_scores,
            theta=subjects,
            fill='toself',
            name='年级平均'
        ))
    
    # Calculate max for y-axis range
    max_score = max(scores)
    if average_data:
        avg_scores = list(average_data.values())
        max_score = max(max_score, max(avg_scores))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_score]
            )
        ),
        showlegend=True,
        title="学科成绩雷达图"
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_top_students_chart(df: pd.DataFrame, score_column: str = 'total_scaled',
                             n: int = 10) -> str:
    """Create a horizontal bar chart of top students.
    
    Args:
        df: DataFrame with student data.
        score_column: Column to rank by.
        n: Number of top students to show.
        
    Returns:
        HTML string of the chart.
    """
    top_df = df.nlargest(n, score_column)
    
    fig = px.bar(
        top_df, 
        x=score_column, 
        y='name',
        orientation='h',
        title=f"全校前{n}名",
        labels={score_column: '分数', 'name': '姓名'}
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="分数",
        yaxis_title="学生"
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


# ==================== Wave 1: New Chart Types ====================

def create_box_plot(df: pd.DataFrame, score_column: str = 'total_scaled',
                    group_column: str = 'class_id', title: str = None) -> str:
    """Create a box plot showing score distribution with quartiles and outliers.
    
    箱线图展示数据的五数概括：最小值、Q1、中位数、Q3、最大值，以及异常值。
    适合用于比较不同班级/群体的成绩分布差异。
    
    Args:
        df: DataFrame with student data.
        score_column: Column to analyze (e.g., 'total_scaled', 'chinese').
        group_column: Column to group by (e.g., 'class_id').
        title: Chart title. Auto-generated if None.
        
    Returns:
        HTML string of the chart.
    """
    if score_column not in df.columns or group_column not in df.columns:
        return "<p>数据不可用</p>"
    
    if title is None:
        title = f"{score_column} 成绩分布箱线图"
    
    # Filter out NaN values
    plot_df = df[[score_column, group_column]].dropna()
    
    if plot_df.empty:
        return "<p>无有效数据</p>"
    
    # Create box plot
    fig = go.Figure()
    
    # Get unique groups sorted
    groups = sorted(plot_df[group_column].unique())
    
    for group in groups:
        group_data = plot_df[plot_df[group_column] == group][score_column]
        fig.add_trace(go.Box(
            y=group_data,
            name=str(group),
            boxpoints='outliers',  # Show only outliers
            jitter=0.3,
            pointpos=-1.8
        ))
    
    fig.update_layout(
        title=title,
        yaxis_title="分数",
        xaxis_title="班级" if group_column == 'class_id' else group_column,
        showlegend=False,
        boxmode='group'
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_heatmap(df: pd.DataFrame, index_col: str = 'class_id',
                   columns_subjects: List[str] = None,
                   aggfunc: str = 'mean', title: str = None) -> str:
    """Create a heatmap showing class × subject performance matrix.
    
    热力图用于展示班级×学科的成绩矩阵，颜色深浅表示分数高低。
    
    Args:
        df: DataFrame with student data.
        index_col: Column to use as rows (e.g., 'class_id').
        columns_subjects: List of subject columns to include.
        aggfunc: Aggregation function ('mean', 'median', 'max', 'min').
        title: Chart title. Auto-generated if None.
        
    Returns:
        HTML string of the chart.
    """
    if columns_subjects is None:
        # Default subjects
        columns_subjects = ['chinese', 'math', 'english', 'physics', 
                           'chemistry', 'biology', 'total_scaled']
    
    # Filter to existing columns
    available_cols = [c for c in columns_subjects if c in df.columns]
    if not available_cols or index_col not in df.columns:
        return "<p>数据不可用</p>"
    
    if title is None:
        title = "班级学科成绩热力图"
    
    # Create pivot table
    pivot_df = df.groupby(index_col)[available_cols].agg(aggfunc)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=[str(x) for x in pivot_df.index],
        colorscale='RdYlGn',  # Red (low) to Green (high)
        colorbar=dict(title="分数"),
        hoverongaps=False,
        text=np.round(pivot_df.values, 1),
        texttemplate="%{text}",
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="学科",
        yaxis_title="班级",
        height=max(400, len(pivot_df) * 30 + 100)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_scatter_with_regression(df: pd.DataFrame, x_col: str = 'math',
                                    y_col: str = 'physics', 
                                    color_col: str = 'class_id',
                                    show_regression: bool = True,
                                    title: str = None) -> str:
    """Create a scatter plot with optional regression line.
    
    散点图用于展示两个变量之间的关系，可添加回归线显示趋势。
    
    Args:
        df: DataFrame with student data.
        x_col: Column for X axis.
        y_col: Column for Y axis.
        color_col: Column for color grouping (optional).
        show_regression: Whether to show regression line.
        title: Chart title. Auto-generated if None.
        
    Returns:
        HTML string of the chart.
    """
    if x_col not in df.columns or y_col not in df.columns:
        return "<p>数据不可用</p>"
    
    if title is None:
        title = f"{x_col} vs {y_col} 相关性分析"
    
    # Filter out NaN values
    plot_df = df[[x_col, y_col] + ([color_col] if color_col and color_col in df.columns else [])].dropna()
    
    if plot_df.empty:
        return "<p>无有效数据</p>"
    
    # Create scatter plot
    if color_col and color_col in plot_df.columns:
        fig = px.scatter(
            plot_df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            labels={x_col: x_col, y_col: y_col},
            opacity=0.7
        )
    else:
        fig = px.scatter(
            plot_df,
            x=x_col,
            y=y_col,
            title=title,
            labels={x_col: x_col, y_col: y_col},
            opacity=0.7
        )
    
    # Add regression line if requested
    if show_regression:
        try:
            from scipy import stats
            
            x_data = plot_df[x_col].values
            y_data = plot_df[y_col].values
            
            # Calculate linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
            
            # Create regression line points
            x_range = np.linspace(x_data.min(), x_data.max(), 100)
            y_pred = slope * x_range + intercept
            
            fig.add_trace(go.Scatter(
                x=x_range,
                y=y_pred,
                mode='lines',
                name=f'回归线 (r={r_value:.3f})',
                line=dict(color='red', dash='dash')
            ))
            
            # Add annotation with regression equation
            fig.add_annotation(
                x=0.02, y=0.98,
                xref="paper", yref="paper",
                text=f"y = {slope:.2f}x + {intercept:.2f}<br>R² = {r_value**2:.3f}",
                showarrow=False,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="gray",
                borderwidth=1
            )
        except (ImportError, ValueError, Exception) as e:
            # Skip regression if scipy not available or calculation fails
            import logging
            logging.getLogger(__name__).warning(f"Regression calculation failed: {e}")
            pass
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        height=500
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_violin_plot(df: pd.DataFrame, score_column: str = 'total_scaled',
                       group_column: str = 'class_id', 
                       show_box: bool = True,
                       title: str = None) -> str:
    """Create a violin plot showing score distribution density.
    
    小提琴图结合了箱线图和核密度估计，展示数据分布的形态。
    
    Args:
        df: DataFrame with student data.
        score_column: Column to analyze.
        group_column: Column to group by.
        show_box: Whether to show inner box plot.
        title: Chart title. Auto-generated if None.
        
    Returns:
        HTML string of the chart.
    """
    if score_column not in df.columns or group_column not in df.columns:
        return "<p>数据不可用</p>"
    
    if title is None:
        title = f"{score_column} 成绩分布小提琴图"
    
    # Filter out NaN values
    plot_df = df[[score_column, group_column]].dropna()
    
    if plot_df.empty:
        return "<p>无有效数据</p>"
    
    fig = px.violin(
        plot_df,
        y=score_column,
        x=group_column,
        box=show_box,
        points="outliers",
        title=title,
        labels={score_column: '分数', group_column: '班级'}
    )
    
    fig.update_layout(
        xaxis_title="班级" if group_column == 'class_id' else group_column,
        yaxis_title="分数",
        height=500
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_multi_student_radar(students_data: List[Dict], 
                               subjects: List[str] = None,
                               title: str = None) -> str:
    """Create a radar chart comparing multiple students.
    
    多学生雷达图用于对比多个学生在各学科的表现。
    
    Args:
        students_data: List of dicts with student name and subject scores.
        subjects: List of subject names to include.
        title: Chart title. Auto-generated if None.
        
    Returns:
        HTML string of the chart.
    """
    if not students_data:
        return "<p>无数据</p>"
    
    if title is None:
        title = "多学生成绩对比雷达图"
    
    # Get all subjects if not specified
    if subjects is None:
        subjects = list(students_data[0].keys())
        subjects = [s for s in subjects if s not in ['name', 'student_id', 'class_id']]
    
    if not subjects:
        return "<p>无学科数据</p>"
    
    fig = go.Figure()
    
    # Add each student as a trace
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', 
              '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
    
    for i, student in enumerate(students_data):
        name = student.get('name', f'学生{i+1}')
        values = [student.get(s, 0) for s in subjects]
        # Close the polygon
        values.append(values[0])
        theta = subjects + [subjects[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=theta,
            fill='toself',
            name=name,
            line=dict(color=colors[i % len(colors)]),
            opacity=0.6
        ))
    
    # Calculate max for range
    max_val = 0
    for student in students_data:
        for s in subjects:
            val = student.get(s, 0)
            if val > max_val:
                max_val = val
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_val * 1.1]
            )
        ),
        showlegend=True,
        title=title,
        height=500
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_correlation_matrix(df: pd.DataFrame, 
                              subject_columns: List[str] = None,
                              title: str = None) -> str:
    """Create a correlation matrix heatmap for subjects.
    
    相关性矩阵展示各学科成绩之间的相关系数。
    
    Args:
        df: DataFrame with student data.
        subject_columns: List of subject columns to analyze.
        title: Chart title. Auto-generated if None.
        
    Returns:
        HTML string of the chart.
    """
    if subject_columns is None:
        subject_columns = ['chinese', 'math', 'english', 'physics', 
                          'chemistry', 'biology']
    
    # Filter to existing columns
    available_cols = [c for c in subject_columns if c in df.columns]
    
    if len(available_cols) < 2:
        return "<p>学科数据不足</p>"
    
    if title is None:
        title = "学科成绩相关性矩阵"
    
    # Calculate correlation matrix
    corr_matrix = df[available_cols].corr()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu_r',  # Red-Blue diverging
        zmin=-1,
        zmax=1,
        colorbar=dict(title="相关系数"),
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont={"size": 11}
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="学科",
        yaxis_title="学科",
        height=max(400, len(available_cols) * 50 + 100),
        width=max(500, len(available_cols) * 60 + 150)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_score_distribution_by_line(df: pd.DataFrame, 
                                      score_column: str = 'total_scaled',
                                      line_config: Dict = None,
                                      title: str = None) -> str:
    """Create a histogram with score line overlays.
    
    成绩分布图叠加分数线标记，直观展示各线达标情况。
    
    Args:
        df: DataFrame with student data.
        score_column: Column to analyze.
        line_config: Dict with line thresholds (e.g., {'985': 600, '211': 550}).
        title: Chart title. Auto-generated if None.
        
    Returns:
        HTML string of the chart.
    """
    if score_column not in df.columns:
        return "<p>数据不可用</p>"
    
    if title is None:
        title = f"{score_column} 成绩分布与分数线"
    
    scores = df[score_column].dropna()
    
    # Create histogram
    fig = px.histogram(
        scores,
        nbins=30,
        title=title,
        labels={'value': '分数', 'count': '人数'}
    )
    
    # Add score line markers if config provided
    if line_config:
        colors = {'985': '#FFD700', '211': '#C0C0C0', 'yiben': '#CD7F32'}
        for line_name, threshold in line_config.items():
            if threshold:
                fig.add_vline(
                    x=threshold,
                    line_dash="dash",
                    line_color=colors.get(line_name, 'red'),
                    annotation_text=f"{line_name}线: {threshold}",
                    annotation_position="top right"
                )
    
    fig.update_layout(
        xaxis_title="分数",
        yaxis_title="人数",
        bargap=0.1,
        height=450
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_class_rank_change_chart(comparison_data: List[Dict],
                                   title: str = None) -> str:
    """Create a chart showing class rank changes between exams.
    
    班级排名变化图展示各班级在两次考试间的排名变动。
    
    Args:
        comparison_data: List of dicts with class_id, rank_before, rank_after.
        title: Chart title. Auto-generated if None.
        
    Returns:
        HTML string of the chart.
    """
    if not comparison_data:
        return "<p>无数据</p>"
    
    if title is None:
        title = "班级排名变化对比"
    
    classes = [str(d['class_id']) for d in comparison_data]
    ranks_before = [d.get('rank_before', 0) for d in comparison_data]
    ranks_after = [d.get('rank_after', 0) for d in comparison_data]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='考试前排名',
        x=classes,
        y=ranks_before,
        marker_color='#636EFA'
    ))
    
    fig.add_trace(go.Bar(
        name='考试后排名',
        x=classes,
        y=ranks_after,
        marker_color='#EF553B'
    ))
    
    fig.update_layout(
        barmode='group',
        title=title,
        xaxis_title="班级",
        yaxis_title="排名（越低越好）",
        yaxis=dict(autorange="reversed"),  # Lower rank number is better
        height=450
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


# ==================== Chart Configuration ====================

# Chart themes configuration
CHART_THEMES = {
    'default': {
        'colors': ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A'],
        'paper_bgcolor': 'white',
        'plot_bgcolor': 'white',
        'font_color': '#333'
    },
    'dark': {
        'colors': ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A'],
        'paper_bgcolor': '#1a1a2e',
        'plot_bgcolor': '#16213e',
        'font_color': '#eee'
    },
    'colorful': {
        'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'],
        'paper_bgcolor': '#fafafa',
        'plot_bgcolor': '#ffffff',
        'font_color': '#2d3436'
    }
}


def apply_chart_theme(fig: go.Figure, theme: str = 'default') -> go.Figure:
    """Apply a theme to a Plotly figure.
    
    Args:
        fig: Plotly figure to style.
        theme: Theme name ('default', 'dark', 'colorful').
        
    Returns:
        Styled figure.
    """
    theme_config = CHART_THEMES.get(theme, CHART_THEMES['default'])
    
    fig.update_layout(
        paper_bgcolor=theme_config['paper_bgcolor'],
        plot_bgcolor=theme_config['plot_bgcolor'],
        font=dict(color=theme_config['font_color'])
    )
    
    return fig


def get_chart_list() -> List[Dict[str, str]]:
    """Get list of available chart types with descriptions.
    
    Returns:
        List of dicts with chart type info.
    """
    return [
        {'id': 'trend', 'name': '趋势折线图', 'description': '展示成绩/排名变化趋势'},
        {'id': 'box', 'name': '箱线图', 'description': '展示成绩分布的五数概括'},
        {'id': 'heatmap', 'name': '热力图', 'description': '班级×学科成绩矩阵'},
        {'id': 'scatter', 'name': '散点图', 'description': '两个变量相关性分析'},
        {'id': 'violin', 'name': '小提琴图', 'description': '成绩分布密度形态'},
        {'id': 'radar', 'name': '雷达图', 'description': '多学科成绩对比'},
        {'id': 'correlation', 'name': '相关性矩阵', 'description': '各学科间相关系数'},
        {'id': 'distribution', 'name': '成绩分布图', 'description': '分数分布直方图'},
        {'id': 'top_students', 'name': '排行榜', 'description': '前N名学生柱状图'},
        {'id': 'class_comparison', 'name': '班级对比', 'description': '班级间成绩对比'},
        {'id': 'line_rate', 'name': '上线率图', 'description': '985/211/一本上线率'},
        {'id': 'rank_change', 'name': '排名变化', 'description': '班级排名变动对比'}
    ]


if __name__ == "__main__":
    # Test the charts module
    print("Charts module loaded.")
    print("Available charts:", [c['name'] for c in get_chart_list()])
