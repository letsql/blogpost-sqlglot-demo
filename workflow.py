from letsql import transpile_predict
from sqlalchemy import create_engine
import pandas as pd

sql = "select patients.eid from patients where predict_xgb('model.json', patients.*) > 1 and patients.rcount < 2;"
sql = transpile_predict(sql)

engine = create_engine('postgresql://user:pass@localhost:5432/patients')
df = pd.read_sql_query(sql, engine)
print(df)
