from engine import MiningRiskEngine
import pandas as pd
import numpy as np

def run_verification():
    print("=== AI Model Correction Verification ===\n")
    engine = MiningRiskEngine()
    
    # 1. Train on normal baseline
    print("[1] Training on normal baseline...")
    engine.train_baseline_model()
    print("Model initialized and trained.\n")
    
    # 2. Test Cases
    test_cases = [
        {
            'name': 'Normal Activity',
            'data': {'ndvi_drop': 0.15, 'nightlight_inc': 0.15, 'acoustic_score': 0.10}
        },
        {
            'name': 'Transitional (Possible Mining)',
            'data': {'ndvi_drop': 0.45, 'nightlight_inc': 0.45, 'acoustic_score': 0.35}
        },
        {
            'name': 'Clear Mining (High Everything)',
            'data': {'ndvi_drop': 0.85, 'nightlight_inc': 0.85, 'acoustic_score': 0.75}
        },
        {
            'name': 'Multivariate Anomaly (High NDVI only, others low)',
            'data': {'ndvi_drop': 0.90, 'nightlight_inc': 0.10, 'acoustic_score': 0.10}
        },
        {
            'name': 'AI Override Test (Extreme Anomaly)',
            'data': {'ndvi_drop': 0.95, 'nightlight_inc': 0.95, 'acoustic_score': 0.95}
        }
    ]
    
    results = []
    for tc in test_cases:
        final_score, ai_score, rule_score = engine.compute_final_score(tc['data'])
        classification = engine.classify_risk(final_score, ai_score)
        
        results.append({
            'Scenario': tc['name'],
            'AI Score': ai_score,
            'Rule Score': rule_score,
            'Final Score': final_score,
            'Result': classification
        })
        
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    
    # Check for divergence
    divergence = np.abs(df['AI Score'] - df['Rule Score']).mean()
    print(f"\nAverage Divergence (AI vs Rule): {divergence:.4f}")
    
    if divergence > 0.05:
        print("SUCCESS: AI anomaly score diverges meaningfully from rule-based score.")
    else:
        print("WARNING: Divergence is low. Check if model is properly differentiating anomalies.")

if __name__ == "__main__":
    run_verification()
