import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

# Load the dataset
data = pd.read_csv('data/patients.csv')

# Separate features and target
X = data.drop(columns=['lengthofstay', 'eid'] + [col for col in data.columns if col.startswith('facid_')])
y = data['lengthofstay']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=54)

# Train XGBoost Regressor model
model = XGBRegressor(base_score=0.0, max_depth=3, n_estimators=10)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)

# Optionally, you can save the model
model.save_model('model.json')
