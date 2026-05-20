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
    page_icon="🏏",
    layout="wide"
)

# LOAD DATA
@st.cache_data
def load_data():
    return pd.read_csv('data/ipl_crunch_data.csv')
df = load_data()

# ---------------------------------------------------
# GET GLOBAL FILTERS
# ---------------------------------------------------

selected_season = st.session_state.get(
    "selected_season",
    "All"
)

selected_team = st.session_state.get(
    "selected_team",
    "All"
)

# ---------------------------------------------------
# APPLY GLOBAL FILTERS
# ---------------------------------------------------

filtered_df = df.copy()

# Season Filter
if selected_season != "All":
    filtered_df = filtered_df[
        filtered_df['season']
        == selected_season
    ]

# Team Filter
if selected_team != "All":
    filtered_df = filtered_df[
        (filtered_df['team1'] == selected_team)
        |
        (filtered_df['team2'] == selected_team)
    ]

# ---------------------------------------------------
# CREATE OVER COLUMN
# ---------------------------------------------------

filtered_df['over'] = filtered_df[
    'ball'
].astype(str).str.split('.').str[0].astype(int)

# ---------------------------------------------------
# CREATE MATCH PHASE
# ---------------------------------------------------

def get_phase(over):

    if over <= 6:
        return "Powerplay"

    elif over <= 15:
        return "Middle Overs"

    else:
        return "Death Overs"

filtered_df['phase'] = filtered_df[
    'over'
].apply(get_phase)

# ---------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------

st.title("⚡ Match Phase Analysis")

st.markdown("""
Analyze performance across different
match phases including Powerplay,
Middle Overs, and Death Overs.
""")

st.divider()

# ---------------------------------------------------
# PAGE FILTERS
# ---------------------------------------------------

selected_phase = st.selectbox(
    "Select Match Phase",
    [
        "All",
        "Powerplay",
        "Middle Overs",
        "Death Overs"
    ]
)

# ---------------------------------------------------
# APPLY PHASE FILTER
# ---------------------------------------------------

phase_df = filtered_df.copy()

if selected_phase != "All":

    phase_df = phase_df[
        phase_df['phase']
        == selected_phase
    ]

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

total_runs = phase_df[
    'runs_total'
].sum()

total_wickets = phase_df[
    phase_df['wicket_kind'].notna()
].shape[0]

total_balls = phase_df.shape[0]

run_rate = round(
    (total_runs / total_balls) * 6,
    2
)

dot_balls = phase_df[
    phase_df['runs_total'] == 0
].shape[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🏏 Total Runs",
        total_runs
    )

with col2:
    st.metric(
        "🎯 Wickets",
        total_wickets
    )

with col3:
    st.metric(
        "⚡ Run Rate",
        run_rate
    )

with col4:
    st.metric(
        "⚪ Dot Balls",
        dot_balls
    )

st.divider()

# ---------------------------------------------------
# PHASE-WISE RUNS
# ---------------------------------------------------

st.subheader("📈 Phase-wise Run Distribution")

phase_runs = filtered_df.groupby(
    'phase'
)['runs_total'].sum().reset_index()

fig1 = px.bar(
    phase_runs,
    x='phase',
    y='runs_total',
    color='phase',
    title="Runs Across Match Phases"
)

st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ---------------------------------------------------
# PHASE-WISE WICKETS
# ---------------------------------------------------

st.subheader("🎯 Wickets Across Phases")

phase_wickets = filtered_df[
    filtered_df['wicket_kind'].notna()
]

phase_wickets = phase_wickets.groupby(
    'phase'
)['wicket_player_out'].count().reset_index()

fig2 = px.pie(
    phase_wickets,
    values='wicket_player_out',
    names='phase',
    title="Wicket Distribution by Phase"
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---------------------------------------------------
# RUN RATE BY PHASE
# ---------------------------------------------------

st.subheader("⚡ Run Rate by Phase")

phase_rr = filtered_df.groupby(
    'phase'
).agg({
    'runs_total': 'sum',
    'ball': 'count'
})

phase_rr['run_rate'] = (
    phase_rr['runs_total']
    /
    phase_rr['ball']
) * 6

fig3 = px.bar(
    phase_rr,
    x=phase_rr.index,
    y='run_rate',
    color=phase_rr.index,
    title="Run Rate Comparison"
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ---------------------------------------------------
# TEAM PERFORMANCE BY PHASE
# ---------------------------------------------------

st.subheader("👥 Team Performance Across Phases")

team_phase_runs = filtered_df.groupby(
    ['batting_team', 'phase']
)['runs_total'].sum().reset_index()

top_teams = team_phase_runs.groupby(
    'batting_team'
)['runs_total'].sum().sort_values(
    ascending=False
).head(5).index

team_phase_runs = team_phase_runs[
    team_phase_runs['batting_team'].isin(top_teams)
]

fig4 = px.bar(
    team_phase_runs,
    x='batting_team',
    y='runs_total',
    color='phase',
    barmode='group',
    title="Top Teams Across Match Phases"
)

st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ---------------------------------------------------
# OVER-WISE SCORING TREND
# ---------------------------------------------------

st.subheader("📅 Over-wise Scoring Trend")

over_runs = filtered_df.groupby(
    'over'
)['runs_total'].sum().reset_index()

fig5 = px.line(
    over_runs,
    x='over',
    y='runs_total',
    markers=True,
    title="Runs by Over"
)

st.plotly_chart(fig5, use_container_width=True)

st.divider()

# ---------------------------------------------------
# DEATH OVER SPECIALISTS
# ---------------------------------------------------

st.subheader("🔥 Death Over Hitters")

death_df = filtered_df[
    filtered_df['phase']
    == 'Death Overs'
]

death_batters = death_df.groupby(
    'batter'
)['runs_batter'].sum().reset_index()

death_batters = death_batters.sort_values(
    by='runs_batter',
    ascending=False
).head(10)

fig6 = px.bar(
    death_batters,
    x='batter',
    y='runs_batter',
    color='runs_batter',
    title="Top Death Over Batters",
    labels={
        'runs_batter': 'Runs',
        'batter': 'Batter'
    }
)

fig6.update_layout(
    xaxis_title="Batter",
    yaxis_title="Runs",
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.divider()

# ---------------------------------------------------
# POWERPLAY WICKET TAKERS
# ---------------------------------------------------

st.subheader("🎯 Powerplay Wicket Takers")

pp_df = filtered_df[
    filtered_df['phase']
    == 'Powerplay'
]

pp_wickets = pp_df[
    pp_df['wicket_kind'].notna()
]

pp_bowlers = pp_wickets.groupby(
    'bowler'
)['wicket_player_out'].count().sort_values(
    ascending=False
).head(10)

fig7 = px.bar(
    pp_bowlers,
    x=pp_bowlers.index,
    y=pp_bowlers.values,
    title="Top Powerplay Bowlers",
    labels={
        'x': 'Bowler',
        'y': 'Wickets'
    }
)

st.plotly_chart(fig7, use_container_width=True)

st.divider()

# ---------------------------------------------------
# INSIGHTS
# ---------------------------------------------------

st.subheader("🧠 Key Insights")

st.success("""
• Death overs generate the highest scoring rates.

• Powerplay wickets significantly affect
  match momentum.

• Middle overs often determine
  innings stability.

• Teams dominating multiple phases
  generally win more matches.

• Dot-ball pressure in middle overs
  creates wicket opportunities.
""")

st.divider()

# ---------------------------------------------------
# CONCLUSION
# ---------------------------------------------------

st.subheader("📌 Conclusion")

st.markdown("""
IPL matches are heavily influenced by
performance across different phases.
Powerplay aggression, middle-over control,
and death-over execution together
determine overall match outcomes.
""")