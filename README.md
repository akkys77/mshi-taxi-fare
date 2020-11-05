# MSHI Taxi Fare

## Getting Started

### 1. Clone Repo

### 2. Create Virtual Environment

```
python3 -m venv env
source env/bin/activate
```

### 3. Install requirements

```
pip install -r requirements.txt
```

### 4. Launch Back End

```
python taxi_fare.py
```

### 5. Test curl request

#### 5.1. Post taxi fare request 

```
curl --location --request POST '127.0.0.1:5000' \
--header 'Content-Type: application/json' \
--data-raw '{
    "id": 1,
    "distance": 2,
    "startTime": "2020-06-19T13:01:17.031Z",
    "duration": 9000
}'

curl --location --request POST '127.0.0.1:5000' \
--header 'Content-Type: application/json' \
--data-raw '{
    "id": 2,
    "distance": 1,
    "startTime": "2020-06-19T12:01:17.031Z",
    "duration": 6000
}'

curl --location --request POST '127.0.0.1:5000' \
--header 'Content-Type: application/json' \
--data-raw '{
    "id": 3,
    "distance": 5,
    "startTime": "2020-06-19T14:01:17.031Z",
    "duration": 7000
}'
```

Sample result
```
{"data":{"distance":0.2,"duration":9000,"id":3,"startTime":"2020-06-19T13:01:17.031Z","taxiFare":6.0}}
```

#### 5.2. Get all taxi rides
```
curl --location --request GET '127.0.0.1:5000/'
```

Sample results
```
[{"distance":0.2,"duration":7000,"id":1,"startTime":"2020-06-19T14:01:17.031Z","taxiFare":13.5},{"distance":0.2,"duration":7000,"id":2,"startTime":"2020-06-19T14:01:17.031Z","taxiFare":13.5},{"distance":0.2,"duration":9000,"id":3,"startTime":"2020-06-19T13:01:17.031Z","taxiFare":6.0}]
```

#### 5.3. Get Specific ride

```
curl --location --request GET '127.0.0.1:5000/2'
```

Sample results
```
{"distance":0.2,"duration":7000,"id":2,"startTime":"2020-06-19T14:01:17.031Z","taxiFare":13.5}
```