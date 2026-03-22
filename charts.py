"""
Charts Module

This module generates interactive charts using Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
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


if __name__ == "__main__":
    # Test the charts module
    print("Charts module loaded.")
    print("Use create_*_chart() functions to generate charts.")
