import streamlit as st
import pandas as pd
import numpy as np
import googlemaps
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from time import sleep
import datetime
import os

# Page setup
st.set_page_config(layout="wide", page_title="MapBite Analytics Dashboard")
st.title("📍 MapBite Analytics Dashboard")

# ==========================================
# SECURE CREDENTIAL RECOVERY
# ==========================================
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("Missing Security Configuration! Please set 'GOOGLE_API_KEY' inside your Streamlit Secrets panel.")
    st.stop()

# ==========================================
# BUDGET TRACKING & RATE LIMITER ENGINE
# ==========================================
DAILY_RUN_LIMIT = st.secrets["MAX_BUDGET"]  
USAGE_FILE = "api_usage_tracker.txt"

def check_daily_allowance():
    today = str(datetime.date.today())
    if not os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "w") as f:
            f.write(f"{today},0")
        return True, DAILY_RUN_LIMIT
    with open(USAGE_FILE, "r") as f:
        data = f.read().strip().split(",")
    record_date = data[0]
    current_count = int(data[1])
    if record_date != today:
        with open(USAGE_FILE, "w") as f:
            f.write(f"{today},0")
        return True, DAILY_RUN_LIMIT
    remaining = DAILY_RUN_LIMIT - current_count
    if current_count >= DAILY_RUN_LIMIT:
        return False, 0
    return True, remaining

def increment_daily_usage():
    today = str(datetime.date.today())
    with open(USAGE_FILE, "r") as f:
        data = f.read().strip().split(",")
    new_count = int(data[1]) + 1
    with open(USAGE_FILE, "w") as f:
        f.write(f"{today},{new_count}")

allowed_to_run, runs_left = check_daily_allowance()

# ==========================================
# SIDEBAR CONTROL PANEL (WITH RADIUS FORM)
# ==========================================
st.sidebar.header("Target Location Parameters")
lat_input = st.sidebar.number_input("Latitude", value=37.9825405, format="%.7f")
lng_input = st.sidebar.number_input("Longitude", value=23.7373905, format="%.7f")
target_coords = (lat_input, lng_input)

keyword = st.sidebar.text_input("Cuisine/Keyword", value="pizza")
business_type = "restaurant"

# --- NEW: Dynamic Search Strategy Form Fields ---
st.sidebar.markdown("---")
st.sidebar.subheader("Search Strategy")
search_mode = st.sidebar.radio(
    "Select Scope Strategy:",
    options=["Distance Rank (Strict Closest)", "Fixed Radius Bound"]
)

# Render a slider ONLY if the user wants a fixed radius boundary
radius_meters = None
if search_mode == "Fixed Radius Bound":
    radius_meters = st.sidebar.slider(
        "Search Radius (Meters)", 
        min_value=500, 
        max_value=5000, 
        value=2500, 
        step=250,
        help="500m is walkable; 2500m is roughly a 5-10 minute drive layout."
    )

st.sidebar.markdown("---")
st.sidebar.markdown(f"📊 **Remaining Budget Today:** `{runs_left} / {DAILY_RUN_LIMIT} queries left`")

if allowed_to_run:
    run_analysis = st.sidebar.button("Run Market Analysis", type="primary")
else:
    st.sidebar.error("⛔ Daily market analysis budget exhausted! Resets at midnight.")
    run_analysis = False

if "final_df" not in st.session_state:
    st.session_state.final_df = None

# ==========================================
# DATA INGESTION ENGINE (COMPATIBILITY CONTROLLER)
# ==========================================
if run_analysis:
    with st.spinner("Fetching nearby market competitors from Google Maps..."):
        try:
            map_client = googlemaps.Client(key=API_KEY)
            results = []
            next_page = None
            
            for _ in range(3):
                if next_page:
                    response = map_client.places_nearby(page_token=next_page)
                else:
                    # --- NEW: Conditional Payload Processing ---
                    if search_mode == "Fixed Radius Bound":
                        # Radius searches require a defined radius and CANNOT use rank_by
                        response = map_client.places_nearby(
                            location=target_coords,
                            type=business_type,
                            radius=radius_meters,
                            keyword=keyword
                        )
                    else:
                        # Distance rankings CANNOT use a radius parameter
                        response = map_client.places_nearby(
                            location=target_coords, 
                            type=business_type, 
                            rank_by='distance', 
                            keyword=keyword
                        )
                        
                results.extend(response.get('results', []))
                next_page = response.get('next_page_token')
                if not next_page:
                    break
                sleep(2)
            
            df_nearby = pd.DataFrame(results)
            
            if df_nearby.empty:
                st.warning("No competitors found matching your location parameters.")
            else:
                place_ids, names, lats, lngs, ratings, total_reviews, price_levels, websites = [], [], [], [], [], [], [], []
                
                for p_id in df_nearby['place_id'].tolist()[:60]:
                    place = map_client.place(
                        place_id=p_id,
                        fields=['name', 'geometry', 'rating', 'user_ratings_total', 'price_level', 'website']
                    )
                    res = place.get('result', {})
                    
                    place_ids.append(p_id)
                    names.append(res.get('name', 'Unknown'))
                    ratings.append(res.get('rating', np.nan))
                    total_reviews.append(res.get('user_ratings_total', 0))
                    price_levels.append(res.get('price_level', 1))
                    websites.append(res.get('website', '#'))
                    
                    loc = res.get('geometry', {}).get('location', {})
                    lats.append(loc.get('lat', np.nan))
                    lngs.append(loc.get('lng', np.nan))
                
                st.session_state.final_df = pd.DataFrame({
                    'name': names, 'lat': lats, 'lng': lngs, 'rating': ratings,
                    'total_reviews': total_reviews, 'price_level': price_levels, 'website': websites
                }).dropna(subset=['lat', 'lng'])
                
                increment_daily_usage()
                st.rerun()  
                
        except Exception as e:
            st.error(f"An error occurred: {e}")

# ==========================================
# PRESENTATION INTERFACE LAYER
# ==========================================
if st.session_state.final_df is not None:
    df = st.session_state.final_df.copy()
    
    st.markdown("### 🔍 Filter Intelligence Data")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        min_rating = st.slider("Minimum Star Rating", 1.0, 5.0, 1.0, step=0.1)
    with col_f2:
        min_reviews = st.number_input("Minimum Review Volume", min_value=0, value=0, step=10)
    with col_f3:
        price_filter = st.multiselect("Price Tiers (€)", options=[1, 2, 3, 4], default=[1, 2, 3, 4], format_func=lambda x: "€" * x)
        
    filtered_df = df[
        (df['rating'] >= min_rating) & 
        (df['total_reviews'] >= min_reviews) & 
        (df['price_level'].isin(price_filter))
    ]
    
    st.markdown("### 📊 Market Report Summary")
    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    
    with metric_1:
        st.metric("Total Competitors Displayed", len(filtered_df))
    with metric_2:
        avg_market_rating = filtered_df['rating'].mean()
        st.metric("Average Market Rating", f"⭐ {avg_market_rating:.2f}" if not np.isnan(avg_market_rating) else "N/A")
    with metric_3:
        avg_review_vol = filtered_df['total_reviews'].mean()
        st.metric("Avg Review Volume / Venue", f"💬 {int(avg_review_vol)}" if not np.isnan(avg_review_vol) else "N/A")
    with metric_4:
        mode_price = filtered_df['price_level'].mode()
        price_string = "€" * int(mode_price[0]) if not mode_price.empty else "N/A"
        st.metric("Dominant Price Tier", price_string)
        
    st.markdown("### 🗺️ Live Market Density Heatmap")
    m = folium.Map(location=[lat_input, lng_input], zoom_start=14, tiles="OpenStreetMap")
    
    # --- NEW: Draw a translucent circle guide if Fixed Radius search mode is active ---
    if search_mode == "Fixed Radius Bound" and radius_meters:
        folium.Circle(
            location=[lat_input, lng_input],
            radius=radius_meters,
            color="#1E90FF",
            fill=True,
            fill_color="#1E90FF",
            fill_opacity=0.1,
            tooltip=f"Search Scope Limit ({radius_meters}m)"
        ).add_to(m)
        
    heatmap_locs = filtered_df[['lat', 'lng']].values.tolist()
    if heatmap_locs:
        HeatMap(heatmap_locs, radius=25, blur=15).add_to(m)
        
    for idx, row in filtered_df.iterrows():
        popup_content = f"""
        <div style='font-family: sans-serif; font-size: 12px;'>
            <strong>{row['name']}</strong><br>
            Rating: ⭐ {row['rating']} ({int(row['total_reviews'])} reviews)<br>
            Price Tier: {'€'*int(row['price_level'])}<br>
            <a href="{row['website']}" target="_blank" style="color: #1E90FF;">Website Link</a>
        </div>
        """
        folium.Marker(
            location=[row['lat'], row['lng']],
            popup=folium.Popup(popup_content, max_width=250),
            icon=folium.Icon(color="red", icon="cutlery", prefix="fa")
        ).add_to(m)
        
    st_folium(m, width="stretch", height=500, returned_objects=[])
    
    st.markdown("### 🗃️ Raw Competitor Matrix")
    st.dataframe(
        filtered_df[['name', 'rating', 'total_reviews', 'price_level', 'website']],
        width="stretch",
        column_config={"website": st.column_config.LinkColumn("Website View")}
    )
else:
    st.info("👈 Enter your target coordinates and preferences in the panel to map out local market insights.")
