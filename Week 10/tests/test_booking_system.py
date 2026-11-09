import datetime

import pytest

from booking import Booking
from exceptions import (BookingNotFoundError, BookingStateError,
                        DuplicateFlightError,
                        EmptyBookingError, FlightFullError,
                        FlightNotBookableError, FlightNotFoundError,
                        PassengerNotRegisteredError,
                        WrongObjectTypeError)
from flight import Flight
from passenger import Passenger


class TestRegistration:
    def test_flights_and_passengers_are_stored(self, system):
        assert str(system) == (
            'Booking system: 4 flight(s), 3 passenger(s), 0 booking(s), '
            '0 cancelled')

    @pytest.mark.parametrize('not_a_flight', ['QF401', None])
    def test_non_flights_are_rejected(self, empty_system, not_a_flight):
        with pytest.raises(WrongObjectTypeError) as error:
            empty_system.add_flight(not_a_flight)
        assert error.value.expected == 'Flight'
        assert '0 flight(s)' in str(empty_system)

    @pytest.mark.parametrize('not_a_passenger', ['Lui', None])
    def test_non_passengers_are_rejected(self, empty_system,
                                         not_a_passenger):
        with pytest.raises(WrongObjectTypeError,
                           match='Expected a Passenger'):
            empty_system.register_passenger(not_a_passenger)
        assert '0 passenger(s)' in str(empty_system)

    def test_registering_the_same_passport_twice_keeps_one_passenger(
            self, empty_system, lui, lui_duplicate):
        empty_system.register_passenger(lui)
        empty_system.register_passenger(lui_duplicate)
        assert '1 passenger(s)' in str(empty_system)

    def test_adding_the_same_flight_number_twice_raises(
            self, empty_system, scheduled_flight):
        empty_system.add_flight(scheduled_flight)
        with pytest.raises(DuplicateFlightError) as error:
            empty_system.add_flight(Flight('QF401', 'SYD', 'OOL', '11:00',
                                           10, 'scheduled'))
        assert error.value.flight_number == 'QF401'
        # The original flight is kept.
        assert empty_system.get_flight('QF401') is scheduled_flight
        assert '1 flight(s)' in str(empty_system)


class TestCreateBooking:
    def test_successful_booking_is_returned_pending(
            self, system, lui, scheduled_flight, economy_ticket):
        new_booking = system.create_booking(lui, scheduled_flight,
                                            economy_ticket)
        assert isinstance(new_booking, Booking)
        assert new_booking.get_status() == 'pending'
        assert new_booking.get_flight() is scheduled_flight
        assert new_booking.get_passengers() == [lui]

    def test_booking_references_count_up(self, system, lui, sam,
                                         delayed_flight, economy_ticket):
        first = system.create_booking(lui, delayed_flight, economy_ticket)
        second = system.create_booking(sam, delayed_flight, economy_ticket)
        assert first.get_booking_reference() == 'BK0001'
        assert second.get_booking_reference() == 'BK0002'

    def test_booking_is_dated_today(self, system, lui, delayed_flight,
                                    economy_ticket):
        new_booking = system.create_booking(lui, delayed_flight,
                                            economy_ticket)
        assert str(datetime.date.today()) in str(new_booking)

    def test_group_booking_holds_everyone(self, system, lui, sam,
                                          scheduled_flight, economy_ticket):
        new_booking = system.create_booking([lui, sam], scheduled_flight,
                                            economy_ticket)
        assert new_booking.get_passengers() == [lui, sam]

    def test_booking_on_a_delayed_flight_is_allowed(
            self, system, lui, delayed_flight, economy_ticket):
        assert system.create_booking(lui, delayed_flight,
                                     economy_ticket) is not None

    def test_group_can_fill_the_flight_exactly(self, system, lui, sam, alex,
                                               scheduled_flight,
                                               economy_ticket):
        # The scheduled flight has exactly 3 seats.
        group = system.create_booking([lui, sam, alex], scheduled_flight,
                                      economy_ticket)
        assert group is not None
        assert system.seats_booked(scheduled_flight) == 3


class TestCreateBookingFailures:
    def test_unregistered_passenger_is_refused(self, system,
                                               scheduled_flight,
                                               economy_ticket):
        stranger = Passenger('Bob', 'bob@email.com', 'PZ999999')
        with pytest.raises(PassengerNotRegisteredError) as error:
            system.create_booking(stranger, scheduled_flight,
                                  economy_ticket)
        assert error.value.passenger is stranger
        assert str(error.value) == (
            'Bob (passport PZ999999) is not registered')

    def test_group_with_one_unregistered_passenger_is_refused(
            self, system, lui, scheduled_flight, economy_ticket):
        stranger = Passenger('Bob', 'bob@email.com', 'PZ999999')
        with pytest.raises(PassengerNotRegisteredError):
            system.create_booking([lui, stranger], scheduled_flight,
                                  economy_ticket)
        assert system.seats_booked(scheduled_flight) == 0

    def test_empty_passenger_list_is_refused(self, system,
                                             scheduled_flight,
                                             economy_ticket):
        with pytest.raises(EmptyBookingError):
            system.create_booking([], scheduled_flight, economy_ticket)

    def test_flight_not_in_the_system_is_refused(self, system, lui,
                                                 two_seat_flight,
                                                 economy_ticket):
        with pytest.raises(FlightNotFoundError) as error:
            system.create_booking(lui, two_seat_flight, economy_ticket)
        assert error.value.flight_number == 'QF222'

    def test_cancelled_flight_is_refused(self, system, lui,
                                         cancelled_flight, economy_ticket):
        with pytest.raises(FlightNotBookableError) as error:
            system.create_booking(lui, cancelled_flight, economy_ticket)
        assert error.value.status == 'cancelled'
        assert str(error.value) == (
            'Flight QF500 is cancelled and is not taking bookings')

    def test_departed_flight_is_refused(self, system, lui, departed_flight,
                                        economy_ticket):
        with pytest.raises(FlightNotBookableError, match='departed'):
            system.create_booking(lui, departed_flight, economy_ticket)

    def test_group_bigger_than_the_remaining_seats_is_refused(
            self, system, lui, sam, alex, scheduled_flight, economy_ticket):
        system.create_booking([lui, sam], scheduled_flight, economy_ticket)
        # One seat left, two people want it.
        with pytest.raises(FlightFullError) as error:
            system.create_booking([alex, lui], scheduled_flight,
                                  economy_ticket)
        assert error.value.seats_requested == 2
        assert error.value.seats_left == 1
        assert system.seats_booked(scheduled_flight) == 2

    def test_flight_with_no_seats_is_refused(self, empty_system, lui,
                                             economy_ticket):
        empty_flight = Flight('QF0', 'SYD', 'NTL', '08:00', 0, 'scheduled')
        empty_system.register_passenger(lui)
        empty_system.add_flight(empty_flight)
        with pytest.raises(FlightFullError, match='0 seat'):
            empty_system.create_booking(lui, empty_flight, economy_ticket)

    def test_text_in_the_passenger_list_is_rejected(self, system, lui,
                                                    scheduled_flight,
                                                    economy_ticket):
        with pytest.raises(WrongObjectTypeError) as error:
            system.create_booking([lui, 'Sam'], scheduled_flight,
                                  economy_ticket)
        assert error.value.received == 'Sam'
        assert '0 booking(s)' in str(system)

    def test_text_is_rejected_as_a_ticket(self, system, lui,
                                          scheduled_flight):
        with pytest.raises(WrongObjectTypeError, match='Expected a Ticket'):
            system.create_booking(lui, scheduled_flight, 'economy')

    def test_text_is_rejected_as_a_flight(self, system, lui,
                                          economy_ticket):
        with pytest.raises(WrongObjectTypeError, match='Expected a Flight'):
            system.create_booking(lui, 'QF401', economy_ticket)

    def test_failed_booking_does_not_use_up_a_reference(
            self, system, lui, cancelled_flight, delayed_flight,
            economy_ticket):
        with pytest.raises(FlightNotBookableError):
            system.create_booking(lui, cancelled_flight, economy_ticket)
        next_booking = system.create_booking(lui, delayed_flight,
                                             economy_ticket)
        assert next_booking.get_booking_reference() == 'BK0001'

    def test_failed_booking_is_not_stored(self, system, lui,
                                          cancelled_flight, economy_ticket):
        with pytest.raises(FlightNotBookableError):
            system.create_booking(lui, cancelled_flight, economy_ticket)
        assert '0 booking(s)' in str(system)


class TestSeatsBooked:
    def test_empty_flight_has_no_seats_booked(self, system,
                                              scheduled_flight):
        assert system.seats_booked(scheduled_flight) == 0

    def test_every_passenger_in_a_group_takes_a_seat(
            self, system, lui, sam, scheduled_flight, economy_ticket):
        system.create_booking([lui, sam], scheduled_flight, economy_ticket)
        assert system.seats_booked(scheduled_flight) == 2

    def test_seats_add_up_across_bookings(self, system, lui, sam,
                                          scheduled_flight, economy_ticket):
        system.create_booking(lui, scheduled_flight, economy_ticket)
        system.create_booking(sam, scheduled_flight, economy_ticket)
        assert system.seats_booked(scheduled_flight) == 2

    def test_other_flights_are_not_counted(self, system, lui, sam,
                                           scheduled_flight, delayed_flight,
                                           economy_ticket):
        system.create_booking(lui, scheduled_flight, economy_ticket)
        system.create_booking(sam, delayed_flight, economy_ticket)
        assert system.seats_booked(scheduled_flight) == 1
        assert system.seats_booked(delayed_flight) == 1

    def test_cancelled_bookings_are_not_counted(self, system, lui,
                                                scheduled_flight,
                                                economy_ticket):
        system.create_booking(lui, scheduled_flight, economy_ticket)
        system.cancel_booking('BK0001')
        assert system.seats_booked(scheduled_flight) == 0


class TestCancelBooking:
    def test_cancelling_returns_the_cancelled_booking(
            self, system, lui, scheduled_flight, economy_ticket):
        system.create_booking(lui, scheduled_flight, economy_ticket)
        cancelled = system.cancel_booking('BK0001')
        assert cancelled.get_booking_reference() == 'BK0001'
        assert cancelled.get_status() == 'cancelled'

    def test_cancelling_is_counted_by_the_system(self, system, lui,
                                                 scheduled_flight,
                                                 economy_ticket):
        system.create_booking(lui, scheduled_flight, economy_ticket)
        system.cancel_booking('BK0001')
        assert '1 cancelled' in str(system)

    def test_cancelling_a_confirmed_booking_works(self, system, lui,
                                                  scheduled_flight,
                                                  economy_ticket):
        confirmed = system.create_booking(lui, scheduled_flight,
                                          economy_ticket)
        confirmed.confirm_booking()
        assert system.cancel_booking('BK0001') is confirmed
        assert confirmed.get_status() == 'cancelled'

    def test_unknown_reference_raises(self, system):
        with pytest.raises(BookingNotFoundError) as error:
            system.cancel_booking('BK9999')
        assert error.value.booking_reference == 'BK9999'
        assert str(error.value) == (
            "No booking found with reference 'BK9999'")

    @pytest.mark.parametrize('bad_reference', [1, None, ['BK0001']])
    def test_non_text_reference_raises(self, system, bad_reference):
        with pytest.raises(BookingNotFoundError):
            system.cancel_booking(bad_reference)

    def test_cancelling_twice_raises_the_second_time(
            self, system, lui, scheduled_flight, economy_ticket):
        system.create_booking(lui, scheduled_flight, economy_ticket)
        system.cancel_booking('BK0001')
        with pytest.raises(BookingStateError, match='already cancelled'):
            system.cancel_booking('BK0001')
        assert '1 cancelled' in str(system)

    def test_booking_on_a_departed_flight_stays_active(
            self, system, lui, delayed_flight, economy_ticket):
        late = system.create_booking(lui, delayed_flight, economy_ticket)
        delayed_flight.set_status('departed')
        with pytest.raises(BookingStateError):
            system.cancel_booking('BK0001')
        # The failed cancel leaves the booking and its seat as they were.
        assert late.get_status() == 'pending'
        assert system.seats_booked(delayed_flight) == 1
        assert '0 cancelled' in str(system)


class TestAvailableFlights:
    def test_only_bookable_flights_are_listed(self, system,
                                              scheduled_flight,
                                              delayed_flight):
        assert system.get_available_flights() == [scheduled_flight,
                                                  delayed_flight]

    def test_empty_system_has_no_available_flights(self, empty_system):
        assert empty_system.get_available_flights() == []

    def test_full_flight_is_not_listed(self, system, lui, sam, alex,
                                       scheduled_flight, delayed_flight,
                                       economy_ticket):
        system.create_booking([lui, sam, alex], scheduled_flight,
                              economy_ticket)
        assert system.get_available_flights() == [delayed_flight]

    def test_flight_is_listed_again_after_a_cancellation(
            self, system, lui, sam, alex, scheduled_flight, economy_ticket):
        system.create_booking([lui, sam, alex], scheduled_flight,
                              economy_ticket)
        system.cancel_booking('BK0001')
        assert scheduled_flight in system.get_available_flights()

    def test_flight_drops_off_the_list_when_it_departs(
            self, system, scheduled_flight):
        scheduled_flight.set_status('departed')
        assert scheduled_flight not in system.get_available_flights()
