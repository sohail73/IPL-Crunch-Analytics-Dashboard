from Home import load_data
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# PAGE AND SIDEBAR CONFIG
st.markdown("""
<style>
[data-testid="stSidebarNav"]::before {
    content: "🏏 IPL Analytics";
    margin-left: 20px;
    margin-top: 20px;
    font-size: 30px;
    position: relative;
    top: 0px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Match Phase Analysis",
    page_icon="⚡",
    layout="wide"
)

# LOAD DATA
df = load_data()
filtered_df = df.copy()

# CREATE MATCH PHASE
def get_phase(over_val):
    if over_val < 6:  # 0,1,2,3,4,5 (Overs 1 to 6)
        return "Powerplay"
    elif over_val < 15:  # 6,7,8,9,10,11,12,13,14 (Overs 7 to 15)
        return "Middle Overs"
    else:  # 15,16,17,18,19 (Overs 16 to 20)
        return "Death Overs"


filtered_df['phase'] = filtered_df['over'].apply(get_phase)
filtered_df['is_wicket'] = filtered_df['wicket_kind'].notna().astype(int)
filtered_df['is_dot'] = (filtered_df['runs_total'] == 0).astype(int)

# PAGE TITLE
st.title("Match Phase Analytics")
st.markdown("""
Deconstruct match progression across strategic segments: **Powerplay** (Overs 1-6), 
**Middle Overs** (Overs 7-15), and **Death Overs** (Overs 16-20).
""")
st.divider()

# PAGE FILTERS
selected_phase = st.selectbox(
    "Select Match Phase Focus",
    ["All", "Powerplay", "Middle Overs", "Death Overs"]
)

# APPLY PHASE FILTER
phase_df = filtered_df.copy()
if selected_phase != "All":
    phase_df = phase_df[phase_df['phase'] == selected_phase]

# KPI SECTION (ACCURATE METRICS)
total_runs = phase_df['runs_total'].sum()
total_wickets = phase_df['is_wicket'].sum()
total_balls = phase_df.shape[0]
run_rate = round((total_runs / total_balls) * 6, 2) if total_balls > 0 else 0.0
dot_balls = phase_df['is_dot'].sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Runs Scored", f"{total_runs:,}")
with col2:
    st.metric("Total Wickets Fallen", f"{total_wickets:,}")
with col3:
    st.metric("Phase Run Rate", f"{run_rate}")
with col4:
    st.metric("Total Dot Deliveries", f"{dot_balls:,}")

st.divider()

# CHARTS GRID 1: RUNS & WICKETS OVERVIEW
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Phase-wise Run Distribution")
    phase_runs = filtered_df.groupby('phase')['runs_total'].sum().reset_index()

    fig1 = px.bar(
        phase_runs,
        x='runs_total',
        y='phase',
        orientation='h',
        color='phase',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title="Cumulative Runs Across Match Phases",
        labels={'runs_total': 'Total Runs', 'phase': 'Match Phase'},
        template='plotly_white'
    )
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=380)
    fig1.update_traces(texttemplate='%{x:,}', textposition='outside')
    st.plotly_chart(fig1, use_container_width=True)

with col_g2:
    st.subheader("Wicket Distribution by Phase")
    phase_wickets = filtered_df.groupby('phase')['is_wicket'].sum().reset_index()

    fig2 = px.pie(
        phase_wickets,
        values='is_wicket',
        names='phase',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Safe,
        title="Where Do Batsmen Lose Wickets Most?"
    )
    fig2.update_layout(template='plotly_white', height=380, margin=dict(t=30, b=10, l=10, r=10))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
# CHARTS GRID 2: RUN RATE & TEAM COMPARISON

col_g3, col_g4 = st.columns(2)

with col_g3:
    st.subheader("Run Rate Intensity Comparison")
    phase_rr = filtered_df.groupby('phase').agg({'runs_total': 'sum', 'match_id': 'count'}).reset_index()
    phase_rr['run_rate'] = (phase_rr['runs_total'] / phase_rr['match_id']) * 6

    fig3 = px.bar(
        phase_rr,
        x='run_rate',
        y='phase',
        orientation='h',
        color='phase',
        color_discrete_sequence=px.colors.qualitative.Vivid,
        title="Standard Scoring Pace (Run Rate)",
        labels={'run_rate': 'Run Rate', 'phase': 'Match Phase'},
        template='plotly_white'
    )
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=380)
    fig3.update_traces(texttemplate='%{x:.2f}', textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

with col_g4:
    st.subheader("Top Franchise Production by Phase")
    team_phase_runs = filtered_df.groupby(['batting_team', 'phase'])['runs_total'].sum().reset_index()

    # Extracting top 5 franchises for high clarity representation
    top_teams = filtered_df.groupby('batting_team')['runs_total'].sum().sort_values(ascending=False).head(5).index
    team_phase_runs = team_phase_runs[team_phase_runs['batting_team'].isin(top_teams)]

    fig4 = px.bar(
        team_phase_runs,
        x='batting_team',
        y='runs_total',
        color='phase',
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="Top 5 Teams Run Splits Across Phases",
        labels={'runs_total': 'Runs Scored', 'batting_team': 'Franchise Team'},
        template='plotly_white'
    )
    fig4.update_layout(height=380)
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# CHARTS GRID 3: OVER-BY-OVER PROGRESSION
st.subheader("Over-wise Scoring Progression Curve")
over_runs_data = filtered_df.groupby('over')['runs_total'].sum().reset_index()

over_runs_data['Display Over'] = over_runs_data['over'] + 1

fig5 = px.line(
    over_runs_data,
    x='Display Over',
    y='runs_total',
    markers=True,
    title="Cumulative Runs Scored for Every Over (Overs 1 to 20)",
    labels={'Display Over': 'Over Number', 'runs_total': 'Total Runs Scored'},
    template='plotly_white'
)
fig5.update_traces(line=dict(color='#059669', width=3), marker=dict(size=8, color='#0f172a'))
fig5.update_layout(xaxis=dict(tickmode='linear', dtick=1), height=400)
st.plotly_chart(fig5, use_container_width=True)

st.divider()

# CHARTS GRID 4: PHASE SPECIALISTS (HORIZONTAL LOOK)
col_g5, col_g6 = st.columns(2)

with col_g5:
    st.subheader("Death Over Hitters")
    death_df = filtered_df[filtered_df['phase'] == 'Death Overs']
    death_batters = death_df.groupby('batter')['runs_batter'].sum().reset_index()
    death_batters = death_batters.sort_values(by='runs_batter', ascending=False).head(10)

    fig6 = px.bar(
        death_batters,
        x='runs_batter',
        y='batter',
        orientation='h',
        color='runs_batter',
        color_continuous_scale='Sunsetdark',
        title="Top 10 Batters in Death Phase (Overs 16-20)",
        labels={'runs_batter': 'Runs Scored', 'batter': 'Batter'},
        template='plotly_white'
    )
    fig6.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=400)
    fig6.update_traces(texttemplate='%{x}', textposition='outside')
    st.plotly_chart(fig6, use_container_width=True)

with col_g6:
    st.subheader("Powerplay Wicket Takers")
    pp_df = filtered_df[filtered_df['phase'] == 'Powerplay']
    pp_bowlers = pp_df[pp_df['wicket_kind'].notna()].groupby('bowler')['is_wicket'].sum().sort_values(
        ascending=False).head(10).reset_index()

    fig7 = px.bar(
        pp_bowlers,
        x='is_wicket',
        y='bowler',
        orientation='h',
        color='is_wicket',
        color_continuous_scale='Ice',
        title="Top 10 Bowlers in Powerplay Phase (Overs 1-6)",
        labels={'is_wicket': 'Wickets Taken', 'bowler': 'Bowler'},
        template='plotly_white'
    )
    fig7.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=400)
    fig7.update_traces(texttemplate='%{x}', textposition='outside')
    st.plotly_chart(fig7, use_container_width=True)

st.divider()

# DYNAMIC INSIGHTS ENGINE (PURE STREAMLIT STYLE)
st.subheader("Analytical Insights & Strategic Takeaways")

if selected_phase == "All":
    ins_col1, ins_col2 = st.columns(2)

    with ins_col1:
        st.info("""
        **The Death Over Volatility**
        The Run Rate chart reveals that **Death Overs** always possess the steepest scoring intensity. While total runs might look lower due to fewer overs, the pace of scoring makes it the ultimate differentiator between winning and losing.
        """)

        st.success("""
        **Middle Overs Accumulation Framework**
        The **Middle Overs** host the maximum aggregate runs. Teams that preserve resources in the Powerplay can structurally dictate terms here by executing risk-mitigated strike rotation.
        """)

    with ins_col2:
        st.warning("""
        **Wicket Density Risk Matrix**
        The Pie chart highlights that wickets are highly concentrated in specific inflection points. Batsmen face high-leverage risk periods both at the start (swing/seam) and at the absolute tail-end (forced acceleration).
        """)

        st.success("""
        **Over 1 to 20 Progression Path**
        The line graph clearly traces the structural scoring dips and surges. Scoring usually slows right after the Powerplay restrictions end (Over 6) and starts its vertical exponential climb from Over 15 onwards.
        """)
else:
    phase_percentage_runs = round((total_runs / filtered_df['runs_total'].sum()) * 100, 1)

    ins_col1, ins_col2 = st.columns(2)

    with ins_col1:
        st.info(f"""
        **Specific Segment Evaluation: {selected_phase}**
        - This tactical phase accounts for **{phase_percentage_runs}%** of all total runs scored in IPL history. 
        - Operating at a localized Run Rate of **{run_rate}**, teams must construct distinct squad profiles to optimize efficiency in this window.
        """)

    with ins_col2:
        # Dynamic phase tag assignment
        if selected_phase == "Powerplay":
            strategy_tip = "Maximize boundary percentage before field restrictions open up."
        elif selected_phase == "Middle Overs":
            strategy_tip = "Focus on high-density strike rotation and minimizing dot ball strings against spin."
        else:
            strategy_tip = "Deploy heavy vertical bat acceleration and high-intent boundary hunting regardless of risk."

        st.success(f"""
        **Strategic Directive for {selected_phase}:**
        - _"{strategy_tip}"_
        - Managing the combination of **{total_wickets} fallen wickets** against **{dot_balls:,} dot balls** dictates whether a franchise finishes ahead of the par line in this specific phase.
        """)

st.divider()
# SUMMARY

st.subheader("Summary")

st.markdown("""
> T20 matches are won by mastering localized sub-phases. A premium coaching setup splits a 20-over game into three distinct tactical modules, matching player specialties dynamically to phase-specific pressures.
""")

st.markdown("""
### Tactical Coach's Phase Blueprint:
1. **Powerplay (Overs 1-6):** Target a clean launch vector. Bowlers must hunt for swing/seam breakthroughs, while batters utilize the vacant outfield for aerial risks.
2. **Middle Overs (Overs 7-15):** The engine room of the innings. Success here requires mapping defensive spinners against high-intent strike rotators to sustain momentum without shedding wickets.
3. **Death Overs (Overs 16-20):** Pure execution variance. Teams must stack death-over hitters capable of targeting specific boundary dimensions against yorker/slower-ball execution specialists.
""")