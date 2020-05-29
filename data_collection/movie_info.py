import requests 

def get_movie_info(title):
    URL = 'http://www.omdbapi.com'
    params = {
        'apikey': 'af245c21',
        't': title
    }
    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News', 'Reality-TV', 'Romance', 'Sci-Fi', 'Sport', 'Talk-Show', 'Thriller', 'War', 'Western']
    num_genres = len(genres)

    r = requests.get(URL, params=params)
    movie_info = r.json()

    movie_genres = list(movie_info['Genre'].split(','))
    for j in movie_genres:
        movie_genres[movie_genres.index(j)] = j.replace(' ', '')

    movie_data = []

    for i in range(num_genres):
        movie_data.append(0)
    
    genre_weight = 1 / len(movie_genres)

    for y in movie_genres:
        movie_data[genres.index(y)] = genre_weight

    imdb_rating = eval(movie_info['Ratings'][0]['Value'])
    movie_data.append(imdb_rating)

    return movie_data

def get_movie_ui(title):
    URL = 'http://www.omdbapi.com'
    params = {
        'apikey': 'af245c21',
        't': title
    }

    r = requests.get(URL, params=params)
    movie_result = r.json()

    movie_ui = [movie_result['Title'], movie_result['Year'], movie_result['Rated'], movie_result['Poster']]
    return movie_ui
