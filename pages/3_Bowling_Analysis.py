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
    page_title="Bowling Analysis",
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
# PAGE TITLE
# ---------------------------------------------------

st.title("🎯 Bowling Analytics")

st.markdown("""
Analyze bowling performance, wicket-taking ability,
economy rates, pressure bowling,
and match impact across IPL seasons.
""")

st.divider()

# ---------------------------------------------------
# PAGE FILTERS
# ---------------------------------------------------

bowlers = sorted(
    filtered_df['bowler'].dropna().unique()
)

selected_bowler = st.selectbox(
    "Select Bowler",
    ["All"] + list(bowlers)
)

# ---------------------------------------------------
# APPLY BOWLER FILTER
# ---------------------------------------------------

bowling_df = filtered_df.copy()

if selected_bowler != "All":
    bowling_df = bowling_df[
        bowling_df['bowler']
        == selected_bowler
    ]

# ---------------------------------------------------
# WICKET DATA
# ---------------------------------------------------

wickets_df = bowling_df[
    bowling_df['wicket_kind'].notna()
]

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

total_wickets = wickets_df.shape[0]

total_runs_conceded = bowling_df[
    'runs_total'
].sum()

total_balls = bowling_df.shape[0]

economy = round(
    (total_runs_conceded / total_balls) * 6,
    2
)

dot_balls = bowling_df[
    bowling_df['runs_total'] == 0
].shape[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🎯 Total Wickets",
        total_wickets
    )

with col2:
    st.metric(
        "💰 Economy Rate",
        economy
    )

with col3:
    st.metric(
        "⚪ Dot Balls",
        dot_balls
    )

with col4:
    st.metric(
        "🏏 Runs Conceded",
        total_runs_conceded
    )

st.divider()

# ---------------------------------------------------
# TOP WICKET TAKERS
# ---------------------------------------------------

st.subheader("🔥 Top Wicket Takers")

top_bowlers = filtered_df[
    filtered_df['wicket_kind'].notna()
]

top_bowlers = top_bowlers.groupby(
    'bowler'
)['wicket_player_out'].count().sort_values(
    ascending=False
).head(10)

fig1 = px.bar(
    top_bowlers,
    x=top_bowlers.index,
    y=top_bowlers.values,
    title="Top IPL Wicket Takers",
    labels={
        'x': 'Bowler',
        'y': 'Wickets'
    }
)

st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ---------------------------------------------------
# BEST ECONOMY BOWLERS
# ---------------------------------------------------

st.subheader("💰 Best Economy Bowlers")

economy_df = filtered_df.groupby(
    'bowler'
).agg({
    'runs_total': 'sum',
    'ball': 'count'
})

economy_df['economy'] = (
    economy_df['runs_total']
    /
    economy_df['ball']
) * 6

economy_df = economy_df[
    economy_df['ball'] > 300
]

best_economy = economy_df.sort_values(
    by='economy'
).head(10)

fig2 = px.bar(
    best_economy,
    x='economy',
    y=best_economy.index,
    orientation='h',
    title="Best Economy Rates (Min 300 Balls)",
    labels={
        'economy': 'Economy Rate',
        'y': 'Bowler'
    }
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---------------------------------------------------
# DOT BALL ANALYSIS
# ---------------------------------------------------

st.subheader("⚪ Dot Ball Specialists")

dot_ball_df = filtered_df[
    filtered_df['runs_total'] == 0
]

dot_ball_stats = dot_ball_df.groupby(
    'bowler'
)['runs_total'].count().sort_values(
    ascending=False
).head(10)

fig3 = px.bar(
    dot_ball_stats,
    x=dot_ball_stats.values,
    y=dot_ball_stats.index,
    orientation='h',
    title="Most Dot Balls",
    labels={
        'x': 'Dot Balls',
        'y': 'Bowler'
    }
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ---------------------------------------------------
# SEASON-WISE WICKETS
# ---------------------------------------------------

st.subheader("📅 Season-wise Wickets")

season_wickets = filtered_df[
    filtered_df['wicket_kind'].notna()
]

season_wickets = season_wickets.groupby(
    'season'
)['wicket_player_out'].count().reset_index()

fig4 = px.line(
    season_wickets,
    x='season',
    y='wicket_player_out',
    markers=True,
    title="Total IPL Wickets by Season"
)

st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ---------------------------------------------------
# TEAM BOWLING PERFORMANCE
# ---------------------------------------------------

st.subheader("👥 Team Bowling Strength")

team_bowling_df = filtered_df.copy()

# Create Bowling Team Column
team_bowling_df['bowling_team'] = team_bowling_df.apply(
    lambda x:
    x['team2']
    if x['batting_team'] == x['team1']
    else x['team1'],
    axis=1
)

team_wickets = team_bowling_df[
    team_bowling_df['wicket_kind'].notna()
]

team_wickets = team_wickets.groupby(
    'bowling_team'
)['wicket_player_out'].count().sort_values(
    ascending=False
)

fig5 = px.bar(
    team_wickets,
    x=team_wickets.index,
    y=team_wickets.values,
    title="Team-wise Wickets",
    labels={
        'x': 'Team',
        'y': 'Wickets'
    }
)

st.plotly_chart(fig5, use_container_width=True)

# ---------------------------------------------------
# PLAYER WICKET DISTRIBUTION
# ---------------------------------------------------

if selected_bowler != "All":

    st.subheader(
        f"📈 {selected_bowler} Wicket Types"
    )

    wicket_types = wickets_df[
        'wicket_kind'
    ].value_counts()

    fig6 = px.pie(
        values=wicket_types.values,
        names=wicket_types.index,
        title=f"{selected_bowler} Dismissal Types"
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )

    st.divider()

# ---------------------------------------------------
# INSIGHTS
# ---------------------------------------------------

st.subheader("🧠 Key Insights")

st.success("""
• Dot-ball pressure is a major factor
  in successful bowling performances.

• Economy rate often impacts matches
  more than wicket count alone.

• Death-over specialists play a critical
  role in IPL victories.

• Consistent wicket-taking bowlers
  influence match momentum heavily.

• Balanced bowling attacks perform
  better across long tournaments.
""")

st.divider()

# ---------------------------------------------------
# CONCLUSION
# ---------------------------------------------------

st.subheader("📌 Conclusion")

st.markdown("""
Bowling success in IPL depends on wicket-taking,
economy control, pressure creation,
and adaptability across match phases.
Strong bowling units consistently
shape match outcomes.
""")