import requests
from bs4 import BeautifulSoup 

def get_random_movie():
    r = requests.get('https://www.suggestmemovie.com/')
    c = r.text
    soup = BeautifulSoup(c, features='html.parser')
    random_movie = soup.find('h1')
    text = random_movie.text
    return text[:-5]
