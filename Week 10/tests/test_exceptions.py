import pytest

from economy_ticket import EconomyTicket
from exceptions import (BookingNotFoundError, BookingStateError,
                        BookingSystemError, DuplicatePassengerError,
                        EmptyBookingError, FlightFullError,
                        FlightNotBookableError, FlightNotFoundError,
                        InvalidBaggageError, InvalidFareError,
                        InvalidFlightStatusError, InvalidStateError,
                        InvalidValueError, NotFoundError,
                        ParticipationError, PassengerNotRegisteredError,
                        WrongObjectTypeError)
from passenger import Passenger


class TestExceptionHierarchy:
    @pytest.mark.parametrize('error_class, category', [
        (BookingNotFoundError, NotFoundError),
        (FlightNotFoundError, NotFoundError),
        (PassengerNotRegisteredError, NotFoundError),
        (BookingStateError, InvalidStateError),
        (FlightNotBookableError, InvalidStateError),
        (FlightFullError, InvalidStateError),
        (InvalidFareError, InvalidValueError),
        (InvalidBaggageError, InvalidValueError),
        (InvalidFlightStatusError, InvalidValueError),
        (EmptyBookingError, InvalidValueError),
        (WrongObjectTypeError, ParticipationError),
        (DuplicatePassengerError, ParticipationError),
    ])
    def test_each_error_belongs_to_its_category(self, error_class,
                                                category):
        assert issubclass(error_class, category)
        assert issubclass(category, BookingSystemError)
        assert issubclass(BookingSystemError, Exception)

    def test_parent_class_catches_a_specific_error(self, system):
        # Catching the parent works for any booking error.
        with pytest.raises(BookingSystemError):
            system.get_booking('BK0404')


class TestEconomyBaggage:
    @pytest.mark.parametrize('bad_count', [-1, 'one', 1.5, None, True])
    def test_bad_bag_counts_are_rejected(self, bad_count):
        with pytest.raises(InvalidBaggageError) as error:
            EconomyTicket(250.0, bad_count)
        assert error.value.ticket_type == 'Economy'
        assert error.value.max_bags is None

    def test_message_explains_the_rule(self):
        with pytest.raises(InvalidBaggageError) as error:
            EconomyTicket(250.0, -2)
        assert str(error.value) == (
            'Economy only allows a whole number of 0 or more checked bags, '
            'got -2')


class TestLookups:
    def test_known_flight_is_found(self, system, delayed_flight):
        assert system.get_flight('QF643') is delayed_flight

    def test_unknown_flight_raises(self, system):
        with pytest.raises(FlightNotFoundError,
                           match='Flight QF999 is not in the booking'):
            system.get_flight('QF999')

    def test_known_booking_is_found(self, system, lui, scheduled_flight,
                                    economy_ticket):
        new_booking = system.create_booking(lui, scheduled_flight,
                                            economy_ticket)
        assert system.get_booking('BK0001') is new_booking

    def test_unknown_booking_raises(self, system):
        with pytest.raises(BookingNotFoundError):
            system.get_booking('BK0001')


class TestAddPassengerToBooking:
    def test_registered_passenger_is_added(self, system, lui, sam,
                                           scheduled_flight,
                                           economy_ticket):
        system.create_booking(lui, scheduled_flight, economy_ticket)
        updated = system.add_passenger_to_booking('BK0001', sam)
        assert updated.get_passengers() == [lui, sam]
        assert system.seats_booked(scheduled_flight) == 2

    def test_unregistered_passenger_raises(self, system, lui,
                                           scheduled_flight,
                                           economy_ticket):
        new_booking = system.create_booking(lui, scheduled_flight,
                                            economy_ticket)
        stranger = Passenger('Bob', 'bob@email.com', 'PZ999999')
        with pytest.raises(PassengerNotRegisteredError):
            system.add_passenger_to_booking('BK0001', stranger)
        assert new_booking.get_passengers() == [lui]

    def test_full_flight_raises(self, system, lui, sam, alex,
                                scheduled_flight, economy_ticket):
        # The scheduled flight has 3 seats.
        system.create_booking([lui, sam], scheduled_flight, economy_ticket)
        system.create_booking(alex, scheduled_flight, economy_ticket)
        extra = Passenger('Jo', 'jo@email.com', 'PD333444')
        system.register_passenger(extra)
        with pytest.raises(FlightFullError) as error:
            system.add_passenger_to_booking('BK0001', extra)
        assert error.value.seats_left == 0
        assert system.seats_booked(scheduled_flight) == 3

    def test_unknown_booking_raises(self, system, sam):
        with pytest.raises(BookingNotFoundError):
            system.add_passenger_to_booking('BK0077', sam)


class TestHandledRequests:
    # The request_* methods catch the error, report it and return None.
    # Nothing should escape to the caller.
    def test_successful_request_returns_the_booking(
            self, system, lui, scheduled_flight, economy_ticket):
        new_booking = system.request_booking(lui, scheduled_flight,
                                             economy_ticket)
        assert new_booking.get_booking_reference() == 'BK0001'
        assert system.get_error_log() == []

    def test_failed_booking_is_reported_not_raised(
            self, system, lui, cancelled_flight, economy_ticket, capsys):
        result = system.request_booking(lui, cancelled_flight,
                                        economy_ticket)
        assert result is None
        message = ('Could not create booking: Flight QF500 is cancelled '
                   'and is not taking bookings')
        assert message in capsys.readouterr().out
        assert system.get_error_log() == [message]

    def test_failed_booking_leaves_the_system_unchanged(
            self, system, lui, sam, alex, scheduled_flight, economy_ticket):
        system.request_booking([lui, sam], scheduled_flight, economy_ticket)
        before = str(system)
        stranger = Passenger('Bob', 'bob@email.com', 'PZ999999')
        system.request_booking([alex, stranger], scheduled_flight,
                               economy_ticket)
        assert str(system) == before
        assert system.seats_booked(scheduled_flight) == 2

    def test_system_keeps_working_after_a_failure(
            self, system, lui, cancelled_flight, delayed_flight,
            economy_ticket):
        assert system.request_booking(lui, cancelled_flight,
                                      economy_ticket) is None
        # The failure didn't use up a reference or break anything.
        next_booking = system.request_booking(lui, delayed_flight,
                                              economy_ticket)
        assert next_booking.get_booking_reference() == 'BK0001'

    def test_confirmation_request(self, system, lui, scheduled_flight,
                                  economy_ticket):
        new_booking = system.request_booking(lui, scheduled_flight,
                                             economy_ticket)
        assert system.request_confirmation('BK0001') is new_booking
        assert new_booking.get_status() == 'confirmed'

    def test_failed_confirmation_is_reported(self, system, lui,
                                             scheduled_flight,
                                             economy_ticket):
        new_booking = system.request_booking(lui, scheduled_flight,
                                             economy_ticket)
        system.request_confirmation('BK0001')
        assert system.request_confirmation('BK0001') is None
        assert new_booking.get_status() == 'confirmed'
        assert 'already confirmed' in system.get_error_log()[0]

    def test_unknown_reference_is_reported(self, system):
        assert system.request_confirmation('BK0404') is None
        assert system.request_cancellation('BK0404') is None
        assert len(system.get_error_log()) == 2

    def test_cancellation_request_frees_the_seats(
            self, system, lui, scheduled_flight, economy_ticket):
        system.request_booking(lui, scheduled_flight, economy_ticket)
        cancelled = system.request_cancellation('BK0001')
        assert cancelled.get_status() == 'cancelled'
        assert system.seats_booked(scheduled_flight) == 0

    def test_failed_cancellation_keeps_the_seat(
            self, system, lui, delayed_flight, economy_ticket):
        late = system.request_booking(lui, delayed_flight, economy_ticket)
        delayed_flight.set_status('departed')
        assert system.request_cancellation('BK0001') is None
        assert late.get_status() == 'pending'
        assert system.seats_booked(delayed_flight) == 1
        assert '0 cancelled' in str(system)

    def test_add_passenger_request(self, system, lui, sam,
                                   scheduled_flight, economy_ticket):
        system.request_booking(lui, scheduled_flight, economy_ticket)
        updated = system.request_add_passenger('BK0001', sam)
        assert updated.get_passengers() == [lui, sam]

    def test_duplicate_passenger_request_is_reported(
            self, system, lui, lui_duplicate, scheduled_flight,
            economy_ticket):
        new_booking = system.request_booking(lui, scheduled_flight,
                                             economy_ticket)
        assert system.request_add_passenger('BK0001', lui_duplicate) is None
        assert new_booking.get_passengers() == [lui]
        assert 'already on booking BK0001' in system.get_error_log()[0]

    def test_flight_status_change_request(self, system, delayed_flight):
        assert system.request_flight_status_change(
            'QF643', 'departed') is delayed_flight
        assert delayed_flight.get_status() == 'departed'

    def test_invalid_flight_status_request_is_reported(self, system,
                                                       delayed_flight):
        assert system.request_flight_status_change('QF643', 'boarding') \
            is None
        assert delayed_flight.get_status() == 'delayed'
        assert "Invalid flight status: 'boarding'" in (
            system.get_error_log()[0])

    def test_unknown_flight_status_request_is_reported(self, system):
        assert system.request_flight_status_change('QF999', 'delayed') \
            is None
        assert 'QF999' in system.get_error_log()[0]

    def test_error_log_is_a_copy(self, system):
        system.request_cancellation('BK0404')
        system.get_error_log().clear()
        assert len(system.get_error_log()) == 1
