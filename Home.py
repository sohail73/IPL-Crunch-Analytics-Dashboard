import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# GLOBAL PLOTLY CONFIG
pio.templates["custom"] = pio.templates["plotly_dark"]
pio.templates["custom"].layout.colorway = ["#1E90FF", "red"]
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


# LOAD DATASET
@st.cache_data
def load_data():
    return pd.read_csv('data/clean_ipl_data.csv')


df = load_data()

# MATCH LEVEL DATA PREPARATION
match_level = df.drop_duplicates(subset='match_id').copy()
match_level['toss_and_match_win'] = match_level['toss_winner'] == match_level['winner']

# DASHBOARD HEADER
st.title("IPL Crunch Analytics Dashboard")
st.markdown("""
Explore multi-dimensional IPL insights, match-winning vectors, batting dominance milestones, 
bowling impact depth, and stadium surface intelligence across all historic seasons.
""")
st.caption("**Data Temporal Range:** 2008 – May 2026")
st.divider()

# GLOBAL METRICS KPI BAND
total_matches = match_level['match_id'].nunique()
total_teams = len(pd.unique(df[['team1', 'team2']].stack().drop_duplicates()))
total_seasons = match_level['season'].nunique()

# Highest score calculation logic
highest_score = df.groupby(['match_id', 'batting_team'])['runs_total'].sum().max()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Matches Played", f"{total_matches:,}")
with col2:
    st.metric("Competing Franchises", total_teams)
with col3:
    st.metric("Completed Seasons", total_seasons)
with col4:
    st.metric("Peak Team Innings Total", highest_score)

st.divider()

# SECTION 1: TOSS INFLUENCE & ORANGE CAP METRIC CARD
col_t1, col_t2, col_t3 = st.columns([2, 2, 2.2])

with col_t1:
    st.markdown("#### Toss Win Conversion Matrix")
    match_level['Toss_Result'] = np.where(match_level['toss_and_match_win'], 'Toss Winner Won', 'Toss Winner Lost')
    toss_pie_data = match_level['Toss_Result'].value_counts().reset_index()

    fig_toss_pie = px.pie(
        toss_pie_data,
        values='count',
        names='Toss_Result',
        hole=0.4,
        color='Toss_Result',
        color_discrete_map={'Toss Winner Won': '#00E6B4', 'Toss Winner Lost': '#d62728'}
    )
    fig_toss_pie.update_layout(template='plotly_white', showlegend=True, height=320,
                               margin=dict(t=10, b=10, l=10, r=10))
    fig_toss_pie.update_traces(textinfo='percent+value',
                               hovertemplate="<b>%{label}</b><br>Matches: %{value}<extra></extra>")
    st.plotly_chart(fig_toss_pie, use_container_width=True)

with col_t2:
    st.markdown("#### Toss Decision Split")
    toss_decision = match_level['toss_decision'].value_counts().reset_index()
    toss_decision.columns = ['Decision', 'Count']

    fig2 = px.bar(
        toss_decision,
        x='Decision',
        y='Count',
        color='Decision',
        color_discrete_map={'field': '#00E6B4', 'bat': '#d62728'}
    )
    fig2.update_traces(texttemplate='%{y}', textposition='outside')
    fig2.update_layout(
        template='plotly_white',
        showlegend=False,
        height=320,
        yaxis_range=[0, max(toss_decision['Count']) + 120]
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_t3:
    st.markdown("#### IPL Run-Machine Profile")

    # Custom container architecture for player showcase card
    card_col1, card_col2 = st.columns([1, 1.2])
    with card_col1:
        st.image("virat.png", use_container_width=True)
    with card_col2:
        st.markdown("### **VIRAT KOHLI**")
        st.markdown("🏆 **All-Time Top Scorer**")
        st.markdown("""
        * **Total Runs:** 9,050  
        * **Matches:** 268  
        * **Batting Avg:** 40.04  
        * **Consistency:** Elite Baseline
        """)

st.divider()
# SECTION 2: HIGH CLARITY HORIZONTAL GRAPHICS BLOCK
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("### Top 10 All-Time Highest Run Scorers")
    batter_stats = df.groupby('batter').agg(total_runs=('runs_batter', 'sum')).reset_index()
    top_scorers_df = batter_stats.sort_values(by='total_runs', ascending=False).head(10)

    fig3 = px.bar(
        top_scorers_df,
        x='total_runs',
        y='batter',
        orientation='h',
        color='total_runs',
        color_continuous_scale='Plasma',
        labels={'total_runs': 'Total Cumulative Runs', 'batter': 'Batsman Name'},
        template='plotly_white'
    )
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False, height=400)
    fig3.update_traces(texttemplate='%{x:,}', textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

with col_g2:
    st.markdown("### Top 10 All-Time Leading Wicket Takers")
    bowler_wickets_list = ['caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket']
    df_wickets = df[df['wicket_kind'].isin(bowler_wickets_list)]
    top_bowlers_df = df_wickets.groupby('bowler').size().reset_index(name='Wickets').sort_values(by='Wickets',
                                                                                                 ascending=False).head(
        10)

    fig4 = px.bar(
        top_bowlers_df,
        x='Wickets',
        y='bowler',
        orientation='h',
        color='Wickets',
        color_continuous_scale='Viridis',
        labels={'Wickets': 'Total Wickets Taken', 'bowler': 'Bowler Name'},
        template='plotly_white'
    )
    fig4.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False, height=400)
    fig4.update_traces(texttemplate='%{x}', textposition='outside')
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# SECTION 3: VENUE SCALE ANALYSIS
st.markdown("### Heavyweight Venues (Most Matches Hosted)")
# Use cleaned_venue dynamically
venue_col = 'cleaned_venue' if 'cleaned_venue' in df.columns else 'venue'
top_venues_df = match_level.groupby(venue_col)['match_id'].nunique().reset_index(name='Matches').sort_values(
    by='Matches', ascending=False).head(10)

fig5 = px.bar(
    top_venues_df,
    x='Matches',
    y=venue_col,
    orientation='h',
    color='Matches',
    color_continuous_scale='Cividis',
    labels={'Matches': 'Matches Hosted Count', venue_col: 'Stadium Name'},
    template='plotly_white'
)
fig5.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False, height=380)
fig5.update_traces(texttemplate='%{x}', textposition='outside')
st.plotly_chart(fig5, use_container_width=True)

st.divider()

# SECTION 4: CONSOLIDATED GLOBAL INSIGHTS SUMMARY
st.markdown("### Centralized Dashboard Analytical Takeaways")

ins_col1, ins_col2, ins_col3 = st.columns(3)

with ins_col1:
    st.info(
        "**Elite Batting Benchmarks**\n\n"
        "**Virat Kohli** leads the all-time charts with **9,050 runs** in 268 innings, "
        "maintaining a stellar average of **40.04**. Long-term tracking shows consistency over individual spikes."
    )

with ins_col2:
    st.success(
        "**Bowling Multipliers**\n\n"
        "Spin profiles and variation engine anchors lead the ranks. Leg-spinners dominate the charts, proving the long-term impact of drift and deceptive trajectory controls over simple raw velocity."
    )

with ins_col3:
    st.warning(
        "**The Chasing Meta-Trend**\n\n"
        "Teams strongly lean towards chasing, electing to **Field First in ~66%** of matches. "
        "However, toss data shows a **50.49%** breakdown, confirming it yields minimal systemic winning edge."
    )
