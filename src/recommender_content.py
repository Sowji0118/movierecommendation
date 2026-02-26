import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle
import os

class ContentRecommender:
    def __init__(self, movies_df):
        self.movies_df = movies_df
        self.tfidf_matrix = None
        self.cosine_sim = None
        
    def fit(self):
        """Precomputes TF-IDF matrix and cosine similarity."""
        tfidf = TfidfVectorizer(stop_words='english')
        
        # Combine overview and genres for content comparison
        self.movies_df['content'] = self.movies_df['overview'] + " " + self.movies_df['genres'].str.replace('|', ' ')
        
        self.tfidf_matrix = tfidf.fit_transform(self.movies_df['content'])
        self.cosine_sim = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)
        
    def get_recommendations(self, title, top_n=10):
        """Returns top_n recommended movies based on similarity."""
        if title not in self.movies_df['title'].values:
            return []
            
        idx = self.movies_df[self.movies_df['title'] == title].index[0]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n+1]
        
        movie_indices = [i[0] for i in sim_scores]
        return self.movies_df.iloc[movie_indices][['movie_id', 'title']].to_dict('records')

    def save_model(self, path='models/content_engine.pkl'):
        if not os.path.exists('models'):
            os.makedirs('models')
        with open(path, 'wb') as f:
            pickle.dump((self.tfidf_matrix, self.cosine_sim), f)

if __name__ == "__main__":
    df = pd.read_csv('data/movies.csv')
    recommender = ContentRecommender(df)
    recommender.fit()
    print("Content recommendations for 'The Dark Knight':")
    print(recommender.get_recommendations('The Dark Knight', top_n=3))
    recommender.save_model()
