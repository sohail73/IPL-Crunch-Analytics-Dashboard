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
venue_cleaner = {
    # Mumbai
    'Wankhede Stadium, Mumbai': 'Wankhede Stadium',
    'Dr DY Patil Sports Academy, Mumbai': 'Dr DY Patil Sports Academy',
    'Brabourne Stadium, Mumbai': 'Brabourne Stadium',

    # Bengaluru
    'M Chinnaswamy Stadium': 'M. Chinnaswamy Stadium',
    'M.Chinnaswamy Stadium': 'M. Chinnaswamy Stadium',
    'M Chinnaswamy Stadium, Bengaluru': 'M. Chinnaswamy Stadium',

    # Chennai
    'MA Chidambaram Stadium': 'M.A. Chidambaram Stadium, Chepauk',
    'MA Chidambaram Stadium, Chepauk, Chennai': 'M.A. Chidambaram Stadium, Chepauk',
    'MA Chidambaram Stadium, Chepauk': 'M.A. Chidambaram Stadium, Chepauk',

    # Delhi
    'Feroz Shah Kotla': 'Arun Jaitley Stadium',
    'Arun Jaitley Stadium, Delhi': 'Arun Jaitley Stadium',

    # Hyderabad
    'Rajiv Gandhi International Stadium': 'Rajiv Gandhi International Stadium, Uppal',
    'Rajiv Gandhi International Stadium, Uppal, Hyderabad': 'Rajiv Gandhi International Stadium, Uppal',

    # Kolkata
    'Eden Gardens, Kolkata': 'Eden Gardens',

    # Mohali / Mullanpur
    'Punjab Cricket Association Stadium, Mohali': 'PCA IS Bindra Stadium, Mohali',
    'Punjab Cricket Association IS Bindra Stadium, Mohali': 'PCA IS Bindra Stadium, Mohali',
    'Punjab Cricket Association IS Bindra Stadium': 'PCA IS Bindra Stadium, Mohali',
    'Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh': 'PCA IS Bindra Stadium, Mohali',
    'Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh': 'Maharaja Yadavindra Singh Stadium, Mullanpur',
    'Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur': 'Maharaja Yadavindra Singh Stadium, Mullanpur',

    # Pune
    'Maharashtra Cricket Association Stadium, Pune': 'Maharashtra Cricket Association Stadium',

    # Jaipur
    'Sawai Mansingh Stadium, Jaipur': 'Sawai Mansingh Stadium',

    # Vizag
    'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam': 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Stadium',
    'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium': 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Stadium',

    # Ahmedabad
    'Sardar Patel Stadium, Motera': 'Narendra Modi Stadium, Ahmedabad',

    # Abu Dhabi
    'Zayed Cricket Stadium, Abu Dhabi': 'Sheikh Zayed Stadium'
}

df['venue'] = df['venue'].replace(venue_cleaner).str.strip()

# MATCH LEVEL DATA
match_level = df.drop_duplicates(subset='match_id')

# PAGE TITLE
st.title("Toss Impact Analysis")

st.markdown("""
Analyze how toss decisions influence
match outcomes across IPL seasons.
""")
st.divider()

# PAGE FILTERS
venues = sorted(df['venue'].unique())

selected_venue = st.selectbox(
    "Select Venue",
    ["All"] + list(venues)
)
# APPLY VENUE FILTER
if selected_venue != "All":
    match_level = match_level[match_level['venue'] == selected_venue]

# KPI SECTION
total_matches = match_level.shape[0]

match_level['toss_and_match_win'] = match_level['toss_winner'] == match_level['winner']
toss_win_percentage = match_level['toss_and_match_win'].mean() * 100

bat_first_wins = match_level[match_level['toss_decision']== 'bat'].shape[0]

field_first_wins = match_level[match_level['toss_decision']== 'field'].shape[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Matches",total_matches)

with col2:
    st.metric("Bat First Decisions",bat_first_wins)

with col3:
    st.metric("Field First Decisions",field_first_wins)

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
season_map = {
    '2007/08': 2008,
    '2009/10': 2010,
    '2020/21': 2020
}
match_level['season'] = match_level['season'].replace(season_map)
match_level['season'] =match_level['season'].astype(int)

st.subheader("Season-wise Toss Impact")

season_toss = match_level.groupby('season').apply(lambda x: ((x['toss_winner']==x['winner']).mean()) * 100).reset_index(name='win_percentage')

fig4 = px.line(
    season_toss,
    x='season',
    y='win_percentage',
    markers=True
)

st.plotly_chart(fig4, use_container_width=True)

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

team_toss = (match_level.groupby('toss_winner')['toss_match_win'].mean().mul(100).sort_values(ascending=False))

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

# 1. Logic to identify the dominant trend (Decisions based)
if bat_first_wins > field_first_wins:
    pref_statement = f"captains prefer to **Bat First** after winning the toss at this venue ({bat_first_wins} times)."
else:
    pref_statement = f"captains heavily prefer to **Field First (Chase)** after winning the toss at this venue ({field_first_wins} times)."

# 2. Strongest team on this venue (Highest toss-to-win conversion)
if len(team_toss) > 0:
    top_team = team_toss.index[0]
    top_team_pct = round(team_toss.values[0], 1)
    team_statement = f"**{top_team}** has capitalized best on toss advantages in this segment, boasting a Toss-to-Match conversion rate of **{top_team_pct}%**."
else:
    team_statement = "Toss conversion analytics are processing based on the applied data filters."

# 3. Streamlit Display Card UI (Aligned with the dark theme layout)
st.success(f"""
- **Overall Toss Advantage:** Under the **{selected_venue}** filter context, teams winning the toss have a match-winning probability of **{toss_win_percentage}%**. 

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
