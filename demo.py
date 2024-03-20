import pandas as pd
import xgboost as xgb
from sqlalchemy import create_engine


model = xgb.XGBRegressor()
model.load_model("model.json")

engine = create_engine('postgresql://user:pass@localhost:5432/patients')
query = "SELECT * FROM patients;"
df = pd.read_sql_query(query, engine)

columns_to_drop = [col for col in df.columns if col.startswith('facid_')]
X = df.set_index('eid').drop(columns=columns_to_drop)

predictions = model.predict(X)
df_with_predictions = X.assign(lengthofstay=predictions)
mask = df_with_predictions["rcount"].lt(2) & df_with_predictions["lengthofstay"].gt(1)
filtered = df_with_predictions[mask]
result = filtered.reset_index()[['eid']]
print(result)
