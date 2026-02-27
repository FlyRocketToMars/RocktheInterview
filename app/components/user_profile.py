"""
User Profile Component
Display user profile, stats, badges, and contributions
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.gamification import gamification, get_profile, get_leaderboard, record_daily_login, check_badges


def render_profile_card(profile: dict, show_full: bool = True):
    """Render a user profile card."""
    
    username = profile.get("username", "匿名用户")
    points = profile.get("points", 0)
    level_name = profile.get("level_name", "🌱 新手")
    level_desc = profile.get("level_description", "")
    streak = profile.get("current_streak", 0)
    badges = profile.get("badges", [])
    badge_details = profile.get("badge_details", [])
    progress = profile.get("progress_to_next_level", 0)
    
    # Profile header
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Avatar placeholder
        st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 4rem;">👤</div>
            <div style="font-size: 1.2rem; font-weight: bold;">{username}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### {level_name}")
        st.caption(level_desc)
        
        # Progress bar to next level
        st.progress(progress)
        st.caption(f"距下一级: {int(progress * 100)}%")
        
        # Stats row
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        with stat_col1:
            st.metric("⭐ 积分", points)
        with stat_col2:
            st.metric("🔥 连续", f"{streak}天")
        with stat_col3:
            st.metric("📝 回答", profile.get("total_answers", 0))
        with stat_col4:
            st.metric("❓ 提问", profile.get("total_questions", 0))
    
    with col3:
        rank = gamification.get_user_rank(username)
        st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 2rem;">🏅</div>
            <div style="font-size: 1.5rem; font-weight: bold;">#{rank}</div>
            <div style="font-size: 0.9rem; color: #888;">排行榜</div>
        </div>
        """, unsafe_allow_html=True)
    
    if show_full:
        st.markdown("---")
        
        # Badges section
        st.markdown("### 🏆 徽章收藏")
        
        if badge_details:
            badge_cols = st.columns(min(len(badge_details), 5))
            for i, badge in enumerate(badge_details):
                with badge_cols[i % 5]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; background: #1e293b; border-radius: 10px; margin: 5px;">
                        <div style="font-size: 2rem;">{badge.get('icon', '🏅')}</div>
                        <div style="font-size: 0.8rem; font-weight: bold;">{badge.get('name', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("还没有获得徽章，继续努力！")
        
        # Available badges
        with st.expander("查看所有可获得的徽章"):
            for badge_id, badge in gamification.BADGES.items():
                earned = badge_id in badges
                status = "✅ 已获得" if earned else "🔒 未解锁"
                st.markdown(f"**{badge['icon']} {badge['name']}** - {badge['description']} ({status})")


def render_leaderboard():
    """Render the community leaderboard."""
    
    st.markdown("### 🏆 社区排行榜")
    
    leaderboard = get_leaderboard(limit=20)
    
    if not leaderboard:
        st.info("暂无排名数据")
        return
    
    # Top 3 special display
    if len(leaderboard) >= 3:
        col1, col2, col3 = st.columns(3)
        
        with col2:  # First place in center
            user = leaderboard[0]
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #ffd700 0%, #ffec8b 100%); border-radius: 15px;">
                <div style="font-size: 3rem;">🥇</div>
                <div style="font-size: 1.2rem; font-weight: bold; color: #333;">{user.get('username', '匿名')}</div>
                <div style="font-size: 1.5rem; color: #333;">⭐ {user.get('points', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col1:  # Second place
            user = leaderboard[1]
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%); border-radius: 15px; margin-top: 20px;">
                <div style="font-size: 2.5rem;">🥈</div>
                <div style="font-size: 1rem; font-weight: bold; color: #333;">{user.get('username', '匿名')}</div>
                <div style="font-size: 1.2rem; color: #333;">⭐ {user.get('points', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:  # Third place
            user = leaderboard[2]
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #cd7f32 0%, #daa520 100%); border-radius: 15px; margin-top: 20px;">
                <div style="font-size: 2.5rem;">🥉</div>
                <div style="font-size: 1rem; font-weight: bold; color: #333;">{user.get('username', '匿名')}</div>
                <div style="font-size: 1.2rem; color: #333;">⭐ {user.get('points', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Rest of leaderboard
    st.markdown("#### 完整排名")
    
    for i, user in enumerate(leaderboard):
        rank = i + 1
        rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
        
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
        
        with col1:
            st.markdown(f"**{rank_emoji}**")
        with col2:
            level_info = gamification.get_level_info(user.get("points", 0))
            st.markdown(f"**{user.get('username', '匿名')}** {level_info[1]}")
        with col3:
            st.markdown(f"⭐ {user.get('points', 0)}")
        with col4:
            st.markdown(f"📝 {user.get('total_answers', 0)} 回答")


def render_user_profile():
    """Main render function for user profile page."""
    
    st.markdown("## 👤 个人中心")
    st.markdown("*查看你的成就、积分和排名*")
    
    # Check if user is logged in
    username = st.session_state.get("username", "")
    
    if not username:
        st.warning("请先设置你的昵称")
        new_username = st.text_input("输入昵称", key="profile_username")
        if st.button("确认"):
            if new_username:
                st.session_state.username = new_username
                st.rerun()
        return
    
    # Record daily login
    login_result = record_daily_login(username)
    if login_result.get("points", 0) > 0:
        st.toast(f"🎉 每日登录奖励: +{login_result['points']} 积分！连续 {login_result['streak']} 天")
    
    # Check for new badges
    new_badges = check_badges(username)
    for badge in new_badges:
        st.toast(f"🏆 获得新徽章: {badge}")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 我的资料", "🏆 排行榜", "🎯 成就进度"])
    
    with tab1:
        col_l, col_r = st.columns([5, 1])
        with col_r:
            if st.button("🚪 退出登录 (Logout)", use_container_width=True):
                from components.auth import logout
                logout()
                st.rerun()
                
        profile = get_profile(username)
        render_profile_card(profile)
        
        st.markdown("---")
        
        # Recent activity (placeholder)
        st.markdown("### 📝 最近动态")
        st.info("暂无最近动态")
    
    with tab2:
        render_leaderboard()
    
    with tab3:
        st.markdown("### 🎯 成就进度")
        
        profile = get_profile(username)
        
        # Show progress towards different achievements
        achievements = [
            {
                "name": "回答达人",
                "target": 50,
                "current": profile.get("total_answers", 0),
                "icon": "📝"
            },
            {
                "name": "获赞之星",
                "target": 100,
                "current": profile.get("total_upvotes_received", 0),
                "icon": "👍"
            },
            {
                "name": "提问大师",
                "target": 20,
                "current": profile.get("total_questions", 0),
                "icon": "❓"
            },
            {
                "name": "连续登录",
                "target": 30,
                "current": profile.get("max_streak", 0),
                "icon": "🔥"
            },
        ]
        
        for ach in achievements:
            progress = min(ach["current"] / ach["target"], 1.0)
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                st.markdown(f"### {ach['icon']}")
            with col2:
                st.markdown(f"**{ach['name']}**")
                st.progress(progress)
            with col3:
                st.markdown(f"**{ach['current']}/{ach['target']}**")


if __name__ == "__main__":
    render_user_profile()
