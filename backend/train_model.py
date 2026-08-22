"""VOLT-LOGIC Battery ML Model Training Script

Trained from NASA Battery Cleaned Dataset (Battery_Data_Cleaned.csv) based on
Kata_Mamah_WIN_AIC.ipynb specifications.

Features:
- Capacity: Battery capacity measurement (Ah / normalized)
- Re: Electrolyte / internal ohmic resistance (Ohm)
- Rct: Charge transfer resistance (Ohm)
- ambient_temperature: Operational / ambient temperature (deg C)

Target (Battery_Status):
- HEALTHY ('aman'): Capacity > 0.8249 and Re < 0.0777 and Rct < 0.1251
- CRITICAL ('tidak aman'): Capacity < 0.7751 or Re > 0.0958 or Rct > 0.1589
- WARNING ('perlu di test lebih lanjut'): Otherwise
"""

import os
import csv
import json
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def find_dataset_path():
    candidates = [
        os.path.join(os.path.dirname(__file__), "Battery_Data_Cleaned.csv"),
        os.path.join(os.path.dirname(__file__), "data", "Battery_Data_Cleaned.csv"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "Battery_Data_Cleaned.csv"),
        "Battery_Data_Cleaned.csv",
        "backend/Battery_Data_Cleaned.csv",
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    raise FileNotFoundError("Could not find Battery_Data_Cleaned.csv in expected directories.")

def load_battery_dataset(csv_path: str):
    capacities = []
    res = []
    rcts = []
    temps = []
    labels = []

    # Thresholds defined in Kata_Mamah_WIN_AIC.ipynb
    # Capacity: mean = 0.8249, 25th = 0.7751
    # Re: mean = 0.0777, 75th = 0.0958
    # Rct: mean = 0.1251, 75th = 0.1589

    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cap = float(row["Capacity"])
                re_val = float(row["Re"])
                rct_val = float(row["Rct"])
                temp = float(row["ambient_temperature"])
            except (ValueError, KeyError):
                continue

            # Apply classification criteria from notebook
            if cap > 0.8249 and re_val < 0.0777 and rct_val < 0.1251:
                label = "HEALTHY"  # 'aman'
            elif cap < 0.7751 or re_val > 0.0958 or rct_val > 0.1589:
                label = "CRITICAL"  # 'tidak aman'
            else:
                label = "WARNING"  # 'perlu di test lebih lanjut'

            capacities.append(cap)
            res.append(re_val)
            rcts.append(rct_val)
            temps.append(temp)
            labels.append(label)

    X = np.column_stack([capacities, res, rcts, temps])
    y = np.array(labels)
    return X, y

def train_and_export_model():
    dataset_path = find_dataset_path()
    print(f"[LOAD] Loading dataset from: {dataset_path}")
    X, y = load_battery_dataset(dataset_path)
    print(f"[DATA] Dataset loaded: {X.shape[0]} samples with 4 features (Capacity, Re, Rct, ambient_temperature)")

    # Stratified Train-Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Build Pipeline with StandardScaler and Balanced Random Forest
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            class_weight="balanced",
            random_state=42,
            max_depth=15
        ))
    ])

    print("[TRAIN] Training Random Forest (Class Balanced) Pipeline...")
    pipeline.fit(X_train, y_train)

    # Evaluation
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n[EVAL] Model Evaluation Accuracy: {acc * 100:.2f}%")
    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred))

    # Save model artifact
    output_dir = os.path.join(os.path.dirname(__file__), "model")
    os.makedirs(output_dir, exist_ok=True)
    model_file = os.path.join(output_dir, "classifier.joblib")
    joblib.dump(pipeline, model_file)
    print(f"[SAVE] Exported serialized model pipeline to: {model_file}")

    # Save scaler params & metadata for front-end / inspection
    scaler = pipeline.named_steps["scaler"]
    metadata = {
        "model_name": "Battery_Health_Classifier",
        "version": "v2.0.0-battery-eis",
        "features": ["Capacity", "Re", "Rct", "ambient_temperature"],
        "classes": list(pipeline.classes_),
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "accuracy": round(float(acc), 4),
        "dataset_samples": int(X.shape[0]),
        "source_notebook": "Kata_Mamah_WIN_AIC.ipynb",
        "source_dataset": "Battery_Data_Cleaned.csv"
    }
    meta_path = os.path.join(output_dir, "model_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[META] Model metadata exported to: {meta_path}")

    return pipeline

if __name__ == "__main__":
    train_and_export_model()
