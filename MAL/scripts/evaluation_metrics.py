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
    Displays feature relevance (importances or coefficients) in a separate plot.
    
    Parameters:
    model: Trained model (sklearn or keras).
    X_train: Training features.
    X_test: Validation/Test features.
    y_train: Training labels.
    y_test: Validation/Test labels.
    is_classification: Boolean, if True uses classification metrics, else regression.
    
    Returns:
    List of matplotlib figures: [fig_metrics, fig_relevance] (fig_relevance is optional)
    """
    datasets = [('Train', X_train, y_train), ('Test/Validation', X_test, y_test)]
    
    is_keras = 'keras' in str(type(model)).lower()
    model_name = type(model).__name__
    if is_keras:
        model_name = f"Keras {model_name}"

    # Performance Metrics Plot
    if is_classification:
        fig_metrics, axes_metrics = plt.subplots(1, 2, figsize=(15, 6))
    else:
        fig_metrics, axes_metrics = plt.subplots(2, 2, figsize=(15, 12))
        
    fig_metrics.suptitle(f'Model Evaluation: {model_name} ({"Classification" if is_classification else "Regression"})', fontsize=16)

    for i, (name, X, y) in enumerate(datasets):
        # Predict
        if is_keras:
            y_pred = model.predict(X, verbose=0)
        else:
            y_pred = model.predict(X)
            
        # Handle labels and predictions for classification
        y_true_labels = y
        if is_classification:
            if hasattr(y, 'ndim') and y.ndim > 1 and y.shape[1] > 1:
                y_true_labels = np.argmax(np.array(y), axis=1)
            
            if is_keras:
                if y_pred.ndim > 1 and y_pred.shape[1] > 1:
                    y_pred = np.argmax(y_pred, axis=1)
                elif y_pred.ndim > 1 and y_pred.shape[1] == 1:
                    y_pred = (y_pred > 0.5).astype(int).flatten()
                else:
                    y_pred = (y_pred > 0.5).astype(int)
        else:
            if hasattr(y_pred, 'ndim') and y_pred.ndim > 1:
                y_pred = y_pred.flatten()
            if hasattr(y, 'ndim') and y.ndim > 1:
                y_true_labels = np.array(y).flatten()

        print(f"\n--- {name} Metrics ---")
        
        if is_classification:
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
            
            cm = confusion_matrix(y_true_labels, y_pred)
            disp_cm = ConfusionMatrixDisplay(confusion_matrix=cm)
            disp_cm.plot(ax=axes_metrics[i], cmap='Blues', colorbar=False)
            axes_metrics[i].grid(False)
            axes_metrics[i].set_title(f'Confusion Matrix ({name})')
        else:
            mse = mean_squared_error(y_true_labels, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_true_labels, y_pred)
            r2 = r2_score(y_true_labels, y_pred)
            
            print(f"MSE:  {mse:.4f}")
            print(f"RMSE: {rmse:.4f}")
            print(f"MAE:  {mae:.4f}")
            print(f"R2:   {r2:.4f}")
            
            axes_metrics[0, i].scatter(y_true_labels, y_pred, alpha=0.5)
            axes_metrics[0, i].plot([y_true_labels.min(), y_true_labels.max()], [y_true_labels.min(), y_true_labels.max()], 'r--', lw=2)
            axes_metrics[0, i].set_xlabel('Actual')
            axes_metrics[0, i].set_ylabel('Predicted')
            axes_metrics[0, i].set_title(f'Predicted vs Actual ({name})')
            
            residuals = y_true_labels - y_pred
            axes_metrics[1, i].scatter(y_pred, residuals, alpha=0.5)
            axes_metrics[1, i].axhline(y=0, color='r', linestyle='--')
            axes_metrics[1, i].set_xlabel('Predicted')
            axes_metrics[1, i].set_ylabel('Residuals')
            axes_metrics[1, i].set_title(f'Residuals vs Predicted ({name})')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    figures = [fig_metrics]

    # Feature Relevance Plot (Separate Figure)
    has_importance = hasattr(model, 'feature_importances_')
    has_coef = hasattr(model, 'coef_')
    has_coefs = hasattr(model, 'coefs_') and len(model.coefs_) > 0
    
    if has_importance or has_coef or has_coefs:
        feature_names = X_train.columns if hasattr(X_train, 'columns') else [f"Feature {j}" for j in range(X_train.shape[1])]
        
        if has_importance:
            print("\n--- Feature Importances (Top 20) ---")
            relevance = pd.Series(model.feature_importances_, index=feature_names)
            relevance_title = "Top 20 Feature Importances"
        elif has_coef:
            print("\n--- Model Coefficients (Top 20 by Absolute Value) ---")
            coef = model.coef_
            if coef.ndim > 1: coef = coef[0]
            relevance = pd.Series(coef, index=feature_names)
            relevance_title = "Top 20 Model Coefficients"
        else:
            print("\n--- MLP Feature Relevance (Mean Absolute Weights of First Layer, Top 20) ---")
            mlp_relevance = np.mean(np.abs(model.coefs_[0]), axis=1)
            relevance = pd.Series(mlp_relevance, index=feature_names)
            relevance_title = "Top 20 MLP Feature Relevance (Mean Abs Weights)"

        sort_relevance = relevance.abs().sort_values(ascending=False)
        top_indices = sort_relevance.head(20).index
        top_relevance = relevance.loc[top_indices]
        print(top_relevance)
        
        fig_relevance, ax_relevance = plt.subplots(figsize=(10, 8))
        top_relevance.plot(kind='barh', ax=ax_relevance).invert_yaxis()
        ax_relevance.set_title(f"{relevance_title} ({model_name})")
        ax_relevance.set_xlabel("Value")
        plt.tight_layout()
        figures.append(fig_relevance)

    return figures


def compare_models(models, X_train, X_test, y_train, y_test, is_classification=True, plot_title="Model Comparison", pre_fitted=None):
    """
    Fits and evaluates a dictionary of models, displays a comparison table, and plots accuracy/metrics.
    
    Parameters:
    models: dict of model name -> model instance
    X_train: training features
    X_test: test/validation features
    y_train: training labels
    y_test: test/validation labels
    is_classification: True for classification models, False for regression models
    plot_title: Title for the bar plot
    pre_fitted: list of model names that are already fitted and should not be refit
    
    Returns:
    DataFrame containing the comparison results.
    """
    if pre_fitted is None:
        pre_fitted = []
        
    results = []
    for model_name, model in models.items():
        if model_name not in pre_fitted:
            model.fit(X_train, y_train)
            
        is_keras = 'keras' in str(type(model)).lower()
        if is_keras:
            train_pred = model.predict(X_train, verbose=0)
            test_pred = model.predict(X_test, verbose=0)
        else:
            train_pred = model.predict(X_train)
            test_pred = model.predict(X_test)
        
        if is_classification:
            y_train_true = y_train
            if hasattr(y_train, 'ndim') and y_train.ndim > 1 and y_train.shape[1] > 1:
                y_train_true = np.argmax(np.array(y_train), axis=1)
                
            y_test_true = y_test
            if hasattr(y_test, 'ndim') and y_test.ndim > 1 and y_test.shape[1] > 1:
                y_test_true = np.argmax(np.array(y_test), axis=1)
                
            train_pred_labels = train_pred
            test_pred_labels = test_pred
            
            if is_keras:
                if train_pred.ndim > 1 and train_pred.shape[1] > 1:
                    train_pred_labels = np.argmax(train_pred, axis=1)
                    test_pred_labels = np.argmax(test_pred, axis=1)
                elif train_pred.ndim > 1 and train_pred.shape[1] == 1:
                    train_pred_labels = (train_pred > 0.5).astype(int).flatten()
                    test_pred_labels = (test_pred > 0.5).astype(int).flatten()
                else:
                    train_pred_labels = (train_pred > 0.5).astype(int)
                    test_pred_labels = (test_pred > 0.5).astype(int)
                    
            train_acc = accuracy_score(y_train_true, train_pred_labels)
            test_acc = accuracy_score(y_test_true, test_pred_labels)
            test_f1 = f1_score(y_test_true, test_pred_labels, average="macro", zero_division=0)
            
            results.append({
                "Model": model_name,
                "Train Accuracy": train_acc,
                "Test Accuracy": test_acc,
                "Test Macro F1": test_f1,
            })
        else:
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
            train_r2 = r2_score(y_train, train_pred)
            test_r2 = r2_score(y_test, test_pred)
            results.append({
                "Model": model_name,
                "Train RMSE": train_rmse,
                "Test RMSE": test_rmse,
                "Train R2": train_r2,
                "Test R2": test_r2,
            })
            
    df_results = pd.DataFrame(results).set_index("Model")
    if is_classification:
        df_results = df_results.sort_values("Test Accuracy", ascending=False).round(4)
    else:
        df_results = df_results.sort_values("Test RMSE", ascending=True).round(4)
        
    try:
        from IPython.display import display
        display(df_results)
    except ImportError:
        print(df_results)
        
    fig, ax = plt.subplots(figsize=(9, 4))
    if is_classification:
        df_results[["Train Accuracy", "Test Accuracy"]].plot(kind="bar", ax=ax, edgecolor="black")
        ax.set_ylabel("Accuracy")
        ax.set_ylim(0, 1)
    else:
        df_results[["Train RMSE", "Test RMSE"]].plot(kind="bar", ax=ax, edgecolor="black")
        ax.set_ylabel("RMSE")
        
    ax.set_title(plot_title)
    plt.xticks(rotation=15, ha="right")
    ax.grid(axis="y")
    plt.tight_layout()
    plt.show()
    
    return df_results