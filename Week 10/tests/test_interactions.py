import pytest

from booking import Booking
from exceptions import (BookingStateError, DuplicatePassengerError,
                        FlightFullError)
from ticket import Ticket


class TestTicketPolymorphism:
    # Booking only knows about the Ticket abstraction, so every concrete
    # ticket type should work through it.
    def test_booking_total_with_an_economy_ticket(
            self, lui, sam, scheduled_flight, economy_ticket):
        group = Booking('BK0001', '2026-10-31', [lui, sam],
                        scheduled_flight, economy_ticket)
        assert group.total_cost() == pytest.approx(285.0 * 2)

    def test_booking_total_with_a_business_ticket_and_lounge(
            self, lui, sam, scheduled_flight, business_ticket):
        group = Booking('BK0001', '2026-10-31', [lui, sam],
                        scheduled_flight, business_ticket)
        assert group.total_cost() == pytest.approx(615.0 * 2)

    def test_booking_total_with_a_business_ticket_and_no_lounge(
            self, lui, sam, scheduled_flight, business_ticket_no_lounge):
        group = Booking('BK0001', '2026-10-31', [lui, sam],
                        scheduled_flight, business_ticket_no_lounge)
        assert group.total_cost() == pytest.approx(500.0 * 2)

    def test_both_ticket_types_are_tickets(self, economy_ticket,
                                           business_ticket):
        for ticket in (economy_ticket, business_ticket):
            assert isinstance(ticket, Ticket)

    def test_same_call_gives_different_results_for_each_type(
            self, economy_ticket, business_ticket):
        tickets = [economy_ticket, business_ticket]
        prices = [ticket.calculate_price() for ticket in tickets]
        descriptions = [ticket.baggage_allowance() for ticket in tickets]
        assert prices == pytest.approx([285.0, 615.0])
        assert descriptions[0] != descriptions[1]

    def test_each_type_prints_its_own_string(self, economy_ticket,
                                             business_ticket):
        assert str(economy_ticket).startswith('Economy ticket')
        assert str(business_ticket).startswith('Business ticket')

    def test_cheaper_ticket_type_lowers_the_booking_total(
            self, lui, scheduled_flight, economy_ticket, business_ticket):
        economy_booking = Booking('BK0001', '2026-10-31', [lui],
                                  scheduled_flight, economy_ticket)
        business_booking = Booking('BK0002', '2026-10-31', [lui],
                                   scheduled_flight, business_ticket)
        assert economy_booking.total_cost() < business_booking.total_cost()


class TestBookingAndFlightRelationship:
    def test_booking_reacts_when_its_flight_departs(self, booking,
                                                    scheduled_flight):
        scheduled_flight.set_status('departed')
        with pytest.raises(BookingStateError):
            booking.cancel_booking()
        with pytest.raises(BookingStateError):
            booking.confirm_booking()
        assert booking.get_status() == 'pending'

    def test_booking_reacts_when_its_flight_is_cancelled(self, booking,
                                                         scheduled_flight):
        scheduled_flight.set_status('cancelled')
        with pytest.raises(BookingStateError):
            booking.confirm_booking()
        # Passengers can still cancel their own booking.
        assert booking.cancel_booking() is True

    def test_two_bookings_share_one_flight_object(self, booking,
                                                  group_booking):
        assert booking.get_flight() is group_booking.get_flight()

    def test_booking_string_follows_the_flight_it_holds(self, booking):
        assert 'QF401' in str(booking)


class TestBookingAndPassengerRelationship:
    def test_same_passenger_can_be_on_separate_bookings(
            self, system, lui, scheduled_flight, delayed_flight,
            economy_ticket):
        first = system.create_booking(lui, scheduled_flight, economy_ticket)
        second = system.create_booking(lui, delayed_flight, economy_ticket)
        assert first.get_passengers() == second.get_passengers() == [lui]

    def test_same_passenger_cannot_be_added_to_a_booking_twice(
            self, system, lui, lui_duplicate, scheduled_flight,
            economy_ticket):
        new_booking = system.create_booking(lui, scheduled_flight,
                                            economy_ticket)
        with pytest.raises(DuplicatePassengerError):
            new_booking.add_passenger(lui_duplicate)
        assert new_booking.total_cost() == pytest.approx(285.0)

    def test_passenger_added_to_a_booking_later_takes_a_seat(
            self, system, lui, sam, scheduled_flight, economy_ticket):
        # The system counts the passengers on each booking, so someone
        # added straight to a booking is counted too.
        new_booking = system.create_booking(lui, scheduled_flight,
                                            economy_ticket)
        new_booking.add_passenger(sam)
        assert system.seats_booked(scheduled_flight) == 2


class TestBookingWorkflow:
    def test_book_confirm_then_cancel(self, system, lui, sam,
                                      scheduled_flight, economy_ticket):
        group = system.create_booking([lui, sam], scheduled_flight,
                                      economy_ticket)
        assert group.get_status() == 'pending'

        assert group.confirm_booking() is True
        assert group.get_status() == 'confirmed'

        assert system.cancel_booking('BK0001') is group
        assert group.get_status() == 'cancelled'

    def test_cancelling_frees_seats_for_someone_else(
            self, system, lui, sam, alex, scheduled_flight, economy_ticket):
        system.create_booking([lui, sam, alex], scheduled_flight,
                              economy_ticket)
        # The flight is full, so nobody else can book.
        with pytest.raises(FlightFullError):
            system.create_booking(lui, scheduled_flight, economy_ticket)

        system.cancel_booking('BK0001')
        replacement = system.create_booking(lui, scheduled_flight,
                                            economy_ticket)
        assert replacement is not None
        assert replacement.get_booking_reference() == 'BK0002'

    def test_bookings_on_different_flights_do_not_affect_each_other(
            self, system, lui, sam, alex, scheduled_flight, delayed_flight,
            economy_ticket, business_ticket):
        system.create_booking([lui, sam, alex], scheduled_flight,
                              economy_ticket)
        other = system.create_booking([lui, sam, alex], delayed_flight,
                                      business_ticket)
        # Filling the small flight leaves the big one untouched.
        assert other is not None
        assert system.get_available_flights() == [delayed_flight]
        assert other.total_cost() == pytest.approx(615.0 * 3)

    def test_failed_cancel_leaves_the_flight_and_booking_unchanged(
            self, system, lui, delayed_flight, economy_ticket):
        late = system.create_booking(lui, delayed_flight, economy_ticket)
        late.confirm_booking()
        delayed_flight.set_status('departed')

        with pytest.raises(BookingStateError):
            system.cancel_booking('BK0001')
        assert late.get_status() == 'confirmed'
        assert delayed_flight.get_status() == 'departed'

    def test_references_stay_unique_across_many_bookings(
            self, system, lui, delayed_flight, economy_ticket):
        references = [
            system.create_booking(lui, delayed_flight, economy_ticket)
            .get_booking_reference()
            for _ in range(12)
        ]
        assert len(set(references)) == 12
        assert references[0] == 'BK0001'
        assert references[-1] == 'BK0012'
