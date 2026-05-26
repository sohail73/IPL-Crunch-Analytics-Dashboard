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


# Milte-julte naamo ko merge karne ke liye cleaning map
def clean_venue(venue):
    v = str(venue).lower().strip()
    if 'wankhede' in v:
        return 'Wankhede Stadium (Mumbai)'
    elif 'eden gardens' in v:
        return 'Eden Gardens (Kolkata)'
    elif 'chinnaswamy' in v:
        return 'M. Chinnaswamy Stadium (Bengaluru)'
    elif 'chidambaram' in v or 'chepauk' in v:
        return 'MA Chidambaram Stadium (Chennai)'
    elif 'feroz shah kotla' in v or 'arun jaitley' in v:
        return 'Arun Jaitley Stadium (Delhi)'
    elif 'rajiv gandhi' in v or 'uppal' in v:
        return 'Rajiv Gandhi Intl Stadium (Hyderabad)'
    elif 'sawai mansingh' in v:
        return 'Sawai Mansingh Stadium (Jaipur)'
    elif 'punjab cricket' in v or 'mohali' in v or 'is bindra' in v:
        return 'IS Bindra PCA Stadium (Mohali)'
    elif 'narendra modi' in v or 'motera' in v or 'sardar patel' in v:
        return 'Narendra Modi Stadium (Ahmedabad)'
    elif 'dubai' in v:
        return 'Dubai International Stadium'
    else:
        return venue

df['cleaned_venue'] = df['venue'].apply(clean_venue)
# ---- FIX 1: Clean season mapping BEFORE dropping duplicates and filtering ----
season_map = {
    '2007/08': 2008,
    '2009/10': 2010,
    '2020/21': 2020
}
df['season'] = df['season'].replace(season_map)
# Safe string extraction for any remaining slash values like '2024/25'
df['season'] = df['season'].astype(str).str.split('/').str[0]
df['season'] = pd.to_numeric(df['season'], errors='coerce').fillna(2008).astype(int)

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

selected_venue = st.selectbox(
    "Select Venue",
    ["All"] + list(venues)
)

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
    # ---- FIX 2: Safe handling of Bar Chart dataframe mapping to prevent ValueError ----
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

venue_toss_df = match_level.groupby('cleaned_venue').agg(
    Total_Matches=('match_id', 'nunique'),
    Toss_And_Match_Wins=('toss_and_match_win', 'sum')
).reset_index()

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
    # ---- FIX 3: Groupby without using .apply lambda loop for structural stability ----
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
team_cleaner = {
    'Rising Pune Supergiants': 'Rising Pune Supergiant',
    'Delhi Daredevils': 'Delhi Capitals',
    'Kings XI Punjab': 'Punjab Kings',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru'
}
match_level['toss_winner'] = match_level['toss_winner'].replace(team_cleaner)
match_level['winner'] = match_level['winner'].replace(team_cleaner)
match_level['toss_match_win'] = match_level['toss_winner'] == match_level['winner']

st.subheader("Teams Converting Toss Wins into Match Wins")

# Efficient groupby alternative to keep indexing structural integrity clean
team_toss_df = match_level.groupby('toss_winner').agg(
    Total_Toss_Wins=('match_id', 'nunique'),
    Toss_Matches_Won=('toss_match_win', 'sum')
).reset_index()

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
st.subheader("Key Insights")

if bat_first_wins > field_first_wins:
    pref_statement = f"captains prefer to **Bat First** after winning the toss at this venue ({bat_first_wins} times)."
else:
    pref_statement = f"captains heavily prefer to **Field First (Chase)** after winning the toss at this venue ({field_first_wins} times)."

if len(team_toss) > 0:
    top_team = team_toss.index[0]
    top_team_pct = round(team_toss.values[0], 1)
    team_statement = f"**{top_team}** has capitalized best on toss advantages in this segment, boasting a Toss-to-Match conversion rate of **{top_team_pct}%**."
else:
    team_statement = "Toss conversion analytics are processing based on the applied data filters."

st.success(f"""
- **Overall Toss Advantage:** Under the **{selected_venue}** filter context, teams winning the toss have a match-winning probability of **{round(toss_win_percentage, 2)}%**. 

- **Captain's Mindset:** According to historical data, {pref_statement}

- **Team Dominance:** {team_statement}

- **Tactical Shift:** Due to modern dynamic ground dimensions, dew factors, and tactical shifts in the ongoing IPL 2026 season, the dominance of chasing teams has risen significantly.
""")

st.divider()

# CONCLUSION
st.subheader("Conclusion")
st.markdown(f"""
While toss advantages definitely play a measurable role at **{selected_venue}**, they are rarely the sole deciding factor of a fixture. 
On-field execution, powerplay bowling lengths, boundary defense metrics, and tactical adaptability ultimately dictate final match outcomes.
""")