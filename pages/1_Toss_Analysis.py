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
    page_title="Toss Analysis",
    page_icon="🏏",
    layout="wide"
)

# LOAD DATA
@st.cache_data
def load_data():
    return pd.read_csv('data/ipl_crunch_data.csv')
df = load_data()

# GET GLOBAL FILTERS

selected_season = st.session_state.get(
    "selected_season",
    "All"
)

selected_team = st.session_state.get(
    "selected_team",
    "All"
)

# APPLY GLOBAL FILTERS
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
# MATCH LEVEL DATA

match_level = filtered_df.drop_duplicates(
    subset='match_id'
)

# PAGE TITLE
st.title("Toss Impact Analysis")

st.markdown("""
Analyze how toss decisions influence
match outcomes across IPL seasons.
""")
st.divider()

# PAGE FILTERS
venues = sorted(
    match_level['venue'].dropna().unique()
)

selected_venue = st.selectbox(
    "Select Venue",
    ["All"] + list(venues)
)
# APPLY VENUE FILTER
if selected_venue != "All":
    match_level = match_level[
        match_level['venue']
        == selected_venue
    ]

# KPI SECTION
total_matches = match_level.shape[0]

toss_win_matches = match_level[
    match_level['toss_winner']
    ==
    match_level['winner']
]

toss_win_percentage = round(
    (
        toss_win_matches.shape[0]
        /
        total_matches
    ) * 100,
    2
)

bat_first_wins = match_level[
    match_level['toss_decision']
    == 'bat'
].shape[0]

field_first_wins = match_level[
    match_level['toss_decision']
    == 'field'
].shape[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Matches",
        total_matches
    )

with col2:
    st.metric(
        "Toss Win Match %",
        f"{toss_win_percentage}%"
    )

with col3:
    st.metric(
        "Bat First Decisions",
        bat_first_wins
    )

with col4:
    st.metric(
        "Field First Decisions",
        field_first_wins
    )

st.divider()

# TOSS WIN VS MATCH WIN

st.subheader("Toss Winner vs Match Winner")

col1, col2 = st.columns(2)

with col1:

    fig1 = go.Figure(data=[
        go.Pie(
            labels=[
                "Won Match",
                "Lost Match"
            ],
            values=[
                toss_win_percentage,
                100 - toss_win_percentage
            ],
            hole=0.45
        )
    ])

    fig1.update_layout(
        title="Toss Winner Match Success"
    )

    st.plotly_chart(fig1, use_container_width=True)

with col2:

    toss_decision_counts = match_level[
        'toss_decision'
    ].value_counts()

    fig2 = px.bar(
        x=toss_decision_counts.index,
        y=toss_decision_counts.values,
        title="Toss Decisions",
        labels={
            'x': 'Decision',
            'y': 'Count'
        }
    )

    st.plotly_chart(fig2, use_container_width=True)

st.divider()
# VENUE-WISE TOSS IMPACT
st.subheader("Venue-wise Toss Impact")

venue_toss = match_level.groupby(
    'venue'
).apply(
    lambda x: (
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
    title="Top Venues Where Toss Matters Most",
    labels={
        'x': 'Toss Win Match %',
        'y': 'Venue'
    }
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# SEASON-WISE TOSS IMPACT
st.subheader("Season-wise Toss Impact")

season_toss = match_level.groupby(
    'season'
).apply(
    lambda x: (
        (
            x['toss_winner']
            ==
            x['winner']
        ).mean()
    ) * 100
).reset_index(name='win_percentage')

fig4 = px.line(
    season_toss,
    x='season',
    y='win_percentage',
    markers=True,
    title="Toss Impact Across Seasons"
)

st.plotly_chart(fig4, use_container_width=True)

st.divider()

# TEAM-WISE TOSS PERFORMANCE
st.subheader("Team-wise Toss Success")

match_level['toss_match_win'] = (
    match_level['toss_winner'] == match_level['winner']
)

team_toss = (
    match_level.groupby('toss_winner')['toss_match_win']
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

fig5 = px.bar(
    team_toss,
    x=team_toss.index,
    y=team_toss.values,
    title="Teams Converting Toss Wins into Match Wins",
    labels={
        'x': 'Team',
        'y': 'Success %'
    }
)

st.plotly_chart(fig5, use_container_width=True)

st.divider()
# INSIGHTS
st.subheader("Key Insights")

st.success(f"""
• Teams winning the toss won {toss_win_percentage}% matches.

• Toss impact varies significantly across venues.

• Chasing decisions are generally preferred in IPL.

• Certain teams convert toss advantages more effectively.

• Toss influence changes across seasons due to evolving strategies.
""")

st.divider()
# CONCLUSION

st.subheader("Conclusion")

st.markdown("""
Toss advantage exists in IPL, but it is not the
sole deciding factor. Venue conditions,
team strength, and match execution often
have greater influence on outcomes.
""")