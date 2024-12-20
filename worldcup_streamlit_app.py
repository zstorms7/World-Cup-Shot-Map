import pandas as pd
import streamlit as st
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt
import matplotlib.patches as patches


st.title("2018 World Cup Shot Map")
st.subheader("Filter by match, team, and shot details to analyze performance!")


df = pd.read_csv('2018wcmatches.csv')


df['x'] = pd.to_numeric(df['x'], errors='coerce')
df['y'] = pd.to_numeric(df['y'], errors='coerce')
df['shot_end_location_y'] = pd.to_numeric(df['shot_end_location_y'], errors='coerce')
df['shot_end_location_z'] = pd.to_numeric(df['shot_end_location_z'], errors='coerce')
df['shot_statsbomb_xg'] = pd.to_numeric(df['shot_statsbomb_xg'], errors='coerce')


selected_match = st.selectbox("Select a Match", df['Match'].sort_values().unique())
filtered_match_df = df[df['Match'] == selected_match]


teams = filtered_match_df['team'].unique()
selected_teams = st.multiselect("Select Teams", teams, default=teams)


shot_outcomes = ['Goal', 'Saved', 'All']
selected_outcome = st.selectbox("Select Shot Outcome (Goal View)", shot_outcomes)


team_shots_df = filtered_match_df[filtered_match_df['team'].isin(selected_teams)]
if selected_outcome != 'All':
    team_shots_df = team_shots_df[team_shots_df['shot_outcome'] == selected_outcome]
team_shots_df = team_shots_df.dropna(subset=['x', 'y', 'shot_outcome', 'shot_statsbomb_xg'])


saves_count = team_shots_df[team_shots_df['shot_outcome'] == 'Saved'].shape[0]
goals_count = team_shots_df[team_shots_df['shot_outcome'] == 'Goal'].shape[0]


goal_view_df = team_shots_df[team_shots_df['shot_outcome'].isin(['Goal', 'Saved'])]


st.write("### Match Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Shots", len(goal_view_df))
with col2:
    st.metric("Goals", goals_count)
with col3:
    st.metric("Saves", saves_count)
with col4:
    st.metric("Total xG", round(goal_view_df['shot_statsbomb_xg'].sum(), 2))


st.write("### xG by Team")
team_xg = goal_view_df.groupby('team')['shot_statsbomb_xg'].sum()
for team, xg in team_xg.items():
    st.write(f"**{team}:** {round(xg, 2)} xG")


view = st.radio("Select View", ["Pitch View", "Goal View"])

if view == "Goal View":
    
    goal_y_min = 36  
    goal_y_max = 44  
    goal_height = 2.44  

   
    min_y = goal_view_df['shot_end_location_y'].min()
    max_y = goal_view_df['shot_end_location_y'].max()
    goal_view_df['normalized_y'] = (
        (goal_view_df['shot_end_location_y'] - min_y) / (max_y - min_y) * (goal_y_max - goal_y_min) + goal_y_min
    )

    
    goal_view_df['normalized_z'] = goal_view_df['shot_end_location_z']

    
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('green') 
    ax.set_facecolor('green')

    
    goal_rect = patches.Rectangle((goal_y_min, 0), goal_y_max - goal_y_min, goal_height, linewidth=3, edgecolor='white', facecolor='none')
    ax.add_patch(goal_rect)

   
    net_spacing = 0.3  
    horizontal_lines = int(goal_height / net_spacing)
    vertical_lines = int((goal_y_max - goal_y_min) / net_spacing)
    for i in range(horizontal_lines + 1):
        ax.plot([goal_y_min, goal_y_max], [i * net_spacing, i * net_spacing], color='white', lw=0.5)
    for i in range(vertical_lines + 1):
        ax.plot([goal_y_min + i * net_spacing, goal_y_min + i * net_spacing], [0, goal_height], color='white', lw=0.5)

    
    for _, shot in goal_view_df.iterrows():
        color = 'blue' if shot['shot_outcome'] == 'Goal' else 'yellow'  
        ax.scatter(
            x=shot['normalized_y'],  
            y=shot['normalized_z'],  
            color=color,
            edgecolors='black',
            s=100, 
            alpha=1
        )

    
    handles = [plt.Line2D([0], [0], marker='o', color='white', label='Goal', markerfacecolor='blue', markersize=8),
               plt.Line2D([0], [0], marker='o', color='white', label='Saved', markerfacecolor='yellow', markersize=8)]
    ax.legend(handles=handles, loc='upper left', fontsize='small', title="Shot Details", title_fontsize='small')

   
    ax.set_xlim(goal_y_min - 1, goal_y_max + 1)
    ax.set_ylim(-0.5, goal_height + 0.5)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    ax.set_title("Goal View - Shots on Target")

    
    st.pyplot(fig)

elif view == "Pitch View":
   
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='green', line_color='white', half=True)
    fig, ax = pitch.draw(figsize=(10, 10))
    
    
    for _, shot in team_shots_df.iterrows():
        size = 500 * shot['shot_statsbomb_xg']  
        if shot['shot_outcome'] == 'Goal':
            color = 'blue'
        elif shot['shot_outcome'] == 'Saved':
            color = 'yellow'
        else:
            color = 'red'  
        pitch.scatter(
            x=shot['x'],
            y=shot['y'],
            ax=ax,
            s=size,
            color=color,
            edgecolors='black',
            alpha=0.8
        )

    
    handles = [plt.Line2D([0], [0], marker='o', color='white', label='Goal', markerfacecolor='blue', markersize=8),
               plt.Line2D([0], [0], marker='o', color='white', label='Saved', markerfacecolor='yellow', markersize=8),
               plt.Line2D([0], [0], marker='o', color='white', label='Other Outcomes', markerfacecolor='red', markersize=8)]
    ax.legend(handles=handles, loc='upper right', fontsize='small', title="Shot Details", title_fontsize='small')

    
    st.pyplot(fig)
