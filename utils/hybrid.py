import pandas as pd
import os
import pickle
from utils.collaborative import CollaborativeUtility
from utils.content_based import ContentBasedUtility

class HybridUtility:
    def __init__(self, movies_path='data/movies.csv', ratings_path='data/ratings.csv'):
        self.movies_path = movies_path
        self.ratings_path = ratings_path
        self.collab_util = CollaborativeUtility(ratings_path=ratings_path)
        self.content_util = ContentBasedUtility(movies_path=movies_path)
        self.movies_df = None
        self.ratings_df = None
        
    def load_data(self):
        """Loads data for hybrid logic."""
        if self.movies_df is None:
            self.movies_df = pd.read_csv(self.movies_path)
        if self.ratings_df is None:
            self.ratings_df = pd.read_csv(self.ratings_path)
        return self.movies_df, self.ratings_df

    def get_hybrid_recommendations(self, user_id, top_n=10, collab_weight=0.7):
        """
        Combines collaborative and content-based scores with a weighted ranking system.
        Handles cold-start (new user) and sparse rating scenarios dynamically.
        """
        self.load_data()
        
        # Determine user history depth
        user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
        num_ratings = len(user_ratings)
        
        # Scenario 1: New User (Cold Start - 0 ratings)
        if num_ratings == 0:
            print(f"User {user_id} is new. Using content-based methodology based on popular titles.")
            # Fallback: Content-based recs for a 'trending' movie or just top movies
            # For this utility, we'll return top N movies from content engine candidates
            return self.movies_df.head(top_n)[['movie_id', 'title']].to_dict('records')

        # Scenario 2: Sparse Ratings (< 3 ratings)
        # Shift weight towards content-based to avoid noise in collaborative filtering
        if num_ratings < 3:
            collab_weight = 0.3
            print(f"User {user_id} has sparse ratings ({num_ratings}). Weighting content-based higher.")

        # Hybrid Logic Implementation
        # 1. Get Collaborative scores for all movies
        # We'll use a slightly different approach for the hybrid: get scores for a subset of candidates
        # to ensure fast performance.
        
        # For simplicity in this demo, we'll get top collaborative picks first
        collab_recs = self.collab_util.get_user_recommendations(user_id, self.movies_df, top_n=top_n*3)
        
        # 2. Re-rank or augment with Content-based similarity
        # If the user has rated movies, find movies similar to their highest rated one
        best_rated_movie_id = user_ratings.sort_values(by='rating', ascending=False).iloc[0]['movie_id']
        best_movie_title = self.movies_df[self.movies_df['movie_id'] == best_rated_movie_id]['title'].values[0]
        
        content_recs = self.content_util.get_similar_movies(best_movie_title, top_n=top_n*3)
        
        # Combine and Score
        combined_scores = {}
        
        # Score collaborative candidates
        for rec in collab_recs:
            combined_scores[rec['movie_id']] = combined_scores.get(rec['movie_id'], 0) + (collab_weight * 1.0) # Normalized weight
            
        # Score content candidates
        content_weight = 1.0 - collab_weight
        for rec in content_recs:
            combined_scores[rec['movie_id']] = combined_scores.get(rec['movie_id'], 0) + (content_weight * 1.0)

        # Sort combined results
        sorted_ids = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        top_ids = [s[0] for s in sorted_ids[:top_n]]
        
        return self.movies_df[self.movies_df['movie_id'].isin(top_ids)][['movie_id', 'title']].to_dict('records')

if __name__ == "__main__":
    # Integration test
    hb = HybridUtility()
    
    print("Hybrid recommendations for User 1 (Active User):")
    print(hb.get_hybrid_recommendations(1, top_n=5))
    
    print("\nHybrid recommendations for User 999 (New User):")
    print(hb.get_hybrid_recommendations(999, top_n=5))
