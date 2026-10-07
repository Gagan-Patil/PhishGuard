import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import shap
import os
import warnings
from sklearn.metrics import confusion_matrix, classification_report
from features import extract_features

# Suppress warnings for clean output
warnings.filterwarnings('ignore')

def main():
    print("Starting Phase 6: Evaluation & Explainability...")
    os.makedirs('reports/figures', exist_ok=True)
    
    # 1. Load the Realistic Imbalanced Test Data
    print("Loading imbalanced test set...")
    df_test = pd.read_csv('data/processed/urls_imbalanced.csv')
    model = joblib.load('backend/model.joblib')
    
    # 2. Extract Features
    print("Extracting features (this may take a few seconds)...")
    X_test = pd.DataFrame(df_test['url'].apply(extract_features).tolist())
    y_test = df_test['label']
    
    # 3. Predict & Plot Confusion Matrix
    y_pred = model.predict(X_test)
    
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6,4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Safe (0)', 'Phishing (1)'], 
                yticklabels=['Safe (0)', 'Phishing (1)'])
    plt.title('Confusion Matrix on Realistic Imbalanced Data')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.savefig('reports/figures/confusion_matrix.png', bbox_inches='tight')
    plt.close()
    
    print("\n--- Classification Report (Imbalanced Set) ---")
    print(classification_report(y_test, y_pred))
    
    # 4. SHAP Feature Explainability
    print("Generating SHAP summary plot (this proves to judges the model isn't guessing)...")
    try:
        # Use a model-agnostic explainer to handle pipelines safely
        explainer = shap.Explainer(model.predict, X_test.head(100)) # subset for speed
        shap_values = explainer(X_test.head(100))
        
        plt.figure(figsize=(8,5))
        shap.summary_plot(shap_values, X_test.head(100), show=False)
        plt.savefig('reports/figures/shap_summary.png', bbox_inches='tight')
        plt.close()
        print("Saved SHAP summary plot to reports/figures/shap_summary.png")
    except Exception as e:
        print(f"SHAP generation skipped (normal for some mock models): {e}")

    print("\nPhase 6 Evaluation Complete!")

if __name__ == "__main__":
    main()