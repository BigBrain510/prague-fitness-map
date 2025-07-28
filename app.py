import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# Load district boundaries
districts = gpd.read_file("prague_core_districts.geojson")
district_names = ["All Prague"] + sorted(districts["name"].dropna().unique().tolist())

# Load studio data
yoga_df = pd.read_csv("Filtered_Yoga_Studio_List.csv")
pilates_df = pd.read_csv("Filtered_Pilates_Studio_List.csv")
barre_df = pd.read_csv("Filtered_Barre_Studio_List.csv")

# Sidebar filters
st.sidebar.header("Filter Options")
studio_options = st.sidebar.multiselect(
    "Select Studio Types", ["Yoga", "Pilates", "Barre"], default=["Yoga", "Pilates", "Barre"]
)
selected_district = st.sidebar.selectbox("Select Neighborhood", district_names)

# Color logic
color_map = {
    "Yoga": "blue",
    "Pilates": "green",
    "Barre": "red"
}

# Combine data into one DataFrame
yoga_df["Type"] = "Yoga"
pilates_df["Type"] = "Pilates"
barre_df["Type"] = "Barre"
studio_data = pd.concat([yoga_df, pilates_df, barre_df])

# Filter by studio type
studio_data = studio_data[studio_data["Type"].isin(studio_options)]

# Filter by neighborhood (spatial)
if selected_district != "All Prague":
    selected_geom = districts[districts["name"] == selected_district].geometry.values[0]
    studio_data = studio_data[
        studio_data.apply(lambda row: selected_geom.contains(
            gpd.points_from_xy([row["Longitude"]], [row["Latitude"]])[0]
        ), axis=1)
    ]

# Map creation
m = folium.Map(location=[50.08, 14.43], zoom_start=12)

# Add district overlays
folium.GeoJson(districts).add_to(m)

# Marker cluster
cluster = MarkerCluster().add_to(m)

# Add markers
for _, row in studio_data.iterrows():
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=6,
        color=color_map.get(row["Type"], "gray"),
        fill=True,
        fill_opacity=0.8,
        popup=f"{row['Name']} ({row['Type']})"
    ).add_to(cluster)

# Display map
st_data = st_folium(m, width=1000, height=700)

