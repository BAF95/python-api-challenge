# Dependencies and Setup
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import requests
import gmaps
import os
g_key = "AIzaSyA0NkEcEvIrOXoRNQb2K5H_dpn0q-knM9Q"


file_to_load= "Resources\cities.csv"
city_data=pd.read_csv(file_to_load)
city_data.head()

max_hum=city_data['Humidity (%)'].max()
max_hum
gmaps.configure(api_key=g_key)

# Store 'Lat' and 'Lng' into  locations:
city_data = city_data.dropna()  # drop NaN values
locations = city_data[['Lat', 'Lng']].astype(float)

# Convert humidity level to float and store:
humidity_rate = city_data['Humidity (%)'].astype(float)

# Create a humidity heat map layer:
fig = gmaps.figure()

heat_layer = gmaps.heatmap_layer(locations, weights=humidity_rate,
                                 dissipating=False, max_intensity=max_hum,
                                 point_radius=3)

fig.add_layer(heat_layer)
fig


# Create new data frame with requested weather conditions:
city_data_narrow = city_data[(city_data['Max Temp (F)'] < 80) &
                             (city_data['Max Temp (F)'] > 65) &
                             (city_data['Wind Speed (mph)'] < 10) &
                             (city_data['Cloudiness (%)'] < 15) &
                             (city_data['Humidity (%)'] < 30)]
city_data_narrow = city_data_narrow.dropna()  # drop any rows will null values
city_data_narrow.count()

# Set up lists to hold response info:
name = []  # list for hotel name
city = []  # list for hotel city
country = []  # list for hotel country
lat = []  # list for hotel latitude
lng = []  # list for hotel longitude

# Loop through the list of cities and perform a request for data on each and add to corresponding lists:

count = 1  # set counter to start value 1 for printouts of the current set count

print('Beginning Data Retrieval')
print('-----------------------------')
for i in range(len(city_data_narrow)):

    lati = str(city_data_narrow.iloc[i, 3])
    lngi = str(city_data_narrow.iloc[i, 4])

    target_coordinates = lati + ', ' + lngi
    target_search = 'Hotel'
    target_radius = 5000
    target_type = 'lodging'

    # Set up a parameters dictionary:
    params = {
        'location': target_coordinates,
        'keyword': target_search,
        'radius': target_radius,
        'type': target_type,
        'key': g_key
    }

    # Base url:
    base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

    # Run a request using the above params dictionary:
    response = requests.get(base_url, params=params)
    # print(response.url)

    # Convert response to json:
    places_data = response.json()
    # print(json.dumps(places_data, indent=4, sort_keys=True))

    # Print user feedback:
    print(
        'Looking for Hotels near: ' + str(city_data_narrow.iloc[i, 0]) + ' | Record ' + str(count) + ' of Total ' + str(
            len(city_data_narrow)))

    # Add requested data to  result lists:
    try:  # ignore errors in response
        name.append(places_data['results'][0]['name'])
        city.append(city_data_narrow.iloc[i, 0])
        country.append(city_data_narrow.iloc[i, 1])
        lat.append(places_data['results'][0]['geometry']['location']['lat'])
        lng.append(places_data['results'][0]['geometry']['location']['lng'])
    except IndexError:
        print(
            'No Hotel Near Location... Skipping...')  # in case one of the responses comes back with error "IndexError"
        # which could be no hotel near location

    count = count + 1

# Print Ending Log Statement:
print('-------------------------------')
print('Data Retrieval Complete')
print('-------------------------------')

# NOTE: Do not change any of the code in this cell.
hotel_dict={
    'City': city,
    'Country': country,
    'Lat': lat,
    'Lng': lng,
    'Hotel Name': name
}
hotel_df=pd.DataFrame(hotel_dict)
hotel_df.count()
# Using the template add the hotel marks to the heatmap:
info_box_template = """
<dl>
<dt>Name</dt><dd>{Hotel Name}</dd>
<dt>City</dt><dd>{City}</dd>
<dt>Country</dt><dd>{Country}</dd>
</dl>
"""
# Store the DataFrame Row:
# NOTE: be sure to update with your DataFrame name!
hotel_info = [info_box_template.format(**row) for index, row in hotel_df.iterrows()]
locations = hotel_df[['Lat', 'Lng']]

# Customize the size of the figure:
figure_layout = {
    'width': '955px',
    'height': '600px',
    'border': '1px solid black',
    'padding': '1px',
    'margin': '0 auto 0 auto'
}
fig = gmaps.figure(layout=figure_layout)

# Assign the marker layer to a variable:
markers = gmaps.marker_layer(locations, info_box_content=hotel_info)
# Add the layer to the map:
fig.add_layer(markers)
fig


# Create a combined map:
fig = gmaps.figure()

fig.add_layer(heat_layer)
fig.add_layer(markers)

fig