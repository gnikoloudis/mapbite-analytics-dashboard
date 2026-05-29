import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import re
import pandas as pd 
# Import our custom logic modules securely using the unique namespace string
import tracker
import mapbite_analytics as analytics
import matplotlib 

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

# Intercept map interactions smoothly to capture map clicks natively
if "dashboard_map" in st.session_state and st.session_state["dashboard_map"]:
    map_output = st.session_state["dashboard_map"]
    if map_output.get("last_clicked"):
        clicked_lat = map_output["last_clicked"]["lat"]
        clicked_lng = map_output["last_clicked"]["lng"]
        
        if abs(st.session_state.last_lat - clicked_lat) > 0.00001 or abs(st.session_state.last_lng - clicked_lng) > 0.00001:
            st.session_state.last_lat = clicked_lat
            st.session_state.last_lng = clicked_lng
            st.rerun()

# Pre-fetch usage status for blocking buttons if needed
is_under_limit, current_usage = tracker.check_and_increment_tracker(DAILY_MAX_LIMIT)

# ==========================================
# 2. GEOGRAPHIC SIDEBAR SELECTIONS ENGINE
# ==========================================
st.sidebar.header("📍 Target Setup")

# RESTORED: Multi-select Category Options Dropdown
CATEGORY_OPTIONS = {
    "Restaurants 🍔": "restaurant",
    "Cafes ☕": "cafe",
    "Bakeries/Cantines 🥐": "bakery",
    "Bars & Pubs 🍺": "bar",
    "Takeaway / Fast Food 🍕": "takeaway_food"
}

selected_labels = st.sidebar.multiselect(
    "Target Categories:",
    options=list(CATEGORY_OPTIONS.keys()),
    default=["Restaurants 🍔"]
)
selected_categories = [CATEGORY_OPTIONS[lbl] for lbl in selected_labels]

# Restored original keyword variable sub-filter
search_keyword = st.sidebar.text_input(
    "Keyword Sub-Filter:",
    placeholder="e.g., Italian, Sushi, Specialty Coffee, Pizza",
    value="",
    help="Narrow down selected categories to a specific style query."
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
            st.sidebar.error("❌ Could not resolve address. Try verifying the spelling!")
            address_resolved = False
    else:
        st.sidebar.info("💡 Type an address or click anywhere on the map grid layout.")
        address_resolved = False
else:
    # RESTORED: Single string textbox parsing coordinates cleanly
    default_coord_value = f"{st.session_state.last_lat:.7f}, {st.session_state.last_lng:.7f}"
    coord_string = st.sidebar.text_input(
        "Target Coordinates (Lat, Lng):",
        value=default_coord_value,
        help="Pasting coordinates or clicking the map will overwrite this text block instantly."
    )
    
    parsed_coords = re.findall(r"[-+]?\d*\.\d+|\d+", coord_string)
    if len(parsed_coords) >= 2:
        parsed_lat = float(parsed_coords[0])
        parsed_lng = float(parsed_coords[1])
        if abs(st.session_state.last_lat - parsed_lat) > 0.00001 or abs(st.session_state.last_lng - parsed_lng) > 0.00001:
            st.session_state.last_lat = parsed_lat
            st.session_state.last_lng = parsed_lng
    else:
        st.sidebar.error("Format error. Please use: latitude, longitude")
        address_resolved = False

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
                    map_client, st.session_state.last_lat, st.session_state.last_lng, search_radius, selected_categories, search_keyword
                )
                if not df_results.empty:
                    tracker.increment_counter_file(current_usage)
                    st.session_state.analysis_df = df_results
                    st.rerun()
                else:
                    st.warning("📭 No active listings matched your specific category + keyword criteria in this area.")

# Quota tracking progress component
st.sidebar.markdown("---")
st.sidebar.markdown(f"### 📊 App Resource Monitor")
st.sidebar.progress(
    min(current_usage / DAILY_MAX_LIMIT, 1.0), 
    text=f"Daily Limit Usage: {current_usage} / {DAILY_MAX_LIMIT}"
)

# Sidebar metrics documentation panel
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

# RESTORED / FIXED: Map is fully rendered at all times so users can click to select coordinates/epicenter!
st.markdown("### 🛠️ Intelligence Lens Selector")
view_mode = st.radio(
    "Choose Dashboard Analysis Angle:",
    ["🔴 Find Market Gaps & Vulnerabilities (Worst Rated/Highest Traffic)", 
     "👑 Study Market Leaders & Dominance (Best Rated/Highest Traffic)"],
    horizontal=True
)
st.markdown("---")

df = None
if raw_df is not None and not raw_df.empty:
    if 'status' not in raw_df.columns:
        raw_df['status'] = "⚪ N/A"

    if "Find Market Gaps" in view_mode:
        df = raw_df.sort_values(by="Opportunity_Score", ascending=False).reset_index(drop=True)
        df['Market_Rank'] = df.index + 1
        st.metric(label="Peak Opportunity Score", value=f"{df.iloc[0]['Opportunity_Score']} / 15", delta="High Market Gap")
    else:
        df = raw_df.sort_values(by="Market_Dominance_Score", ascending=False).reset_index(drop=True)
        df['Market_Rank'] = df.index + 1
        st.metric(label="Peak Dominance Score", value=f"{df.iloc[0]['Market_Dominance_Score']}", delta="Market Leader to Beat", delta_color="inverse")
else:
    st.info("💡 Map initialization active. Click anywhere on the map or type an address in the sidebar, then run the analysis to view comparative data matrix frames.")

st.markdown("---")

# ROW 1 (TOP): Full-Width Strategic Opportunity / Epicenter Map Selection Grid
st.subheader("🗺️ Strategic Analysis Map")
m = folium.Map(location=[st.session_state.last_lat, st.session_state.last_lng], zoom_start=15)

# Center epicenter pinpoint anchor marker
folium.Marker(
    [st.session_state.last_lat, st.session_state.last_lng],
    popup="📍 <b>Your Proposed Site Core</b>",
    tooltip="Search Epicenter (Click Map to Move Here)",
    icon=folium.Icon(color="red", icon="crosshair", prefix="fa")
).add_to(m)

# Populating points if data frame exists
if df is not None:
    for _, row in df.iterrows():
        if row['lat'] and row['lng']:
            if "Find Market Gaps" in view_mode:
                if row['Market_Rank'] == 1: marker_color, badge_color = "purple", "background-color: #7B1FA2; color: white;"
                elif row['Market_Rank'] in [2, 3, 4]: marker_color, badge_color = "blue", "background-color: #1976D2; color: white;"
                elif row['Market_Rank'] in [5, 6, 7, 8]: marker_color, badge_color = "green", "background-color: #388E3C; color: white;"
                else: marker_color, badge_color = "gray", "background-color: #616161; color: white;"
                
                badge_text = row['Strategic_Recommendation']
                metric_label, metric_value, metric_color_style, map_icon = "Opportunity Index:", row['Opportunity_Score'], "color: #E64A19;", "lightbulb-o"
            else:
                if row['Market_Rank'] == 1: marker_color, badge_color = "darkpurple", "background-color: #4A148C; color: #FFD700; border: 1px solid #FFD700;"
                elif row['Market_Rank'] in [2, 3, 4]: marker_color, badge_color = "orange", "background-color: #FF9800; color: white;"
                elif row['Market_Rank'] in [5, 6, 7, 8]: marker_color, badge_color = "beige", "background-color: #5D4037; color: white;"
                else: marker_color, badge_color = "lightgray", "background-color: #9E9E9E; color: black;"
                
                badge_text = "Market Leader Profile"
                metric_label, metric_value, metric_color_style, map_icon = "Dominance Index:", row['Market_Dominance_Score'], "color: #FF8F00;", "trophy"
            
            row_status = row.get('status', '⚪ N/A')

            popup_html = f"""
            <div style="font-family: 'Arial', sans-serif; width: 230px; padding: 5px;">
                <div style='float: right; font-size: 18px;'>#{row['Market_Rank']}</div>
                <h4 style='margin: 0 0 4px 0; color: #333;'>{row['name']}</h4>
                <div style='margin-bottom: 8px; padding: 3px 6px; border-radius: 4px; font-weight: bold; font-size: 10px; display: inline-block; {badge_color}'>{badge_text}</div>
                <br><small style='color: #666;'>Status: {row_status}</small>
                <table style='width: 100%; font-size: 12px; margin-top: 5px;'>
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
            
    weight_column = 'Opportunity_Score' if "Find Market Gaps" in view_mode else 'Market_Dominance_Score'
    heat_data = [[row['lat'], row['lng'], row[weight_column]] for _, row in df.iterrows()]
    HeatMap(heat_data, radius=30, blur=18, min_opacity=0.4).add_to(m)

# Always render the map object canvas to allow visual epicenter tracking selection updates
st_folium(m, width=1400, height=500, key="dashboard_map")
st.markdown("---")

# Populate tables and legends conditionally if analytics search loop is complete
if df is not None:
    # ROW 2 (MIDDLE): Action Plan & Live Status Legends
    st.markdown("### 📋 Dashboard Map & Operating Schedule Legend Matrix")
    leg_col1, leg_col2, leg_col3, leg_col4 = st.columns(4)
    
    if "Find Market Gaps" in view_mode:
        with leg_col1:
            st.markdown("<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); border-left:6px solid #7B1FA2; min-height:110px;'><strong>🟣 Rank #1: Top Opportunity</strong><br><small>Peak engagement volume combined with lower satisfaction ratings.</small></div>", unsafe_allow_html=True)
        with leg_col2:
            st.markdown("<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); border-left:6px solid #1976D2; min-height:110px;'><strong>🔵 Ranks #2-4: Strong Entry</strong><br><small>High consumer traffic footprints showing clear competitive performance gaps.</small></div>", unsafe_allow_html=True)
        with leg_col3:
            st.markdown("<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); border-left:6px solid #388E3C; min-height:110px;'><strong>🟢 Ranks #5-8: Viable Gap</strong><br><small>Moderate traffic areas with room for strategic market entry optimization.</small></div>", unsafe_allow_html=True)
    else:
        with leg_col1:
            st.markdown("<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); border-left:6px solid #4A148C; min-height:110px;'><strong>👑 Rank #1: Market Leader</strong><br><small>Apex territory competitor. Commanding volume with elite reputation management.</small></div>", unsafe_allow_html=True)
        with leg_col2:
            st.markdown("<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); border-left:6px solid #FF9800; min-height:110px;'><strong>🔸 Ranks #2-4: Premium Tier</strong><br><small>Dependable high-traction establishments maintaining top tier market volume.</small></div>", unsafe_allow_html=True)
        with leg_col3:
            st.markdown("<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); border-left:6px solid #5D4037; min-height:110px;'><strong>🟤 Ranks #5-8: Mainstream Core</strong><br><small>Established standard neighborhood options with healthy market presence.</small></div>", unsafe_allow_html=True)

    with leg_col4:
        st.markdown("<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); background-color:rgba(0,0,0,0.03); min-height:110px;'><strong>⏰ Operational Status Codes</strong><br><small>🟢 <b>Open:</b> Operating right now.<br>🔴 <b>Closed:</b> Closed/Out of hours.<br>⚪ <b>N/A:</b> Google listing lacks hours data.</small></div>", unsafe_allow_html=True)
          
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ROW 3 (BOTTOM): Full-Width Analytical Data Matrix Grid
    st.subheader("📊 Intelligence Analytics Matrix")
    
    # 1. Safely translate numeric price tiers into repeated icon strings
    df['Price_Tier_Icons'] = df['price_level'].apply(
        lambda x: "💵" * int(max(1, min(4, x))) if pd.notnull(x) else "💵💵"
    )
    
    # 2. Dynamic Status Bullets: Calculate thresholds and apply Green/Amber/Red logic
    # Quality Gap Index (Opportunity_Score) color thresholds
    max_opp = df['Opportunity_Score'].max() if not df.empty else 1
    df['Opp_Icon'] = df['Opportunity_Score'].apply(
        lambda x: "🔴" if x > (max_opp * 0.6) else ("🟠" if x > (max_opp * 0.3) else "🟢")
    )
    
    # Value Deficit Index (Premium_Gap_Score) color thresholds
    max_prem = df['Premium_Gap_Score'].max() if not df.empty else 1
    df['Prem_Icon'] = df['Premium_Gap_Score'].apply(
        lambda x: "🔴" if x > (max_prem * 0.6) else ("🟠" if x > (max_prem * 0.3) else "🟢")
    )
    
    # Dominance Index (Market_Dominance_Score) color thresholds (Higher is better -> Green)
    max_dom = df['Market_Dominance_Score'].max() if not df.empty else 1
    df['Dom_Icon'] = df['Market_Dominance_Score'].apply(
        lambda x: "🟢" if x > (max_dom * 0.6) else ("🟠" if x > (max_dom * 0.3) else "🔴")
    )
    
    # 3. Create display strings joining the status bullet and the float value
    df['Quality_Gap_Display'] = df.apply(lambda r: f"{r['Opp_Icon']} {r['Opportunity_Score']:.1f}", axis=1)
    df['Value_Deficit_Display'] = df.apply(lambda r: f"{r['Prem_Icon']} {r['Premium_Gap_Score']:.1f}", axis=1)
    df['Dominance_Display'] = df.apply(lambda r: f"{r['Dom_Icon']} {r['Market_Dominance_Score']:.1f}", axis=1)
    
    # 4. Re-map the visualization display data columns array sequence
    display_columns = [
        'Market_Rank', 'name', 'status', 'Strategic_Recommendation', 
        'rating', 'total_reviews', 'Price_Tier_Icons', 
        'Quality_Gap_Display', 'Value_Deficit_Display', 'Dominance_Display', 'website'
    ]
    
    # 5. Render the data table frame using clean, decoupled text columns
    st.dataframe(
        df[display_columns],
        width="stretch",
        height=400,
        column_config={
            "Market_Rank": st.column_config.NumberColumn("Rank", format="# %d"),
            "name": st.column_config.TextColumn("Establishment"),
            "status": st.column_config.TextColumn("Operational Status"),
            "Strategic_Recommendation": st.column_config.TextColumn("Strategic Profile"),
            "rating": st.column_config.NumberColumn("Rating", format="%.1f"),
            "total_reviews": st.column_config.NumberColumn("Reviews", format="%d"),
            "Price_Tier_Icons": st.column_config.TextColumn("Price Tier"),
            "Quality_Gap_Display": st.column_config.TextColumn("Quality Gap Index"),
            "Value_Deficit_Display": st.column_config.TextColumn("Value Deficit Index"),
            "Dominance_Display": st.column_config.TextColumn("Dominance Index"),
            "website": st.column_config.LinkColumn("Site Link", display_text="Open 🔗")
        },
        hide_index=True
    )