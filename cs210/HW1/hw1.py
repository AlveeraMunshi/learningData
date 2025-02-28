# FILL IN ALL THE FUNCTIONS IN THIS TEMPLATE
# MAKE SURE YOU TEST YOUR FUNCTIONS WITH MULTIPLE TEST CASES
# ASIDE FROM THE SAMPLE FILES PROVIDED TO YOU, TEST ON YOUR OWN FILES

# WHEN DONE, SUBMIT THIS FILE TO AUTOLAB

from collections import defaultdict
from collections import Counter

# YOU MAY NOT CODE ANY OTHER IMPORTS

# ------ TASK 1: READING DATA  --------

# 1.1
def read_ratings_data(f):
    # parameter f: movie ratings file name f (e.g. "movieRatingSample.txt")
    # return: dictionary that maps movie to ratings
    # WRITE YOUR CODE BELOW
    print("\nReading Ratings Data...") # for debugging
    movie_ratings = defaultdict(list)
    with open(f, 'r') as file:
        for line in file:
            movie, rating, _ = line.strip().split('|')
            movie_ratings[movie.strip()].append(float(rating.strip()))
    print("Movie Ratings:", dict(movie_ratings)) # for debugging
    return dict(movie_ratings)
    

# 1.2
def read_movie_genre(f):
    # parameter f: movies genre file name f (e.g. "genreMovieSample.txt")
    # return: dictionary that maps movie to genre
    # WRITE YOUR CODE BELOW
    movie_genre = {}
    print("\nReading Movie Genre Data...") # for debugging
    with open(f, 'r') as file:
        for line in file:
            genre, id, movie = line.strip().split('|')
            movie_genre[movie.strip()] = genre.strip()
    print("Movie Genre:", movie_genre) # for debugging
    return movie_genre

# ------ TASK 2: PROCESSING DATA --------

# 2.1
def create_genre_dict(d):
    # parameter d: dictionary that maps movie to genre
    # return: dictionary that maps genre to movies
    # WRITE YOUR CODE BELOW
    print("\nCreating Genre Dictionary...") # for debugging
    genre_movies = defaultdict(list)
    for movie, genre in d.items():
        genre_movies[genre].append(movie)
    print("Genre Movies:", dict(genre_movies)) # for debugging
    return dict(genre_movies)
    
# 2.2
def calculate_average_rating(d):
    # parameter d: dictionary that maps movie to ratings
    # return: dictionary that maps movie to average rating
    # WRITE YOUR CODE BELOW
    print("\nCalculating Average Ratings...") # for debugging
    movie_avg = {}
    for movie, ratings in d.items():
        movie_avg[movie] = sum(ratings) / len(ratings)
    print("Movie Average Ratings:", movie_avg) # for debugging
    return movie_avg
    
# ------ TASK 3: RECOMMENDATION --------

# 3.1
def get_popular_movies(d, n=10):
    # parameter d: dictionary that maps movie to average rating
    # parameter n: integer (for top n), default value 10
    # return: dictionary that maps movie to average rating, 
    #         in ranked order from highest to lowest average rating
    # WRITE YOUR CODE BELOW
    print("\nGetting Popular Movies...") # for debugging
    sorted_movies = sorted(d.items(), key=lambda x: x[1], reverse=True) # x[1] is the avg rating
    print("Sorted Movies:", sorted_movies) # for debugging
    if len(sorted_movies) < n:
        return dict(sorted_movies)
    return dict(sorted_movies[:n]) # subset of top n results
    
# 3.2
def filter_movies(d, thres_rating=3):
    # parameter d: dictionary that maps movie to average rating
    # parameter thres_rating: threshold rating, default value 3
    # return: dictionary that maps movie to average rating
    # WRITE YOUR CODE BELOW
    print("\nFiltering Movies...") # for debugging
    print("Threshold Rating:", thres_rating) # for debugging
    filtered = {movie: rating for movie, rating in d.items() if rating >= thres_rating}
    print("Filtered Movies:", filtered) # for debugging
    return filtered
# Note: This function filters movies based on a threshold rating.
# It creates a new dictionary containing only movies with an average rating
# greater than or equal to the specified threshold.
    
# 3.3
def get_popular_in_genre(genre, genre_to_movies, movie_to_average_rating, n=5):
    # parameter genre: genre name (e.g. "Comedy")
    # parameter genre_to_movies: dictionary that maps genre to movies
    # parameter movie_to_average_rating: dictionary  that maps movie to average rating
    # parameter n: integer (for top n), default value 5
    # return: dictionary that maps movie to average rating
    # WRITE YOUR CODE BELOW
    print("\nGetting Popular Movies in Genre:", genre) # for debugging
    genre_movies = genre_to_movies.get(genre, [])
    movies_ratings = {movie: movie_to_average_rating[movie] 
                     for movie in genre_movies 
                     if movie in movie_to_average_rating}
    print("Movies Ratings in Genre:", movies_ratings) # for debugging
    return get_popular_movies(movies_ratings, n)
# Note: This function retrieves the popular movies in a given genre.
# It first collects the movies in the specified genre,
# then filters their ratings, and finally returns the n most popular movies based on average ratings.
    
# 3.4
def get_genre_rating(genre, genre_to_movies, movie_to_average_rating):
    # parameter genre: genre name (e.g. "Comedy")
    # parameter genre_to_movies: dictionary that maps genre to movies
    # parameter movie_to_average_rating: dictionary  that maps movie to average rating
    # return: average rating of movies in genre
    # WRITE YOUR CODE BELOW
    print("\nCalculating Genre Rating for:", genre) # for debugging
    genre_movies = genre_to_movies.get(genre, [])
    ratings = [movie_to_average_rating[movie] 
              for movie in genre_movies 
              if movie in movie_to_average_rating]
    print("Ratings in Genre:", ratings) # for debugging
    print("Average Rating:", sum(ratings) / len(ratings) if ratings else 0) # for debugging
    return sum(ratings) / len(ratings) if ratings else 0
# Note: This function calculates the average rating of movies in a given genre.
# It first retrieves the list of movies for the specified genre,
# then collects their average ratings, and finally computes the average rating for the genre.
# If there are no movies in the genre, it returns 0.
# Note: The function uses list comprehension to filter and collect ratings efficiently.
# Note: The function handles the case where there are no movies in the genre by returning 0.
    
# 3.5
def genre_popularity(genre_to_movies, movie_to_average_rating, n=5):
    # parameter genre_to_movies: dictionary that maps genre to movies
    # parameter movie_to_average_rating: dictionary  that maps movie to average rating
    # parameter n: integer (for top n), default value 5
    # return: dictionary that maps genre to average rating
    # WRITE YOUR CODE BELOW
    print("\nCalculating Genre Popularity...") # for debugging
    genre_ratings = {}
    for genre in genre_to_movies:
        avg_rating = get_genre_rating(genre, genre_to_movies, movie_to_average_rating)
        genre_ratings[genre] = avg_rating
    print("Genre Ratings:", genre_ratings) # for debugging
    return get_popular_movies(genre_ratings, n)
# Note: This function calculates the average rating for each genre and returns the
# top n genres with the highest average ratings.
# Note: The function uses the get_genre_rating function to calculate the average rating for each genre.
# Note: The function uses the get_popular_movies function to get the top n genres.
# Note: The function returns a dictionary that maps genre to average rating, sorted by average rating in descending order.

# ------ TASK 4: USER FOCUSED  --------

# 4.1
def read_user_ratings(f):
    # parameter f: movie ratings file name (e.g. "movieRatingSample.txt")
    # return: dictionary that maps user to list of (movie,rating)
    # WRITE YOUR CODE BELOW
    print("\nReading User Ratings...") # for debugging
    user_ratings = defaultdict(list)
    with open(f, 'r') as file:
        for line in file:
            movie, rating, user_id = line.strip().split('|')
            user_ratings[user_id.strip()].append((movie.strip(), float(rating.strip())))
    print("User Ratings:", dict(user_ratings)) # for debugging
    return dict(user_ratings)
# Note: This function reads the ratings data and organizes it by user.
# Each user is mapped to a list of tuples, where each tuple contains a movie and its rating.
# This allows for easy access to all ratings given by a specific user.
# Note: The function uses defaultdict to handle cases where a user has not rated any movies.
# This ensures that the function returns an empty list for such users.
# Note: The function returns a dictionary where each key is a user ID and the value is a list of (movie, rating) tuples.
    
# 4.2
def get_user_genre(user_id, user_to_movies, movie_to_genre):
    # parameter user_id: user id
    # parameter user_to_movies: dictionary that maps user to movies and ratings
    # parameter movie_to_genre: dictionary that maps movie to genre
    # return: top genre that user likes
    # WRITE YOUR CODE BELOW
    print("\nGetting User Genre for:", user_id) # for debugging
    if user_id not in user_to_movies: # if user does not exist
        return None
    
    genre_ratings = defaultdict(list)
    # Collect ratings by genre
    for movie, rating in user_to_movies[user_id]:
        if movie in movie_to_genre:
            genre = movie_to_genre[movie]
            genre_ratings[genre].append(rating)
    print("Genre Ratings:", dict(genre_ratings)) # for debugging
    
    # Calculate average rating for each genre
    genre_avg = {genre: sum(ratings)/len(ratings) for genre, ratings in genre_ratings.items()}
    print("Genre Averages:", genre_avg) # for debugging
    
    if not genre_avg: # if user has not rated any movies in any genre
        return None
    print("Top Genre:", max(genre_avg.items(), key=lambda x: x[1])[0]) # for debugging
    return max(genre_avg.items(), key=lambda x: x[1])[0] # find max by highest rating, but then take the genre name from the generated tuple
# Note: This function returns the genre with the highest average rating from the user's rated movies.
# If the user has not rated any movies, it returns None.
    
# 4.3    
def recommend_movies(user_id, user_to_movies, movie_to_genre, movie_to_average_rating):
    # parameter user_id: user id
    # parameter user_to_movies: dictionary that maps user to movies and ratings
    # parameter movie_to_genre: dictionary that maps movie to genre
    # parameter movie_to_average_rating: dictionary that maps movie to average rating
    # return: dictionary that maps movie to average rating
    # WRITE YOUR CODE BELOW
    print("\nRecommending Movies for User:", user_id) # for debugging
    if user_id not in user_to_movies:
        return {}
    print("User: ", user_id)
    
    top_genre = get_user_genre(user_id, user_to_movies, movie_to_genre)
    if not top_genre:
        return {}
    print("Top Genre:", top_genre) # for debugging
    
    # Get movies user has rated
    rated_movies = set(movie for movie, _ in user_to_movies[user_id])
    print("Rated Movies:", rated_movies) # for debugging
    
    # Get all movies in top genre
    all_genre_movies = set(movie for movie, genre in movie_to_genre.items() 
                         if genre == top_genre)
    print("All Genre Movies:", all_genre_movies) # for debugging
    
    # Movies not yet rated by user
    unrated_movies = all_genre_movies - rated_movies
    print("Unrated Movies:", unrated_movies) # for debugging
    
    # Create dict of unrated movies with their average ratings
    unrated_ratings = {movie: movie_to_average_rating[movie] 
                      for movie in unrated_movies 
                      if movie in movie_to_average_rating}
    print("Unrated Ratings:", unrated_ratings) # for debugging
    
    # Sort and get top 3
    print("Top 3 Recommendations:") # for debugging
    if not unrated_ratings:
        return {}
    return get_popular_movies(unrated_ratings, 3)
# Note: This function recommends movies to a user based on their top genre.
# It finds the top genre from the user's rated movies, identifies unrated movies in that genre,
# and recommends the top 3 unrated movies based on average ratings.

# -------- main function for your testing -----
def main():
    # write all your test code here
    # this function will be ignored by us when grading
    
    # Test Task 1
    print("\nTask 1: Reading Data")
    ratings_data = "/Users/alveeramunshi/Documents/GitHub/learningData/cs210/HW1/movieRatingSample.txt"
    genre_data = "/Users/alveeramunshi/Documents/GitHub/learningData/cs210/HW1/genreMovieSample.txt"
    print("\n2.1")
    ratings = read_ratings_data(ratings_data)
    print("\n2.2")
    genres = read_movie_genre(genre_data)
    print("\nRatings:", ratings)
    print("Genres:", genres)
    
    # Test Task 2
    print("\nTask 2: Processing Data")
    print("\n2.1")
    genre_dict = create_genre_dict(genres)
    print("\n2.2")
    avg_ratings = calculate_average_rating(ratings)
    print("\nGenre Dict:", genre_dict)
    print("Avg Ratings:", avg_ratings)
    
    # Test Task 3
    print("\nTask 3: Recommendation")
    print("\n3.1")
    popular = get_popular_movies(avg_ratings, 1)
    print("\n3.2")
    filtered = filter_movies(avg_ratings, 4.5)
    print("\n3.3")
    genre_pop = get_popular_in_genre("Adventure", genre_dict, avg_ratings)
    print("\n3.4")
    genre_rate = get_genre_rating("Adventure", genre_dict, avg_ratings)
    print("\n3.5")
    genre_popularity_dict = genre_popularity(genre_dict, avg_ratings)
    print("\nPopular:", popular)
    print("Filtered:", filtered)
    print("Genre Popular:", genre_pop)
    print("Genre Rating:", genre_rate)
    print("Genre Popularity:", genre_popularity_dict)
    
    # Test Task 4
    print("\nTask 4: User Focused")
    print("\n4.1")
    user_ratings = read_user_ratings(ratings_data)
    print("\n4.2")
    user1_genre = get_user_genre("user1", user_ratings, genres)
    user2_genre = get_user_genre("user2", user_ratings, genres)
    print("\n4.3")
    recommendations1 = recommend_movies("user1", user_ratings, genres, avg_ratings)
    recommendations2 = recommend_movies("user2", user_ratings, genres, avg_ratings)
    print("\nUser Ratings:", user_ratings)
    print("User1 Genre:", user1_genre)
    print("User2 Genre:", user2_genre)
    print("User1 Recommendations:", recommendations1)
    print("User2 Recommendations:", recommendations2)
    
# DO NOT write ANY CODE (including variable names) outside of any of the above functions
# In other words, ALL code your write (including variable names) MUST be inside one of
# the above functions
    
# program will start at the following main() function call
# when you execute hw1.py
main()