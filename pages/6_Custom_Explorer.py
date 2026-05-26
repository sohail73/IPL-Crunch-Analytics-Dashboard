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
    page_title="Custom Analytics Explorer",
    page_icon="🛠️",
    layout="wide"
)

# LOAD DATA
df = load_data()
filtered_df = df.copy()

# PAGE TITLE
st.title("Custom Cross-Section Explorer")
st.markdown("""
Cross-examine performance matrices by filtering specifically down to **Seasons** and **Team Matchups**. 
Build your own data slice dynamically!
""")
st.divider()
# CROSS FILTERS SECTION (HORIZONTAL BAND FOR EASY ACCESS)
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    seasons = sorted(filtered_df['season'].dropna().unique())
    selected_season = st.selectbox("Select IPL Season", ["All Seasons"] + [str(s) for s in seasons])

with col_f2:
    all_teams = sorted(pd.unique(filtered_df[['team1', 'team2']].stack().dropna().drop_duplicates()))
    selected_team1 = st.selectbox("Select Primary Team (Team 1)", ["All Teams"] + list(all_teams))

with col_f3:
    # Filter available teams for Team 2 to avoid selecting the same team
    team2_options = [t for t in all_teams if t != selected_team1] if selected_team1 != "All Teams" else all_teams
    selected_team2 = st.selectbox("Select Opponent Team (Team 2)", ["All Teams"] + list(team2_options))

# APPLYING THE EXPLORER FILTERS LOGIC
# 1. Season Filter
if selected_season != "All Seasons":
    filtered_df = filtered_df[filtered_df['season'] == int(selected_season)]

# 2. Team Matchup Filters
if selected_team1 != "All Teams" and selected_team2 != "All Teams":
    # Strict Head-to-Head Matchup
    filtered_df = filtered_df[
        ((filtered_df['team1'] == selected_team1) & (filtered_df['team2'] == selected_team2)) |
        ((filtered_df['team1'] == selected_team2) & (filtered_df['team2'] == selected_team1))
        ]
elif selected_team1 != "All Teams":
    # Matches involving at least Team 1
    filtered_df = filtered_df[(filtered_df['team1'] == selected_team1) | (filtered_df['team2'] == selected_team1)]
elif selected_team2 != "All Teams":
    # Matches involving at least Team 2
    filtered_df = filtered_df[(filtered_df['team1'] == selected_team2) | (filtered_df['team2'] == selected_team2)]

# Match Level DataFrame for metrics
match_level = filtered_df.drop_duplicates(subset='match_id').copy()
# DYNAMIC METRICS BLOCKS
if match_level.empty:
    st.warning(
        "No matches found for this specific combination of Season and Team Matchup. Please alter your filters!")
else:
    total_m = match_level['match_id'].nunique()
    total_runs = filtered_df['runs_total'].sum()

    # Boundary calculations
    fours = filtered_df[filtered_df['runs_batter'] == 4].shape[0]
    sixes = filtered_df[filtered_df['runs_batter'] == 6].shape[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Matches in Slice", f"{total_m:,}")
    with col2:
        st.metric("Total Phase Runs", f"{total_runs:,}")
    with col3:
        st.metric("Total Fours (4s)", f"{fours:,}")
    with col4:
        st.metric("Total Sixes (6s)", f"{sixes:,}")

    st.divider()

    # EXPLORER VISUALIZATIONS
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Venues Custom Distribution")
        venue_data = match_level['venue'].value_counts().head(10).reset_index()
        venue_data.columns = ['Venue', 'Matches']

        fig1 = px.bar(
            venue_data,
            x='Matches',
            y='Venue',
            orientation='h',
            color='Matches',
            color_continuous_scale='Tealgrn',
            template='plotly_white',
            title="Where Did These Teams Play Most?"
        )
        fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False, height=380)
        st.plotly_chart(fig1, use_container_width=True)

    with col_g2:
        st.subheader("Toss Decision Behavior")
        toss_data = match_level['toss_decision'].value_counts().reset_index()
        toss_data.columns = ['Decision', 'Count']

        fig2 = px.pie(
            toss_data,
            values='Count',
            names='Decision',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe,
            title="Toss Selection Patterns in this Subset"
        )
        fig2.update_layout(template='plotly_white', height=380)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    # INTERACTIVE SCORING RADAR/LINE TREND
    st.subheader("Innings-wise Run Progression Trend")

    # Calculate average runs per over in this specific subset
    over_runs = filtered_df.groupby(['innings', 'over'])['runs_total'].mean().reset_index()
    over_runs['Display Over'] = over_runs['over'] + 1
    over_runs = over_runs[over_runs['innings'].isin([1, 2])]  # keep 1st and 2nd innings only
    over_runs['Innings'] = over_runs['innings'].map({1: '1st Innings Bag', 2: '2nd Innings Chasing'})

    fig3 = px.line(
        over_runs,
        x='Display Over',
        y='runs_total',
        color='Innings',
        markers=True,
        labels={'runs_total': 'Avg Runs Per Over', 'Display Over': 'Over Number'},
        template='plotly_white',
        title="Innings-wise Run Velocity (Over-by-Over Curve)"
    )
    fig3.update_layout(xaxis=dict(tickmode='linear', dtick=1), height=400)
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()
    # UNDERLYING MATCH LIST TABLE
    st.subheader("Filtered Match Logs")
    st.markdown("Here is the exact record of matches filtered out based on your dynamic sidebar rules:")

    # Preparing a clean viewable tabular format
    display_matches = match_level[
        ['season', 'date', 'team1', 'team2', 'venue', 'toss_winner', 'toss_decision', 'winner']].copy()
    display_matches.columns = ['Season', 'Match Date', 'Team 1', 'Team 2', 'Stadium Venue', 'Toss Winner',
                               'Toss Choice', 'Match Winner']

    st.dataframe(display_matches.reset_index(drop=True), use_container_width=True)