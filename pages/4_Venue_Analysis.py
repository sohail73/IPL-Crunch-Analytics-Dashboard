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
    page_title="Venue Analysis",
    page_icon="🏟",
    layout="wide"
)

# LOAD DATA
df = load_data()

df['is_toss_and_match_win'] = (df['toss_winner'] == df['winner']).astype(int)

filtered_df = df.copy()
match_level = filtered_df.drop_duplicates(subset='match_id').copy()

# PAGE TITLE

st.title("Venue & Ground Analytics")
st.markdown("""
Analyze venue behavior, scoring trends, toss dominance patterns, 
and franchise success matrices across various IPL stadiums.
""")
st.divider()

# PAGE FILTERS

venues = sorted(match_level['venue'].dropna().unique())
selected_venue = st.selectbox("Select Venue Focus", ["All"] + list(venues))

# APPLY VENUE FILTER
venue_df = filtered_df.copy()
venue_match_df = match_level.copy()

if selected_venue != "All":
    venue_df = venue_df[venue_df['venue'] == selected_venue]
    venue_match_df = venue_match_df[venue_match_df['venue'] == selected_venue]

# KPI SECTION

total_matches = venue_match_df['match_id'].nunique()

match_team_runs = venue_df.groupby(['match_id', 'innings', 'batting_team'])['runs_total'].sum().reset_index()
if not match_team_runs.empty:
    avg_score = round(match_team_runs['runs_total'].mean(), 2)
    highest_score = match_team_runs['runs_total'].max()
else:
    avg_score = 0.0
    highest_score = 0

total_venues_count = venue_match_df['venue'].nunique()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Matches Hosted", f"{total_matches:,}")
with col2:
    st.metric("Avg Innings Score", f"{avg_score}")
with col3:
    st.metric("Highest Team Total", f"{highest_score}")
with col4:
    st.metric("Active Venues", f"{total_venues_count}")

st.divider()

# CHARTS GRID 1: MOST USED & HIGHEST SCORING

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Most Used IPL Venues")
    venue_counts = match_level['venue'].value_counts().head(10).reset_index()
    venue_counts.columns = ['venue', 'count']

    fig1 = px.bar(
        venue_counts,
        x='count',
        y='venue',
        orientation='h',
        color='count',
        color_continuous_scale='Blues',
        labels={'count': 'Matches Hosted', 'venue': 'Stadium Name'},
        template='plotly_white'
    )
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=400)
    fig1.update_traces(texttemplate='%{x}', textposition='outside')
    st.plotly_chart(fig1, use_container_width=True)

with col_g2:
    st.subheader("Top High-Scoring Venues")
    # FIX: Added 'season' to the groupby list so it remains in the output columns
    all_venue_scores = filtered_df.groupby(['season', 'venue', 'match_id', 'innings', 'batting_team'])[
        'runs_total'].sum().reset_index()

    # Filter for stadiums that hosted minimum 5 matches to keep benchmarks standard
    venue_stats = all_venue_scores.groupby('venue').agg(
        avg_runs=('runs_total', 'mean'),
        match_count=('match_id', 'nunique')
    ).reset_index()

    highest_avg_venues = venue_stats[venue_stats['match_count'] >= 5].sort_values(by='avg_runs', ascending=False).head(
        10)

    fig2 = px.bar(
        highest_avg_venues,
        x='avg_runs',
        y='venue',
        orientation='h',
        color='avg_runs',
        color_continuous_scale='Mint',
        labels={'avg_runs': 'Avg Innings Score', 'venue': 'Stadium Name'},
        template='plotly_white'
    )
    fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=400)
    fig2.update_traces(texttemplate='%{x:.1f}', textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# CHARTS GRID 2: TOSS BIAS & CITY POPULARITY

col_g3, col_g4 = st.columns(2)

with col_g3:
    st.subheader("Toss Advantage Hotspots")
    toss_advantage = match_level.groupby('venue').agg(
        total_m=('match_id', 'count'),
        toss_match_wins=('is_toss_and_match_win', 'sum')
    ).reset_index()

    toss_advantage['Toss Win Match %'] = (toss_advantage['toss_match_wins'] / toss_advantage['total_m']) * 100
    top_toss_venues = toss_advantage[toss_advantage['total_m'] >= 5].sort_values(by='Toss Win Match %',
                                                                                 ascending=False).head(10)

    fig3 = px.bar(
        top_toss_venues,
        x='Toss Win Match %',
        y='venue',
        orientation='h',
        color='Toss Win Match %',
        color_continuous_scale='Purples',
        labels={'Toss Win Match %': 'Toss Conversion Rate (%)', 'venue': 'Venue'},
        template='plotly_white'
    )
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=400)
    fig3.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

with col_g4:
    st.subheader("Distribution by Cities")
    city_matches = match_level['city'].value_counts().head(10).reset_index()
    city_matches.columns = ['City', 'Matches Hosted']

    fig4 = px.pie(
        city_matches,
        values='Matches Hosted',
        names='City',
        color_discrete_sequence=px.colors.qualitative.Safe,
        hole=0.4
    )
    fig4.update_layout(template='plotly_white', height=400, margin=dict(t=20, b=20, l=10, r=10))
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# CHARTS GRID 3: TEAM SUCCESS & SEASON TREND

col_g5, col_g6 = st.columns(2)

with col_g5:
    st.subheader("Dominant Franchises at Venues")
    team_venue_wins = venue_match_df.groupby(['venue', 'winner'])['match_id'].count().reset_index()
    top_team_venue = team_venue_wins.sort_values(by='match_id', ascending=False).head(10)

    fig5 = px.bar(
        top_team_venue,
        x='match_id',
        y='winner',
        color='venue',
        orientation='h',
        labels={'winner': 'Franchise Team', 'match_id': 'Total Wins'},
        template='plotly_white'
    )
    fig5.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
    st.plotly_chart(fig5, use_container_width=True)

with col_g6:
    st.subheader("Historical Scoring Evolution")
    # FIX: Now this groupby runs perfectly because 'season' column is present
    season_avg = all_venue_scores.groupby('season')['runs_total'].mean().reset_index()
    season_avg['season'] = season_avg['season'].astype(str)

    fig6 = px.line(
        season_avg,
        x='season',
        y='runs_total',
        markers=True,
        labels={'season': 'IPL Season', 'runs_total': 'Avg Innings Score'},
        template='plotly_white'
    )
    fig6.update_traces(line=dict(color='#0284c7', width=3), marker=dict(size=8, color='#0f172a'))
    fig6.update_layout(height=400)
    st.plotly_chart(fig6, use_container_width=True)

st.divider()

# DYNAMIC INSIGHTS

st.subheader("Analytical Insights & Strategic Takeaways")

if selected_venue == "All":
    ins_col1, ins_col2 = st.columns(2)

    with ins_col1:
        st.info("""
        **Ground Dimension & Score Correlations**
        Certain stadiums consistently record higher average innings totals. This baseline helps data scientists understand pitch behavior, distinguishing high-altitude or short-boundary grounds from defensive spinner tracks.
        """)

        st.success("""
        **Fortress Dominance Index**
        The franchise venue matrix reveals that top teams build severe regional fortresses. Winning heavily at home venues acts as a critical cushion to lock down playoff spots early in a season.
        """)

    with ins_col2:
        st.warning("""
        **Structural Toss Leverage**
        Toss Win Match percentages show massive variation across venues. Grounds with severe dew pressure or flattening track cycles offer captains a heavy strategic edge right at the flip.
        """)

        st.success("""
        **Evolving T20 Batting Baseline**
        The historical season line trend establishes that the league-wide run average has shifted upward over time. Better batting depths and tactical powerplay utilization continuously change par scores.
        """)
else:
    # Custom automated calculations for the individual venue selected
    venue_toss_row = toss_advantage[toss_advantage['venue'] == selected_venue]
    toss_pct = round(venue_toss_row['Toss Win Match %'].values[0], 1) if not venue_toss_row.empty else 0

    ins_col1, ins_col2 = st.columns(2)

    with ins_col1:
        st.info(f"""
        **Specific Evaluation: {selected_venue}**
        - This stadium has hosted **{total_matches} matches** with a historic average team total of **{avg_score} runs**. This establishes the true operational par score for teams executing their first innings strategy here.
        """)

    with ins_col2:
        if toss_pct >= 55:
            bias_tag = "Critical Advantage (Chasing/Dew Dominant)"
        elif toss_pct <= 45:
            bias_tag = "Defensive Track (Pitch Deterioration Bias)"
        else:
            bias_tag = "Neutral Matrix (Execution Dependent)"

        st.success(f"""
        **Local Flip Conversion: {toss_pct}%**
        At {selected_venue}, the side winning the toss goes on to claim match victory **{toss_pct}%** of the time. 
        - This tactical conversion classifies the ground context as a **{bias_tag}**.
        """)

st.divider()

# SUMMARY & CAPTAIN'S PLAYBOOK
st.subheader("Summary")

st.markdown("""
> Venue behaviors shape match outcomes far before player match-ups begin. A professional tactical unit cannot rely on generic team combinations; squad depth must align perfectly with local stadium dimensions and surface patterns to optimize win distributions.
""")

st.markdown("""
### Strategic Captain's Ground Guidelines:
1. **Calibrate True Par Scores:** When batting first on high-scoring venues, target an acceleration index 15-20 runs above the tournament average line.
2. **Mitigate Toss Leverage:** On venues where the toss conversion clears 55%, defensive bowling deep configurations (extra death options) must be deployed to deny the chasing side an easy tempo.
3. **Regional Adaptation:** Tailor squad selections dynamically between high-pace bouncy surfaces and low-drift turning tracks to minimize ground baseline variance.
""")