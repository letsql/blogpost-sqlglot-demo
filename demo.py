# the idea is to get a trained model
# and put it in the context of a sql query
# do branch pruning
# do tree pruning
# do model inlining / fetching only the required columns
# could we do data filtering?

# also talk about how the information encoded in the model is not taken into account
# how the modeler has to know which column to drop
# how data is pulled that is not used

import pandas as pd
import xgboost as xgb
from sqlalchemy import create_engine


model = xgb.XGBRegressor()
model.load_model("model.json")

engine = create_engine('postgresql://user:pass@localhost:5432/patients')
query = "SELECT * FROM patients;"
df = pd.read_sql_query(query, engine)
X = df.drop(columns=['lengthofstay', 'eid'] + [col for col in df.columns if col.startswith('facid_')])

predictions = model.predict(X)
df_with_predictions = X.assign(lengthofstay=predictions)
result = df_with_predictions[df_with_predictions["rcount"].lt(2) & df_with_predictions["lengthofstay"].gt(1)]
print(result)