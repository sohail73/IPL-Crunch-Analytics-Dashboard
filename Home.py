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
Explore IPL trends, match-winning patterns,
batting dominance, bowling impact,
venue intelligence, and advanced insights.
""")

st.divider()
# Data Preprocessing
#total matches
total_matches = match_level['match_id'].nunique()

#total teams
team_cleaner={
    'Rising Pune Supergiants': 'Rising Pune Supergiant',
    'Delhi Daredevils': 'Delhi Capitals',
    'Kings XI Punjab': 'Punjab Kings',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru'
}
df['team1']=df['team1'].replace(team_cleaner)
df['team2']=df['team2'].replace(team_cleaner)
total_teams = len(pd.unique(df[['team1','team2']].stack().drop_duplicates()))

# total seasons
season_map = {
    '2007/08': 2008,
    '2009/10': 2010,
    '2020/21': 2020
}
df['season'] = df['season'].replace(season_map)
df['season'] =df['season'].astype(int)
total_seasons = len(sorted(df['season'].unique()))

# highest score
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
        "Total Seasons",
        total_seasons
    )

with col4:
    st.metric(
        "Highest Score",
        highest_score
    )
st.divider()

# TOSS IMPACT OVERVIEW

df['toss_and_match_win'] = df['toss_winner'] == df['winner']

toss_win_percentage = df['toss_and_match_win'].mean() * 100
col1, col2, col3 = st.columns([2,2,2])

# ---------------- PIE CHART ---------------- #
with col1:
    st.markdown("#### Toss Winner Match Success")
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

    st.plotly_chart(fig, use_container_width=True)


# ---------------- BAR CHART ---------------- #
with col2:
    st.markdown("#### Toss Decisions")
    toss_decision = match_level[
        'toss_decision'
    ].value_counts()

    fig2 = px.bar(
        x=toss_decision.index,
        y=toss_decision.values,
        labels={
            'x': 'Decision',
            'y': 'Count'
        }
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------------- PLAYER CARD ---------------- #
with col3:

    st.markdown("#### Top Run Scorer")

    c1, c2 = st.columns([2,1])

    with c1:
        st.image(
            "virat.png"
        )

    with c2:
        st.markdown("### VIRAT KOHLI")
        st.markdown("### 9050 Runs")
        st.markdown("Matches: 269")
        st.markdown("Average: 40.04")

#insights
st.subheader("Insight")
st.info("""
- Winning the toss does not guarantee match victory. IPL matches remain highly competitive regardless of toss outcome.
- Teams mostly prefer bowling first, showing a strong chasing trend in modern IPL seasons.
- Virat Kohli remains the highest run scorer in IPL history with remarkable consistency across seasons.
""")

st.divider()

# TOP BATTERS
st.subheader("Top 10 IPL Run Scorers")

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
    labels={
        'x': 'Runs',
        'y': 'Batter'
    }
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# TOP BOWLERS
st.subheader("Top IPL Wicket Takers")

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
    labels={
        'x': 'Bowler',
        'y': 'Wickets'
    }
)

st.plotly_chart(fig4, use_container_width=True)
st.info("""
- Spin bowlers and death-over specialists dominate the IPL wicket charts, showing the importance of variation and consistency in T20 cricket
- Yuzvendra Chahal leads the wicket charts, proving the long-term impact  of quality spin bowling in IPL history
""")
st.divider()

# VENUE OVERVIEW

st.subheader("Top IPL Venues")

venue_counts = match_level[
    'venue'
].value_counts().head(10)

fig5 = px.bar(
    venue_counts,
    x=venue_counts.values,
    y=venue_counts.index,
    orientation='h',
    labels={
        'x': 'Matches Hosted',
        'y': 'Venue'
    }
)

st.plotly_chart(fig5, use_container_width=True)

st.info("- Eden Gardens has hosted the highest number of IPL matches, making it one of the league's most iconic venues.")
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

