import pandas as pd
import xgboost as xgb
from sqlalchemy import create_engine


model = xgb.XGBRegressor()
model.load_model("model.json")

engine = create_engine('postgresql://user:pass@localhost:5432/patients')
query = "SELECT * FROM patients;"
df = pd.read_sql_query(query, engine)

X = df.set_index('eid').drop(columns=['lengthofstay'] + [col for col in df.columns if col.startswith('facid_')])

predictions = model.predict(X)
df_with_predictions = X.assign(lengthofstay=predictions)
filtered = df_with_predictions[df_with_predictions["rcount"].lt(2) & df_with_predictions["lengthofstay"].gt(1)]
result = filtered.reset_index()[['eid']]
print(result)
