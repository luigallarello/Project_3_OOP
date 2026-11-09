import pytest

from exceptions import (FlightStatusChangeError, InvalidCapacityError,
                        InvalidFlightStatusError)
from flight import Flight


class TestFlightStatus:
    def test_constructor_keeps_a_valid_status(self, delayed_flight):
        assert delayed_flight.get_status() == 'delayed'

    def test_constructor_with_invalid_status_raises(self):
        # The flight is never created, so there's no invalid flight around.
        with pytest.raises(InvalidFlightStatusError) as error:
            Flight('QF1', 'SYD', 'MEL', '10:00', 100, 'boarding')
        assert error.value.status == 'boarding'
        assert 'boarding' in str(error.value)

    def test_status_can_be_set_to_scheduled(self, delayed_flight):
        delayed_flight.set_status('scheduled')
        assert delayed_flight.get_status() == 'scheduled'

    def test_status_can_be_set_to_delayed(self, scheduled_flight):
        scheduled_flight.set_status('delayed')
        assert scheduled_flight.get_status() == 'delayed'

    def test_status_can_be_set_to_departed(self, scheduled_flight):
        scheduled_flight.set_status('departed')
        assert scheduled_flight.get_status() == 'departed'

    def test_status_can_be_set_to_cancelled(self, scheduled_flight):
        scheduled_flight.set_status('cancelled')
        assert scheduled_flight.get_status() == 'cancelled'

    def test_invalid_status_raises_and_old_status_kept(self,
                                                       delayed_flight):
        with pytest.raises(InvalidFlightStatusError,
                           match="Invalid flight status: 'flying'"):
            delayed_flight.set_status('flying')
        assert delayed_flight.get_status() == 'delayed'

    def test_error_lists_the_valid_statuses(self, scheduled_flight):
        with pytest.raises(InvalidFlightStatusError) as error:
            scheduled_flight.set_status('boarding')
        assert 'cancelled, delayed, departed, scheduled' in str(error.value)

    def test_status_is_case_sensitive(self, scheduled_flight):
        with pytest.raises(InvalidFlightStatusError):
            scheduled_flight.set_status('CANCELLED')
        assert scheduled_flight.get_status() == 'scheduled'


class TestFlightString:
    def test_string_shows_route_time_status_and_seats(self,
                                                      scheduled_flight):
        assert str(scheduled_flight) == (
            'QF401: SYD -> MEL at 10:00 (scheduled, 3 seats)')

    def test_string_updates_after_status_change(self, scheduled_flight):
        scheduled_flight.set_status('delayed')
        assert '(delayed, 3 seats)' in str(scheduled_flight)


class TestFlightCapacity:
    def test_zero_capacity_is_allowed(self):
        # Boundary: the smallest valid capacity.
        assert Flight('QF0', 'SYD', 'NTL', '08:00', 0,
                      'scheduled').get_capacity() == 0

    @pytest.mark.parametrize('bad_capacity', [-1, 'lots', 2.5, True, None])
    def test_bad_capacity_is_rejected(self, bad_capacity):
        with pytest.raises(InvalidCapacityError) as error:
            Flight('QF1', 'SYD', 'MEL', '10:00', bad_capacity, 'scheduled')
        assert error.value.capacity == bad_capacity


class TestFlightStatusChanges:
    @pytest.mark.parametrize('final, new', [
        ('departed', 'scheduled'), ('departed', 'delayed'),
        ('cancelled', 'scheduled'), ('cancelled', 'departed'),
    ])
    def test_final_status_cannot_change(self, final, new):
        flight = Flight('QF1', 'SYD', 'MEL', '10:00', 100, final)
        with pytest.raises(FlightStatusChangeError) as error:
            flight.set_status(new)
        assert error.value.current_status == final
        assert error.value.new_status == new
        assert flight.get_status() == final

    def test_setting_the_same_final_status_is_allowed(self,
                                                      departed_flight):
        departed_flight.set_status('departed')
        assert departed_flight.get_status() == 'departed'

    def test_scheduled_and_delayed_flights_are_bookable(
            self, scheduled_flight, delayed_flight):
        assert scheduled_flight.is_bookable()
        assert delayed_flight.is_bookable()

    def test_departed_and_cancelled_flights_are_not_bookable(
            self, departed_flight, cancelled_flight):
        assert not departed_flight.is_bookable()
        assert not cancelled_flight.is_bookable()
