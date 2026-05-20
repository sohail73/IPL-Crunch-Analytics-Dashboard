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
    page_title="IPL Crunch Analytics Dashboard",
    page_icon="🏏",
    layout="wide"
)


#LOAD DATASET
@st.cache_data
def load_data():
    return pd.read_csv('data/ipl_crunch_data.csv')
df = load_data()


# MATCH LEVEL DATA
match_level = df.drop_duplicates(
    subset='match_id'
)
# HEADER
st.title("IPL Crunch Analytics Dashboard")

st.markdown("""
### Advanced Cricket Analytics Platform

Explore IPL trends, match-winning patterns,
batting dominance, bowling impact,
venue intelligence, and advanced insights.
""")

st.divider()

# KPI SECTION
total_matches = match_level['match_id'].nunique()

total_teams = len(pd.unique(df[['team1', 'team2']].values.ravel()))

total_seasons = df['season'].nunique()

highest_score = df.groupby(
    ['match_id', 'batting_team']
)['runs_total'].sum().max()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Matches",
        total_matches
    )

with col2:
    st.metric(
        "Total Teams",
        total_teams
    )

with col3:
    st.metric(
        "Seasons",
        total_seasons
    )

with col4:
    st.metric(
        "Highest Score",
        highest_score
    )
st.divider()

# TOSS IMPACT OVERVIEW
st.subheader("Toss Impact Overview")

toss_win_matches = match_level[
    match_level['toss_winner']
    ==
    match_level['winner']
]

toss_win_percentage = round(
    (
        toss_win_matches.shape[0]
        /
        match_level.shape[0]
    ) * 100,
    2
)
col1, col2 = st.columns(2)

with col1:

    fig = go.Figure(data=[
        go.Pie(
            labels=[
                'Won Match',
                'Lost Match'
            ],
            values=[
                toss_win_percentage,
                100 - toss_win_percentage
            ],
            hole=0.45
        )
    ])
    fig.update_layout(
        title="Toss Winner Match Success"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    toss_decision = match_level[
        'toss_decision'
    ].value_counts()

    fig2 = px.bar(
        x=toss_decision.index,
        y=toss_decision.values,
        title="Toss Decisions",
        labels={
            'x': 'Decision',
            'y': 'Count'
        }
    )

    st.plotly_chart(fig2, use_container_width=True)

st.info(
    f"Teams winning the toss won "
    f"{toss_win_percentage}% matches overall."
)

st.divider()

# TOP BATTERS
st.subheader("Top Batters")

top_batters = df.groupby(
    'batter'
)['runs_batter'].sum().sort_values(
    ascending=False
).head(10)

fig3 = px.bar(
    top_batters,
    x=top_batters.values,
    y=top_batters.index,
    orientation='h',
    title="Top 10 IPL Run Scorers",
    labels={
        'x': 'Runs',
        'y': 'Batter'
    }
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# TOP BOWLERS
st.subheader("Top Bowlers")

wickets = df[
    df['wicket_kind'].notna()
]

top_bowlers = wickets.groupby(
    'bowler'
)['wicket_player_out'].count().sort_values(
    ascending=False
).head(10)

fig4 = px.bar(
    top_bowlers,
    x=top_bowlers.index,
    y=top_bowlers.values,
    title="Top IPL Wicket Takers",
    labels={
        'x': 'Bowler',
        'y': 'Wickets'
    }
)

st.plotly_chart(fig4, use_container_width=True)

st.divider()

# VENUE OVERVIEW

st.subheader("Venue Overview")

venue_counts = match_level[
    'venue'
].value_counts().head(10)

fig5 = px.bar(
    venue_counts,
    x=venue_counts.values,
    y=venue_counts.index,
    orientation='h',
    title="Top IPL Venues",
    labels={
        'x': 'Matches Hosted',
        'y': 'Venue'
    }
)

st.plotly_chart(fig5, use_container_width=True)

st.divider()

# QUICK INSIGHTS
st.subheader("Quick Insights")

st.success(f"""
• Teams winning the toss won {toss_win_percentage}% matches overall.

• Strong powerplay starts often create match momentum.

• Death overs heavily influence final match outcomes.

• Certain venues strongly favor chasing teams.

• Consistent teams dominate across all match phases.
""")

st.divider()

