# THA Data Engineer

## 1. Architecture and Design Rationale

At minimum, the app must comprise of Data Storage and a Backend to process and serve requests. Since processing a request involves aggregating history data to return the correct result, and all of our data are well structured, I decided to use AWS Redshift as a Datawarehouse.

Intuitively, we don't want to over-query the DBMS by running a query that aggregate all time data for every request. An table called `revenues` contains aggregated data is generated, and now the backend only needs to query this table. 

_table layout_

With this new table, access to the original tables (`impressions`,`clicks`,`conversions`) is no longer neccessary. We only need those tables when there is new data and we need to compute the aggregations for `revenues`. Thus, I decide to store those tables in S3 to minimize cost from Redshift which is much more.

Redshift provides a fucntionality called Spectrum to directly query data files from S3. This is convenient in this case since we don't have to COPY the data back to Redshift in case we need any aggregations.





### 1.1 Permanent Storage
## Deployment
Deployment is done in 2 steps: Create a docker image to ensure everything needed is available during deployment.

First, create a credentials file in the root project directory so that the deplyoment container can deploy everything on your behalf
```
[default]
aws_access_key_id = <MY_ACCESS_KEY_ID>
aws_secret_access_key = <MY_SECRET_ACCESS_KEY>
```

```
docker build . -t tha-deployment && \
docker run -v $PWD/web:/app/web -v $PWD/init_data:/app/init_data -v $PWD/infra:/app/infra tha-deployment
```

## Performance Testing

## Unclarities and Assumptions

## Improvements
### Security
- Potential public S3
- Authentication to S3 objects through own account
- 


