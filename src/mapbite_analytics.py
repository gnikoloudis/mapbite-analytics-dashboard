import googlemaps
import pandas as pd
import numpy as np

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
        print(f"Global Geocoding Error: {e}")
    return None, None

def fetch_and_rank_competitors(map_client, lat, lng, radius, selected_categories, keyword_filter):
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

            places_result = map_client.places_nearby(**search_args)
            results = places_result.get('results', [])
            
            for p in results:
                p_id = p.get('place_id')
                if p_id not in seen_place_ids:
                    seen_place_ids.add(p_id)
                    all_raw_results.append(p)
        except Exception:
            continue

    if not all_raw_results:
        return pd.DataFrame()
        
    processed_restaurants = []
    
    for place in all_raw_results[:20]:
        p_id = place.get('place_id')
        try:
            details = map_client.place(
                place_id=p_id,
                fields=['name', 'rating', 'user_ratings_total', 'price_level', 'website', 'business_status', 'geometry', 'opening_hours']
            ).get('result', {})
            
            if details.get('business_status') == 'OPERATIONAL':
                hours_info = details.get('opening_hours')
                if hours_info is not None and 'open_now' in hours_info:
                    status_text = "🟢 Open" if hours_info['open_now'] else "🔴 Closed"
                else:
                    status_text = "⚪ N/A"
                
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
        except Exception:
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
    
    def assign_strategic_action(rank):
        if rank == 1: return "🥇 Top Market Opportunity"
        elif rank in [2, 3, 4]: return "🥈 Strong Entry Zone"
        elif rank in [5, 6, 7, 8]: return "🥉 Viable Market Gap"
        return "🔹 Low Priority Target"
        
    df['Strategic_Recommendation'] = df['Market_Rank'].apply(assign_strategic_action)
    return df