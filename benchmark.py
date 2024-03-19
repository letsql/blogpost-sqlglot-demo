import pandas as pd
import xgboost as xgb
from sqlalchemy import create_engine

from letsql import transpile_predict

from timing import Timer

engine = create_engine('postgresql://user:pass@localhost:5432/patients')

with Timer("postgres + pandas"):
    model = xgb.XGBRegressor()
    model.load_model("model.json")

    query = "SELECT * FROM patients;"
    df = pd.read_sql_query(query, engine)

    X = df.set_index('eid').drop(columns=['lengthofstay'] + [col for col in df.columns if col.startswith('facid_')])

    predictions = model.predict(X)
    df_with_predictions = X.assign(lengthofstay=predictions)
    filtered = df_with_predictions[df_with_predictions["rcount"].lt(2) & df_with_predictions["lengthofstay"].gt(1)]
    expected = filtered.reset_index()[['eid']]

with Timer("postgres"):
    sql = "select patients.eid from patients where predict_xgb('model.json', patients.*) > 1 and patients.rcount < 2;"
    sql = transpile_predict(sql)
    actual = pd.read_sql_query(sql, engine)

pd.testing.assert_series_equal(expected.squeeze(), actual.squeeze(), check_names=False)
