import pandas as pd
import pickle
from src.recommender_content import ContentRecommender
from src.recommender_collaborative import CollaborativeRecommender

def test_recommendations():
    print("Running Verification Tests...")
    
    # Check data
    movies_df = pd.read_csv('data/movies.csv')
    ratings_df = pd.read_csv('data/ratings.csv')
    assert len(movies_df) > 0, "Movies dataset is empty"
    assert len(ratings_df) > 0, "Ratings dataset is empty"
    print("✅ Datasets verified.")
    
    # Check Content-based engine
    cr = ContentRecommender(movies_df)
    cr.fit()
    recs = cr.get_recommendations('Inception', top_n=5)
    assert len(recs) > 0, "Content engine returned no recommendations"
    print("✅ Content engine verified.")
    
    # Check Collaborative engine
    colr = CollaborativeRecommender(ratings_df)
    colr.fit()
    pred = colr.predict(1, 1)
    assert 1.0 <= pred <= 5.0, f"Collaborative engine returned invalid prediction: {pred}"
    print("✅ Collaborative engine verified.")
    
    print("All backend tests passed!")

if __name__ == "__main__":
    test_recommendations()
