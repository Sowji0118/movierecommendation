import pandas as pd
import numpy as np

def create_sample_data():
    """Outputs sample movie data for development."""
    movies_data = {
        'movie_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'title': [
            'The Dark Knight', 'Inception', 'The Matrix', 'Pulp Fiction', 
            'Forrest Gump', 'The Shawshank Redemption', 'The Godfather', 
            'Interstellar', 'Parasite', 'Avengers: Endgame'
        ],
        'genres': [
            'Action|Crime|Drama', 'Action|Sci-Fi|Thriller', 'Action|Sci-Fi', 
            'Crime|Drama', 'Drama|Romance', 'Drama', 'Crime|Drama', 
            'Adventure|Drama|Sci-Fi', 'Comedy|Drama|Thriller', 'Action|Adventure|Sci-Fi'
        ],
        'overview': [
            'Batman raises the stakes in his war on crime.',
            'A thief who steals corporate secrets through use of dream-sharing technology.',
            'A computer hacker learns from mysterious rebels about the true nature of his reality.',
            'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine.',
            'The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal.',
            'Two imprisoned men bond over a number of years.',
            'The aging patriarch of an organized crime dynasty transfers control to his reluctant son.',
            'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
            'Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.',
            'After the devastating events of Infinity War, the universe is in ruins.'
        ]
    }
    
    ratings_data = {
        'user_id': np.random.randint(1, 50, 100),
        'movie_id': np.random.randint(1, 11, 100),
        'rating': np.random.uniform(1.0, 5.0, 100)
    }
    
    movies_df = pd.DataFrame(movies_data)
    ratings_df = pd.DataFrame(ratings_data)
    
    movies_df.to_csv('data/movies.csv', index=False)
    ratings_df.to_csv('data/ratings.csv', index=False)
    print("Sample data created in data/ directory.")

if __name__ == "__main__":
    import os
    if not os.path.exists('data'):
        os.makedirs('data')
    create_sample_data()
