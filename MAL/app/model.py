import pandas as pd
import joblib
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import SGD, Adam
from tensorflow.keras import regularizers
from tensorflow.keras.layers import Dense, Input, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

APP_DIR = Path(__file__).resolve().parent
DATASET_PATH = APP_DIR / "focus_dataset.csv"
MODEL_PATHS = {
    "decision_tree": APP_DIR / "dt_model.pkl",
    "random_forest": APP_DIR / "rf_model.pkl",
    "gradient_boosting": APP_DIR / "gb_model.pkl",
    "neural_network": APP_DIR / "nn_model.h5",
}
df = pd.read_csv(DATASET_PATH)

# Use columns that actually exist in your CSV to avoid the KeyError
FEATURE_COLUMNS = [col for col in ['temperature', 'humidity', 'co2_level', 'light_level'] if col in df.columns]

# If none of those match, fallback to whatever is in the CSV (like temperature or maxTemp)
if not FEATURE_COLUMNS:
    FEATURE_COLUMNS = df.drop(columns=['rating', 'timestamp', 'timePeriod'], errors='ignore').columns.tolist()

# Ensure we only keep numeric columns
X = df[FEATURE_COLUMNS].select_dtypes(include=[np.number])
FEATURE_COLUMNS = X.columns.tolist()
y = df['rating']

X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.2, random_state=42, stratify=y_train_val)


dt_model = DecisionTreeClassifier(random_state=42, max_depth=3) 
rf_model = RandomForestClassifier(random_state=42, n_estimators=100)
gb_model = GradientBoostingClassifier(random_state=42, n_estimators=100)

print("Training Tree Models...")
dt_model.fit(X_train, y_train)
rf_model.fit(X_train, y_train)
gb_model.fit(X_train, y_train)

dt_preds = dt_model.predict(X_val)
rf_preds = rf_model.predict(X_val)
gb_preds = gb_model.predict(X_val)

nn_model = Sequential([
    Input(shape=(X_train.shape[1],)),
    Dense(16, activation='relu'),
    Dense(6, activation='softmax')
])

nn_model.compile(optimizer=Adam(learning_rate=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

print("Training Neural Network...")
nn_history = nn_model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=50, verbose=0)

print("\n--- Model Accuracies ---")
print(f"Decision Tree     - Train: {dt_model.score(X_train, y_train):.4f}, Val: {dt_model.score(X_val, y_val):.4f}")
print(f"Random Forest     - Train: {rf_model.score(X_train, y_train):.4f}, Val: {rf_model.score(X_val, y_val):.4f}")
print(f"Gradient Boosting - Train: {gb_model.score(X_train, y_train):.4f}, Val: {gb_model.score(X_val, y_val):.4f}")
print(f"Neural Network    - Train: {nn_history.history['accuracy'][-1]:.4f}, Val: {nn_history.history['val_accuracy'][-1]:.4f}")

# Save the models
joblib.dump(dt_model, MODEL_PATHS["decision_tree"])
joblib.dump(rf_model, MODEL_PATHS["random_forest"])
joblib.dump(gb_model, MODEL_PATHS["gradient_boosting"])
nn_model.save(MODEL_PATHS["neural_network"])


def predict(temperature, humidity, co2_level, light_level):
    input_df = pd.DataFrame(
        [[temperature, humidity, co2_level, light_level]],
        columns=FEATURE_COLUMNS
    )
    prediction = rf_model.predict(input_df)
    return int(prediction[0])
