import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium


st.set_page_config(layout="wide")

# Load studio data
yoga_df = pd.read_csv("Filtered_Yoga_Studio_List.csv")
pilates_df = pd.read_csv("Filtered_Pilates_Studio_List.csv")
barre_df = pd.read_csv("Filtered_Barre_Studio_List.csv")

# Load districts
districts = gpd.read_file("prague_core_districts.geojson")
districts = districts[["name", "geometry"]]  # Ensure clean structure

# Convert studio data to GeoDataFrames
def df_to_gdf(df):
    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]), crs="EPSG:4326")

yoga_gdf = df_to_gdf(yoga_df)
pilates_gdf = df_to_gdf(pilates_df)
barre_gdf = df_to_gdf(barre_df)

# Sidebar filters
st.sidebar.header("Filter Options")
studio_types = st.sidebar.multiselect("Select Studio Types", ["Yoga", "Pilates", "Barre"], default=["Yoga", "Pilates", "Barre"])
district_options = ["All Prague"] + sorted(districts["name"].dropna().unique())
selected_district = st.sidebar.selectbox("Select Neighborhood", district_options)

# Filter by district (spatial join)
def filter_by_district(gdf):
    if selected_district == "All Prague":
        return gdf
    district_geom = districts[districts["name"] == selected_district]
    return gpd.sjoin(gdf, district_geom, how="inner", predicate="intersects")

# Filter studios
filtered_layers = []
if "Yoga" in studio_types:
    filtered_layers.append(("Yoga", filter_by_district(yoga_gdf), "brown"))
if "Pilates" in studio_types:
    filtered_layers.append(("Pilates", filter_by_district(pilates_gdf), "orange"))
if "Barre" in studio_types:
    filtered_layers.append(("Barre", filter_by_district(barre_gdf), "pink"))

# Create Folium map
m = folium.Map(location=[50.0755, 14.4378], zoom_start=12, tiles="openstreetmap")

# Add districts
if selected_district != "All Prague":
    folium.GeoJson(
        data=districts[districts["name"] == selected_district],
        style_function=lambda x: {"fillColor": "#ffff00", "color": "#000000", "fillOpacity": 0.2},
        name="Selected District"
    ).add_to(m)

# Add markers
for label, gdf, color in filtered_layers:
    group = folium.FeatureGroup(name=f"{label} ({len(gdf)})", show=True)
    for _, row in gdf.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=f"{row['Name']}<br>{row['Address']}",
            icon=folium.Icon(color="gray", icon="info-sign")
        ).add_to(group)
    group.add_to(m)

folium.LayerControl().add_to(m)

# Show map
st_data = st_folium(m, width=1200, height=700)

HeatMap(data=all_coords.values.tolist(), radius=13, blur=15).add_to(m)

st_data = st_folium(m, width=800, height=600)
