from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
import pandas as pd
import pickle
import os

class CollaborativeRecommender:
    def __init__(self, ratings_df):
        self.ratings_df = ratings_df
        self.model = SVD()
        self.trainset = None
        
    def fit(self):
        """Trains the SVD model."""
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(self.ratings_df[['user_id', 'movie_id', 'rating']], reader)
        self.trainset = data.build_full_trainset()
        self.model.fit(self.trainset)
        
    def predict(self, user_id, movie_id):
        """Predicts rating for a specific user and movie."""
        return self.model.predict(user_id, movie_id).est

    def get_top_n(self, user_id, movies_df, n=10):
        """Returns top n recommended movies for a user."""
        all_movie_ids = movies_df['movie_id'].unique()
        rated_movies = self.ratings_df[self.ratings_df['user_id'] == user_id]['movie_id'].values
        movies_to_predict = [m for m in all_movie_ids if m not in rated_movies]
        
        predictions = []
        for m_id in movies_to_predict:
            est = self.predict(user_id, m_id)
            predictions.append((m_id, est))
            
        predictions.sort(key=lambda x: x[1], reverse=True)
        top_movie_ids = [p[0] for p in predictions[:n]]
        
        return movies_df[movies_df['movie_id'].isin(top_movie_ids)][['movie_id', 'title']].to_dict('records')

    def save_model(self, path='models/collab_engine.pkl'):
        if not os.path.exists('models'):
            os.makedirs('models')
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)

if __name__ == "__main__":
    r_df = pd.read_csv('data/ratings.csv')
    m_df = pd.read_csv('data/movies.csv')
    recommender = CollaborativeRecommender(r_df)
    recommender.fit()
    print("Collaborative recommendations for User 1:")
    print(recommender.get_top_n(1, m_df, n=3))
    recommender.save_model()
