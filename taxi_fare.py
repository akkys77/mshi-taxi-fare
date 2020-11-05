import pytest
from dateutil.parser import isoparse
from flask import Flask, request, jsonify
import json

INITIAL_CHARGE = 1
DISTANCE_CHARGE = 0.5
DISTANCE_INCREMENT = 0.2  # 1/5 of a mile
NIGHT_CHARGE = 0.5
BUSY_CHARGE = 1
DURATION = 1000  # seconds

#pylint: disable=too-many-arguments

class TaxiRide:
    def __init__(self, taxi_fare_id, distance, start_time, duration):
        self.taxi_fare_id = taxi_fare_id
        self.taxi_fares = []
        self.distance = distance
        self.start_time = start_time
        self.initial_charge = INITIAL_CHARGE
        self.distance_charge = DISTANCE_CHARGE
        self.distance_increment = DISTANCE_INCREMENT
        self.duration = duration

    def increment_taxi_fare_id(self):
        self.taxi_fare_id += 1

    def add_initial_charge(self):
        """Add initial charge to taxi ride, if value not specified uses INITIAL_CHARGE constant"""
        try:
            if float(self.initial_charge):
                return self.initial_charge
        except:
            raise TypeError("Only floats are allowed")

    def add_start_time_charge(self):
        """Add time and duration related charges"""
        native_datetime_start_time = isoparse(self.start_time)
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

    def add_distance_charge(self):
        """Add distance charge to taxi ride, if value not specified uses DISTANCE_CHARGE and DISTANCE_INCREMENT constant"""
        try:
            if float(self.distance) and float(self.distance_charge) and float(self.distance_increment):
                return (self.distance/self.distance_increment)*(self.distance_charge + self.add_start_time_charge())
        except:
            raise TypeError("Only floats are allowed")

    def compute_ride_charge(self):
        """Compute taxi ride fare, distance in miles, start_time as an ISO date. If value not specified uses INITIAL_CHARGE, DISTANCE_CHARGE and DISTANCE_INCREMENT constant"""
        self.increment_taxi_fare_id()
        taxi_fare = self.add_initial_charge() + self.add_distance_charge()
        ride = {"id": self.taxi_fare_id, "distance": self.distance_increment,
                       "startTime": self.start_time, "duration": self.duration, "taxiFare":taxi_fare}
        self.taxi_fares.append(ride)
        return ride
    
    def get_taxi_fares(self):
        return self.taxi_fares


class TestTaxiRide():
    def setup(self):
        self.taxi_ride = TaxiRide(1,10, "2020-06-19T14:01:17.031Z")

    def test_add_initial_charge(self):
        assert self.taxi_ride.add_initial_charge() == 1
        self.taxi_ride.initial_charge = 2.5
        assert self.taxi_ride.add_initial_charge() == 2.5

    def test_add_initial_charge_exception(self):
        with pytest.raises(TypeError) as e:
            self.taxi_ride.initial_charge = "test"
            assert self.taxi_ride.add_initial_charge()
        assert str(e.value) == "Only floats are allowed"

    def test_add_distance_charge(self):
        assert self.taxi_ride.add_distance_charge() == 10*self.taxi_ride.distance_charge / \
            self.taxi_ride.distance_increment
        self.taxi_ride.distance_charge = 1.2
        self.taxi_ride.distance_increment = 0.1
        assert self.taxi_ride.add_distance_charge() == 120

    def test_add_distance_charge_exception(self):
        with pytest.raises(TypeError) as e:
            self.taxi_ride.distance = "test"
            assert self.taxi_ride.add_distance_charge()
        assert str(e.value) == "Only floats are allowed"

    # @pytest.mark.parametrize("time, expected", [("2020-06-19T14:01:17.031Z",0),("2020-06-19T17:01:17.031Z",1)])
    def test_add_start_time_charge(self):
        # No added charge 06:00 - 16:00
        self.taxi_ride.start_time = "2020-06-19T14:01:17.031Z"
        assert self.taxi_ride.add_start_time_charge() == 0
        # Add busy charge 16:00 - 19:00
        self.taxi_ride.start_time = "2020-06-19T17:01:17.031Z"
        assert self.taxi_ride.add_start_time_charge() == 1
        # No added charge 19:00 - 20:00
        self.taxi_ride.start_time = "2020-06-19T19:59:17.031Z"
        assert self.taxi_ride.add_start_time_charge() == 0
        # Add night charge 20:00 - 06:00
        self.taxi_ride.start_time = "2020-06-19T05:59:17.031Z"
        assert self.taxi_ride.add_start_time_charge() == 0.5
        # No added charge 06:00 - 16:00
        self.taxi_ride.start_time = "2020-06-19T06:00:00.000Z"
        assert self.taxi_ride.add_start_time_charge() == 0
        # Add night charge 20:00 - 06:00
        self.taxi_ride.start_time = "2020-06-19T20:59:17.031Z"
        assert self.taxi_ride.add_start_time_charge() == 0.5

    def test_add_start_time_charge_exception(self):
        with pytest.raises(ValueError) as e:
            self.taxi_ride.start_time = "2020-06-19T25:59:17.031Z"
            assert self.taxi_ride.add_start_time_charge()
        assert str(e.value) == "hour must be in 0..23"

    def test_compute_ride_charge(self):
        self.taxi_ride.duration = 10
        self.taxi_ride.start_time = "2020-06-19T14:01:17.031Z"
        assert self.taxi_ride.compute_ride_charge() == 26
        self.taxi_ride.duration = 10
        self.taxi_ride.start_time = "2020-06-19T14:01:17.031Z"
        self.taxi_ride.initial_charge = 5
        assert self.taxi_ride.compute_ride_charge() == 30
        self.taxi_ride.duration = 10
        self.taxi_ride.start_time = "2020-06-19T14:01:17.031Z"
        self.taxi_ride.initial_charge = 5
        self.taxi_ride.distance_charge = 1.2
        self.taxi_ride.distance_increment = 0.1
        assert self.taxi_ride.compute_ride_charge() == 125


app = Flask(__name__)


taxi_ride = TaxiRide(0, 0, "2020-06-19T14:01:17.031Z", 0)
@app.route('/', methods=['POST'])
def result():
    req = request.get_json()
    taxi_ride.distance = req['distance']
    taxi_ride.duration = req['duration']
    taxi_ride.start_time = req['startTime']
    return jsonify({'taxiFare': taxi_ride.compute_ride_charge()}), 200, {'ContentType': 'application/json'}

@app.route('/', methods=['GET'])
def return_all_taxi_rides():
    return jsonify(taxi_ride.get_taxi_fares())

@app.route('/<id>', methods=['GET'])
def return_a_taxi_ride(id):
    taxi_rides = taxi_ride.get_taxi_fares()
    res ="Not Found"
    for ride in taxi_rides:
        if int(ride['id'])==int(id):
            res = ride
            break
    return jsonify(res)

if __name__ == "__main__":
    app.run()
