import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

data = pd.read_csv("crop_recommendation.csv")

X = data.drop("crop", axis=1)
y = data["crop"]

model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, "crop_model.pkl")

print("Model trained successfully")