import pytest
from dateutil.parser import isoparse
from flask import Flask, request

INITIAL_CHARGE = 1
DISTANCE_CHARGE = 0.5
DISTANCE_INCREMENT = 0.2 #1/5 of a mile
# START_TIME =  "2020-06-19T14:01:17.031Z" # ISO DATE
NIGHT_CHARGE = 0.5
BUSY_CHARGE = 1
DURATION = 1000 #seconds

def add_initial_charge(initial_charge=INITIAL_CHARGE):
    """Add initial charge to taxi ride, if value not specified uses INITIAL_CHARGE constant"""
    try:
        if float(initial_charge):
            return initial_charge
    except:
        raise TypeError("Only floats are allowed")
  
def add_start_time_charge(start_time):
    """Add time and duration related charges"""
    native_datetime_start_time = isoparse(start_time)
    tmp_hour = native_datetime_start_time.hour
    # night charge
    if tmp_hour >= 20 or tmp_hour < 6:
        res = NIGHT_CHARGE
    # busy charge
    elif tmp_hour >= 16 and tmp_hour < 19:
        res = BUSY_CHARGE
    else:
        res = 0
    return res

def add_distance_charge(distance, start_time, distance_charge=DISTANCE_CHARGE, distance_increment=DISTANCE_INCREMENT):
    """Add distance charge to taxi ride, if value not specified uses DISTANCE_CHARGE and DISTANCE_INCREMENT constant"""
    try:
        if float(distance) and float(distance_charge) and float(distance_increment):
            return (distance/distance_increment)*(distance_charge+add_start_time_charge(start_time))
    except:
        raise TypeError("Only floats are allowed")

def compute_ride_charge(distance, start_time, initial_charge=INITIAL_CHARGE, distance_charge=DISTANCE_CHARGE, distance_increment=DISTANCE_INCREMENT):
    """Compute taxi ride fare, distance in miles, start_time as an ISO date. If value not specified uses INITIAL_CHARGE, DISTANCE_CHARGE and DISTANCE_INCREMENT constant"""
    return add_initial_charge(initial_charge) + add_distance_charge(distance, start_time, distance_charge, distance_increment) 

def test_add_initial_charge():
    assert add_initial_charge()==1
    assert add_initial_charge(2.5)==2.5

def test_add_initial_charge_exception():
    with pytest.raises(TypeError) as e:
        assert add_initial_charge("test")
    assert str(e.value) == "Only floats are allowed" 

def test_add_distance_charge():
    assert add_distance_charge(10,"2020-06-19T14:01:17.031Z")==10*DISTANCE_CHARGE/DISTANCE_INCREMENT
    assert add_distance_charge(10,"2020-06-19T14:01:17.031Z",1.2,0.1)==120

def test_add_distance_charge_exception():
    with pytest.raises(TypeError) as e:
        assert add_distance_charge("test",14)
    assert str(e.value) == "Only floats are allowed" 

def test_add_start_time_charge():
    assert add_start_time_charge("2020-06-19T14:01:17.031Z")==0 # No added charge 06:00 - 16:00
    assert add_start_time_charge("2020-06-19T17:01:17.031Z")==1 # Add busy charge 16:00 - 19:00
    assert add_start_time_charge("2020-06-19T19:59:17.031Z")==0 # No added charge 19:00 - 20:00
    assert add_start_time_charge("2020-06-19T05:59:17.031Z")==0.5 # Add night charge 20:00 - 06:00
    assert add_start_time_charge("2020-06-19T06:00:00.000Z")==0 # No added charge 06:00 - 16:00
    assert add_start_time_charge("2020-06-19T20:59:17.031Z")==0.5 # Add night charge 20:00 - 06:00

def test_add_start_time_charge_exception():
    with pytest.raises(ValueError) as e:
        assert add_start_time_charge("2020-06-19T25:59:17.031Z")
    assert str(e.value) == "hour must be in 0..23" 


def test_compute_ride_charge():
    assert compute_ride_charge(10, "2020-06-19T14:01:17.031Z")==26
    assert compute_ride_charge(10, "2020-06-19T14:01:17.031Z", 5)==30
    assert compute_ride_charge(10, "2020-06-19T14:01:17.031Z", 5, 1.2,0.1)==125

app = Flask(__name__)
@app.route('/', methods=['POST'])
def result():
    print(request.form['foo']) # should display 'bar'
    # return 'Received !' # response to your request.
    return str(compute_ride_charge(10, "2020-06-19T14:01:17.031Z", 5, 1.2,0.1))

# result()