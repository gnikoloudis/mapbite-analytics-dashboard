# Import custom modules
import tracker
import mapbite_analytics as analytics
from config_lang import LANG_DICT  
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import re
import pandas as pd 
import logging

# ==========================================
# 0. CONSOLE LOGGING ENGINE CONFIGURATION
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()] # Sent exclusively to standard output (Console Only)
)
logger = logging.getLogger("mapbite")

# ==========================================
# 1. UI INITIALIZATION & PLATFORM TOKENS
# ==========================================
st.set_page_config(
    page_title="MapBite - Competitor Intelligence Dashboard",
    page_icon="🍔",
    layout="wide"
)

# Handle API Key validation
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    map_client = analytics.get_map_client(API_KEY)
else:
    st.error("🔑 Google API Key missing! Please configure GOOGLE_API_KEY inside your Streamlit secrets.")
    st.stop()

# DYNAMIC CONFIG: Fetch Daily Cap Limit directly from Streamlit Secrets
DAILY_MAX_LIMIT = st.secrets.get("DAILY_MAX_LIMIT", 5)
ALL_RAW_RESULTS_LIMIT = st.secrets.get("ALL_RAW_RESULTS_LIMIT", 20)

# Initialize dynamic session states with the NEW default coordinates
if "analysis_df" not in st.session_state:
    st.session_state.analysis_df = None
if "last_lat" not in st.session_state:
    st.session_state.last_lat = 37.9714787
if "last_lng" not in st.session_state:
    st.session_state.last_lng = 23.7265527

# Pre-fetch usage status for blocking buttons if needed
is_under_limit, current_usage = tracker.check_and_increment_tracker(DAILY_MAX_LIMIT)

# ==========================================
# 2. LOCALIZATION RESOLVER & MAP INTERCEPT
# ==========================================
with st.sidebar:
    selected_lang = st.selectbox(
        "🌐 Language / Γλώσσα",
        options=["English", "Ελληνικά"],
        index=0
    )
    lang_code = "en" if selected_lang == "English" else "el"

t = LANG_DICT[lang_code]

# Safety check: Ensure the radio key state matches the currently active language options
if "loc_radio_key" in st.session_state:
    if st.session_state["loc_radio_key"] not in t["loc_mode_opt"]:
        st.session_state["loc_radio_key"] = t["loc_mode_opt"][0]

# Intercept map interactions smoothly to capture map clicks natively
if "dashboard_map" in st.session_state and st.session_state["dashboard_map"]:
    map_output = st.session_state["dashboard_map"]
    if map_output.get("last_clicked"):
        clicked_lat = map_output["last_clicked"]["lat"]
        clicked_lng = map_output["last_clicked"]["lng"]
        
        if abs(st.session_state.last_lat - clicked_lat) > 0.00001 or abs(st.session_state.last_lng - clicked_lng) > 0.00001:
            st.session_state.last_lat = clicked_lat
            st.session_state.last_lng = clicked_lng
            # Automatically switch the sidebar input to "Coordinates" mode
            st.session_state["loc_radio_key"] = t["loc_mode_opt"][1]
            st.rerun()

# Render primary text headers using the active language configuration
st.title(t["title"])
st.markdown(t["subtitle"])

# ==========================================
# 3. GEOGRAPHIC SIDEBAR SELECTIONS ENGINE
# ==========================================
st.sidebar.header(t["sidebar_settings"])

CATEGORY_OPTIONS = t["categories_opt"]

selected_labels = st.sidebar.multiselect(
    t["categories_title"],
    options=list(CATEGORY_OPTIONS.keys()),
    default=[list(CATEGORY_OPTIONS.keys())[0]]
)
selected_categories = [CATEGORY_OPTIONS[lbl] for lbl in selected_labels]

search_keyword = st.sidebar.text_input(
    t["keyword_lbl"],
    placeholder=t["keyword_ph"],
    value="",
    help=t["keyword_help"]
)

# Bind the radio button to the session_state so the map click can control it dynamically
input_mode = st.sidebar.radio(
    t["loc_mode_lbl"],
    t["loc_mode_opt"],
    key="loc_radio_key"
)

address_resolved = True

if input_mode == t["loc_mode_opt"][0]:
    address_string = st.sidebar.text_input(t["addr_lbl"], placeholder=t["addr_ph"])
    
    if address_string:
        lat, lng = analytics.resolve_address(map_client, address_string)
        if lat and lng:
            st.session_state.last_lat, st.session_state.last_lng = lat, lng
            st.sidebar.success(f"{t['addr_success']} `{lat:.5f}, {lng:.5f}`")
        else:
            st.sidebar.error(t["addr_error"])
            address_resolved = False
    else:
        st.sidebar.info(t["addr_info"])
        address_resolved = False
else:
    default_coord_value = f"{st.session_state.last_lat:.7f}, {st.session_state.last_lng:.7f}"
    coord_string = st.sidebar.text_input(
        t["coord_lbl"],
        value=default_coord_value,
        help=t["coord_help"]
    )
    
    parsed_coords = re.findall(r"[-+]?\d*\.\d+|\d+", coord_string)
    if len(parsed_coords) >= 2:
        parsed_lat = float(parsed_coords[0])
        parsed_lng = float(parsed_coords[1])
        if abs(st.session_state.last_lat - parsed_lat) > 0.00001 or abs(st.session_state.last_lng - parsed_lng) > 0.00001:
            st.session_state.last_lat = parsed_lat
            st.session_state.last_lng = parsed_lng
    else:
        st.sidebar.error(t["coord_error"])
        address_resolved = False

search_radius = st.sidebar.slider(t["radius_lbl"], min_value=200, max_value=3000, value=1000, step=100)

# Execution trigger hooks
if address_resolved:
    if not is_under_limit:
        st.sidebar.error(t["limit_reached"])
        st.sidebar.button(t["btn_run"], disabled=True, width="stretch")
    else:
        if st.sidebar.button(t["btn_run"], width="stretch"):
            logger.info(f"🚀 User requested analytics search around footprint epicenter: {st.session_state.last_lat}, {st.session_state.last_lng}")
            with st.spinner(t["btn_spinner"]):
                df_results = analytics.fetch_and_rank_competitors(
                        map_client, st.session_state.last_lat, st.session_state.last_lng, search_radius, selected_categories, search_keyword, t, ALL_RAW_RESULTS_LIMIT)
                if not df_results.empty:
                    tracker.increment_counter_file(current_usage)
                    st.session_state.analysis_df = df_results
                    st.rerun()
                else:
                    st.warning(t["no_results"])

# Quota tracking progress component
st.sidebar.markdown("---")
st.sidebar.markdown(t["resource_lbl"])
st.sidebar.progress(
    min(current_usage / DAILY_MAX_LIMIT, 1.0), 
    text=f"{t['limit_lbl']} {current_usage} / {DAILY_MAX_LIMIT}"
)

# Sidebar metrics documentation panel
st.sidebar.markdown("---")
st.sidebar.markdown(t["metric_panel_lbl"])
st.sidebar.markdown(t["metric_panel_text"])

# ==========================================
# 4. RESULTS VIEW DASHBOARD GENERATION
# ==========================================
raw_df = st.session_state.analysis_df

st.markdown(t["lens_lbl"])
view_mode = st.radio(
    t["lens_choices_title"],
    t["lens_choices"],
    horizontal=True,
    index=0,
    label_visibility="collapsed"
)
st.markdown("---")

df = None
if raw_df is not None and not raw_df.empty:
    if 'status' not in raw_df.columns:
        raw_df['status'] = "⚪ N/A"

    if t["find_market_gaps"] in view_mode:
        df = raw_df.sort_values(by="Opportunity_Score", ascending=False).reset_index(drop=True)
        df['Market_Rank'] = df.index + 1
        st.metric(label=t["peak_opp_lbl"], value=f"{df.iloc[0]['Opportunity_Score']} / 15", delta=t["peak_opp_delta"])
    else:
        df = raw_df.sort_values(by="Market_Dominance_Score", ascending=False).reset_index(drop=True)
        df['Market_Rank'] = df.index + 1
        st.metric(label=t["peak_dom_lbl"], value=f"{df.iloc[0]['Market_Dominance_Score']}", delta=t["peak_dom_delta"], delta_color="inverse")
else:
    st.info(t["map_init_info"])

st.markdown("---")

# ROW 1 (TOP): Full-Width Strategic Opportunity Map Selection Grid
st.subheader(t["map_title"])
m = folium.Map(location=[st.session_state.last_lat, st.session_state.last_lng], zoom_start=15)

folium.Marker(
    [st.session_state.last_lat, st.session_state.last_lng],
    popup=t["map_epicenter_pop"],
    tooltip=t["map_epicenter_tt"],
    icon=folium.Icon(color="red", icon="crosshair", prefix="fa")
).add_to(m)

if df is not None:
    for _, row in df.iterrows():
        if row['lat'] and row['lng']:
            if t["find_market_gaps"] in view_mode:
                if row['Market_Rank'] == 1: marker_color, badge_color = "purple", "background-color: #7B1FA2; color: white;"
                elif row['Market_Rank'] in [2, 3, 4]: marker_color, badge_color = "blue", "background-color: #1976D2; color: white;"
                elif row['Market_Rank'] in [5, 6, 7, 8]: marker_color, badge_color = "green", "background-color: #388E3C; color: white;"
                else: marker_color, badge_color = "gray", "background-color: #616161; color: white;"
                
                badge_text = row['Strategic_Recommendation']
                metric_label, metric_value, metric_color_style, map_icon = t["map_popup_opp_idx"], row['Opportunity_Score'], "color: #E64A19;", "lightbulb-o"
            else:
                if row['Market_Rank'] == 1: marker_color, badge_color = "darkpurple", "background-color: #4A148C; color: #FFD700; border: 1px solid #FFD700;"
                elif row['Market_Rank'] in [2, 3, 4]: marker_color, badge_color = "orange", "background-color: #FF9800; color: white;"
                elif row['Market_Rank'] in [5, 6, 7, 8]: marker_color, badge_color = "beige", "background-color: #5D4037; color: white;"
                else: marker_color, badge_color = "lightgray", "background-color: #9E9E9E; color: black;"
                
                badge_text = "Market Leader Profile" if lang_code == "en" else "Προφίλ Ηγέτη Αγοράς"
                metric_label, metric_value, metric_color_style, map_icon = t["map_popup_dom_idx"], row['Market_Dominance_Score'], "color: #FF8F00;", "trophy"
            
            row_status = row.get('status', '⚪ N/A')

            popup_html = f"""
            <div style="font-family: 'Arial', sans-serif; width: 230px; padding: 5px;">
                <div style='float: right; font-size: 18px;'>#{row['Market_Rank']}</div>
                <h4 style='margin: 0 0 4px 0; color: #333;'>{row['name']}</h4>
                <div style='margin-bottom: 8px; padding: 3px 6px; border-radius: 4px; font-weight: bold; font-size: 10px; display: inline-block; {badge_color}'>{badge_text}</div>
                <br><small style='color: #666;'>{t['map_popup_status']}: {row_status}</small>
                <table style='width: 100%; font-size: 12px; margin-top: 5px;'>
                    <tr><td>{t['map_popup_rating']}</td><td style='text-align: right; font-weight: bold;'>⭐ {row['rating']}</td></tr>
                    <tr><td>{t['map_popup_reviews']}</td><td style='text-align: right; font-weight: bold;'>💬 {int(row['total_reviews'])}</td></tr>
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
            
    weight_column = 'Opportunity_Score' if (t["find_market_gaps"] in view_mode) else 'Market_Dominance_Score'
    heat_data = [[row['lat'], row['lng'], row[weight_column]] for _, row in df.iterrows()]
    HeatMap(heat_data, radius=30, blur=18, min_opacity=0.4).add_to(m)

st_folium(m, width=1400, height=500, key="dashboard_map")
st.markdown("---")

if df is not None:
    # ROW 2 (MIDDLE): Action Plan & Live Status Legends
    st.markdown(t["legend_title"])
    leg_col1, leg_col2, leg_col3, leg_col4 = st.columns(4)
    
    if t["find_market_gaps"] in view_mode:
        with leg_col1:
            st.markdown(f"<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); border-left:6px solid #7B1FA2; min-height:110px;'>{t['leg1_gap']}</div>", unsafe_allow_html=True)
        with leg_col2:
            st.markdown(f"<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); border-left:6px solid #1976D2; min-height:110px;'>{t['leg2_gap']}</div>", unsafe_allow_html=True)
        with leg_col3:
            st.markdown(f"<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); border-left:6px solid #388E3C; min-height:110px;'>{t['leg3_gap']}</div>", unsafe_allow_html=True)
    else:
        with leg_col1:
            st.markdown(f"<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); border-left:6px solid #4A148C; min-height:110px;'>{t['leg1_dom']}</div>", unsafe_allow_html=True)
        with leg_col2:
            st.markdown(f"<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); border-left:6px solid #FF9800; min-height:110px;'>{t['leg2_dom']}</div>", unsafe_allow_html=True)
        with leg_col3:
            st.markdown(f"<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); border-left:6px solid #5D4037; min-height:110px;'>{t['leg3_dom']}</div>", unsafe_allow_html=True)

    with leg_col4:
        st.markdown(f"<div style='padding:12px; border-radius:6px; border:1px solid var(--text-color); background-color:rgba(0,0,0,0.03); min-height:110px;'>{t['leg_hours']}</div>", unsafe_allow_html=True)
          
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ROW 3 (BOTTOM): Full-Width Analytical Data Matrix Grid
    st.subheader(t["matrix_title"])
    
    df['Price_Tier_Icons'] = df['price_level'].apply(
        lambda x: "💵" * int(max(1, min(4, x))) if pd.notnull(x) else "💵💵"
    )
    
    max_opp = df['Opportunity_Score'].max() if not df.empty else 1
    df['Opp_Icon'] = df['Opportunity_Score'].apply(
        lambda x: "🔴" if x > (max_opp * 0.6) else ("🟠" if x > (max_opp * 0.3) else "🟢")
    )
    max_prem = df['Premium_Gap_Score'].max() if not df.empty else 1
    df['Prem_Icon'] = df['Premium_Gap_Score'].apply(
        lambda x: "🔴" if x > (max_prem * 0.6) else ("🟠" if x > (max_prem * 0.3) else "🟢")
    )
    max_dom = df['Market_Dominance_Score'].max() if not df.empty else 1
    df['Dom_Icon'] = df['Market_Dominance_Score'].apply(
        lambda x: "🟢" if x > (max_dom * 0.6) else ("🟠" if x > (max_dom * 0.3) else "🔴")
    )
    
    df['Quality_Gap_Display'] = df.apply(lambda r: f"{r['Opp_Icon']} {r['Opportunity_Score']:.1f}", axis=1)
    df['Value_Deficit_Display'] = df.apply(lambda r: f"{r['Prem_Icon']} {r['Premium_Gap_Score']:.1f}", axis=1)
    df['Dominance_Display'] = df.apply(lambda r: f"{r['Dom_Icon']} {r['Market_Dominance_Score']:.1f}", axis=1)
    
    display_columns = [
        'Market_Rank', 'name', 'status', 'Strategic_Recommendation', 
        'rating', 'total_reviews', 'Price_Tier_Icons', 
        'Quality_Gap_Display', 'Value_Deficit_Display', 'Dominance_Display', 'website'
    ]
    
    st.dataframe(
        df[display_columns],
        width="stretch",
        height=400,
        column_config={
            "Market_Rank": st.column_config.NumberColumn(t["col_rank"], format="# %d"),
            "name": st.column_config.TextColumn(t["col_establishment"]),
            "status": st.column_config.TextColumn(t["col_status"]),
            "Strategic_Recommendation": st.column_config.TextColumn(t["col_profile"]),
            "rating": st.column_config.NumberColumn(t["col_rating"], format="%.1f"),
            "total_reviews": st.column_config.NumberColumn(t["col_reviews"], format="%d"),
            "Price_Tier_Icons": st.column_config.TextColumn(t["col_price"]),
            "Quality_Gap_Display": st.column_config.TextColumn(t["col_gap"]),
            "Value_Deficit_Display": st.column_config.TextColumn(t["col_deficit"]),
            "Dominance_Display": st.column_config.TextColumn(t["col_dom"]),
            "website": st.column_config.LinkColumn(t["col_site"], display_text=t["col_site_btn"])
        },
        hide_index=True
    )
    # Calculates the total Open, Permanently Closed, and Temporarily Closed counts based on the 'status' column in the dataframe and displays them as an info box below the table for a quick market status overview. This provides users
    if df is not None and 'status' in df.columns:

        perm_closed_count = df[df['status'] == t["status_perm_closed"]].shape[0]
        temp_closed_count = df[df['status'] == t["status_temp_closed"]].shape[0]

        total_open_count = df[df['status'] == t["status_open"]].shape[0]
        total_closed_count = df[df['status'] == t["status_closed"]].shape[0]
        
        total_na_count = df[df['status'] == t["status_na"]].shape[0]

        total_in_business = total_open_count + total_closed_count
        total_out_of_business = perm_closed_count
        

        st.markdown("---")
        # Create three columns for a dashboard effect
        col1, col2, col3,col4 = st.columns(4)
    
        # Use st.metric for an "immersive" dashboard look
        col1.metric(label=f"{t['in_business']}", value=total_in_business)
        col2.metric(label=f"{t['status_temp_closed']}", value=temp_closed_count)        
        col3.metric(label=f"{t['out_of_business']}", value=total_out_of_business)
        col4.metric(label=f"{t['status_na']}", value=total_na_count)

            
        
    #    st.info(f"ℹ️ **Market Status Summary:** {total_in_business} {t['in_business']},  {total_out_of_business} {t['out_of_business']} , {total_na_count} {t['status_na']}")
    
    # ROW 4: Methodology / Transparency Section (NEW)
    st.markdown("---")
    st.subheader(t["method_title"])
    st.markdown(t["method_text"])
    
    st.markdown("---")
