import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import plotly.io as pio

pio.templates["custom"] = pio.templates["plotly_dark"]

pio.templates["custom"].layout.colorway = [
    "#1E90FF",  # blue
    "red",  # sky blue
]

pio.templates.default = "custom"
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
    return pd.read_csv('data/clean_ipl_data.csv')
df = load_data()


# MATCH LEVEL DATA
match_level = df.drop_duplicates(subset='match_id')
# HEADER
st.title("IPL Crunch Analytics Dashboard")

st.markdown("""
Explore IPL trends, match-winning patterns,
batting dominance, bowling impact,
venue intelligence, and advanced insights.
""")
st.markdown('Data Source: 2008 - May 2026')

st.divider()

#total matches
total_matches = match_level['match_id'].nunique()
total_teams = len(pd.unique(df[['team1','team2']].stack().drop_duplicates()))

# total seasons
total_seasons = len(sorted(df['season'].unique()))

# highest score
highest_score = df.groupby(['match_id', 'batting_team'])['runs_total'].sum().max()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Matches",total_matches)

with col2:
    st.metric("Total Teams",total_teams)

with col3:
    st.metric("Total Seasons",total_seasons)

with col4:
    st.metric("Highest Score",highest_score)
st.divider()

# TOSS IMPACT OVERVIEW

df['toss_and_match_win'] = df['toss_winner'] == df['winner']

toss_win_percentage = df['toss_and_match_win'].mean() * 100
col1, col2, col3 = st.columns([2,2,2])

# PIE CHART
with col1:
    st.markdown("#### Toss Winner Match Success")
    matches_df = df[['match_id', 'toss_winner', 'toss_decision', 'winner']].drop_duplicates()

    matches_df['Toss_Result'] = matches_df.apply(lambda row: 'Toss Winner Won' if row['toss_winner'] == row['winner'] else 'Toss Winner Lost', axis=1)

    fig_toss_pie = px.pie(
        matches_df,
        names='Toss_Result',
        hole=0.5,
        color='Toss_Result',

        color_discrete_map={'Toss Winner Won': '#00E6B4', 'Toss Winner Lost': '#d62728'}
    )

    fig_toss_pie.update_traces(
        textinfo='percent+value',
        hovertemplate="<b>%{label}</b><br>Matches: %{value}<br>Percentage: %{percent}<extra></extra>"
    )

    st.plotly_chart(fig_toss_pie, use_container_width=True)

# BAR CHART
with col2:
    st.markdown("#### Toss Decisions")
    toss_decision = match_level['toss_decision'].value_counts()

    fig2 = px.bar(
        x=toss_decision.index,
        y=toss_decision.values,
        labels={'x': 'Decision', 'y': 'Count'},
        color=toss_decision.index,
        color_discrete_sequence=[
            '#00E6B4',
            '#d62728',
        ],
    )

    fig2.update_traces(texttemplate='%{y}', textposition='outside')
    fig2.update_layout(
        template='plotly_white',
        showlegend=False,
        yaxis_range=[0, max(toss_decision.values) + 100],
    )

    st.plotly_chart(fig2, use_container_width=True)

# PLAYER CARD
with col3:

    st.markdown("#### Top Run Scorer")
    c1, c2 = st.columns([2,1])

    with c1:
        st.image("virat.png")

    with c2:
        st.markdown("### VIRAT KOHLI")
        st.markdown("### 9050 Runs")
        st.markdown("Matches: 268")
        st.markdown("Average: 40.04")

#insights
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    st.info("- Winning the toss does not guarantee match victory. IPL matches remain highly competitive regardless of toss outcome.")

with col_in2:
    st.success("- Teams mostly prefer bowling first, showing a strong chasing trend in modern IPL seasons.")

with col_in3:
    st.warning("- Virat Kohli remains the highest run scorer in IPL history with remarkable consistency across seasons.")

st.divider()

# TOP BATTERS

st.subheader("Top 10 IPL Run Scorers")

batter_stats = (df.groupby('batter').agg(total_runs=('runs_batter', 'sum'),matches_batted=('match_id', 'nunique'),).reset_index())

top_scorers_df = batter_stats.sort_values(by='total_runs', ascending=False).head(10)

fig3 = px.bar(
    top_scorers_df,
    x='batter',
    y='total_runs',
    labels={'batter': 'Batsman', 'total_runs': 'Total Runs'},
    title='Top 10 IPL Run Scorers',
    color='total_runs',
    color_continuous_scale='Plasma',
)

st.plotly_chart(fig3, use_container_width=True)

st.info("- Virat Kohli dominates the IPL run charts, highlighting his long-term consistency and elite batting performance.")
st.divider()

# TOP BOWLERS
st.subheader("Top IPL Wicket Takers")

bowler_wickets = ['caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket']
df_wickets = df[df['wicket_kind'].isin(bowler_wickets)]


top_bowlers_df = (df_wickets.groupby('bowler').size().reset_index(name='Wickets').sort_values(by='Wickets', ascending=False).head(10))

fig4 = px.bar(
    top_bowlers_df,
    x='bowler',
    y='Wickets',
    labels={'bowler': 'Bowler', 'Wickets': 'Total Wickets'},
    title='Top 10 IPL Wicket Takers',
    color='Wickets',
    color_continuous_scale='Viridis',
)

st.plotly_chart(fig4, use_container_width=True)

st.info("""
- Spin bowlers and death-over specialists dominate the IPL wicket charts, showing the importance of variation and consistency in T20 cricket
- Yuzvendra Chahal leads the wicket charts, proving the long-term impact  of quality spin bowling in IPL history
""")
st.divider()

# VENUE OVERVIEW

st.subheader("Top IPL Venues")

top_venues_df = (df.groupby('cleaned_venue')['match_id'].nunique().reset_index(name='Matches').sort_values(by='Matches', ascending=False).head(10))
fig5 = px.bar(
    top_venues_df,
    x='cleaned_venue',
    y='Matches',
    labels={'cleaned_venue': 'Stadium', 'Matches': 'Matches Played'},
    title='Top 10 IPL Venues by Matches Played',
    color='Matches',
    color_continuous_scale='Cividis',
)
st.plotly_chart(fig5, use_container_width=True)

st.info("- Wankhede Stadium (Mumbai) has hosted the highest number of IPL matches, making it one of the league's most iconic venues.")
st.divider()

# KEY INSIGHTS

st.markdown("### Insights")

col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    st.info(
        "** Batting Dominance**\n\n"
        "**Virat Kohli** leads the all-time charts with **9,050 runs** in 268 innings, "
        "maintaining a stellar average of **40.04**. He remains the ultimate run-machine of IPL."
    )

with col_in2:
    st.success(
        "** Bowling King**\n\n"
        "**Yuzvendra Chahal** sits right at the top as the leading wicket-taker with **229 wickets** in 181 matches. "
        "His leg-spin has been the most effective weapon in IPL history."
    )

with col_in3:
    st.warning(
        "** The Toss Trend **\n\n"
        "Teams strongly prefer chasing, electing to **Field First in ~66%** of matches. "
        "However, winning the toss only gives a minor edge, with a match win success rate of **50.49%**."
    )

