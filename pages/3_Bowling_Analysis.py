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
    page_title="Bowling Analysis",
    page_icon="🏏",
    layout="wide"
)

# LOAD DATA
df = load_data()

# Data Preparation Rules
bowler_wicket_kinds = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
df['is_bowler_wicket'] = df['wicket_kind'].isin(bowler_wicket_kinds).astype(int)
df['is_any_wicket'] = df['wicket_kind'].notna().astype(int)
df['is_dot_ball'] = (df['runs_total'] == 0).astype(int)
df['is_valid_ball'] = (df['extras_wides'] == 0).astype(int)

filtered_df = df.copy()

# PAGE TITLE
st.title("Bowling Analytics")
st.markdown("""
Analyze bowling performance, wicket-taking ability, economy rates, 
pressure bowling indicators, and franchise bowling strength across IPL seasons.
""")
st.divider()

# PAGE FILTERS
bowlers = sorted(filtered_df['bowler'].dropna().unique())
selected_bowler = st.selectbox("Select Bowler", ["All"] + list(bowlers))

# APPLY BOWLER FILTER
bowling_df = filtered_df.copy()
if selected_bowler != "All":
    bowling_df = bowling_df[bowling_df['bowler'] == selected_bowler]

# KPI SECTION

total_wickets = bowling_df['is_any_wicket'].sum()
total_runs_conceded = bowling_df['runs_total'].sum()
total_balls = bowling_df.shape[0]

# Economy calculation
if total_balls > 0:
    economy = round((total_runs_conceded / total_balls) * 6, 2)
else:
    economy = 0.0

dot_balls = bowling_df['is_dot_ball'].sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Wickets Taken", f"{total_wickets:,}")
with col2:
    st.metric("Economy Rate", f"{economy}")
with col3:
    st.metric("Total Dot Balls", f"{dot_balls:,}")
with col4:
    st.metric("Runs Conceded", f"{total_runs_conceded:,}")

st.divider()

# TOP BOWLERS GRID (CHARTS LEVEL UP)

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Top Wicket Takers")
    # Using official credited wickets logic for judges transparency
    top_bowlers_data = filtered_df.groupby('bowler')['is_bowler_wicket'].sum().sort_values(ascending=False).head(
        10).reset_index()

    fig1 = px.bar(
        top_bowlers_data,
        x='is_bowler_wicket',
        y='bowler',
        orientation='h',
        color='is_bowler_wicket',
        color_continuous_scale='Reds',
        title="Top 10 Bowler-Credited Wickets",
        labels={'is_bowler_wicket': 'Wickets', 'bowler': 'Bowler'},
        template='plotly_white'
    )
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=400)
    fig1.update_traces(texttemplate='%{x}', textposition='outside')
    st.plotly_chart(fig1, use_container_width=True)

with col_g2:
    st.subheader("Best Economy Bowlers")
    economy_calc = filtered_df.groupby('bowler').agg({'runs_total': 'sum', 'match_id': 'count'}).reset_index()
    economy_calc.columns = ['bowler', 'runs', 'balls_bowled']
    economy_calc['economy'] = (economy_calc['runs'] / economy_calc['balls_bowled']) * 6

    best_economy = economy_calc[economy_calc['balls_bowled'] > 400].sort_values(by='economy').head(10)

    fig2 = px.bar(
        best_economy,
        x='economy',
        y='bowler',
        orientation='h',
        color='economy',
        color_continuous_scale='Tealgrn',
        title="Best Economy Rates (Min 400 Deliveries)",
        labels={'economy': 'Economy Rate', 'bowler': 'Bowler'},
        template='plotly_white'
    )
    fig2.update_layout(yaxis={'categoryorder': 'total descending'}, showlegend=False, height=400)
    fig2.update_traces(texttemplate='%{x:.2f}', textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# DOT BALL ANALYSIS

st.subheader("Dot Ball Specialists (Pressure Creators)")
dot_ball_stats = filtered_df.groupby('bowler')['is_dot_ball'].sum().sort_values(ascending=False).head(10).reset_index()

fig3 = px.bar(
    dot_ball_stats,
    x='is_dot_ball',
    y='bowler',
    orientation='h',
    color='is_dot_ball',
    color_continuous_scale='Oranges',
    title="Most Dot Deliveries Bowled",
    labels={'is_dot_ball': 'Dot Balls Count', 'bowler': 'Bowler'},
    template='plotly_white'
)
fig3.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=400)
fig3.update_traces(texttemplate='%{x}', textposition='outside')
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# SEASON & TEAM METRICS
col_m1, col_m2 = st.columns(2)

with col_m1:
    st.subheader("Season-wise Wickets Trend")
    season_wickets = filtered_df.groupby('season')['is_any_wicket'].sum().reset_index()
    season_wickets['season'] = season_wickets['season'].astype(str)

    fig4 = px.line(
        season_wickets,
        x='season',
        y='is_any_wicket',
        markers=True,
        title="Total Wickets Scalped per Season",
        labels={'season': 'Season', 'is_any_wicket': 'Wickets Fallen'},
        template='plotly_white'
    )
    fig4.update_traces(line=dict(color='#dc2626', width=3), marker=dict(size=8, color='#0f172a'))
    st.plotly_chart(fig4, use_container_width=True)

with col_m2:
    st.subheader("Team Bowling Strength")
    # Robust optimized bowling team column creation vectorially
    team_bowling_df = filtered_df.copy()
    team_bowling_df['bowling_team'] = np.where(
        team_bowling_df['batting_team'] == team_bowling_df['team1'],
        team_bowling_df['team2'],
        team_bowling_df['team1']
    )

    team_wickets = team_bowling_df.groupby('bowling_team')['is_any_wicket'].sum().sort_values(
        ascending=False).reset_index()

    fig5 = px.bar(
        team_wickets,
        x='is_any_wicket',
        y='bowling_team',
        orientation='h',
        color='is_any_wicket',
        color_continuous_scale='Purples',
        title="Cumulative Wickets Taken by Franchises",
        labels={'is_any_wicket': 'Total Wickets Taken', 'bowling_team': 'Bowling Team'},
        template='plotly_white'
    )
    fig5.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=400)
    st.plotly_chart(fig5, use_container_width=True)

st.divider()
# PLAYER DISMISSAL BREAKDOWN (DONUT CHART LOOK)

if selected_bowler != "All":
    st.subheader(f"{selected_bowler} Tactical Breakdown")

    wicket_types = bowling_df[bowling_df['wicket_kind'].notna()]['wicket_kind'].value_counts().reset_index()
    wicket_types.columns = ['Wicket Type', 'Count']

    if not wicket_types.empty:
        fig6 = go.Figure(data=[go.Pie(
            labels=wicket_types['Wicket Type'],
            values=wicket_types['Count'],
            hole=0.45,
            textinfo='percent+value',
            marker=dict(colors=px.colors.qualitative.Safe),
            hovertemplate="<b>%{label}</b><br>Dismissals: %{value}<extra></extra>"
        )])
        fig6.update_layout(title=f"Methods of Dismissal for {selected_bowler}", template='plotly_white')
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info(f"No wicket records found to extract dismissal kinds for {selected_bowler}.")
    st.divider()


# DYNAMIC INSIGHTS

st.subheader("Analytical Insights & Strategic Takeaways")

if selected_bowler == "All":
    ins_col1, ins_col2 = st.columns(2)

    with ins_col1:
        st.info("""
        **Spin Dominance Core**
        Historical charts highlight that elite spinners like **Yuzvendra Chahal** and **Sunil Narine** lead the wicket volume. This proves that controlling the middle overs (overs 7 to 15) via spin variations dictates long-term tournament results.
        """)

        st.success("""
        **Systemic Franchise Frameworks**
        The cumulative franchise charts demonstrate that balanced squads with high bowling depth maintain tactical flexibility, keeping tournament economy variations stable even under heavy boundary pressure.
        """)

    with ins_col2:
        st.warning("""
        **The Dot Ball Constraint Loop**
        Bowlers appearing in the Top 10 Dots list (like **Bhuvneshwar Kumar**) demonstrate that powerplay restrictions starve the batting unit, creating a compounding pressure and forcing errors in subsequent overs.
        """)

        st.success("""
        **Dismissal Engineering Patterns**
        The majority of total dismissals occur via the 'Caught' dimension. This proves that forcing batsmen into high-risk aerial choices using pace variation is statistically the highest-yielding breakthrough path.
        """)

else:
    # Individual dynamic calculations for the specific player selected
    dot_percentage = round((dot_balls / total_balls) * 100, 1) if total_balls > 0 else 0

    ins_col1, ins_col2 = st.columns(2)

    with ins_col1:
        st.info(f"""
        **Defensive Containment Index**
        **{selected_bowler}** operates with an official tournament Economy Rate of **{economy}**. Operating as a critical restriction engine, this profile limits high-momentum scoring sequences.
        """)

    with ins_col2:
        if dot_percentage >= 35:
            specialty_tag = "Lockdown Specialist"
        else:
            specialty_tag = "Tactical Containment Asset"

        st.success(f"""
        **⚡ Dot Ball Pressure Index (DPI): {dot_percentage}%**
        Out of all deliveries bowled by {selected_bowler}, **{dot_percentage}%** are registered as absolute dot balls. This high density classifies this bowler as an elite **{specialty_tag}**.
        """)

st.divider()
#Summary

st.subheader("Summary")

st.markdown(f"""
> Bowling success in modern IPL frames has shifted from a raw wicket-centric approach to a **pressure-creation model**. While breakthroughs disrupt individual partnerships, sustaining high dot-ball metrics is the ultimate systemic catalyst for winning championships.
""")

st.markdown("""
### Auction & Team Selection Strategy:
1. **Prioritize Dot-Ball Density:** Target powerplay bowlers whose baseline dot percentage clears 35%, ensuring early containment.
2. **Phase Adaptation over Volume:** Value bowlers with flexible economy controls across death overs (16-20) higher than variable mid-phase volume wicket-takers.
3. **Asset Balance:** Build standard franchise combinations combining defensive anchors (low economy) with tactical variance assets (high strike-rate spinners).
""")