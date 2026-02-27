"""
Progress Tracker - Comprehensive progress visualization
Shows knowledge map, weak points heatmap, and timeline
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List
import json
from pathlib import Path


def render_progress_page(user_email: str):
    """Render comprehensive progress tracking page."""
    
    st.markdown("## 📊 Progress Tracking")
    st.markdown("*Your journey to interview success*")
    
    # Get user progress data
    progress_data = _get_user_progress(user_email)
    
    # Top stats row
    render_top_stats(progress_data)
    
    st.markdown("---")
    
    # Main content in tabs
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "🗺️ Knowledge Map", "🔥 Weak Points"])
    
    with tab1:
        render_overview_tab(progress_data)
    
    with tab2:
        render_knowledge_map(progress_data)
    
    with tab3:
        render_weak_points_heatmap(progress_data)


def render_top_stats(progress_data: Dict):
    """Render top-level statistics."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📚 Total Questions",
            value=progress_data['total_completed'],
            delta=f"+{progress_data['this_week']} this week"
        )
    
    with col2:
        st.metric(
            label="⏱️ Study Hours",
            value=f"{progress_data['total_hours']}h",
            delta=f"+{progress_data['hours_this_week']}h this week"
        )
    
    with col3:
        st.metric(
            label="🔥 Current Streak",
            value=f"{progress_data['streak_days']} days",
            delta="Keep going!" if progress_data['streak_days'] >= 7 else None
        )
    
    with col4:
        days_left = progress_data.get('days_to_interview')
        if days_left:
            st.metric(
                label="📅 Days to Interview",
                value=days_left,
                delta=f"{progress_data['readiness']}% ready"
            )
        else:
            st.metric(
                label="🎯 Overall Progress",
                value=f"{progress_data['overall_progress']}%"
            )


def render_overview_tab(progress_data: Dict):
    """Render overview tab with charts."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Progress by Category")
        
        # Radar chart for different categories
        categories = ['Coding', 'System Design', 'ML Theory', 'Behavioral', 'LLM/GenAI']
        values = [
            progress_data['coding_progress'],
            progress_data['system_design_progress'],
            progress_data['ml_theory_progress'],
            progress_data['behavioral_progress'],
            progress_data['llm_progress']
        ]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(59, 130, 246, 0.3)',
            line=dict(color='rgb(59, 130, 246)', width=2)
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False,
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Daily Activity")
        
        # Line chart for daily progress
        dates = [(datetime.now() - timedelta(days=i)).strftime('%m/%d') for i in range(29, -1, -1)]
        questions_per_day = progress_data.get('daily_questions', [2, 3, 5, 4, 6, 3, 7, 4, 5, 6, 8, 5, 4, 6, 7, 5, 8, 6, 7, 9, 6, 8, 7, 9, 8, 10, 7, 9, 8, 10])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=questions_per_day,
            mode='lines+markers',
            line=dict(color='rgb(16, 185, 129)', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.2)'
        ))
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Questions Completed",
            height=400,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Timeline to interview
    st.markdown("### 🎯 Timeline to Interview")
    render_timeline(progress_data)


def render_timeline(progress_data: Dict):
    """Render timeline visualization."""
    days_left = progress_data.get('days_to_interview', 60)
    total_days = progress_data.get('total_prep_days', 90)
    days_passed = total_days - days_left
    
    progress_pct = (days_passed / total_days) * 100
    
    # Progress bar with milestones
    st.markdown(f"""
    <div style="background: #1e293b; padding: 2rem; border-radius: 12px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
            <span>Start</span>
            <span style="color: #3b82f6; font-weight: bold;">{days_passed} days / {total_days} days</span>
            <span>Interview Day 🎯</span>
        </div>
        <div style="background: #334155; height: 20px; border-radius: 10px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #3b82f6, #8b5cf6); height: 100%; width: {progress_pct}%; transition: width 0.3s;"></div>
        </div>
        <div style="margin-top: 1rem; text-align: center; color: #94a3b8;">
            <strong>{days_left} days remaining</strong> - Stay focused! 💪
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_knowledge_map(progress_data: Dict):
    """Render knowledge map visualization."""
    st.markdown("### 🗺️ Knowledge Coverage Map")
    
    # Tree map showing topic coverage
    topics = {
        'Coding': {
            'Array': 85,
            'Tree': 70,
            'Graph': 60,
            'DP': 55,
            'Heap': 75
        },
        'System Design': {
            'Recommendation': 65,
            'Search': 50,
            'Messaging': 40,
            'Storage': 70
        },
        'ML Theory': {
            'Supervised': 90,
            'Unsupervised': 75,
            'Deep Learning': 80,
            'Optimization': 70
        }
    }
    
    # Flatten for treemap
    labels = []
    parents = []
    values = []
    colors = []
    
    for category, subtopics in topics.items():
        labels.append(category)
        parents.append("")
        values.append(sum(subtopics.values()) / len(subtopics))
        colors.append(sum(subtopics.values()) / len(subtopics))
        
        for topic, score in subtopics.items():
            labels.append(topic)
            parents.append(category)
            values.append(score)
            colors.append(score)
    
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(
            colorscale='RdYlGn',
            cmid=50,
            colorbar=dict(title="Mastery %"),
            line=dict(width=2)
        ),
        text=[f"{v:.0f}%" for v in values],
        textposition="middle center",
        hovertemplate='<b>%{label}</b><br>Mastery: %{value:.0f}%<extra></extra>'
    ))
    
    fig.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 **Tip**: Green = Strong, Yellow = Needs Practice, Red = Focus Here!")


def render_weak_points_heatmap(progress_data: Dict):
    """Render weak points heatmap."""
    st.markdown("### 🔥 Weak Points Analysis")
    
    # Heatmap of performance by topic and difficulty
    topics = ['Array', 'Tree', 'Graph', 'DP', 'Heap', 'Design', 'String', 'Math']
    difficulties = ['Easy', 'Medium', 'Hard']
    
    # Mock data - replace with real data
    performance = [
        [95, 85, 70],  # Array
        [90, 75, 60],  # Tree
        [85, 65, 45],  # Graph
        [80, 60, 40],  # DP
        [90, 80, 65],  # Heap
        [75, 55, 35],  # Design
        [95, 85, 75],  # String
        [85, 70, 55]   # Math
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=performance,
        x=difficulties,
        y=topics,
        colorscale='RdYlGn',
        text=[[f"{val}%" for val in row] for row in performance],
        texttemplate="%{text}",
        textfont={"size": 12},
        colorbar=dict(title="Success Rate")
    ))
    
    fig.update_layout(
        title="Performance Heatmap by Topic & Difficulty",
        xaxis_title="Difficulty",
        yaxis_title="Topic",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.markdown("### 💡 AI Recommendations")
    
    weak_topics = [
        ("DP - Hard", 40, "🎯 High Priority"),
        ("Design - Hard", 35, "🎯 High Priority"),
        ("Graph - Hard", 45, "⚠️ Medium Priority"),
        ("DP - Medium", 60, "⚠️ Medium Priority")
    ]
    
    for topic, score, priority in weak_topics:
        color = "#ef4444" if "High" in priority else "#f59e0b"
        st.markdown(f"""
        <div style="background: #1e293b; padding: 1rem; border-left: 4px solid {color}; border-radius: 8px; margin-bottom: 0.5rem;">
            <strong>{topic}</strong> - {score}% success rate
            <span style="float: right; color: {color};">{priority}</span>
        </div>
        """, unsafe_allow_html=True)


def _get_user_progress(user_email: str) -> Dict:
    """Get user progress data."""
    # Import here to avoid circular dependency
    from components.user_progress import progress_manager
    return progress_manager.get_progress_stats(user_email)
