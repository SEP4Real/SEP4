import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)


def evaluate_model(model, X_train, X_test, y_train, y_test, is_classification=True):
    """
    Automatically evaluate the model on both training and test sets.
    Supports both classification and regression.
    Supports Scikit-Learn and TensorFlow/Keras models.
    Displays feature importances if available.
    
    Parameters:
    model: Trained model (sklearn or keras).
    X_train: Training features.
    X_test: Validation/Test features.
    y_train: Training labels.
    y_test: Validation/Test labels.
    is_classification: Boolean, if True uses classification metrics, else regression.
    """
    datasets = [('Train', X_train, y_train), ('Test/Validation', X_test, y_test)]
    
    is_keras = 'keras' in str(type(model)).lower()
    model_name = type(model).__name__
    if is_keras:
        model_name = f"Keras {model_name}"

    # Feature Relevance Logic (Importance or Coefficients)
    has_importance = hasattr(model, 'feature_importances_')
    has_coef = hasattr(model, 'coef_')
    has_relevance = has_importance or has_coef
    
    if is_classification:
        n_rows = 2 if has_relevance else 1
        fig, axes = plt.subplots(n_rows, 2, figsize=(15, 6 * n_rows))
        if n_rows == 1:
            axes = axes.reshape(1, -1)
    else:
        n_rows = 3 if has_relevance else 2
        fig, axes = plt.subplots(n_rows, 2, figsize=(15, 6 * n_rows))
        
    fig.suptitle(f'Model Evaluation: {model_name} ({"Classification" if is_classification else "Regression"})', fontsize=16)

    for i, (name, X, y) in enumerate(datasets):
        # Predict
        if is_keras:
            y_pred = model.predict(X, verbose=0)
        else:
            y_pred = model.predict(X)
            
        # Handle labels and predictions for classification
        y_true_labels = y
        if is_classification:
            # Convert one-hot encoded true labels to class indices
            if hasattr(y, 'ndim') and y.ndim > 1 and y.shape[1] > 1:
                y_true_labels = np.argmax(np.array(y), axis=1)
            
            # Convert probabilities to class indices if it's a Keras model or probability output
            if is_keras:
                if y_pred.ndim > 1 and y_pred.shape[1] > 1:
                    y_pred = np.argmax(y_pred, axis=1)
                elif y_pred.ndim > 1 and y_pred.shape[1] == 1:
                    y_pred = (y_pred > 0.5).astype(int).flatten()
                else:
                    y_pred = (y_pred > 0.5).astype(int)
        else:
            # Flatten regression predictions if they are 2D (common in Keras)
            if hasattr(y_pred, 'ndim') and y_pred.ndim > 1:
                y_pred = y_pred.flatten()
            if hasattr(y, 'ndim') and y.ndim > 1:
                y_true_labels = np.array(y).flatten()

        print(f"\n--- {name} Metrics ---")
        
        if is_classification:
            # Classification Logic
            unique_labels = np.unique(y_true_labels)
            avg_method = 'binary' if len(unique_labels) <= 2 else 'weighted'
            
            acc = accuracy_score(y_true_labels, y_pred)
            prec = precision_score(y_true_labels, y_pred, average=avg_method, zero_division=0)
            rec = recall_score(y_true_labels, y_pred, average=avg_method, zero_division=0)
            f1 = f1_score(y_true_labels, y_pred, average=avg_method, zero_division=0)
            
            print(f"Accuracy:  {acc:.4f}")
            print(f"Precision ({avg_method}): {prec:.4f}")
            print(f"Recall ({avg_method}):    {rec:.4f}")
            print(f"F1 Score ({avg_method}):  {f1:.4f}")
            
            # Confusion Matrix
            cm = confusion_matrix(y_true_labels, y_pred)
            disp_cm = ConfusionMatrixDisplay(confusion_matrix=cm)
            disp_cm.plot(ax=axes[0, i], cmap='Blues', colorbar=False)
            axes[0, i].set_title(f'Confusion Matrix ({name})')
        else:
            # Regression Logic
            mse = mean_squared_error(y_true_labels, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_true_labels, y_pred)
            r2 = r2_score(y_true_labels, y_pred)
            
            print(f"MSE:  {mse:.4f}")
            print(f"RMSE: {rmse:.4f}")
            print(f"MAE:  {mae:.4f}")
            print(f"R2:   {r2:.4f}")
            
            # Prediction vs Actual Plot
            axes[0, i].scatter(y_true_labels, y_pred, alpha=0.5)
            axes[0, i].plot([y_true_labels.min(), y_true_labels.max()], [y_true_labels.min(), y_true_labels.max()], 'r--', lw=2)
            axes[0, i].set_xlabel('Actual')
            axes[0, i].set_ylabel('Predicted')
            axes[0, i].set_title(f'Predicted vs Actual ({name})')
            
            # Residual Plot
            residuals = y_true_labels - y_pred
            axes[1, i].scatter(y_pred, residuals, alpha=0.5)
            axes[1, i].axhline(y=0, color='r', linestyle='--')
            axes[1, i].set_xlabel('Predicted')
            axes[1, i].set_ylabel('Residuals')
            axes[1, i].set_title(f'Residuals vs Predicted ({name})')

    # Add Relevance Plot and Print
    if has_relevance:
        feature_names = X_train.columns if hasattr(X_train, 'columns') else [f"Feature {j}" for j in range(X_train.shape[1])]
        
        if has_importance:
            print("\n--- Feature Importances (Top 20) ---")
            relevance = pd.Series(model.feature_importances_, index=feature_names)
            title = "Top 20 Feature Importances"
        else:
            print("\n--- Model Coefficients (Top 20 by Absolute Value) ---")
            # Handle multi-output coef_ if necessary (take first row or mean)
            coef = model.coef_
            if coef.ndim > 1:
                coef = coef[0]
            relevance = pd.Series(coef, index=feature_names)
            title = "Top 20 Model Coefficients"

        # For sorting and plotting top 20, use absolute values but keep original for bar chart
        sort_relevance = relevance.abs().sort_values(ascending=False)
        top_indices = sort_relevance.head(20).index
        top_relevance = relevance.loc[top_indices]
        
        print(top_relevance)
        
        # Plot relevance
        imp_ax = axes[-1, 0]
        top_relevance.plot(kind='barh', ax=imp_ax).invert_yaxis()
        imp_ax.set_title(title)
        
        if axes.shape[1] > 1:
            axes[-1, 1].axis('off')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    return fig