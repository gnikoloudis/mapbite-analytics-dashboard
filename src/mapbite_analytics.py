import googlemaps
import pandas as pd
import numpy as np

def get_map_client(api_key):
    """Initializes the connection client instance."""
    return googlemaps.Client(key=api_key)

def resolve_address(map_client, address_string):
    """
    Translates any plain-text address string globally into precise Lat/Lng coordinates.
    Uses region biasing to resolve local ambiguities without breaking global queries.
    """
    try:
        search_query = address_string.strip()
        if not search_query:
            return None, None
            
        geocode_result = map_client.geocode(search_query, region="gr")
        if geocode_result:
            location_data = geocode_result[0]['geometry']['location']
            return location_data['lat'], location_data['lng']
            
    except Exception as e:
        print(f"Global Geocoding Error: {e}")
    return None, None

def fetch_and_rank_competitors(map_client, lat, lng, radius, cuisine_preference):
    """
    Queries Google Places, filters by target cuisine, details profiles,
    and returns a sorted DataFrame based on recommendation scoring.
    """
    # Build search keyword dynamically based on user cuisine input
    search_keyword = 'restaurant'
    if cuisine_preference.strip():
        search_keyword = f"{cuisine_preference.strip()} restaurant"

    # 1. Nearby search query
    places_result = map_client.places_nearby(
        location=(lat, lng),
        radius=radius,
        keyword=search_keyword
    )
    raw_results = places_result.get('results', [])
    
    if not raw_results:
        return pd.DataFrame()
        
    processed_restaurants = []
    
    # 2. Detailed profile processing loop (Capped to 20 for API budget protection)
    for place in raw_results[:20]:
        p_id = place.get('place_id')
        try:
            details = map_client.place(
                place_id=p_id,
                fields=['name', 'rating', 'user_ratings_total', 'price_level', 'website', 'business_status', 'geometry']
            ).get('result', {})
            
            if details.get('business_status') == 'OPERATIONAL':
                processed_restaurants.append({
                    'name': details.get('name', 'Unknown Restaurant'),
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
    
    # NEW ALIGNED FORMULA: Exponentially rewards poor ratings in high-traffic zones
    # Ensure price_level is numeric, default missing to a baseline of 2 (mid-range)
    df['price_level'] = pd.to_numeric(df['price_level'], errors='coerce').fillna(2)

    # 1. Base Opportunity Score (Quality Gap - Your original)
    df['Opportunity_Score'] = np.log1p(df['total_reviews']) * ((5.0 - df['rating']) ** 2)
    df['Opportunity_Score'] = df['Opportunity_Score'].round(1)

    # 2. Premium Gap Score (Value Deficit - Your original)
    df['Premium_Gap_Score'] = df['Opportunity_Score'] * (df['price_level'] / 2.0)
    df['Premium_Gap_Score'] = df['Premium_Gap_Score'].round(1)

    # ADD THIS 3. Market Dominance Score (The Absolute Best Competitors)
    df['Market_Dominance_Score'] = np.log1p(df['total_reviews']) * df['rating']
    df['Market_Dominance_Score'] = df['Market_Dominance_Score'].round(1)
    
    # Re-sort hierarchy based on new alignment
    df = df.sort_values(by='Opportunity_Score', ascending=False).reset_index(drop=True)
    df['Market_Rank'] = df.index + 1
    
    # Fixed matching assignments to pair perfectly with your Streamlit UI tabs
    def assign_strategic_action(rank):
        if rank == 1: return "🥇 Top Market Opportunity"
        elif rank in [2, 3, 4]: return "🥈 Strong Entry Zone"
        elif rank in [5, 6, 7, 8]: return "🥉 Viable Market Gap"
        return "🔹 Low Priority Target"
        
    df['Strategic_Recommendation'] = df['Market_Rank'].apply(assign_strategic_action)
    return df