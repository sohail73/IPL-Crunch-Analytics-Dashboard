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
    page_title="Venue Analysis",
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
# MATCH LEVEL DATA
# ---------------------------------------------------

match_level = filtered_df.drop_duplicates(
    subset='match_id'
)

# ---------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------

st.title("🏟 Venue Analysis")

st.markdown("""
Analyze venue behavior, scoring trends,
toss impact, win patterns,
and stadium conditions across IPL venues.
""")

st.divider()

# ---------------------------------------------------
# PAGE FILTERS
# ---------------------------------------------------

venues = sorted(
    match_level['venue'].dropna().unique()
)

selected_venue = st.selectbox(
    "Select Venue",
    ["All"] + list(venues)
)

# ---------------------------------------------------
# APPLY VENUE FILTER
# ---------------------------------------------------

venue_df = filtered_df.copy()
venue_match_df = match_level.copy()

if selected_venue != "All":

    venue_df = venue_df[
        venue_df['venue']
        == selected_venue
    ]

    venue_match_df = venue_match_df[
        venue_match_df['venue']
        == selected_venue
    ]

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

total_matches = venue_match_df[
    'match_id'
].nunique()

avg_score = round(
    venue_df.groupby(
        ['match_id', 'batting_team']
    )['runs_total'].sum().mean(),
    2
)

highest_score = venue_df.groupby(
    ['match_id', 'batting_team']
)['runs_total'].sum().max()

total_venues = venue_match_df[
    'venue'
].nunique()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🏏 Total Matches",
        total_matches
    )

with col2:
    st.metric(
        "📈 Average Score",
        avg_score
    )

with col3:
    st.metric(
        "🔥 Highest Score",
        highest_score
    )

with col4:
    st.metric(
        "🏟 Venues",
        total_venues
    )

st.divider()

# ---------------------------------------------------
# MOST USED VENUES
# ---------------------------------------------------

st.subheader("🏟 Most Used IPL Venues")

venue_counts = match_level[
    'venue'
].value_counts().head(10)

fig1 = px.bar(
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

st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ---------------------------------------------------
# VENUE SCORING ANALYSIS
# ---------------------------------------------------

st.subheader("📈 Highest Scoring Venues")

venue_scores = filtered_df.groupby(
    ['venue', 'match_id', 'batting_team']
)['runs_total'].sum().reset_index()

venue_avg_scores = venue_scores.groupby(
    'venue'
)['runs_total'].mean().sort_values(
    ascending=False
).head(10)

fig2 = px.bar(
    venue_avg_scores,
    x=venue_avg_scores.values,
    y=venue_avg_scores.index,
    orientation='h',
    title="Highest Average Team Scores",
    labels={
        'x': 'Average Score',
        'y': 'Venue'
    }
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---------------------------------------------------
# TOSS IMPACT BY VENUE
# ---------------------------------------------------

st.subheader("📊 Toss Impact by Venue")

venue_toss = match_level.groupby(
    'venue'
).apply(
    lambda x:
    (
        (
            x['toss_winner']
            ==
            x['winner']
        ).mean()
    ) * 100
).sort_values(
    ascending=False
).head(10)

fig3 = px.bar(
    venue_toss,
    x=venue_toss.values,
    y=venue_toss.index,
    orientation='h',
    title="Venues Where Toss Matters Most",
    labels={
        'x': 'Toss Win Match %',
        'y': 'Venue'
    }
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ---------------------------------------------------
# CITY-WISE MATCHES
# ---------------------------------------------------

st.subheader("🌆 City-wise IPL Matches")

city_matches = match_level[
    'city'
].value_counts().head(10)

fig4 = px.pie(
    values=city_matches.values,
    names=city_matches.index,
    title="Top IPL Cities"
)

st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ---------------------------------------------------
# TEAM PERFORMANCE AT VENUES
# ---------------------------------------------------

st.subheader("👥 Team Performance at Venues")

team_venue_wins = venue_match_df.groupby(
    ['venue', 'winner']
)['match_id'].count().reset_index()

top_team_venue = team_venue_wins.sort_values(
    by='match_id',
    ascending=False
).head(10)

fig5 = px.bar(
    top_team_venue,
    x='winner',
    y='match_id',
    color='venue',
    title="Most Successful Teams at Venues",
    labels={
        'winner': 'Team',
        'match_id': 'Wins'
    }
)

st.plotly_chart(fig5, use_container_width=True)

st.divider()

# ---------------------------------------------------
# SEASON-WISE VENUE TREND
# ---------------------------------------------------

st.subheader("📅 Venue Scoring Trends")

season_scores = filtered_df.groupby(
    ['season', 'match_id', 'batting_team']
)['runs_total'].sum().reset_index()

season_avg = season_scores.groupby(
    'season'
)['runs_total'].mean().reset_index()

fig6 = px.line(
    season_avg,
    x='season',
    y='runs_total',
    markers=True,
    title="Average IPL Team Scores by Season"
)

st.plotly_chart(fig6, use_container_width=True)

st.divider()

# ---------------------------------------------------
# INSIGHTS
# ---------------------------------------------------

st.subheader("🧠 Key Insights")

st.success("""
• Certain venues consistently produce
  higher-scoring matches.

• Toss advantage varies significantly
  depending on venue conditions.

• Chasing teams perform better
  at specific stadiums.

• Venue dimensions strongly impact
  batting strategies.

• Some teams dominate consistently
  at their home venues.
""")

st.divider()

# ---------------------------------------------------
# CONCLUSION
# ---------------------------------------------------

st.subheader("📌 Conclusion")

st.markdown("""
Venue conditions play a critical role
in IPL outcomes. Pitch behavior,
boundary dimensions, weather,
and toss decisions together shape
team strategies and match results.
""")