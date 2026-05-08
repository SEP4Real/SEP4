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
    precision_recall_curve,
    PrecisionRecallDisplay,
    roc_curve,
    roc_auc_score,
    RocCurveDisplay,
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)

def evaluate_model(model, X_train, X_test, y_train, y_test, is_classification=True):
    """
    Automatically evaluate the model on both training and test sets.
    Supports both classification and regression.
    
    Parameters:
    model: Trained model.
    X_train: Training features.
    X_test: Validation/Test features.
    y_train: Training labels.
    y_test: Validation/Test labels.
    is_classification: Boolean, if True uses classification metrics, else regression.
    """
    datasets = [('Train', X_train, y_train), ('Test/Validation', X_test, y_test)]
    
    if is_classification:
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    else:
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
    fig.suptitle(f'Model Evaluation: {type(model).__name__} ({"Classification" if is_classification else "Regression"})', fontsize=16)

    for i, (name, X, y) in enumerate(datasets):
        y_pred = model.predict(X)
        
        print(f"\n--- {name} Metrics ---")
        
        if is_classification:
            # Classification Logic
            # Check if multiclass
            unique_labels = np.unique(y)
            avg_method = 'binary' if len(unique_labels) <= 2 else 'weighted'
            
            acc = accuracy_score(y, y_pred)
            prec = precision_score(y, y_pred, average=avg_method, zero_division=0)
            rec = recall_score(y, y_pred, average=avg_method, zero_division=0)
            f1 = f1_score(y, y_pred, average=avg_method, zero_division=0)
            
            print(f"Accuracy:  {acc:.4f}")
            print(f"Precision ({avg_method}): {prec:.4f}")
            print(f"Recall ({avg_method}):    {rec:.4f}")
            print(f"F1 Score ({avg_method}):  {f1:.4f}")
            
            # Confusion Matrix
            cm = confusion_matrix(y, y_pred)
            disp_cm = ConfusionMatrixDisplay(confusion_matrix=cm)
            disp_cm.plot(ax=axes[i], cmap='Blues', colorbar=False)
            axes[i].set_title(f'Confusion Matrix ({name})')
        else:
            # Regression Logic
            mse = mean_squared_error(y, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            print(f"MSE:  {mse:.4f}")
            print(f"RMSE: {rmse:.4f}")
            print(f"MAE:  {mae:.4f}")
            print(f"R2:   {r2:.4f}")
            
            # Prediction vs Actual Plot
            axes[0, i].scatter(y, y_pred, alpha=0.5)
            axes[0, i].plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
            axes[0, i].set_xlabel('Actual')
            axes[0, i].set_ylabel('Predicted')
            axes[0, i].set_title(f'Predicted vs Actual ({name})')
            
            # Residual Plot
            residuals = y - y_pred
            axes[1, i].scatter(y_pred, residuals, alpha=0.5)
            axes[1, i].axhline(y=0, color='r', linestyle='--')
            axes[1, i].set_xlabel('Predicted')
            axes[1, i].set_ylabel('Residuals')
            axes[1, i].set_title(f'Residuals vs Predicted ({name})')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    return fig

if __name__ == "__main__":
    print("Model evaluation module loaded. Use evaluate_model(model, X_train, X_test, y_train, y_test) to evaluate your models.")
