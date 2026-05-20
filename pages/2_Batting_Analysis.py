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

# PAGE TITLE


st.title("Batting Analytics")

st.markdown("""
Analyze batter performance, strike rates,
boundary dominance, consistency,
and batting impact across IPL seasons.
""")

st.divider()

# PAGE FILTERS


batters = sorted(
    filtered_df['batter'].dropna().unique()
)

selected_batter = st.selectbox(
    "Select Batter",
    ["All"] + list(batters)
)

# APPLY BATTER FILTER


batting_df = filtered_df.copy()

if selected_batter != "All":
    batting_df = batting_df[
        batting_df['batter']
        == selected_batter
    ]

# KPI SECTION


total_runs = batting_df[
    'runs_batter'
].sum()

total_balls = batting_df.shape[0]

strike_rate = round(
    (total_runs / total_balls) * 100,
    2
)

total_fours = batting_df[
    batting_df['runs_batter'] == 4
].shape[0]

total_sixes = batting_df[
    batting_df['runs_batter'] == 6
].shape[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🏏 Total Runs",
        total_runs
    )

with col2:
    st.metric(
        "⚡ Strike Rate",
        strike_rate
    )

with col3:
    st.metric(
        "4️⃣ Fours",
        total_fours
    )

with col4:
    st.metric(
        "6️⃣ Sixes",
        total_sixes
    )

st.divider()

# TOP BATTERS


st.subheader("🔥 Top Run Scorers")

top_batters = filtered_df.groupby(
    'batter'
)['runs_batter'].sum().sort_values(
    ascending=False
).head(10)

fig1 = px.bar(
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

st.plotly_chart(fig1, use_container_width=True)

st.divider()

# STRIKE RATE ANALYSIS


st.subheader("⚡ Strike Rate Analysis")

batter_stats = filtered_df.groupby(
    'batter'
).agg({
    'runs_batter': 'sum',
    'ball': 'count'
})

batter_stats['strike_rate'] = (
    batter_stats['runs_batter']
    /
    batter_stats['ball']
) * 100

batter_stats = batter_stats[
    batter_stats['ball'] > 300
]

top_sr = batter_stats.sort_values(
    by='strike_rate',
    ascending=False
).head(10)

fig2 = px.bar(
    top_sr,
    x='strike_rate',
    y=top_sr.index,
    orientation='h',
    title="Best Strike Rates (Min 300 Balls)",
    labels={
        'strike_rate': 'Strike Rate',
        'y': 'Batter'
    }
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# BOUNDARY ANALYSIS


st.subheader("🎯 Boundary Dominance")

boundary_df = filtered_df[
    filtered_df['runs_batter'].isin([4, 6])
]

boundary_stats = boundary_df.groupby(
    'batter'
)['runs_batter'].count().sort_values(
    ascending=False
).head(10)

fig3 = px.bar(
    boundary_stats,
    x=boundary_stats.values,
    y=boundary_stats.index,
    orientation='h',
    title="Most Boundaries",
    labels={
        'x': 'Boundaries',
        'y': 'Batter'
    }
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# RUNS BY SEASON

st.subheader("📅 Season-wise Batting Trend")

season_runs = filtered_df.groupby(
    'season'
)['runs_batter'].sum().reset_index()

fig4 = px.line(
    season_runs,
    x='season',
    y='runs_batter',
    markers=True,
    title="Total IPL Runs by Season"
)

st.plotly_chart(fig4, use_container_width=True)

st.divider()

# TEAM BATTING STRENGTH

st.subheader("👥 Team Batting Strength")

team_runs = filtered_df.groupby(
    'batting_team'
)['runs_batter'].sum().sort_values(
    ascending=False
)

fig5 = px.bar(
    team_runs,
    x=team_runs.index,
    y=team_runs.values,
    title="Team-wise Total Runs",
    labels={
        'x': 'Team',
        'y': 'Runs'
    }
)

st.plotly_chart(fig5, use_container_width=True)

st.divider()

# PLAYER RUN DISTRIBUTION


if selected_batter != "All":

    st.subheader(f"📈 {selected_batter} Run Distribution")

    run_distribution = batting_df[
        'runs_batter'
    ].value_counts().sort_index()

    fig6 = px.bar(
        x=run_distribution.index,
        y=run_distribution.values,
        title=f"{selected_batter} Scoring Pattern",
        labels={
            'x': 'Runs Per Ball',
            'y': 'Frequency'
        }
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )

    st.divider()

# INSIGHTS


st.subheader("🧠 Key Insights")

st.success("""
• High strike rates often correlate with
  match-winning performances.

• Boundary frequency heavily impacts
  batting dominance.

• Certain players maintain consistency
  across multiple IPL seasons.

• Aggressive middle-order batting
  changes match momentum significantly.

• Teams with balanced batting depth
  perform better under pressure.
""")

st.divider()


# CONCLUSION

st.subheader("📌 Conclusion")

st.markdown("""
Batting success in IPL depends not only on
total runs but also on strike rotation,
boundary conversion, consistency,
and adaptability across match situations.
""")