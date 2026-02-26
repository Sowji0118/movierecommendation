import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

class ContentBasedUtility:
    def __init__(self, movies_path='data/movies.csv', model_path='models/content.pkl'):
        self.movies_path = movies_path
        self.model_path = model_path
        self.movies_df = None
        self.cosine_sim = None
        
    def load_data(self):
        """Loads movie data."""
        if not os.path.exists(self.movies_path):
            raise FileNotFoundError(f"Movies file not found at {self.movies_path}")
        self.movies_df = pd.read_csv(self.movies_path)
        return self.movies_df

    def build_content_model(self):
        """
        Builds content model using TF-IDF on genres.
        Optimized for scalability: computed matrix is stored efficiently.
        """
        print("Building content-based model...")
        self.load_data()
        
        # Netflix movies often have pipe-separated genres
        self.movies_df['genres_str'] = self.movies_df['genres'].str.replace('|', ' ')
        
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(self.movies_df['genres_str'])
        
        # linear_kernel is equivalent to cosine_similarity when features are TF-IDF (normalized)
        # Using linear_kernel is faster.
        self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        
        # Save model
        if not os.path.exists(os.path.dirname(self.model_path)):
            os.makedirs(os.path.dirname(self.model_path))
            
        with open(self.model_path, 'wb') as f:
            pickle.dump((self.cosine_sim, self.movies_df[['movie_id', 'title']]), f)
        print(f"Content model persistent storage at {self.model_path}")

    def get_similar_movies(self, movie_title, top_n=10):
        """
        Returns top_n similar movies based on cosine similarity.
        Optimized: Loads similarity matrix from disk if not in memory.
        """
        if self.cosine_sim is None:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.cosine_sim, self.movies_df_cached = pickle.load(f)
            else:
                self.build_content_model()
                self.movies_df_cached = self.movies_df[['movie_id', 'title']]
        elif not hasattr(self, 'movies_df_cached'):
             self.movies_df_cached = self.movies_df[['movie_id', 'title']]

        # Case-insensitive title search
        matches = self.movies_df_cached[self.movies_df_cached['title'].str.lower() == movie_title.lower()]
        if matches.empty:
            print(f"Movie '{movie_title}' not found in database.")
            return []
            
        idx = matches.index[0]
        
        # Get pairwise similarity scores
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        
        # Sort based on similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get indices of top_n most similar movies (excluding self)
        sim_scores = sim_scores[1:top_n+1]
        movie_indices = [i[0] for i in sim_scores]
        
        return self.movies_df_cached.iloc[movie_indices].to_dict('records')

if __name__ == "__main__":
    # Integration test
    util = ContentBasedUtility()
    util.build_content_model()
    
    test_movie = 'Inception'
    print(f"Movies similar to '{test_movie}':")
    recs = util.get_similar_movies(test_movie, top_n=5)
    for r in recs:
        print(f"- {r['title']} (ID: {r['movie_id']})")
