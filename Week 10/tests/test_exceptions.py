import pytest

from business_ticket import BusinessTicket
from economy_ticket import EconomyTicket
from exceptions import (BookingNotFoundError, BookingStateError,
                        BookingSystemError, DuplicateFlightError,
                        DuplicatePassengerError, EmptyBookingError,
                        FlightFullError, FlightNotBookableError,
                        FlightNotFoundError, FlightStatusChangeError,
                        InvalidBaggageError, InvalidCapacityError,
                        InvalidFareError, InvalidFlightStatusError,
                        InvalidPassengerDetailsError, InvalidStateError,
                        InvalidValueError, NotFoundError,
                        ParticipationError, PassengerNotRegisteredError,
                        WrongObjectTypeError)
from flight import Flight
from passenger import Passenger


class TestExceptionHierarchy:
    @pytest.mark.parametrize('error_class, category', [
        (BookingNotFoundError, NotFoundError),
        (FlightNotFoundError, NotFoundError),
        (PassengerNotRegisteredError, NotFoundError),
        (BookingStateError, InvalidStateError),
        (FlightNotBookableError, InvalidStateError),
        (FlightFullError, InvalidStateError),
        (FlightStatusChangeError, InvalidStateError),
        (InvalidCapacityError, InvalidValueError),
        (InvalidPassengerDetailsError, InvalidValueError),
        (DuplicateFlightError, ParticipationError),
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


class TestCancelledSeats:
    # The booking's own status is the only record of a cancellation, so
    # cancelling through the booking or the system gives the same result.
    def test_cancelling_through_the_booking_frees_the_seat(
            self, system, lui, sam, two_seat_flight, economy_ticket):
        system.add_flight(two_seat_flight)
        first = system.create_booking([lui, sam], two_seat_flight,
                                      economy_ticket)
        first.cancel_booking()
        assert system.seats_booked(two_seat_flight) == 0
        assert '1 cancelled' in str(system)
        assert system.create_booking(lui, two_seat_flight,
                                     economy_ticket) is not None

    def test_seats_booked_needs_a_flight(self, system):
        with pytest.raises(WrongObjectTypeError, match='Expected a Flight'):
            system.seats_booked('QF401')


class TestMoreHandledRequests:
    def test_none_instead_of_passengers_is_reported(
            self, system, scheduled_flight, economy_ticket):
        assert system.request_booking(None, scheduled_flight,
                                      economy_ticket) is None
        assert 'Expected a list of Passengers' in system.get_error_log()[0]

    def test_flight_request_adds_a_new_flight(self, empty_system,
                                              scheduled_flight):
        assert empty_system.request_add_flight(
            scheduled_flight) is scheduled_flight
        assert '1 flight(s)' in str(empty_system)

    def test_duplicate_flight_request_is_reported(self, system):
        copy = Flight('QF401', 'SYD', 'OOL', '11:00', 10, 'scheduled')
        assert system.request_add_flight(copy) is None
        assert system.get_flight('QF401') is not copy
        assert 'already in the booking system' in system.get_error_log()[0]

    def test_passenger_request_registers_them(self, empty_system, lui):
        assert empty_system.request_register_passenger(lui) is lui
        assert '1 passenger(s)' in str(empty_system)

    def test_bad_passenger_request_is_reported(self, empty_system):
        assert empty_system.request_register_passenger('Lui') is None
        assert '0 passenger(s)' in str(empty_system)
        assert 'Expected a Passenger' in empty_system.get_error_log()[0]

    def test_reopening_a_departed_flight_is_reported(self, system,
                                                     departed_flight):
        assert system.request_flight_status_change('QF900',
                                                   'scheduled') is None
        assert departed_flight.get_status() == 'departed'
        assert 'cannot be changed to scheduled' in (
            system.get_error_log()[0])


class TestCreationRequests:
    # Objects built through the system are checked by their constructors.
    # A bad value is reported and None is returned instead of a crash.
    def test_valid_flight_is_created(self, empty_system):
        flight = empty_system.request_new_flight('QF1', 'SYD', 'MEL',
                                                 '10:00', 100, 'scheduled')
        assert isinstance(flight, Flight)
        assert flight.get_flight_number() == 'QF1'
        assert empty_system.get_error_log() == []

    def test_bad_capacity_is_reported(self, empty_system):
        assert empty_system.request_new_flight('QF1', 'SYD', 'MEL', '10:00',
                                               -5, 'scheduled') is None
        assert 'Could not create flight: Invalid capacity: -5' in (
            empty_system.get_error_log()[0])

    def test_bad_starting_status_is_reported(self, empty_system):
        assert empty_system.request_new_flight('QF1', 'SYD', 'MEL', '10:00',
                                               100, 'boarding') is None
        assert "'boarding'" in empty_system.get_error_log()[0]

    def test_valid_passenger_is_created(self, empty_system):
        passenger = empty_system.request_new_passenger('Lui',
                                                       'lui@email.com',
                                                       'PA123456')
        assert passenger.get_passport_number() == 'PA123456'

    def test_blank_passenger_name_is_reported(self, empty_system):
        assert empty_system.request_new_passenger('', 'lui@email.com',
                                                  'PA123456') is None
        assert 'Invalid passenger name' in empty_system.get_error_log()[0]

    def test_valid_economy_ticket_is_created(self, empty_system):
        ticket = empty_system.request_new_economy_ticket(250.0, 1)
        assert isinstance(ticket, EconomyTicket)
        assert ticket.calculate_price() == pytest.approx(285.0)

    def test_negative_fare_is_reported(self, empty_system):
        assert empty_system.request_new_economy_ticket(-20.0, 1) is None
        assert 'Could not create economy ticket' in (
            empty_system.get_error_log()[0])

    def test_valid_business_ticket_is_created(self, empty_system):
        ticket = empty_system.request_new_business_ticket(500.0, True, 3)
        assert isinstance(ticket, BusinessTicket)
        assert ticket.calculate_price() == pytest.approx(615.0)

    def test_too_many_business_bags_is_reported(self, empty_system):
        assert empty_system.request_new_business_ticket(500.0, False,
                                                        6) is None
        assert 'Business only allows 0-4' in empty_system.get_error_log()[0]

    def test_failed_creation_can_be_passed_on_safely(self, empty_system):
        # A None from a failed creation is caught again further along, so
        # the program still never crashes.
        flight = empty_system.request_new_flight('QF1', 'SYD', 'MEL',
                                                 '10:00', -1, 'scheduled')
        assert empty_system.request_add_flight(flight) is None
        assert '0 flight(s)' in str(empty_system)
        assert len(empty_system.get_error_log()) == 2
