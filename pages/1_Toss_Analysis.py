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
    page_title="Toss Analysis",
    page_icon="🏏",
    layout="wide"
)

df = load_data()

# MATCH LEVEL DATA
match_level = df.drop_duplicates(subset='match_id').copy()

# PAGE TITLE
st.title("Toss Impact Analysis")
st.markdown("""
Analyze how toss decisions influence
match outcomes across IPL seasons.
""")
st.divider()

# PAGE FILTERS
venues = sorted(match_level['cleaned_venue'].dropna().unique())

selected_venue = st.selectbox("Select Venue",["All"] + list(venues))

# APPLY VENUE FILTER (Using the cleaned column consistently)
if selected_venue != "All":
    match_level = match_level[match_level['cleaned_venue'] == selected_venue]

# KPI SECTION
total_matches = match_level.shape[0]

match_level['toss_and_match_win'] = match_level['toss_winner'] == match_level['winner']

if total_matches > 0:
    toss_win_percentage = match_level['toss_and_match_win'].mean() * 100
else:
    toss_win_percentage = 0

toss_decision_counts = match_level['toss_decision'].value_counts()
bat_first_wins = toss_decision_counts.get('bat', 0)
field_first_wins = toss_decision_counts.get('field', 0)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Matches", total_matches)

with col2:
    st.metric("Bat First Decisions", bat_first_wins)

with col3:
    st.metric("Field First Decisions", field_first_wins)

st.divider()

# TOSS WIN VS MATCH WIN

st.subheader("Toss Winner vs Match Winner")

col1, col2 = st.columns(2)

with col1:
    fig1 = go.Figure(data=[
        go.Pie(
            labels=["Won Match", "Lost Match"],
            values=[toss_win_percentage, 100 - toss_win_percentage],
            hole=0.45,
            textinfo='percent+value',
            marker=dict(colors=['#00E6B4', '#d62728']),
            hovertemplate="<b>%{label}</b><br>Percentage: %{percent}<extra></extra>"
        )
    ])

    fig1.update_layout(
        title="Toss Winner Match Success",
        template='plotly_white',
        margin=dict(t=40, b=10, l=10, r=10)
    )

    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Safe handling of Bar Chart dataframe mapping to prevent ValueError
    if not toss_decision_counts.empty:
        toss_df = toss_decision_counts.reset_index()
        toss_df.columns = ['Decision', 'Count']

        fig2 = px.bar(
            toss_df,
            x='Decision',
            y='Count',
            title="Toss Decisions",
            labels={'Decision': 'Decision', 'Count': 'Count'},
            color='Decision',
            color_discrete_map={'field': '#d62728', 'bat': '#00E6B4'}
        )

        fig2.update_traces(
            texttemplate='%{y}',
            textposition='outside',
            hovertemplate="<b>Decision: %{x}</b><br>Total Count: %{y}<extra></extra>"
        )

        fig2.update_layout(
            template='plotly_white',
            showlegend=False,
            yaxis_range=[0, max(toss_df['Count']) * 1.15]
        )

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No toss decision records found for this filtered view.")

st.divider()

# VENUE-WISE TOSS IMPACT
st.subheader("Top Venues Where Toss Matters Most")
st.markdown("""
- Does winning the toss offer a structural advantage at specific grounds? 
The breakdown below ranks venues based on the match success rate of the team winning the toss.
""")

venue_toss_df = match_level.groupby('cleaned_venue').agg(Total_Matches=('match_id', 'nunique'),Toss_And_Match_Wins=('toss_and_match_win', 'sum')).reset_index()

venue_toss_df = venue_toss_df[venue_toss_df['Total_Matches'] >= 5]

if not venue_toss_df.empty:
    venue_toss_df['Toss Win Match %'] = (venue_toss_df['Toss_And_Match_Wins'] / venue_toss_df['Total_Matches']) * 100
    venue_toss_df = venue_toss_df.sort_values(by='Toss Win Match %', ascending=False).head(10)

    fig3 = px.bar(
        venue_toss_df,
        x='Toss Win Match %',
        y='cleaned_venue',
        orientation='h',
        labels={
            'Toss Win Match %': 'Toss Win Match Win %',
            'cleaned_venue': 'Venue'
        },
        color='Toss Win Match %',
        color_continuous_scale='Greens'
    )

    fig3.update_traces(
        texttemplate='%{x:.1f}%',
        textposition='outside',
        hovertemplate="<b>Venue: %{y}</b><br>Toss Advantage: %{x:.2f}%<extra></extra>"
    )

    fig3.update_layout(
        template='plotly_white',
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(t=40, b=10, l=10, r=10),
        showlegend=False
    )

    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Insufficient benchmark venue entries found for tracking comparisons.")

st.divider()

# SEASON-WISE TOSS IMPACT
st.subheader("Season-wise Toss Impact")

if total_matches > 0:
    # Group by without using .apply lambda loop for structural stability
    season_toss = match_level.groupby('season').agg(
        Total_Matches=('match_id', 'nunique'),
        Toss_And_Match_Wins=('toss_and_match_win', 'sum')
    ).reset_index()

    season_toss['win_percentage'] = (season_toss['Toss_And_Match_Wins'] / season_toss['Total_Matches']) * 100

    fig4 = px.line(
        season_toss,
        x='season',
        y='win_percentage',
        markers=True,
        title="Toss Advantage Trend Across Seasons",
        labels={'season': 'Season', 'win_percentage': 'Win Percentage (%)'},
        template='plotly_white'
    )

    fig4.update_traces(
        line=dict(color='#00E6B4', width=3),
        marker=dict(size=8, color='#d62728'),
        hovertemplate="<b>Season:</b> %{x}<br><b>Win Rate:</b> %{y:.1f}%<extra></extra>"
    )

    fig4.update_layout(
        xaxis=dict(tickmode='linear', dtick=1),
        yaxis_range=[0, 100],
        margin=dict(t=40, b=10, l=10, r=10)
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("No season records matching this venue criteria.")

st.divider()

# TEAM-WISE TOSS PERFORMANCE
match_level['toss_match_win'] = match_level['toss_winner'] == match_level['winner']

st.subheader("Teams Converting Toss Wins into Match Wins")

# Efficient group by alternative to keep indexing structural integrity clean
team_toss_df = match_level.groupby('toss_winner').agg(Total_Toss_Wins=('match_id', 'nunique'),Toss_Matches_Won=('toss_match_win', 'sum')).reset_index()

if not team_toss_df.empty:
    team_toss_df['Success %'] = (team_toss_df['Toss_Matches_Won'] / team_toss_df['Total_Toss_Wins']) * 100
    team_toss_df = team_toss_df.sort_values(by='Success %', ascending=False)

    fig5 = px.bar(
        team_toss_df,
        x='toss_winner',
        y='Success %',
        labels={'toss_winner': 'Team', 'Success %': 'Success %'},
        color='Success %',
        color_continuous_scale='Blues'
    )
    fig5.update_layout(template='plotly_white')
    fig5.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    st.plotly_chart(fig5, use_container_width=True)

    # For feeding clean sorted data metrics into Key Insights below
    team_toss = team_toss_df.set_index('toss_winner')['Success %']
else:
    team_toss = pd.Series(dtype=float)

st.divider()

# INSIGHTS

st.subheader("Data-Driven Insights & Strategic Takeaways")

if total_matches > 0:
    # 1. Base Numbers Extraction for Insights
    top_venue_name = venue_toss_df.iloc[0]['cleaned_venue'] if not venue_toss_df.empty else "N/A"
    top_venue_pct = venue_toss_df.iloc[0]['Toss Win Match %'] if not venue_toss_df.empty else 0

    preferred_decision = "Fielding First" if field_first_wins > bat_first_wins else "Batting First"
    preferred_percentage = (max(field_first_wins, bat_first_wins) / (bat_first_wins + field_first_wins)) * 100 if (
                                                                                                                              bat_first_wins + field_first_wins) > 0 else 0

    best_conversion_team = team_toss_df.iloc[0]['toss_winner'] if not team_toss_df.empty else "N/A"
    best_conversion_val = team_toss_df.iloc[0]['Success %'] if not team_toss_df.empty else 0

    # 2. Render Insights Using Streamlit Alert Boxes and Columns
    ins1, ins2 = st.columns(2)

    with ins1:
        st.info(f"""
        ** Overall Toss Advantage Status**
        - Throughout IPL history under current filters, the team winning the toss wins the match approximately **{toss_win_percentage:.2f}%** of the time. 
        - This indicates that while the toss provides an edge, match simulation control and tactical execution in crunch overs remain the primary drivers of victory.
        """)

        st.success(f"""
        ** Tactical Dominance by Decision**
        - Captains exhibit a strong structural bias toward **{preferred_decision}**, accounting for **{preferred_percentage:.1f}%** of total toss choices.
        - In modern T20 formats, tracking wet conditions (dew factor) and chasing patterns heavily shapes this ongoing trend.
        """)

    with ins2:
        st.warning(f"""
        ** Venue Crucial Hotspot**
        - The toss holds maximum strategic leverage at **{top_venue_name}**, boasting a historic conversion rate of **{top_venue_pct:.1f}%** match wins for the toss winner.
        - Teams playing here should prioritize analytical adjustments based on pitch variance right at the flip.
        """)

        st.error(f"""
        ** Elite Asset Conversion**
        - **{best_conversion_team}** emerges as the most clinical side, converting **{best_conversion_val:.1f}%** of their toss victories into actual match wins.
        - This metrics signals superior defensive depth or clinical chasing setups compared to the tournament baseline.
        """)

    st.markdown("""
    ---
    ### Summary:
    *“The data invalidates the myth that winning the toss guarantees a absolute victory path in the IPL. Instead, it proves that toss luck acts as an **accelerator** rather than a guarantee. High conversion rates are driven heavily by venue dynamics (such as boundary scale and dew patterns) paired with team-specific depth in execution.”*
    """)
else:
    st.info("Please adjust filters to generate strategic match insights.")
