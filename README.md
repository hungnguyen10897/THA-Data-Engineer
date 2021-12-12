# THA Data Engineer

## 1. Architectture
The stack comprises of 4 main components
### 1.1 Permanent Storage
## Deployment
Deployment is done in a docker image to ensure everything needed is available during deployment.

First, create a credentials file in the root project directory so that the deplyoment container can deploy everything
on your behalf
```
[default]
aws_access_key_id = <MY_ACCESS_KEY_ID>
aws_secret_access_key = <MY_SECRET_ACCESS_KEY>
```

```
docker build . -t tha-deployment
```

```
docker run -v $PWD/web:/app/web -v $PWD/init_data:/app/init_data tha-deployment
```


## Performance Testing

## Unclarities and Assumptions

## Improvements
### Security
- Potential public S3
- Authentication to S3 objects through own account
- 


