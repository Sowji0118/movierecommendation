class HybridRecommender:
    def __init__(self, content_engine, collab_engine):
        self.content_engine = content_engine
        self.collab_engine = collab_engine
        
    def get_recommendations(self, user_id, title, movies_df, top_n=10):
        """Combines content and collaborative recommendations."""
        # Get content-based candidates
        content_recs = self.content_engine.get_recommendations(title, top_n=top_n*2)
        
        # Re-rank content candidates using collaborative scores for the user
        scored_recs = []
        for rec in content_recs:
            collab_score = self.collab_engine.predict(user_id, rec['movie_id'])
            scored_recs.append({
                'movie_id': rec['movie_id'],
                'title': rec['title'],
                'score': collab_score # In a real hybrid, we might weight content similarity + collab score
            })
            
        scored_recs.sort(key=lambda x: x['score'], reverse=True)
        return scored_recs[:top_n]

if __name__ == "__main__":
    import pandas as pd
    from recommender_content import ContentRecommender
    from recommender_collaborative import CollaborativeRecommender
    
    m_df = pd.read_csv('data/movies.csv')
    r_df = pd.read_csv('data/ratings.csv')
    
    cr = ContentRecommender(m_df)
    cr.fit()
    
    colr = CollaborativeRecommender(r_df)
    colr.fit()
    
    hr = HybridRecommender(cr, colr)
    print("Hybrid recommendations for User 1 based on 'The Dark Knight':")
    print(hr.get_recommendations(1, 'The Dark Knight', m_df, top_n=3))
