import streamlit as st
import pandas as pd
import numpy as np
import os
import pydeck as pdk
import plotly.express as px

DATA_URL = (os.path.join(os.getcwd(),"data","Motor_Vehicle_Collisions_-_Crashes.csv"))

st.set_page_config(page_title="NYC Collisions", page_icon="🚦")

st.title("Motor Vehicle Collisions in NYC")
st.markdown("Streamlit Dashboard to analyze motor vehicle collisions in New York City.")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH DATE', "CRASH TIME"]])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash date_crash time': 'date/time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data

st.header("Where are the most people injured?")
injured_people = st.slider("Number of perons injured in vehicular collisions", 0, int(data['number of persons injured'].max()))
st.map(data.query("`number of persons injured` >= @injured_people")[['latitude', 'longitude']].dropna(how="any"))

st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]
st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))

midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=data[['date/time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour+1) %24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < hour+1)
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute':range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 dangerous streets for a type")
select = st.selectbox("Affected type of people", ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("`number of pedestrians injured` >= 1")[["on street name", "number of pedestrians injured"]].sort_values(by=['number of pedestrians injured'], ascending=False).dropna(how='any')[:5])

elif select == 'Cyclists':
    st.write(original_data.query("`number of cyclist injured` >= 1")[["on street name", "number of cyclist injured"]].sort_values(by=['number of cyclist injured'], ascending=False).dropna(how='any')[:5])

elif select == 'Motorists':
    st.write(original_data.query("`number of motorist injured` >= 1")[["on street name", "number of motorist injured"]].sort_values(by=['number of motorist injured'], ascending=False).dropna(how='any')[:5])


if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)

footer="""
<style>
a:link , a:visited{
color: white;
background-color: transparent;
text-decoration: underline;
}
.footer {
display: flex;
justify-content: left;
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: #0E1117;
color: white;
text-align: left;
}
</style>
<div class="footer">
<p>Developed by <a style='text-align: left;' href="https://github.com/horizon3902/" target="_blank">Kshitij Agarkar</a></p>
<a style="margin-left: auto" href="https://github.com/horizon3902/movie-recommender-salsa" data-color-scheme="no-preference: dark; light: light; dark: dark;" aria-label="Watch horizon3902/movie-recommender-salsa on GitHub">View on Github</a>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)
