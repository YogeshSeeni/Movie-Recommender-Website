# Movie-Recommender-Website

## Where to find it

You can find this website deployed with heroku at http://yogesh-movie-recommender.herokuapp.com/

## How it Works

The user first selects five movies that they like or don't like based on the 100 most popular movies based on the IMDB website. It then goes through a Feed Forward Neural Network trained with data of the movie from the Omdb movie api, then the model for that user is then uploaded to Firebase Storage. When the user wants to have movies recommended to them, that specific ML model for that user is download from the Firebase Storage, and a random movie that is scraped of https://www.suggestmemovie.com/. If the predictoin from the model is greater than 50% percent, the movie is then recommended.
