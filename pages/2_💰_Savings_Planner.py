"""
Savings Planner Page - AI-powered savings goal creation and tracking
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import time

# Configure page
st.set_page_config(
    page_title="Savings Planner - Taxora",
    page_icon="💰",
    layout="wide"
)

# Backend API configuration
API_BASE_URL = "http://127.0.0.1:8000"

def create_savings_goal(goal_data):
    """Create a new savings goal."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/savings/goal",
            json=goal_data,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def calculate_savings_projection(target_amount, monthly_saving, start_date, target_date):
    """Calculate savings projection and timeline."""
    months_to_target = (target_date.year - start_date.year) * 12 + (target_date.month - start_date.month)
    
    if months_to_target <= 0:
        months_to_target = 1  # Avoid zero or negative months

    total_saved = monthly_saving * months_to_target
    shortfall = max(0, target_amount - total_saved)
    required_monthly = target_amount / months_to_target if months_to_target > 0 else 0
    
    # Generate monthly projection
    projection = []
    current_amount = 0
    for month in range(months_to_target + 1):
        projection.append({
            'month': month,
            'amount': current_amount,
            'target_line': (target_amount / months_to_target) * month if months_to_target > 0 else 0
        })
        current_amount += monthly_saving
    
    return {
        'months_to_target': months_to_target,
        'total_saved': total_saved,
        'shortfall': shortfall,
        'required_monthly': required_monthly,
        'projection': projection,
        'success_rate': min(100, (total_saved / target_amount) * 100) if target_amount > 0 else 0
    }

def main():
    st.title("💰 AI-Powered Savings Planner")
    st.markdown("Create smart savings goals with AI-driven insights and recommendations")
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Savings Overview")
        st.metric("💰 Total Savings", "₹1,25,000", "↗️ +15,000")
        st.metric("🎯 Active Goals", "3", "↗️ +1")
        st.metric("📈 Monthly Growth", "12.5%", "↗️ +2.1%")
        st.markdown("### 🏆 Recent Achievements")
        st.success("✅ Emergency Fund - Completed!")
        st.info("🎯 Vacation Fund - 75% complete")
        st.warning("⏰ House Down Payment - 45% complete")

    tab1, tab2, tab3 = st.tabs(["🎯 Create Goal", "📊 Track Progress", "🤖 AI Insights"])

    # ===== CREATE GOAL TAB =====
    with tab1:
        st.header("🎯 Create New Savings Goal")
        
        with st.form("savings_goal_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📝 Goal Details")
                goal_name = st.text_input("Goal Name:", placeholder="e.g., Emergency Fund, Vacation, New Car")
                target_amount = st.number_input("Target Amount (₹):", min_value=1000, value=100000, step=1000)
                target_date = st.date_input(
                    "Target Date:",
                    value=date.today(),
                    min_value=date.today(),
                    max_value=date(2035, 12, 31)
                )
                description = st.text_area("Description:", placeholder="Describe your savings goal")
            with col2:
                st.subheader("💼 Financial Details")
                monthly_salary = st.number_input("Monthly Salary (₹):", min_value=1000, value=50000, step=1000)
                monthly_saving_target = st.number_input("Monthly Saving Target (₹):", min_value=500, value=10000, step=500)
                saving_method = st.selectbox(
                    "Preferred Saving Method:",
                    ["bank_account", "fixed_deposit", "mutual_fund", "stocks", "mixed"],
                    format_func=lambda x: {
                        "bank_account": "🏦 Bank Savings Account",
                        "fixed_deposit": "🔒 Fixed Deposit",
                        "mutual_fund": "📈 Mutual Funds",
                        "stocks": "📊 Stock Market",
                        "mixed": "🔄 Mixed Portfolio"
                    }[x]
                )
                risk_tolerance = st.select_slider("Risk Tolerance:", options=["Low", "Medium", "High"], value="Medium")

            # Calculate projection
            if target_amount > 0 and monthly_saving_target > 0:
                projection = calculate_savings_projection(target_amount, monthly_saving_target, date.today(), target_date)
                if projection:
                    st.subheader("📊 Savings Projection")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("⏱️ Months to Goal", f"{projection['months_to_target']}")
                    col2.metric("💰 Total Saved", f"₹{projection['total_saved']:,}")
                    col3.metric("🎯 Success Rate", f"{projection['success_rate']:.1f}%")
                    col4.metric("⚠️ Shortfall" if projection['shortfall'] > 0 else "✅ Surplus", f"₹{projection['shortfall']:,}")
                    
                    # Chart
                    df = pd.DataFrame(projection['projection'])
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df['month'], y=df['amount'], mode='lines+markers', name='Your Savings'))
                    fig.add_trace(go.Scatter(x=df['month'], y=[target_amount]*len(df), mode='lines', name='Target Amount', line=dict(dash='dash')))
                    fig.update_layout(title="Savings Projection Over Time", xaxis_title="Months", yaxis_title="Amount (₹)", hovermode='x unified')
                    st.plotly_chart(fig, use_container_width=True)

            # Submit button
            if st.form_submit_button("🚀 Create Goal with AI Analysis"):
                if not goal_name.strip():
                    st.error("❌ Please enter a goal name")
                else:
                    goal_data = {
                        "user_id": f"streamlit_user_{int(time.time())}",
                        "goal_data": {
                            "goal_name": goal_name,
                            "target_amount": target_amount,
                            "monthly_salary": monthly_salary,
                            "monthly_saving_target": monthly_saving_target,
                            "saving_method": saving_method,
                            "target_date": target_date.isoformat(),
                            "description": description,
                            "risk_tolerance": risk_tolerance
                        }
                    }
                    with st.spinner("🤖 AI is analyzing your goal..."):
                        result = create_savings_goal(goal_data)
                        if result and result.get('success'):
                            st.success("✅ Savings goal created successfully!")
                        else:
                            st.error("❌ Failed to create savings goal. Check backend connection.")

    # ===== TRACK PROGRESS TAB =====
    with tab2:
        st.header("📊 Track Your Progress")
        sample_goals = [
            {"name": "Emergency Fund", "target": 150000, "current": 150000, "monthly": 15000, "status": "Completed"},
            {"name": "Vacation Fund", "target": 80000, "current": 60000, "monthly": 8000, "status": "In Progress"},
            {"name": "House Down Payment", "target": 500000, "current": 225000, "monthly": 25000, "status": "In Progress"},
            {"name": "New Car", "target": 300000, "current": 45000, "monthly": 12000, "status": "In Progress"}
        ]
        for goal in sample_goals:
            col1, col2, col3 = st.columns([2,1,1])
            progress = goal["current"]/goal["target"]
            col1.subheader(f"🎯 {goal['name']}")
            col1.progress(progress)
            col1.caption(f"₹{goal['current']:,} / ₹{goal['target']:,} ({progress*100:.1f}%)")
            remaining = goal['target']-goal['current']
            months_left = remaining/goal['monthly'] if goal['monthly']>0 and remaining>0 else 0
            col2.metric("Monthly Saving", f"₹{goal['monthly']:,}")
            col2.caption(f"~{months_left:.1f} months left" if months_left>0 else "Goal achieved!")
            col3.success("✅ Completed") if goal['status']=="Completed" else col3.info("🔄 In Progress")
            st.divider()

    # ===== AI INSIGHTS TAB =====
    with tab3:
        st.header("🤖 AI Financial Insights")
        insights = [
            {"title":"💡 Savings Rate Optimization","content":"Increase savings from 20% to 25% to reach goals faster","type":"info"},
            {"title":"📈 Investment Opportunity","content":"Move excess emergency funds to mutual funds","type":"success"},
            {"title":"⚠️ Goal Timeline Alert","content":"House down payment may need adjustment","type":"warning"},
        ]
        for insight in insights:
            st.info(insight['content']) if insight['type']=="info" else None
            st.success(insight['content']) if insight['type']=="success" else None
            st.warning(insight['content']) if insight['type']=="warning" else None

if __name__=="__main__":
    main()
