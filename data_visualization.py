import os
import math 
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NASA_API_KEY")
START_DATE = os.getenv("START_DATE")
END_DATE = os.getenv("END_DATE")

def fetch_neo_data():
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={START_DATE}&end_date={END_DATE}&api_key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    all_asteroids = []
    for date, asteroids in data['near_earth_objects'].items():
        for asteroid in asteroids:
            all_asteroids.append({
                'name': asteroid['name'],
                'close_approach_date': asteroid['close_approach_data'][0]['close_approach_date'],
                'miss_distance_km': float(asteroid['close_approach_data'][0]['miss_distance']['kilometers']),
                'velocity_km_s': float(asteroid['close_approach_data'][0]['relative_velocity']['kilometers_per_second']),
                'diameter_m': float(asteroid['estimated_diameter']['meters']['estimated_diameter_max']),
                'is_potentially_hazardous_asteroid': asteroid['is_potentially_hazardous_asteroid']
            })

    return pd.DataFrame(all_asteroids)

df_asteroids = fetch_neo_data()

# Miss Distance vs. Velocity vs. Diameter of NEOs 
fig = px.scatter(df_asteroids, x='miss_distance_km', y='velocity_km_s',
                 size='diameter_m', color='diameter_m', hover_name='name',
                 title='Miss Distance vs. Velocity vs. Diameter of NEOs',
                 labels={'velocity_km_s': 'Velocity (km/s)', 'miss_distance_km': 'Miss Distance (km)', 'diameter_m': 'Diameter (m)'},
                 size_max=90,  # Increase the maximum marker size
                 color_continuous_scale='rainbow')  # Change the color scheme

fig.update_layout(
    width=1600,
    height=850,
    xaxis_title='Miss Distance (km)',
    yaxis_title='Velocity (km/s)',
    title='Miss Distance vs. Velocity vs. Diameter of NEOs',
    font=dict(size=23),
    title_font=dict(size=24)
) 

fig.show()

# Total Count and Hazardous Count by date

# Convert 'close_approach_date' column to datetime
df_asteroids['close_approach_date'] = pd.to_datetime(df_asteroids['close_approach_date'])

# Count hazardous and non-hazardous asteroids by date
hazardous_counts = df_asteroids[df_asteroids['is_potentially_hazardous_asteroid']].groupby('close_approach_date').size().reset_index(name='hazardous_count')
non_hazardous_counts = df_asteroids[~df_asteroids['is_potentially_hazardous_asteroid']].groupby('close_approach_date').size().reset_index(name='non_hazardous_count')

# Merge the two counts
counts = pd.merge(hazardous_counts, non_hazardous_counts, on='close_approach_date', how='outer').fillna(0)

# Melt data for plotting
counts_melted = pd.melt(counts, id_vars=['close_approach_date'], value_vars=['hazardous_count', 'non_hazardous_count'], 
                        var_name='Type', value_name='Count')

# Create stacked bar chart with switched colors and patterns
color_discrete_map = {
    'hazardous_count': 'red',
    'non_hazardous_count': 'blue'
}
pattern_shape_map = {
    'non_hazardous_count': '+',
    'hazardous_count': 'x'
}

fig = px.bar(counts_melted, x='close_approach_date', y='Count', color='Type', 
             labels={'close_approach_date': 'Date', 'Count': 'Number of Asteroids'},
             title='Hazardous vs. Non-Hazardous Asteroids by Date',
             barmode='stack', height=400,
             color_discrete_map=color_discrete_map,
             pattern_shape='Type', pattern_shape_map=pattern_shape_map)

# Add data labels
fig.update_traces(texttemplate='%{y}', textposition='inside', textfont_size=14)

# Update layout for larger font sizes
fig.update_layout(
    width=1200,
    height=850,
    xaxis_title='Date',
    yaxis_title='Number of Asteroids',
    font=dict(size=16),
    title_font=dict(size=24),
    uniformtext_minsize=16.5,
    uniformtext_mode='hide'
)

fig.show()

# Smallest Miss Distance (km) by Date 
df_asteroids['close_approach_date'] = pd.to_datetime(df_asteroids['close_approach_date'])

# Get minimum miss distance and corresponding name
min_miss_distance = df_asteroids.groupby('close_approach_date', as_index=False).apply(
    lambda group: group.loc[group['miss_distance_km'].idxmin()]
).reset_index(drop=True)

# Remove brackets from names
min_miss_distance['name'] = min_miss_distance['name'].str.replace(r'[()]', '', regex=True)

# Create 2D line plot
fig = px.line(min_miss_distance, 
              x='close_approach_date', 
              y='miss_distance_km',
              labels={
                  'close_approach_date': 'Close Approach Date',
                  'miss_distance_km': 'Minimum Miss Distance (km)'
              },
              title='Minimum Earth Miss Distance by Date')

# Add custom markers using different PNG images
asteroid_images = ["asteroid1.png", "asteroid2.png", "asteroid3.png", "asteroid4.png", "asteroid5-1.png", "asteroid6.png", "asteroid7.png"]
sizex = sizey = 4e7  # Uniform size for all markers

for i, row in min_miss_distance.iterrows():
    asteroid_image = asteroid_images[i % len(asteroid_images)]
    fig.add_layout_image(
        dict(
            source=asteroid_image,
            x=row['close_approach_date'],
            y=row['miss_distance_km'],
            xref="x", yref="y",
            sizex=sizex,
            sizey=sizey,
            xanchor="center",
            yanchor="middle"
        )
    )

# Update layout and hover information
fig.update_traces(
    mode='lines+markers+text',
    hovertemplate="Name: %{customdata[0]}<br>" +
                  "Date: %{x|%Y-%m-%d}<br>" +
                  "Miss Distance: %{y:.2f} km",
    customdata=min_miss_distance[['name']].to_numpy(),
    text=min_miss_distance['name'],
    textposition="top center",
    textfont=dict(size=20),
    marker=dict(size=36) 
)

fig.update_layout(
    width=1400,
    height=800,
    xaxis_title='Close Approach Date',
    yaxis_title='Minimum Miss Distance (km)',
    title='Minimum Earth Miss Distance by Date',
    font=dict(size=23),
    title_font=dict(size=24)
)

fig.show()


df_two = df_asteroids
df_two.sort_values(by=['close_approach_date'], inplace=True)
df_three = df_two[0:60]
df_three['close_approach_date'] = pd.to_datetime(df_three['close_approach_date'])

# Get minimum miss distance and corresponding name
min_miss_distance = df_three.groupby('close_approach_date', as_index=False).apply(
    lambda group: group.loc[group['miss_distance_km'].idxmin()]
).reset_index(drop=True)

# Remove brackets from names
min_miss_distance['name'] = min_miss_distance['name'].str.replace(r'[()]', '', regex=True)

# Create 2D line plot
fig = px.line(min_miss_distance, 
              x='close_approach_date', 
              y='miss_distance_km',
              labels={
                  'close_approach_date': 'Close Approach Date',
                  'miss_distance_km': 'Minimum Miss Distance (km)'
              },
              title='Minimum Earth Miss Distance by Date')

# Add custom markers using different PNG images
asteroid_images = ["asteroid1.png", "asteroid2.png", "asteroid3.png", "asteroid4.png", "asteroid5-1.png", "asteroid6.png", "asteroid7.png"]
sizex = sizey = 4e7  # Uniform size for all markers

for i, row in min_miss_distance.iterrows():
    asteroid_image = asteroid_images[i % len(asteroid_images)]
    fig.add_layout_image(
        dict(
            source=asteroid_image,
            x=row['close_approach_date'],
            y=row['miss_distance_km'],
            xref="x", yref="y",
            sizex=sizex,
            sizey=sizey,
            xanchor="center",
            yanchor="middle"
        )
    )

# Update layout and hover information
fig.update_traces(
    mode='lines+markers+text',
    hovertemplate="Name: %{customdata[0]}<br>" +
                  "Date: %{x|%Y-%m-%d}<br>" +
                  "Miss Distance: %{y:.2f} km",
    customdata=min_miss_distance[['name']].to_numpy(),
    text=min_miss_distance['name'],
    textposition="top center",
    textfont=dict(size=20),
    marker=dict(size=80) 
)

fig.update_layout(
    width=1400,
    height=800,
    xaxis_title='Close Approach Date',
    yaxis_title='Minimum Miss Distance (km)',
    title='Minimum Earth Miss Distance by Date',
    font=dict(size=23),
    title_font=dict(size=24)
)

fig.show()

# Asteroid Diamater (m) Distribution
# Bin the diameters into a wider range of categories for more granularity
df_asteroids['diameter_bin'] = pd.cut(df_asteroids['diameter_m'], bins=3)
df_asteroids['diameter_mid'] = df_asteroids['diameter_bin'].apply(lambda x: round((x.right + x.left) / 2))  # Round to nearest whole number

# Group by diameter bin to get midpoints for plotting
bin_counts = df_asteroids.groupby('diameter_bin').size().reset_index(name='count')
bin_counts['diameter_mid'] = bin_counts['diameter_bin'].apply(lambda x: round((x.right + x.left) / 2)).astype(int)  # Round to nearest whole number

# Calculate the size scale factor for visibility
size_scale = 100 / bin_counts['diameter_mid'].max()

# Generate hover text including rounded diameter range to nearest 100s
bin_counts['hover_text'] = bin_counts['diameter_bin'].apply(
    lambda x: f"Diameter Range (m): ({100 * math.floor(x.left / 100)} to {100 * math.floor(x.right / 100)})<br>Count: {bin_counts.loc[bin_counts['diameter_bin'] == x, 'count'].values[0]}"
)
# Filter out bins with a count of zero
bin_counts = bin_counts[bin_counts['count'] > 0]

# Calculate the max and min for padding
x_min, x_max = bin_counts['diameter_mid'].min(), bin_counts['diameter_mid'].max()
x_pad = (x_max - x_min) * 0.4  # Adjust padding to 40% for more space

# Create 3D scatter plot
fig = go.Figure(data=[go.Scatter3d(
    x=bin_counts['diameter_mid'],  # X-axis showing the mid-point of diameter bins
    y=[0.5] * len(bin_counts),  # Set Y-axis to a lowered constant value, for example, 0.5
    z=[i for i in range(len(bin_counts))],  # Set Z-axis values step-by-step
    mode='markers+text',  # Add text to markers
    marker=dict(
        size=bin_counts['diameter_mid'] * size_scale,  # Scale marker sizes based on diameter midpoint
        color=bin_counts['diameter_mid'],  # Color by diameter mid-point
        colorscale='Viridis',  # A visually appealing color scale
        opacity=0.8
    ),
    text=bin_counts['hover_text'],  # Use count values as text
    textposition="top center",  # Position text above the marker
    hovertemplate=(
        "Diameter Bin Midpoint: %{x}m<br>" +
        "%{text}<extra></extra>"
    )  # Custom hovertemplate to show the diameter midpoint and text
)])

# Update layout for better visualization with extra padding
fig.update_layout(
    title='3D Scatter Plot of Asteroid Diameter Range',
    scene=dict(
        xaxis=dict(
            title='Diameter Bin Midpoint (m)',
            range=[x_min - x_pad, x_max + x_pad]  # Apply padding to the X-axis
        ),
        yaxis=dict(
            title='',  # No title for Y-axis
            showticklabels=False,  # Hide tick labels on Y-axis
            range=[0, 1]  # Add padding to the Y-axis
        ),
        zaxis=dict(
            title='',  # Title for Z-axis
            tickvals=[i for i in range(len(bin_counts))],  # Set step-by-step tick values
            ticktext=[f"Index {i}" for i in range(len(bin_counts))],  # Optional: Set tick labels
            showticklabels=False,  # Hide tick labels on Y-axis
            range=[-1, len(bin_counts)]  # Adjust range to cover all ticks
            
        )
    ),
    font=dict(size=16),
    title_font=dict(size=24),
    width=1100,  # Set the width of the figure
    height=1100   # Set the height of the figure
)

fig.show()


# Asteroid Diamater (m) Distribution (0 - 1200 Diameter)
df_two_diameter = df_asteroids

df_two_diameter.sort_values(by=['diameter_m'], inplace=True)
# df_two_diameter.to_excel('test_2.xlsx', index=False)
df_three_diameter = df_two_diameter[0:106]

# Bin the diameters into a wider range of categories for more granularity
df_three_diameter['diameter_bin'] = pd.cut(df_three_diameter['diameter_m'], bins=5)
df_three_diameter['diameter_mid'] = df_three_diameter['diameter_bin'].apply(lambda x: round((x.right + x.left) / 2))  # Round to nearest whole number

# Group by diameter bin to get midpoints for plotting
bin_counts = df_three_diameter.groupby('diameter_bin').size().reset_index(name='count')
bin_counts['diameter_mid'] = bin_counts['diameter_bin'].apply(lambda x: round((x.right + x.left) / 2)).astype(int)  # Round to nearest whole number

# Calculate the size scale factor for visibility
size_scale = 100 / bin_counts['diameter_mid'].max()

bin_counts['hover_text'] = bin_counts['diameter_bin'].apply(
    lambda x: f"Diameter: ({100 * math.floor(x.left / 100)} to {100 * math.floor(x.right / 100)}) meters<br>Asteroids: {bin_counts.loc[bin_counts['diameter_bin'] == x, 'count'].values[0]}"
)

# Filter out bins with a count of zero
bin_counts = bin_counts[bin_counts['count'] > 0]

# Calculate the max and min for padding
x_min, x_max = bin_counts['diameter_mid'].min(), bin_counts['diameter_mid'].max()
x_pad = (x_max - x_min) * 0.3  # Adjust padding to 40% for more space

# Create 3D scatter plot
fig = go.Figure(data=[go.Scatter3d(
    x=bin_counts['diameter_mid'],  # X-axis showing the mid-point of diameter bins
    y=[0.5] * len(bin_counts),  # Set Y-axis to a constant value, for example, 0.5
    z=[i for i in range(len(bin_counts))],  # Set Z-axis values step-by-step
    mode='markers+text',  # Add text to markers
    marker=dict(
        size=bin_counts['diameter_mid'] * size_scale,  # Scale marker sizes based on diameter midpoint
        color=bin_counts['diameter_mid'],  # Color by diameter mid-point
        colorscale='Viridis',  # A visually appealing color scale
        opacity=0.8
    ),
    text=bin_counts['hover_text'],  # Use count values as text
    textposition="top center",  # Position text above the marker
    hovertemplate=(
        "Diameter Midpoint: %{x}m<br>" +
        "%{text}<extra></extra>"
    )  # Custom hovertemplate to show the diameter midpoint and text
)])

# Update layout for better visualization with extra padding
fig.update_layout(
    title='3D Scatter Plot of Asteroid Diameter Bins (0 to 1100 meter Range - Zoomed)',
    scene=dict(
        xaxis=dict(
            title='Diameter Bin Midpoint (m)',
            range=[x_min - x_pad, x_max + x_pad]  # Apply padding to the X-axis
        ),
        yaxis=dict(
            title='',  # No title for Y-axis
            showticklabels=False,  # Hide tick labels on Y-axis
            range=[0, 1]  # Add padding to the Y-axis
        ),
        zaxis=dict(
            title='',  # Title for Z-axis
            tickvals=[i for i in range(len(bin_counts))],  # Set step-by-step tick values
            ticktext=[f"Index {i}" for i in range(len(bin_counts))],  # Optional: Set tick labels
            showticklabels=False,  # Hide tick labels on Y-axis
            range=[-1, len(bin_counts)]  # Adjust range to cover all ticks
        )
    ),
    font=dict(size=16),
    title_font=dict(size=24),
    width=1100,  # Set the width of the figure
    height=1100   # Set the height of the figure
)

fig.show()
