# from flask import Flask, request, jsonify
# import requests 

# app = Flask(__name__)

# @app.route('/api/set-user-location', methods=['POST'])
# def set_user_location():
#     data = request.json
#     user_lat = data['lattitude']
#     user_lng = data['longitude']

#     session = {}
    
#     # Store user location for trip planning
#     session['user_location'] = {
#         'lattitude': user_lat,
#         'longitude': user_lng
#     }
    
#     return jsonify({'status': 'success', "session": session})



# # Backend route for IP fallback
# # @app.route('/api/ip-location')
# # def get_ip_location():
# #     user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    
# #     # Use free IP geolocation service
# #     response = requests.get(f'http://ip-api.com/json/{user_ip}')
# #     data = response.json()
# #     print(data)
    
# #     return {
# #         'lattitude': data['lat'],
# #         'longitude': data['lon'],
# #         'city': data['city'],
# #         'country': data['country']
# #     }

# if __name__ == "__main__":
#     app.run(debug=True)



loc = "Amalitech, Kumasi, Ghana"

cleaned = loc.strip()

mclean = cleaned.split()
print(mclean[1])