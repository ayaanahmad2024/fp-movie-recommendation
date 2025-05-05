# fp-movie-recommendation
This project recommends a list of 5 movies to the user based on their preferences such as genre, runtime, year made, and more.
The project uses two csv files (one with IMDB movie data from 2006-2016, and the other with all Oscar data)
The user is prompted to give their preferences, and then the code will compile a list of 5 movie recommendations based on the preferences.
The user is told which of the movies, if any, have been nominated for or have won oscars.

This code requires the library pandas to be installed in order to load the csv files. If it matters, I wrote the whole project in PyCharm on my Mac.
As long as pandas is installed and the IMDB-Movie-Date.csv and oscar_data.csv files are in the project, the code should run.

For this project, I used ChatGPT to help me learn how to use the pandas library to import the csv files, and then how to use pandas to clean the data.
Some of the load_movie_data was written with the help of ChatGPT, specifically normalizing the genre fields, since I wasn't familiar with how to format using pandas
Similar help was used to clean the oscar data.
The get_user_preferences was written almost entirely by me using what we have learned in class, and I just got help with getting a unique list of genres.
ChatGPT helped write the filter_movies function to create a "boolean mask" and filter with different weightings.
ChatGPT also helped slightly with formatting for the show_recommendation function just to make my code as clean as possible, although the logic was my own.
It also helped with the code to repick movies that the user has already seen.
Essentially, I wrote most of the code and I came up with the structure, but I got lots of help from ChatGPT with specific lines and sections to learn how to format with pandas and filter movies.