import googlemaps
import pandas as pd
import numpy as np
import logging

# Set up module-level logging to output straight to the console stream
logger = logging.getLogger("mapbite")

def get_map_client(api_key):
    return googlemaps.Client(key=api_key)

def resolve_address(map_client, address_string):
    try:
        search_query = address_string.strip()
        if not search_query: return None, None
        geocode_result = map_client.geocode(search_query, region="gr")
        if geocode_result:
            location_data = geocode_result[0]['geometry']['location']
            return location_data['lat'], location_data['lng']
    except Exception as e:
        logger.error(f"💥 Global Geocoding API Error: {e}", exc_info=True)
    return None, None

def fetch_and_rank_competitors(map_client, lat, lng, radius, selected_categories, keyword_filter, t, ALL_RAW_RESULTS_LIMIT=20):
    if not selected_categories:
        return pd.DataFrame()

    all_raw_results = []
    seen_place_ids = set()
    cleaned_keyword = keyword_filter.strip() if keyword_filter else None

    for category in selected_categories:
        try:
            search_args = {
                "location": (lat, lng),
                "radius": radius,
                "type": category
            }
            if cleaned_keyword:
                search_args["keyword"] = cleaned_keyword

            logger.info(f"📡 Sending places_nearby request for category: '{category}', keyword: '{cleaned_keyword}'")
            places_result = map_client.places_nearby(**search_args)
            results = places_result.get('results', [])
            logger.info(f"✅ Received {len(results)} raw items for category: '{category}'")
            
            for p in results:
                p_id = p.get('place_id')
                if p_id not in seen_place_ids:
                    seen_place_ids.add(p_id)
                    all_raw_results.append(p)
        except Exception as e:
            # Prints full Google Maps API error response strings directly into your terminal logs
            logger.error(f"❌ Google Maps places_nearby API failure for category '{category}': {e}", exc_info=True)
            continue

    if not all_raw_results:
        logger.warning("📭 Cumulative search across selected categories yielded 0 raw results.")
        return pd.DataFrame()
        
    processed_restaurants = []
    logger.info(f"🔍 Hydrating place profiles for top {min(ALL_RAW_RESULTS_LIMIT, len(all_raw_results))} establishments...")
    
    for place in all_raw_results[:ALL_RAW_RESULTS_LIMIT]:
        p_id = place.get('place_id')
        try:
            details = map_client.place(
                place_id=p_id,
                fields=['name', 'rating', 'user_ratings_total', 'price_level', 'website', 'business_status', 'geometry', 'opening_hours']
            ).get('result', {})

            # Bilingual status logic
            b_status = details.get('business_status')
            hours_info = details.get('opening_hours')
            
            if b_status == 'CLOSED_PERMANENTLY':
                status_text = t["status_perm_closed"]
            elif b_status == 'CLOSED_TEMPORARILY':
                status_text = t["status_temp_closed"]
            elif b_status == 'OPERATIONAL':
                if hours_info and 'open_now' in hours_info:
                    status_text = t["status_open"] if hours_info['open_now'] else t["status_closed"]
                else:
                    status_text = t["status_na"]
            else:
                status_text = t["status_na"]
                
            processed_restaurants.append({
                'name': details.get('name', 'Unknown Establishment'),
                'status': status_text,
                'lat': details.get('geometry', {}).get('location', {}).get('lat'),
                'lng': details.get('geometry', {}).get('location', {}).get('lng'),
                'rating': details.get('rating', 0.0),
                'total_reviews': details.get('user_ratings_total', 0),
                'price_level': details.get('price_level', 2),
                'website': details.get('website', '')
            })
        except Exception as e:
            logger.error(f"❌ Google Maps place details lookup failure for place ID '{p_id}': {e}", exc_info=True)
            continue

    df = pd.DataFrame(processed_restaurants)
    if df.empty:
        return df

    df['rating'] = df['rating'].fillna(0)
    df['total_reviews'] = df['total_reviews'].fillna(0)
    df['price_level'] = pd.to_numeric(df['price_level'], errors='coerce').fillna(2)

    df['Opportunity_Score'] = np.log1p(df['total_reviews']) * ((5.0 - df['rating']) ** 2)
    df['Opportunity_Score'] = df['Opportunity_Score'].round(1)

    df['Premium_Gap_Score'] = df['Opportunity_Score'] * (df['price_level'] / 2.0)
    df['Premium_Gap_Score'] = df['Premium_Gap_Score'].round(1)

    df['Market_Dominance_Score'] = np.log1p(df['total_reviews']) * df['rating']
    df['Market_Dominance_Score'] = df['Market_Dominance_Score'].round(1)
    
    df = df.sort_values(by='Opportunity_Score', ascending=False).reset_index(drop=True)
    df['Market_Rank'] = df.index + 1
    
    def assign_strategic_action(rank, t):
        if rank == 1: return t["strat_rank_1"]
        elif rank in [2, 3, 4]: return t["strat_rank_2"]
        elif rank in [5, 6, 7, 8]: return t["strat_rank_3"]
        return t["strat_rank_4"]
    
    df['Strategic_Recommendation'] = df['Market_Rank'].apply(lambda x: assign_strategic_action(x, t))
    
    return df