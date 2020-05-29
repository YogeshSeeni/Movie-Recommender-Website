import requests 
from bs4 import BeautifulSoup

def get_popular_movies():
    result = requests.get('https://www.imdb.com/chart/moviemeter/')
    c = result.content 
    soup = BeautifulSoup(c, features='html.parser')

    title_columns = soup.find_all("td", class_ = 'titleColumn')
    popular_movies = []

    for i in title_columns:
        popular_movies.append(i.a.text)
        
    return popular_movies

