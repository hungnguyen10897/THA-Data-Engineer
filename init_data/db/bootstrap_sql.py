bootstrap_queries = [
"""
    -- EXTERNAL SCHEMA AND TABLES
    CREATE EXTERNAL SCHEMA ext_tha_schema FROM DATA CATALOG 
    DATABASE 'hung_ext_tha_db' 
    iam_role '{REDSHIFT_SPECTRUM_ROLE_ARN}'
    CREATE EXTERNAL DATABASE IF NOT EXISTS;
""",
"""
    CREATE USER {REDSHIFT_THA_USER} PASSWORD '{REDSHIFT_THA_USER_PASSWORD}';
""","""
    DROP TABLE IF EXISTS revenues;
""","""
    CREATE TABLE revenues(
        campaign_id INT NOT NULL,
        banner_id INT NOT NULL,
        quarter INT NOT NULL,
        revenue FLOAT NOT NULL,
        number_of_clicks INT NOT NULL
);
""","""
    -- Impressions
    DROP TABLE IF EXISTS ext_tha_schema.impressions;
""","""
    CREATE EXTERNAL TABLE ext_tha_schema.impressions(
        banner_id INT8 ,
        campaign_id INT8
    )
    PARTITIONED BY (quarter INT)
    STORED AS PARQUET
    LOCATION 's3://{BUCKET}/impressions/';
""","""
    ALTER TABLE ext_tha_schema.impressions ADD
    PARTITION (quarter= 1) LOCATION 's3://{BUCKET}/impressions/quarter=1/'
    PARTITION (quarter= 2) LOCATION 's3://{BUCKET}/impressions/quarter=2/'
    PARTITION (quarter= 3) LOCATION 's3://{BUCKET}/impressions/quarter=3/'
    PARTITION (quarter= 4) LOCATION 's3://{BUCKET}/impressions/quarter=4/';
""","""
    -- Clicks
    DROP TABLE IF EXISTS ext_tha_schema.clicks;
""","""
    CREATE EXTERNAL TABLE ext_tha_schema.clicks(
        banner_id INT8 ,
        campaign_id INT8,
        click_id INT8
    )
    PARTITIONED BY (quarter INT)
    STORED AS PARQUET
    LOCATION 's3://{BUCKET}/clicks/';
""","""
    ALTER TABLE ext_tha_schema.clicks ADD
    PARTITION (quarter= 1) LOCATION 's3://{BUCKET}/clicks/quarter=1/'
    PARTITION (quarter= 2) LOCATION 's3://{BUCKET}/clicks/quarter=2/'
    PARTITION (quarter= 3) LOCATION 's3://{BUCKET}/clicks/quarter=3/'
    PARTITION (quarter= 4) LOCATION 's3://{BUCKET}/clicks/quarter=4/';
""","""
    -- Conversions
    DROP TABLE IF EXISTS ext_tha_schema.conversions;
""","""
    CREATE EXTERNAL TABLE ext_tha_schema.conversions(
        conversion_id INT8,
        click_id INT8,
        revenue FLOAT
    )
    PARTITIONED BY (quarter INT)
    STORED AS PARQUET
    LOCATION 's3://{BUCKET}/conversions/';
""","""
    ALTER TABLE ext_tha_schema.conversions ADD
    PARTITION (quarter= 1) LOCATION 's3://{BUCKET}/conversions/quarter=1/'
    PARTITION (quarter= 2) LOCATION 's3://{BUCKET}/conversions/quarter=2/'
    PARTITION (quarter= 3) LOCATION 's3://{BUCKET}/conversions/quarter=3/'
    PARTITION (quarter= 4) LOCATION 's3://{BUCKET}/conversions/quarter=4/';
""","""
    -- POPULATE INTERNAL AGGREGATED TABLE
    TRUNCATE TABLE revenues;
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
    FROM ext_tha_schema.impressions AS impressions
    LEFT JOIN ext_tha_schema.clicks AS clicks
    ON impressions.banner_id = clicks.banner_id
        AND impressions.campaign_id = clicks.campaign_id
        AND impressions.quarter = clicks.quarter
    LEFT JOIN  ext_tha_schema.conversions AS conversions
    ON clicks.click_id = conversions.click_id
        AND conversions.quarter = clicks.quarter
    GROUP BY impressions.campaign_id, impressions.banner_id, impressions.quarter;
""","""
    -- CREATE STORED PROCEDURES
    CREATE OR REPLACE PROCEDURE public.synch_new_impressions(ext_table character varying(256), quarter character varying(1))
    LANGUAGE plpgsql
    AS $$
    BEGIN

        DROP TABLE IF EXISTS temp;
        
        -- Create and Populate Temp View
        -- Temp View aggregates data from staging table and current 'revenues'
        EXECUTE(
        'CREATE TEMP TABLE temp AS '
        +  '( '
        +    'SELECT '
        +      'campaign_id, '
        +      'banner_id, '
        +      'quarter, '
        +      'SUM(revenue) AS revenue, '
        +      'SUM(number_of_clicks) AS number_of_clicks '
        +    'FROM ' 
        +    '( '
        +      'SELECT '
        +        'impressions.campaign_id AS campaign_id, '
        +        'impressions.banner_id AS banner_id, '
        +        quarter || ' AS quarter, '
        +        'CASE '
        +            'WHEN SUM(conversions.revenue) IS NOT NULL THEN SUM(conversions.revenue) '
        +            'ELSE 0 '
        +        'END AS revenue, '
        +        'CASE '
        +            'WHEN COUNT(clicks.click_id) IS NOT NULL THEN COUNT(clicks.click_id) '
        +            'ELSE 0 '
        +        'END AS number_of_clicks '
        +      'FROM ( '
        +        'SELECT * FROM ' || ext_table
        +      ') AS impressions '
        +      'LEFT JOIN '
        +        '( '
        +          'SELECT * FROM ext_tha_schema.clicks WHERE quarter= ' || quarter
        +        ') AS clicks '
        +      'ON impressions.banner_id = clicks.banner_id '
        +         'AND impressions.campaign_id = clicks.campaign_id '
        +      'LEFT JOIN '
        +        '( '
        +          'SELECT * FROM ext_tha_schema.conversions WHERE quarter= ' || quarter
        +        ') AS conversions '
        +      'ON clicks.click_id = conversions.click_id '
        +      'GROUP BY impressions.campaign_id, impressions.banner_id '
        +      'UNION ALL '
        +      'SELECT * FROM revenues '
        +    ') '
        +    'GROUP BY campaign_id, banner_id, quarter '
        +  '); '
        );
        
        -- Replace revenues with temp
        TRUNCATE TABLE revenues;

        INSERT INTO revenues SELECT * FROM temp;
        
        DROP TABLE temp;
    END;
    $$;
""","""
    CREATE OR REPLACE PROCEDURE public.synch_new_clicks(ext_table character varying(256), quarter character varying(1))
    LANGUAGE plpgsql
    AS $$
    BEGIN

        DROP TABLE IF EXISTS temp;
        
        -- Create and Populate Temp View
        -- Temp View aggregates data from staging table and current 'revenues'
        EXECUTE(
        'CREATE TEMP TABLE temp AS '
        +  '( '
        +    'SELECT '
        +      'campaign_id, '
        +      'banner_id, '
        +      'quarter, '
        +      'SUM(revenue) AS revenue, '
        +      'SUM(number_of_clicks) AS number_of_clicks '
        +    'FROM ' 
        +    '( '
        +      'SELECT '
        +        'impressions.campaign_id AS campaign_id, '
        +        'impressions.banner_id AS banner_id, '
        +        quarter || ' AS quarter, '
        +        'CASE '
        +            'WHEN SUM(conversions.revenue) IS NOT NULL THEN SUM(conversions.revenue) '
        +            'ELSE 0 '
        +        'END AS revenue, '
        +        'CASE '
        +            'WHEN COUNT(clicks.click_id) IS NOT NULL THEN COUNT(clicks.click_id) '
        +            'ELSE 0 '
        +        'END AS number_of_clicks '
        +      'FROM ( '
        +        'SELECT * FROM ext_tha_schema.impressions WHERE quarter= ' || quarter
        +      ') AS impressions '
        +      'JOIN '
        +        '( '
        +          'SELECT * FROM ' || ext_table
        +        ') AS clicks '
        +      'ON impressions.banner_id = clicks.banner_id '
        +         'AND impressions.campaign_id = clicks.campaign_id '
        +      'LEFT JOIN '
        +        '( '
        +          'SELECT * FROM ext_tha_schema.conversions WHERE quarter= ' || quarter
        +        ') AS conversions '
        +      'ON clicks.click_id = conversions.click_id '
        +      'GROUP BY impressions.campaign_id, impressions.banner_id '
        +      'UNION ALL '
        +      'SELECT * FROM revenues '
        +    ') '
        +    'GROUP BY campaign_id, banner_id, quarter '
        +  '); '
        );
        
        -- Replace revenues with temp
        TRUNCATE TABLE revenues;

        INSERT INTO revenues SELECT * FROM temp;
        
        DROP TABLE temp;
    END;
    $$;
""","""
    CREATE OR REPLACE PROCEDURE public.synch_new_conversions(ext_table character varying(256), quarter character varying(256))
    LANGUAGE plpgsql
    AS $$
    BEGIN

        DROP TABLE IF EXISTS temp;
        
        -- Create and Populate Temp View
        -- Temp View aggregates data from staging table and current 'revenues'
        EXECUTE(
        'CREATE TEMP TABLE temp AS '
        +  '( '
        +    'SELECT '
        +      'campaign_id, '
        +      'banner_id, '
        +      'quarter, '
        +      'SUM(revenue) AS revenue, '
        +      'SUM(number_of_clicks) AS number_of_clicks '
        +    'FROM ' 
        +    '( '
        +      'SELECT '
        +        'impressions.campaign_id AS campaign_id, '
        +        'impressions.banner_id AS banner_id, '
        +        quarter || ' AS quarter, '
        +        'CASE '
        +            'WHEN SUM(conversions.revenue) IS NOT NULL THEN SUM(conversions.revenue) '
        +            'ELSE 0 '
        +        'END AS revenue, '
        +        '0 AS number_of_clicks '
        +      'FROM ( '
        +        'SELECT * FROM ext_tha_schema.impressions WHERE quarter= ' || quarter
        +      ') AS impressions '
        +      'JOIN '
        +        '( '
        +          'SELECT * FROM ext_tha_schema.clicks WHERE quarter= ' || quarter
        +        ') AS clicks '
        +      'ON impressions.banner_id = clicks.banner_id '
        +         'AND impressions.campaign_id = clicks.campaign_id '
        +      'JOIN '
        +        '( '
        +          'SELECT * FROM ' || ext_table
        +        ') AS conversions '
        +      'ON clicks.click_id = conversions.click_id '
        +      'GROUP BY impressions.campaign_id, impressions.banner_id '
        +      'UNION ALL '
        +      'SELECT * FROM revenues '
        +    ') '
        +    'GROUP BY campaign_id, banner_id, quarter '
        +  '); '
        );
        
        -- Replace revenues with temp
        TRUNCATE TABLE revenues;

        INSERT INTO revenues SELECT * FROM temp;
        
        DROP TABLE temp;
    END;
    $$;
""","""
    GRANT ALL PRIVILEGES ON DATABASE {REDSHIFT_DATABASE} TO {REDSHIFT_THA_USER};
""","""
    ALTER SCHEMA public OWNER TO {REDSHIFT_THA_USER};
""","""
    GRANT ALL PRIVILEGES ON ALL PROCEDURES IN SCHEMA public TO {REDSHIFT_THA_USER};
""","""
    ALTER TABLE public.revenues OWNER TO {REDSHIFT_THA_USER};
""","""
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {REDSHIFT_THA_USER};
""","""
    ALTER SCHEMA ext_tha_schema OWNER TO {REDSHIFT_THA_USER};
""","""
    GRANT USAGE ON SCHEMA ext_tha_schema to {REDSHIFT_THA_USER};
""","""
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ext_tha_schema TO {REDSHIFT_THA_USER};
"""
]
