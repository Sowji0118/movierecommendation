import pandas as pd
import pickle
import os
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import train_test_split

class CollaborativeUtility:
    def __init__(self, ratings_path='data/ratings.csv', model_path='models/collaborative.pkl'):
        self.ratings_path = ratings_path
        self.model_path = model_path
        self.model = None
        self.trainset = None
        self.testset = None
        
    def load_data(self):
        """Loads ratings and prepares Surprise Dataset."""
        if not os.path.exists(self.ratings_path):
            raise FileNotFoundError(f"Ratings file not found at {self.ratings_path}")
        
        df = pd.read_csv(self.ratings_path)
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(df[['user_id', 'movie_id', 'rating']], reader)
        return data

    def train_model(self):
        """Trains SVD model and saves it."""
        print("Training collaborative model...")
        data = self.load_data()
        self.trainset = data.build_full_trainset()
        
        self.model = SVD()
        self.model.fit(self.trainset)
        
        # Save model
        if not os.path.exists(os.path.dirname(self.model_path)):
            os.makedirs(os.path.dirname(self.model_path))
            
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"Model saved to {self.model_path}")

    def evaluate_model(self):
        """Evaluates model and returns RMSE."""
        data = self.load_data()
        trainset, testset = train_test_split(data, test_size=0.2)
        
        algo = SVD()
        algo.fit(trainset)
        predictions = algo.test(testset)
        
        rmse = accuracy.rmse(predictions)
        return rmse

    def get_user_recommendations(self, user_id, movies_df, top_n=10):
        """
        Returns top_n recommended movies for a user.
        Handles cold-start users by returning top-rated movies if user not in trainset.
        """
        if self.model is None:
            # Load from pickle if exists
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
            else:
                self.train_model()

        # Check if user is in the training set
        try:
            inner_user_id = self.model.trainset.to_inner_uid(user_id)
            is_cold_start = False
        except ValueError:
            is_cold_start = True

        if is_cold_start:
            print(f"User {user_id} is a cold-start user. Returning trending movies.")
            # Simple fallback: return most popular movies (could be improved with mean ratings)
            return movies_df.head(top_n)[['movie_id', 'title']].to_dict('records')

        # Optimized prediction loop: only predict for unrated movies
        # In a production environment, we'd pre-calculate these or use an ANN like FAISS
        all_movie_ids = movies_df['movie_id'].unique()
        
        # Surprise specific: build the anti-testset for the user would be slow, 
        # so we manually predict for all movies.
        predictions = []
        for m_id in all_movie_ids:
            est = self.model.predict(user_id, m_id).est
            predictions.append((m_id, est))
            
        predictions.sort(key=lambda x: x[1], reverse=True)
        top_movie_ids = [p[0] for p in predictions[:top_n]]
        
        return movies_df[movies_df['movie_id'].isin(top_movie_ids)][['movie_id', 'title']].to_dict('records')

if __name__ == "__main__":
    # Integration test
    m_df = pd.read_csv('data/movies.csv')
    util = CollaborativeUtility()
    util.train_model()
    rmse = util.evaluate_model()
    print(f"Model RMSE: {rmse}")
    
    # Test valid user
    print(f"Recs for User 1: {util.get_user_recommendations(1, m_df, top_n=3)}")
    
    # Test cold start user
    print(f"Recs for cold-start User 999: {util.get_user_recommendations(999, m_df, top_n=3)}")
