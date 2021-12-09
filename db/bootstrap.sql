-- Will be deployed by Terraform
-- INTERNAL
CREATE DATABASE tha;

CREATE USER tha_admin PASSWORD 'WJsXNo1TNw';
GRANT ALL PRIVILEGES ON DATABASE tha TO tha_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tha_admin;

DROP TABLE IF EXISTS revenues;
CREATE TABLE revenues(
    campaign_id INT,
    banner_id INT,
    quarter INT,
    revenue INT,
    number_of_clicks INT
)


-- EXTERNAL SCHEMA AND TABLES
CREATE EXTERNAL SCHEMA ext_tha_schema FROM DATA CATALOG 
DATABASE 'hung_ext_tha_db' 
iam_role 'arn:aws:iam::939595455984:role/hung-redshift-spectrum'
CREATE EXTERNAL DATABASE IF NOT EXISTS;

-- Impressions
DROP TABLE IF EXISTS ext_tha_schema.impressions;
CREATE EXTERNAL TABLE ext_tha_schema.impressions(
    banner_id INT8 ,
    campaign_id INT8
)
PARTITIONED BY (quarter INT)
STORED AS PARQUET
LOCATION 's3://hungthas3/impressions/';

ALTER TABLE ext_tha_schema.impressions ADD
PARTITION (quarter= 1) LOCATION 's3://hungthas3/impressions/quarter=1/'
PARTITION (quarter= 2) LOCATION 's3://hungthas3/impressions/quarter=2/'
PARTITION (quarter= 3) LOCATION 's3://hungthas3/impressions/quarter=3/'
PARTITION (quarter= 4) LOCATION 's3://hungthas3/impressions/quarter=4/';

-- Clicks
DROP TABLE IF EXISTS ext_tha_schema.clicks;
CREATE EXTERNAL TABLE ext_tha_schema.clicks(
    banner_id INT8 ,
    campaign_id INT8,
    click_id INT8
)
PARTITIONED BY (quarter INT)
STORED AS PARQUET
LOCATION 's3://hungthas3/clicks/';

ALTER TABLE ext_tha_schema.clicks ADD
PARTITION (quarter= 1) LOCATION 's3://hungthas3/clicks/quarter=1/'
PARTITION (quarter= 2) LOCATION 's3://hungthas3/clicks/quarter=2/'
PARTITION (quarter= 3) LOCATION 's3://hungthas3/clicks/quarter=3/'
PARTITION (quarter= 4) LOCATION 's3://hungthas3/clicks/quarter=4/';

-- Conversions
DROP TABLE IF EXISTS ext_tha_schema.conversions;
CREATE EXTERNAL TABLE ext_tha_schema.conversions(
    conversion_id INT8,
    click_id INT8,
    revenue FLOAT
)
PARTITIONED BY (quarter INT)
STORED AS PARQUET
LOCATION 's3://hungthas3/conversions/';

ALTER TABLE ext_tha_schema.conversions ADD
PARTITION (quarter= 1) LOCATION 's3://hungthas3/conversions/quarter=1/'
PARTITION (quarter= 2) LOCATION 's3://hungthas3/conversions/quarter=2/'
PARTITION (quarter= 3) LOCATION 's3://hungthas3/conversions/quarter=3/'
PARTITION (quarter= 4) LOCATION 's3://hungthas3/conversions/quarter=4/';

-- POPULATE INTERNAL AGGREGATED TABLE
TRUNCATE TABLE revenues
INSERT INTO revenues
SELECT
    impressions.campaign_id AS campaign_id,
    impressions.banner_id AS banner_id,
    impressions.quarter AS quarter,
    CASE
  		WHEN SUM(conversions.revenue) IS NOT NULL THEN SUM(conversions.revenue)
  		ELSE 0
    END AS revenue,
    CASE 
  		WHEN COUNT(clicks.click_id) IS NOT NULL THEN COUNT(clicks.click_id)
  		ELSE 0
    END AS number_of_clicks
FROM
  (
    SELECT * FROM ext_tha_schema.impressions 
  ) AS impressions
  LEFT JOIN
  (
    SELECT * FROM ext_tha_schema.clicks
  ) AS clicks
  ON
  	impressions.banner_id = clicks.banner_id
  	AND impressions.campaign_id = clicks.campaign_id
    AND impressions.quarter = clicks.quarter
  LEFT JOIN 
  (
    SELECT * FROM ext_tha_schema.conversions
  ) AS conversions
  ON clicks.click_id = conversions.click_id
  	AND conversions.quarter = clicks.quarter
GROUP BY impressions.campaign_id, impressions.banner_id, impressions.quarter;

