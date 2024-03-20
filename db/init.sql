CREATE TABLE patients(
    eid INTEGER,
    rcount INTEGER,
    gender INTEGER,
    dialysisrenalendstage INTEGER,
    asthma INTEGER,
    irondef INTEGER,
    pneum INTEGER,
    substancedependence INTEGER,
    psychologicaldisordermajor INTEGER,
    depress INTEGER,
    psychother INTEGER,
    fibrosisandother INTEGER,
    malnutrition INTEGER,
    hemo INTEGER,
    hematocrit DOUBLE PRECISION,
    neutrophils DOUBLE PRECISION,
    sodium DOUBLE PRECISION,
    glucose DOUBLE PRECISION,
    bloodureanitro DOUBLE PRECISION,
    creatinine DOUBLE PRECISION,
    bmi DOUBLE PRECISION,
    pulse INTEGER,
    respiration DOUBLE PRECISION,
    secondarydiagnosisnonicd9 INTEGER,
    facid_A DOUBLE PRECISION,
    facid_B DOUBLE PRECISION,
    facid_C DOUBLE PRECISION,
    facid_D DOUBLE PRECISION,
    facid_E DOUBLE PRECISION
);

COPY patients(eid, rcount, gender, dialysisrenalendstage, asthma, irondef, pneum, substancedependence, psychologicaldisordermajor, depress, psychother, fibrosisandother, malnutrition, hemo, hematocrit, neutrophils, sodium, glucose, bloodureanitro, creatinine, bmi, pulse, respiration, secondarydiagnosisnonicd9, facid_A, facid_B, facid_C, facid_D, facid_E)
FROM '/app/data/patients.csv'
DELIMITER ','
CSV HEADER;