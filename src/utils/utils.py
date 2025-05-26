from math import radians, sin, cos, sqrt, atan2

# Haversine formula to calculate distance
def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    radius_km = 6371
    return radius_km * c



def sort_location_by_distance(locations):
    sorted_locations = sorted(locations, key=lambda x: x["distance_from_user_km"])
    return sorted_locations
# print(haversine_distance(lat1, lon1, lat2, lon2))