import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy.stats import skew

def handle_skewness(df, threshold=0.75, applied_transforms=None):
    """
    Detects and handles column skewness using Log or Square transformations.
    If applied_transforms is provided, it applies those specific transforms instead of detecting them.
    """
    df_transformed = df.copy()
    numeric_cols = df_transformed.select_dtypes(include=[np.number]).columns
    
    if applied_transforms is None:
        applied_transforms = {}
        for col in numeric_cols:
            skew_val = skew(df_transformed[col])
            if skew_val > threshold:
                applied_transforms[col] = 'log'
            elif skew_val < -threshold:
                applied_transforms[col] = 'square'
    
    for col, transform in applied_transforms.items():
        if col in df_transformed.columns:
            if transform == 'log':
                df_transformed[col] = np.log1p(df_transformed[col])
            elif transform == 'square':
                df_transformed[col] = np.square(df_transformed[col])
                
    return df_transformed, applied_transforms

def combine_highly_correlated(df, threshold=0.8, applied_reductions=None):
    """
    Combines highly correlated features by multiplying them and dropping the original columns.
    If applied_reductions is provided, it applies those specific combinations.
    """
    df_reduced = df.copy()
    
    if applied_reductions is None:
        applied_reductions = []
        while True:
            corr_matrix = df_reduced.corr().abs()
            upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
            pairs = upper[upper > threshold].stack().dropna().sort_values(ascending=False)
            
            if pairs.empty:
                break
                
            (feat1, feat2), correlation_value = pairs.index[0], pairs.values[0]
            applied_reductions.append((feat1, feat2))
            
            new_col_name = f"{feat1}_{feat2}"
            df_reduced[new_col_name] = df_reduced[feat1] * df_reduced[feat2]
            df_reduced = df_reduced.drop(columns=[feat1, feat2])
    else:
        for feat1, feat2 in applied_reductions:
            new_col_name = f"{feat1}_{feat2}"
            if feat1 in df_reduced.columns and feat2 in df_reduced.columns:
                df_reduced[new_col_name] = df_reduced[feat1] * df_reduced[feat2]
                df_reduced = df_reduced.drop(columns=[feat1, feat2])
        
    return df_reduced, applied_reductions

class AutomatedPreprocessor:
    """
    A helper class to bundle the preprocessing steps:
    1. Skewness handling
    2. Correlation-based combination
    3. Scaling
    """
    def __init__(self, skew_threshold=0.75, corr_threshold=0.8):
        self.skew_threshold = skew_threshold
        self.corr_threshold = corr_threshold
        self.skew_transforms = None
        self.corr_reductions = None
        self.scaler = StandardScaler()
        self.columns = None

    def fit_transform(self, X):
        X_skewed, self.skew_transforms = handle_skewness(X, threshold=self.skew_threshold)
        X_reduced, self.corr_reductions = combine_highly_correlated(X_skewed, threshold=self.corr_threshold)
        
        X_scaled = self.scaler.fit_transform(X_reduced)
        self.columns = X_reduced.columns
        
        return pd.DataFrame(X_scaled, columns=self.columns)

    def transform(self, X):
        if self.skew_transforms is None:
            raise ValueError("Preprocessor must be fitted before transform.")
            
        X_skewed, _ = handle_skewness(X, applied_transforms=self.skew_transforms)
        X_reduced, _ = combine_highly_correlated(X_skewed, applied_reductions=self.corr_reductions)
        
        X_scaled = self.scaler.transform(X_reduced)
        return pd.DataFrame(X_scaled, columns=self.columns)
