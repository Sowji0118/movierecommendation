import numpy as np
import pandas as pd
from collections import defaultdict
try:
    from surprise import accuracy
except ImportError:
    accuracy = None

class EvaluationUtility:
    def __init__(self):
        pass

    @staticmethod
    def calculate_rmse(predictions):
        """
        Calculates RMSE from a list of Surprise predictions.
        Fallback to manual calculation if Surprise is not available.
        """
        if accuracy:
            return accuracy.rmse(predictions, verbose=False)
        
        # Manual calculation
        # Surprise predictions are list of tuples/objects with (uid, iid, r_ui, est, details)
        sq_errors = []
        for pred in predictions:
            # Handle both Surprise objects and simple tuples
            if hasattr(pred, 'r_ui') and hasattr(pred, 'est'):
                sq_errors.append((pred.r_ui - pred.est)**2)
            else:
                # Assuming tuple (uid, iid, r_ui, est)
                sq_errors.append((pred[2] - pred[3])**2)
        
        return np.sqrt(np.mean(sq_errors))

    @staticmethod
    def precision_recall_at_k(predictions, k=10, threshold=3.5):
        """
        Return precision and recall at k metrics for each user.
        Based on Surprise documentation example.
        """
        # First map the predictions to each user.
        user_est_true = defaultdict(list)
        for pred in predictions:
            if hasattr(pred, 'uid'):
                user_est_true[pred.uid].append((pred.est, pred.r_ui))
            else:
                user_est_true[pred[0]].append((pred[3], pred[2]))

        precisions = dict()
        recalls = dict()
        for uid, user_ratings in user_est_true.items():
            # Sort user ratings by estimated value
            user_ratings.sort(key=lambda x: x[0], reverse=True)

            # Number of relevant items
            n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)

            # Number of recommended items in top k
            n_rec_k = sum((est >= threshold) for (est, _) in user_ratings[:k])

            # Number of relevant and recommended items in top k
            n_rel_and_rec_k = sum(((true_r >= threshold) and (est >= threshold))
                                  for (est, true_r) in user_ratings[:k])

            # Precision@K: Proportion of recommended items that are relevant
            # When n_rec_k is 0, Precision is undefined. We here set it to 0.
            precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 0

            # Recall@K: Proportion of relevant items that are recommended
            # When n_rel is 0, Recall is undefined. We here set it to 0.
            recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 0

        # Average over all users
        avg_precision = sum(p for p in precisions.values()) / len(precisions)
        avg_recall = sum(r for r in recalls.values()) / len(recalls)

        return avg_precision, avg_recall

    def get_metrics_dict(self, predictions, k=10, threshold=3.5):
        """Returns a formatted dictionary of all evaluation metrics."""
        rmse = self.calculate_rmse(predictions)
        precision, recall = self.precision_recall_at_k(predictions, k=k, threshold=threshold)
        
        return {
            'RMSE': round(rmse, 4),
            f'Precision@{k}': round(precision, 4),
            f'Recall@{k}': round(recall, 4),
            'K': k,
            'Threshold': threshold
        }

    def prepare_viz_data(self, metrics_dict):
        """
        Prepares data for visualization in a dashboard.
        Returns a DataFrame suitable for bar charts.
        """
        viz_data = {
            'Metric': ['RMSE', f"Precision@{metrics_dict['K']}", f"Recall@{metrics_dict['K']}"],
            'Value': [metrics_dict['RMSE'], metrics_dict[f"Precision@{metrics_dict['K']}"], metrics_dict[f"Recall@{metrics_dict['K']}"]]
        }
        return pd.DataFrame(viz_data)

if __name__ == "__main__":
    # Mock predictions for testing: (uid, iid, true_r, est, details)
    mock_preds = [
        (1, 101, 5.0, 4.8),
        (1, 102, 4.0, 3.9),
        (1, 103, 3.0, 4.5), # False positive
        (2, 101, 5.0, 2.0), # False negative
        (2, 104, 1.0, 1.5)
    ]
    
    eval_util = EvaluationUtility()
    metrics = eval_util.get_metrics_dict(mock_preds, k=2)
    print("Evaluation Metrics:")
    print(metrics)
    
    df_viz = eval_util.prepare_viz_data(metrics)
    print("\nVisualization Data:")
    print(df_viz)
