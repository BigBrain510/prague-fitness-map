
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point
from streamlit_folium import st_folium
from folium.plugins import HeatMap

# Load Studio Data
@st.cache_data
def load_data():
    yoga = pd.read_csv("Filtered_Yoga_Studio_List.csv")
    pilates = pd.read_csv("Filtered_Pilates_Studio_List.csv")
    barre = pd.read_csv("Filtered_Barre_Studio_List.csv")
    return yoga, pilates, barre

def df_to_gdf(df):
    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']), crs="EPSG:4326")

@st.cache_data
def load_districts():
    return gpd.read_file("prague_core_districts.geojson")

st.sidebar.header("Filter Options")
selected_types = st.sidebar.multiselect(
    "Select Studio Types", ["Yoga", "Pilates", "Barre"], default=["Yoga", "Pilates", "Barre"]
)

districts = load_districts()
st.write("District columns:", districts.columns)
selected_district = st.sidebar.selectbox("Select Neighborhood", district_names)

yoga, pilates, barre = load_data()
yoga_gdf = df_to_gdf(yoga)
pilates_gdf = df_to_gdf(pilates)
barre_gdf = df_to_gdf(barre)

if selected_district != "All Prague":
    district_geom = districts[districts["name"] == selected_district].geometry.values[0]
    yoga_gdf = yoga_gdf[yoga_gdf.geometry.within(district_geom)]
    pilates_gdf = pilates_gdf[pilates_gdf.geometry.within(district_geom)]
    barre_gdf = barre_gdf[barre_gdf.geometry.within(district_geom)]

m = folium.Map(location=[50.0755, 14.4378], zoom_start=13)

if selected_district != "All Prague":
    folium.GeoJson(district_geom, name=selected_district,
                   style_function=lambda x: {'fillColor': '#ffa', 'color': '#f90', 'weight': 2}).add_to(m)
else:
    for _, row in districts.iterrows():
        folium.GeoJson(row["geometry"], name=row["name"],
                       style_function=lambda x: {'fillColor': '#fff0', 'color': '#aaa', 'weight': 1}).add_to(m)

def add_markers(gdf, color, icon):
    for _, row in gdf.iterrows():
        popup = f"<b>{row['Name']}</b><br>{row['Address']}<br><a href='{row['Google Maps Link']}' target='_blank'>Google Maps</a>"
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup,
            icon=folium.Icon(color=color, icon=icon, prefix="fa")
        ).add_to(m)

if "Yoga" in selected_types:
    add_markers(yoga_gdf, "green", "leaf")
if "Pilates" in selected_types:
    add_markers(pilates_gdf, "blue", "heartbeat")
if "Barre" in selected_types:
    add_markers(barre_gdf, "purple", "star")

all_coords = pd.concat([
    yoga_gdf[['Latitude', 'Longitude']],
    pilates_gdf[['Latitude', 'Longitude']],
    barre_gdf[['Latitude', 'Longitude']]
])
HeatMap(data=all_coords.values.tolist(), radius=13, blur=15).add_to(m)

st_data = st_folium(m, width=800, height=600)
