import pandas as pd
import time
import joblib
import json
import os
from sklearn.model_selection import GroupShuffleSplit
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Import our exact feature engineering function from Phase 4
from features import extract_features

def main():
    print("Starting Phase 5: Model Training...")

    # 1. Load Data
    df = pd.read_csv('data/processed/urls.csv')
    print(f"Loaded {len(df)} URLs.")

    # 2. Extract Features
    print("Extracting features for the whole dataset (this takes 10-30 seconds)...")
    features_list = df['url'].apply(extract_features).tolist()
    X = pd.DataFrame(features_list)
    y = df['label']
    groups = df['domain']

    # Ensure backend directory exists and save the feature column order
    os.makedirs('backend', exist_ok=True)
    with open('backend/feature_columns.json', 'w') as f:
        json.dump(X.columns.tolist(), f)

    # 3. Domain-based Split (Crucial for hackathon judges!)
    gss = GroupShuffleSplit(n_splits=1, train_size=0.8, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    print(f"Training set: {len(X_train)} URLs | Test set: {len(X_test)} URLs")

    # 4. Define Models
    models = {
        "Logistic Regression": Pipeline([('scaler', StandardScaler()), ('lr', LogisticRegression(max_iter=1000, class_weight='balanced'))]),
        "Random Forest": RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
        "XGBoost": xgb.XGBClassifier(scale_pos_weight=1, eval_metric='logloss', random_state=42),
        "LightGBM": lgb.LGBMClassifier(is_unbalance=True, random_state=42, verbose=-1)
    }

    # 5. Train and Evaluate
    results = []
    best_model = None
    best_f1 = 0

    print("Training models...")
    for name, model in models.items():
        # Train
        model.fit(X_train, y_train)
        
        # Inference & Timing
        start_inf = time.time()
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred
        inf_time = (time.time() - start_inf) / len(X_test) * 1000 # ms per URL

        # Metrics
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_proba)
        pr_auc = average_precision_score(y_test, y_proba)

        results.append({
            "Model": name, "Precision": precision, "Recall": recall, 
            "F1": f1, "ROC-AUC": roc_auc, "PR-AUC": pr_auc, "Inf Time (ms)": inf_time
        })

        # Track the best model based on F1 Score
        if f1 > best_f1:
            best_f1 = f1
            best_model = model

    # 6. Save Results & Best Model
    results_df = pd.DataFrame(results).round(4)
    results_df.to_csv('reports/model_comparison.csv', index=False)
    
    print("\n--- Model Comparison Table ---")
    print(results_df.to_string(index=False))

    joblib.dump(best_model, 'backend/model.joblib')
    print(f"\nPhase 5 Complete! Saved Best Model to backend/model.joblib")

if __name__ == "__main__":
    main()