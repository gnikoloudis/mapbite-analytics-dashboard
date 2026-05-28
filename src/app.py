import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

# Import our custom logic modules securely using the unique namespace string
import tracker
import mapbite_analytics as analytics

# ==========================================
# 1. UI INITIALIZATION & PLATFORM TOKENS
# ==========================================
st.set_page_config(
    page_title="MapBite - Competitor Intelligence Dashboard",
    page_icon="🍔",
    layout="wide"
)

st.title("🍔 MapBite Market Intelligence Dashboard")
st.markdown("Benchmark your location, map competitor density, and evaluate neighborhood market power.")

# Handle API Key validation
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    map_client = analytics.get_map_client(API_KEY)
else:
    st.error("🔑 Google API Key missing! Please configure GOOGLE_API_KEY inside your Streamlit secrets.")
    st.stop()

# DYNAMIC CONFIG: Fetch Daily Cap Limit directly from Streamlit Secrets
DAILY_MAX_LIMIT = st.secrets.get("DAILY_MAX_LIMIT", 5)

# Initialize dynamic session states to preserve execution data over refreshes
if "analysis_df" not in st.session_state:
    st.session_state.analysis_df = None
if "last_lat" not in st.session_state:
    st.session_state.last_lat = 37.9825405
if "last_lng" not in st.session_state:
    st.session_state.last_lng = 23.7373905

# Pre-fetch usage status for blocking buttons if needed
is_under_limit, current_usage = tracker.check_and_increment_tracker(DAILY_MAX_LIMIT)

# ==========================================
# 2. GEOGRAPHIC SIDEBAR SELECTIONS ENGINE
# ==========================================
st.sidebar.header("📍 Target Setup")

# Cuisine Preference Field Input
cuisine_input = st.sidebar.text_input(
    "Preferred Cuisine Type:",
    placeholder="e.g., Italian, Sushi, Souvlaki, Burgers",
    value=""
)

input_mode = st.sidebar.radio(
    "Location Selection Mode:",
    ["🔍 Type an Address / Landmark", "⌨️ Input Coordinates Directly"]
)

address_resolved = True

if input_mode == "🔍 Type an Address / Landmark":
    address_string = st.sidebar.text_input("Enter Target Location Address:", placeholder="e.g., Syntagma Square, Athens")
    
    if address_string:
        lat, lng = analytics.resolve_address(map_client, address_string)
        if lat and lng:
            st.session_state.last_lat, st.session_state.last_lng = lat, lng
            st.sidebar.success(f"🎯 Target Locked: `{lat:.5f}, {lng:.5f}`")
        else:
            st.sidebar.error("❌ Could not resolve address. Try verifying the spelling or network connection!")
            address_resolved = False
    else:
        st.sidebar.info("💡 Type an address above to map out a restaurant market zone.")
        address_resolved = False
else:
    with st.sidebar.expander("Precision GPS Coordinates", expanded=True):
        st.session_state.last_lat = st.number_input("Latitude", value=st.session_state.last_lat, format="%.7f")
        st.session_state.last_lng = st.number_input("Longitude", value=st.session_state.last_lng, format="%.7f")

search_radius = st.sidebar.slider("Search Scan Radius (Meters)", min_value=200, max_value=3000, value=1000, step=100)

# Execution trigger hooks
if address_resolved:
    if not is_under_limit:
        st.sidebar.error("🚨 System Daily Query Limit Reached! Try again tomorrow.")
        st.sidebar.button("🚀 Run Competitive Analysis", disabled=True, width="stretch")
    else:
        if st.sidebar.button("🚀 Run Competitive Analysis", width="stretch"):
            with st.spinner("Analyzing neighborhood market dynamics..."):
                df_results = analytics.fetch_and_rank_competitors(
                    map_client, st.session_state.last_lat, st.session_state.last_lng, search_radius, cuisine_input
                )
                if not df_results.empty:
                    tracker.increment_counter_file(current_usage)
                    st.session_state.analysis_df = df_results
                    st.rerun()
                else:
                    st.warning("📭 No active listings for this cuisine type found within this search area.")

# Quota tracking progress component
st.sidebar.markdown("---")
st.sidebar.markdown(f"### 📊 App Resource Monitor")
st.sidebar.progress(
    min(current_usage / DAILY_MAX_LIMIT, 1.0), 
    text=f"Daily Limit Usage: {current_usage} / {DAILY_MAX_LIMIT}"
)

# Clear business intelligence documentation in the sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dual-Score Metric Matrix")
st.sidebar.markdown("""
**🔴 Opportunity Score (Quality Gap)**
* Measures high-volume areas with low customer satisfaction scores. Focuses entirely on raw market operational vulnerabilities.

**💰 Premium Gap Score (Value Deficit)**
* Multiplies the core opportunity index against price tiers. Flags expensive venues charging premium prices but failing to deliver quality.
""")

# ==========================================
# 3. RESULTS VIEW DASHBOARD GENERATION
# ==========================================
raw_df = st.session_state.analysis_df

if raw_df is not None and not raw_df.empty:
    
    # 🌟 INTERFACE VIEW MODE TOGGLE 🌟
    st.markdown("### 🛠️ Intelligence Lens Selector")
    view_mode = st.radio(
        "Choose Dashboard Analysis Angle:",
        ["🔴 Find Market Gaps & Vulnerabilities (Worst Rated/Highest Traffic)", 
         "👑 Study Market Leaders & Dominance (Best Rated/Highest Traffic)"],
        horizontal=True
    )
    st.markdown("---")
    
    # Process dataframe sorting and rankings depending on choice
    if "Find Market Gaps" in view_mode:
        df = raw_df.sort_values(by="Opportunity_Score", ascending=False).reset_index(drop=True)
        df['Market_Rank'] = df.index + 1
        
        top_opportunity = df.iloc[0]
        st.markdown("### 🎯 Core Market Opportunity Summary")
        st.metric(
            label="Peak Opportunity Score", 
            value=f"{top_opportunity['Opportunity_Score']} / 15", 
            delta="High Market Gap"
        )
    else:
        df = raw_df.sort_values(by="Market_Dominance_Score", ascending=False).reset_index(drop=True)
        df['Market_Rank'] = df.index + 1
        
        top_leader = df.iloc[0]
        st.markdown("### 👑 Market Kingpin Summary")
        st.metric(
            label="Peak Dominance Score", 
            value=f"{top_leader['Market_Dominance_Score']}", 
            delta="Market Leader to Beat",
            delta_color="inverse"
        )
        
    st.markdown("---")
    
    # ROW 1 (TOP): Full-Width Strategic Opportunity Map
    st.subheader("🗺️ Strategic Analysis Map")
    m = folium.Map(location=[st.session_state.last_lat, st.session_state.last_lng], zoom_start=15)
    
    # Center pinpoint anchor marker
    folium.Marker(
        [st.session_state.last_lat, st.session_state.last_lng],
        popup="📍 <b>Your Proposed Site Core</b>",
        tooltip="Search Epicenter",
        icon=folium.Icon(color="red", icon="crosshair", prefix="fa")
    ).add_to(m)
    
    for _, row in df.iterrows():
        if row['lat'] and row['lng']:
            
            # 🌟 CHANGES HERE: LINES 122 - 155 ADJUSTED DYNAMICALLY 🌟
            if "Find Market Gaps" in view_mode:
                # Gaps Mode: High ranks mean poor performers/vulnerable spots
                if row['Market_Rank'] == 1:
                    marker_color, badge_color = "purple", "background-color: #7B1FA2; color: white;"
                elif row['Market_Rank'] in [2, 3, 4]:
                    marker_color, badge_color = "blue", "background-color: #1976D2; color: white;"
                elif row['Market_Rank'] in [5, 6, 7, 8]:
                    marker_color, badge_color = "green", "background-color: #388E3C; color: white;"
                else:
                    marker_color, badge_color = "gray", "background-color: #616161; color: white;"
                
                badge_text = row['Strategic_Recommendation']
                metric_label = "Opportunity Index:"
                metric_value = row['Opportunity_Score']
                metric_color_style = "color: #E64A19;"
                map_icon = "lightbulb-o"
            else:
                # Leaders Mode: High ranks mean top market players (Best Rated/High Traffic)
                if row['Market_Rank'] == 1:
                    marker_color, badge_color = "darkpurple", "background-color: #4A148C; color: #FFD700; border: 1px solid #FFD700;"
                elif row['Market_Rank'] in [2, 3, 4]:
                    marker_color, badge_color = "orange", "background-color: #FF9800; color: white;"
                elif row['Market_Rank'] in [5, 6, 7, 8]:
                    marker_color, badge_color = "beige", "background-color: #5D4037; color: white;"
                else:
                    marker_color, badge_color = "lightgray", "background-color: #9E9E9E; color: black;"
                
                badge_text = "Market Leader Profile"
                metric_label = "Dominance Index:"
                metric_value = row['Market_Dominance_Score']
                metric_color_style = "color: #FF8F00;"
                map_icon = "trophy"
            
            popup_html = f"""
            <div style="font-family: 'Arial', sans-serif; width: 230px; padding: 5px;">
                <div style='float: right; font-size: 18px;'>#{row['Market_Rank']}</div>
                <h4 style='margin: 0 0 4px 0; color: #333;'>{row['name']}</h4>
                <div style='margin-bottom: 8px; padding: 3px 6px; border-radius: 4px; font-weight: bold; font-size: 10px; display: inline-block; {badge_color}'>
                    {badge_text}
                </div>
                <table style='width: 100%; font-size: 12px;'>
                    <tr><td>Current Rating:</td><td style='text-align: right; font-weight: bold;'>⭐ {row['rating']}</td></tr>
                    <tr><td>Review Count:</td><td style='text-align: right; font-weight: bold;'>💬 {int(row['total_reviews'])}</td></tr>
                    <tr><td style='{metric_color_style} font-weight: bold;'>{metric_label}</td><td style='text-align: right; font-weight: bold; {metric_color_style}'>{metric_value}</td></tr>
                </table>
            </div>
            """
            folium.Marker(
                [row['lat'], row['lng']],
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=f"Rank #{row['Market_Rank']}: {row['name']}",
                icon=folium.Icon(color=marker_color, icon=map_icon, prefix="fa")
            ).add_to(m)
    
    # Heatmap weight aligns with selected view score
    weight_column = 'Opportunity_Score' if "Find Market Gaps" in view_mode else 'Market_Dominance_Score'
    heat_data = [[row['lat'], row['lng'], row[weight_column]] for _, row in df.iterrows()]
    HeatMap(heat_data, radius=30, blur=18, min_opacity=0.4).add_to(m)
    
    # Display map across the full dashboard container stretch width
    st_folium(m, width=1400, height=500, key="dashboard_map")
    
    st.markdown("---")
    
    # ROW 2 (MIDDLE): Strategic Action Plan Legend Matrix
    st.markdown("### 📋 Dashboard Map Legend Matrix")
    leg_col1, leg_col2, leg_col3, leg_col4 = st.columns(4)
    
    if "Find Market Gaps" in view_mode:
        with leg_col1:
            st.markdown(
                "<div style='padding: 12px; border-radius: 6px; border: 1px solid var(--text-color); border-left: 6px solid #7B1FA2; min-height: 110px;'>"
                "<span style='font-size: 16px;'>🟣</span> <strong>Rank #1: Top Opportunity</strong><br>"
                "<small style='opacity: 0.85;'>Peak volume of active market engagement combined with low satisfaction score performance.</small>"
                "</div>", 
                unsafe_allow_html=True
            )
        with leg_col2:
            st.markdown(
                "<div style='padding: 12px; border-radius: 6px; border: 1px solid var(--text-color); border-left: 6px solid #1976D2; min-height: 110px;'>"
                "<span style='font-size: 16px;'>🔵</span> <strong>Ranks #2-4: Strong Entry</strong><br>"
                "<small style='opacity: 0.85;'>High consumer traffic footprints exhibiting evident performance gaps or operational vulnerabilities.</small>"
                "</div>", 
                unsafe_allow_html=True
            )
        with leg_col3:
            st.markdown(
                "<div style='padding: 12px; border-radius: 6px; border: 1px solid var(--text-color); border-left: 6px solid #388E3C; min-height: 110px;'>"
                "<span style='font-size: 16px;'>🟢</span> <strong>Ranks #5-8: Viable Gap</strong><br>"
                "<small style='opacity: 0.85;'>Moderate traffic areas with review histories indicating clear room for strategic market entry.</small>"
                "</div>", 
                unsafe_allow_html=True
            )
        with leg_col4:
            st.markdown(
                "<div style='padding: 12px; border-radius: 6px; border: 1px solid var(--text-color); border-left: 6px solid #616161; min-height: 110px;'>"
                "<span style='font-size: 16px;'>⚫</span> <strong>Ranks 9+: Low Priority</strong><br>"
                "<small style='opacity: 0.85;'>Establishments with exceptionally high satisfaction records or very low customer interaction volumes.</small>"
                "</div>", 
                unsafe_allow_html=True
            )
    else:
        with leg_col1:
            st.markdown(
                "<div style='padding: 12px; border-radius: 6px; border: 1px solid var(--text-color); border-left: 6px solid #4A148C; min-height: 110px;'>"
                "<span style='font-size: 16px;'>👑</span> <strong>Rank #1: Market Leader</strong><br>"
                "<small style='opacity: 0.85;'>The absolute apex competitor in the territory. Commanding volume with elite reputation management.</small>"
                "</div>", 
                unsafe_allow_html=True
            )
        with leg_col2:
            st.markdown(
                "<div style='padding: 12px; border-radius: 6px; border: 1px solid var(--text-color); border-left: 6px solid #FF9800; min-height: 110px;'>"
                "<span style='font-size: 16px;'>🔸</span> <strong>Ranks #2-4: Premium Tier</strong><br>"
                "<small style='opacity: 0.85;'>Strong, dependable establishments maintaining significant customer traction and solid high ratings.</small>"
                "</div>", 
                unsafe_allow_html=True
            )
        with leg_col3:
            st.markdown(
                "<div style='padding: 12px; border-radius: 6px; border: 1px solid var(--text-color); border-left: 6px solid #5D4037; min-height: 110px;'>"
                "<span style='font-size: 16px;'>🟤</span> <strong>Ranks #5-8: Mainstream Core</strong><br>"
                "<small style='opacity: 0.85;'>Established neighborhood spots holding standard market volume shares with average-to-good ratings.</small>"
                "</div>", 
                unsafe_allow_html=True
            )
        with leg_col4:
            st.markdown(
                "<div style='padding: 12px; border-radius: 6px; border: 1px solid var(--text-color); border-left: 6px solid #9E9E9E; min-height: 110px;'>"
                "<span style='font-size: 16px;'>⚪</span> <strong>Ranks 9+: Micro Players</strong><br>"
                "<small style='opacity: 0.85;'>Low-impact local options, unproven new arrivals, or venues lacking substantial customer feedback.</small>"
                "</div>", 
                unsafe_allow_html=True
            )
          
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ROW 3 (BOTTOM): Full-Width Ranked Competitive Vulnerability Matrix
    st.subheader("📊 Intelligence Analytics Matrix")
    
    # Expanded output array containing all new indicators
    display_columns = [
        'Market_Rank', 'name', 'Strategic_Recommendation', 'rating', 
        'total_reviews', 'price_level', 'Opportunity_Score', 'Premium_Gap_Score', 'Market_Dominance_Score', 'website'
    ]
    
    st.dataframe(
        df[display_columns],
        width="stretch",
        height=400,
        column_config={
            "Market_Rank": st.column_config.NumberColumn("Rank", format="# %d"),
            "name": st.column_config.TextColumn("Establishment Target"),
            "Strategic_Recommendation": st.column_config.TextColumn("Strategic Profile"),
            "rating": st.column_config.NumberColumn("Rating", format="⭐ %.1f"),
            "total_reviews": st.column_config.NumberColumn("Reviews", format="%d 💬"),
            "price_level": st.column_config.NumberColumn("Price Tier", format="💵 %d"),
            "Opportunity_Score": st.column_config.NumberColumn("Quality Gap Index", format="🔴 %.1f"),
            "Premium_Gap_Score": st.column_config.NumberColumn("Value Deficit Index", format="💰 %.1f"),
            "Market_Dominance_Score": st.column_config.NumberColumn("Dominance Index", format="👑 %.1f"),
            "website": st.column_config.LinkColumn("Competitor Site", display_text="Open 🔗")
        },
        hide_index=True
    )