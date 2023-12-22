import pandas as pd
from scipy.spatial.distance import cityblock
from IPython.display import Audio

import streamlit as st
import requests

RAPIDAPI_KEY = '911e96e948msh6d580b260974a79p14c3a5jsnadedb18c43ed'
RAPIDAPI_HOST = 'spotify-web2.p.rapidapi.com'
API_ENDPOINT = 'https://spotify-web2.p.rapidapi.com/search/'


df = pd.read_pickle('new_dataset.pkl')


rec = pd.read_pickle('rec_dataset.pkl')

st.set_page_config(
    page_title="Song Recommendation System",
    page_icon="🎵",
    layout="centered"
)

def recommend_manhattan_distance(df, track_name, num_recommendations):
    # if track_name not in df['track_name'].values:
    #     # If the track is not found, recommend N songs by combined popularity
    #     top_recommendations = df.sort_values(by='combined_popularity', ascending=False).head(num_recommendations)
    #     return top_recommendations[['track_name']]
    
    target_song = df[df['track_name'] == track_name].iloc[0, 2:]  # Exclude non-numeric columns

    
    distances = df.iloc[:, 2:].apply(lambda x: cityblock(target_song, x), axis=1)

    
    similar_songs = pd.DataFrame({'track_name': df['track_name'], 'distance': distances})

    
    similar_songs = similar_songs.sort_values(by='distance', ascending=True)
    similar_songs = similar_songs[similar_songs['track_name'] != track_name]

    top_recommendations = similar_songs.head(num_recommendations)

    return top_recommendations['track_name']

def recommend_by_genre(rec, track_name, num_recommendations):
    input_track_data = rec[rec['track_name'] == track_name]

    input_genres = input_track_data.iloc[:, 3:].columns[input_track_data.iloc[:, 3:].values[0] > 0].tolist()
    matching_genre_songs = rec[rec.iloc[:, 3:][input_genres].sum(axis=1) > 0]

    matching_track_names = matching_genre_songs['track_name'].tolist()

    track_genre_count = []

    for track_name in matching_track_names:
        track_data = rec[rec['track_name'] == track_name]
        genres = track_data.iloc[:, 3:].columns[track_data.iloc[:, 3:].values[0] > 0].tolist()
        matching_genre_count = len(set(input_genres) & set(genres))
        track_genre_count.append((track_name, matching_genre_count))

    sorted_track_genre_count = sorted(track_genre_count, key=lambda x: x[1], reverse=True)

    sorted_matching_track_names = [track_name for track_name, _ in sorted_track_genre_count]

    return sorted_matching_track_names[:num_recommendations]

def recommend_by_artist(rec, track_name, num_recommendations):
    input_track_data = rec[rec['track_name'] == track_name]

    input_artist_name = input_track_data['artist_name'].values[0]
    same_artist_songs = rec[rec['artist_name'] == input_artist_name]

    same_artist_track_names = same_artist_songs['track_name'].tolist()


    return same_artist_track_names[:num_recommendations]

import pandas as pd

def final_recommendation(df, rec, input_track_name, num_recommendations, manhattan_weight=0.2, genre_weight=0.3, artist_weight=0.5):
    # Check if the input track_name exists in the dataset
    # if input_track_name not in df['track_name'].values:
    #     return pd.DataFrame()  # Return an empty DataFrame if the input track is not found

    manhattan_recommendations = recommend_manhattan_distance(df, input_track_name, num_recommendations)
    genre_recommendations = recommend_by_genre(rec, input_track_name, num_recommendations)
    artist_recommendations = recommend_by_artist(rec, input_track_name, num_recommendations)

    final_scores = {}
    
    # Calculate a weighted score for each recommendation method
    for recommendation_list, weight in [(manhattan_recommendations, manhattan_weight), (genre_recommendations, genre_weight), (artist_recommendations, artist_weight)]:
        for i, input_track_name in enumerate(recommendation_list):
            final_scores[input_track_name] = final_scores.get(input_track_name, 0) + (i + 1) * weight

    # Remove the input track from the final recommendations
    if input_track_name in final_scores:
        del final_scores[input_track_name]

    # Sort recommendations by the final score
    sorted_recommendations = sorted(final_scores.keys(), key=lambda x: final_scores[x])
    

    # Create a DataFrame with the final recommendations
    final_recommendations_df = pd.DataFrame(sorted_recommendations, columns=['track_name'])

    return final_recommendations_df[:num_recommendations]

# st.set_page_config(
#     page_title="Song Recommendation System",
#     page_icon="🎵",
#     layout="centered"
# )


# st.markdown(
#     """

# <style>
# body {
#     background: linear-gradient(to bottom, #1DB954, #191414);
#     font-family: 'Arial', sans-serif;
#     margin: 0;
#     padding: 0;
# }
# .stcontainer {
#     max-width: 800px;
#     margin: 0 auto;
#     padding: 20px;
#     background-color: #ffffff;
#     box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
#     border-radius: 10px;
# }

# .title {
#     text-align: center;
#     font-size: 36px;
#     color: #1E90FF;
#     margin-bottom: 20px;
# }

# .subtitle {
#     text-align: center;
#     font-size: 24px;
#     color: #333;
#     margin-bottom: 30px;
# }

# .button {
#     display: block;
#     width: 100%;
#     max-width: 300px;
#     margin: 0 auto;
#     background-color: #1E90FF;
#     color: #fff;
#     border: none;
#     border-radius: 5px;
#     padding: 10px 20px;
#     font-size: 18px;
#     cursor: pointer;
#     margin-top: 20px;
#     transition: background-color 0.3s;
# }

# .button:hover {
#     background-color: #0077B6;
# }

# .recommendations {
#     margin-top: 20px;
# }

# .recommendation-item {
#     display: flex;
#     margin: 20px 0;
#     align-items: center;
# }

# .recommendation-image {
#     width: 100px;
#     height: 100px;
#     border-radius: 10px;
#     margin-right: 20px;
# }

# .recommendation-details {
#     flex: 1;
# }

# .recommendation-title {
#     font-size: 20px;
#     color: #333;
#     margin-bottom: 10px;
# }

# .recommendation-player {
#     display: flex;
#     align-items: center;
# }

# .audio-control {
#     margin-top: 10px;
# }

# </style>

# """,
# unsafe_allow_html=True
# )

def fetch_poster(song_name):
    response = requests.get("https://saavn.me/search/songs?query={}&page=1&limit=2".format(song_name))

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'results' in data['data']:
            if data['data']['results']:
                return data['data']['results'][0]['image'][2]['link']
    return None

def fetch_song_info(track_name):
    """
    Fetch song information using the Spotify API via RapidAPI.
    """
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    }

    params = {
        'q': track_name,
        'type': 'track',
        'limit': 1
    }

    response = requests.get(API_ENDPOINT, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'tracks' in data and 'items' in data['tracks'] and data['tracks']['items']:
            track_info = data['tracks']['items'][0]
            return track_info
        else:
            st.warning("No track information found.")
            st.write("Response data:", data)  # Print the response data for debugging
            return None
    else:
        st.write("Error fetching song information:")
        st.write(response.text)  # Print the response text in case of an error
        return None
    
def display_song_card(track_name, image_url):
    """
    Display song details within an expandable card.
    """
    with st.expander(f"{track_name}", expanded=True):
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(image_url, use_column_width=True)
        with col2:
            unique_button_key = f"song_info_{track_name.replace(' ', '_')}"
            if st.button('Fetch Song Info', key=unique_button_key, help="Click for Song Information"):
                st.subheader(' Songs Details:')
                track_info = fetch_song_info(track_name)
                if track_info:
                    st.write("Song Information:")
                    st.write(f"Song Name: {track_info['data']['name']}")
                    st.write(f"Artist(s): {', '.join([artist['profile']['name'] for artist in track_info['data']['artists']['items'][0]])}")
                    st.write(f"Album: {track_info['data']['albumOfTrack']['name']}")
                    
                else:
                    st.warning("Song information not available.")
            #st.write("Additional song details and information can be displayed here.")



def main():
    #st.set_page_config(page_title='Song Recommender', page_icon="🎵", layout='wide')
    st.title('🎵 Song Recommendation System')
    st.write("Discover your next favorite song!")
    container = st.container()
    # User input for the song and the number of recommendations
    input_track_name = container.selectbox('Select a song', rec['track_name'].values)
    #num_recommendations = st.slider('Select the number of recommendations:', 1, 10, 5)
    num_recommendations = container.number_input('Enter the number of recommendations:', min_value=1)


    if st.button('Get Recommendations',  help='Click to get song recommendations'):
        st.subheader('Recommended Songs:')
        
        # Call the final_recommendation function with user input
        final_recommendations = final_recommendation(df, rec, input_track_name, num_recommendations)

        # if final_recommendations.empty:
        #     st.warning("Input song not found. Please try another song.")
        # else:
        #     # Display recommendations as a nice table
        #     st.table(final_recommendations)

        if final_recommendations.empty:
            st.warning("Input song not found. Please try another song.")
        else:
            # Display recommendations in a table with posters and play buttons
            for i, row in final_recommendations.iterrows():
                st.subheader(f"#{i + 1}")
                track_name = row['track_name']
                image_url = fetch_poster(track_name)
                if image_url:
                    display_song_card(track_name, image_url)
                else:
                    st.warning(f"Could not fetch details for {track_name}.")
                


                    
        
if __name__ == '__main__':
    main()