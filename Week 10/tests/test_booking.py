import pytest

from booking import Booking
from exceptions import (BookingStateError, DuplicatePassengerError,
                        WrongObjectTypeError)


class TestBookingCreation:
    def test_new_booking_starts_pending(self, booking):
        assert booking.get_status() == 'pending'

    def test_new_booking_holds_its_passenger(self, booking, lui):
        assert booking.get_passengers() == [lui]

    def test_new_booking_holds_its_flight(self, booking, scheduled_flight):
        assert booking.get_flight() is scheduled_flight

    def test_group_booking_holds_every_passenger(self, group_booking, lui,
                                                 sam):
        assert group_booking.get_passengers() == [lui, sam]

    def test_booking_copies_the_passenger_list_it_is_given(
            self, lui, sam, scheduled_flight, economy_ticket):
        passengers = [lui]
        new_booking = Booking('BK0009', '2026-10-31', passengers,
                              scheduled_flight, economy_ticket)
        passengers.append(sam)
        assert new_booking.get_passengers() == [lui]


class TestAddPassenger:
    def test_new_passenger_is_added(self, booking, lui, sam):
        assert booking.add_passenger(sam) is True
        assert booking.get_passengers() == [lui, sam]

    def test_same_passenger_is_not_added_twice(self, booking, lui):
        with pytest.raises(DuplicatePassengerError) as error:
            booking.add_passenger(lui)
        assert error.value.passenger is lui
        assert error.value.booking_reference == 'BK0001'
        assert len(booking.get_passengers()) == 1

    def test_different_object_with_same_passport_is_not_added(
            self, booking, lui_duplicate):
        with pytest.raises(DuplicatePassengerError,
                           match='passport PA123456'):
            booking.add_passenger(lui_duplicate)
        assert len(booking.get_passengers()) == 1

    @pytest.mark.parametrize('not_a_passenger', ['Sam', None])
    def test_non_passengers_are_rejected(self, booking, not_a_passenger):
        with pytest.raises(WrongObjectTypeError,
                           match='Expected a Passenger'):
            booking.add_passenger(not_a_passenger)
        assert len(booking.get_passengers()) == 1

    def test_nobody_can_be_added_to_a_cancelled_booking(self, booking,
                                                        sam):
        booking.cancel_booking()
        with pytest.raises(BookingStateError, match='cancelled'):
            booking.add_passenger(sam)
        assert len(booking.get_passengers()) == 1

    def test_returned_list_is_a_copy(self, booking, sam):
        booking.get_passengers().append(sam)
        assert len(booking.get_passengers()) == 1


class TestConfirmBooking:
    def test_pending_booking_can_be_confirmed(self, booking):
        assert booking.confirm_booking() is True
        assert booking.get_status() == 'confirmed'

    def test_confirmed_booking_cannot_be_confirmed_again(self, booking):
        booking.confirm_booking()
        with pytest.raises(BookingStateError) as error:
            booking.confirm_booking()
        assert error.value.action == 'confirmed'
        assert error.value.reason == 'it is already confirmed'
        assert booking.get_status() == 'confirmed'

    def test_cancelled_booking_cannot_be_confirmed(self, booking):
        booking.cancel_booking()
        with pytest.raises(BookingStateError, match='already cancelled'):
            booking.confirm_booking()
        assert booking.get_status() == 'cancelled'

    def test_booking_on_delayed_flight_can_be_confirmed(
            self, lui, delayed_flight, economy_ticket):
        delayed = Booking('BK0004', '2026-10-31', [lui], delayed_flight,
                          economy_ticket)
        assert delayed.confirm_booking() is True

    def test_booking_on_cancelled_flight_cannot_be_confirmed(
            self, lui, cancelled_flight, economy_ticket):
        doomed = Booking('BK0005', '2026-10-31', [lui], cancelled_flight,
                         economy_ticket)
        with pytest.raises(BookingStateError,
                           match='QF500 is not flying'):
            doomed.confirm_booking()
        assert doomed.get_status() == 'pending'

    def test_booking_on_departed_flight_cannot_be_confirmed(
            self, departed_booking):
        with pytest.raises(BookingStateError, match='departed'):
            departed_booking.confirm_booking()
        assert departed_booking.get_status() == 'pending'


class TestCancelBooking:
    def test_pending_booking_can_be_cancelled(self, booking):
        assert booking.cancel_booking() is True
        assert booking.get_status() == 'cancelled'

    def test_confirmed_booking_can_be_cancelled(self, booking):
        booking.confirm_booking()
        assert booking.cancel_booking() is True
        assert booking.get_status() == 'cancelled'

    def test_cancelled_booking_cannot_be_cancelled_again(self, booking):
        booking.cancel_booking()
        with pytest.raises(BookingStateError) as error:
            booking.cancel_booking()
        assert str(error.value) == (
            'Booking BK0001 cannot be cancelled: it is already cancelled')
        assert booking.get_status() == 'cancelled'

    def test_booking_on_departed_flight_cannot_be_cancelled(
            self, departed_booking):
        with pytest.raises(BookingStateError,
                           match='QF900 has already departed'):
            departed_booking.cancel_booking()
        assert departed_booking.get_status() == 'pending'


class TestTotalCost:
    def test_single_passenger_pays_the_ticket_price(self, booking):
        # Economy: 250 + 1 bag at 35.
        assert booking.total_cost() == pytest.approx(285.0)

    def test_cost_is_charged_per_passenger(self, group_booking):
        assert group_booking.total_cost() == pytest.approx(570.0)

    def test_cost_grows_when_a_passenger_is_added(self, booking, sam):
        booking.add_passenger(sam)
        assert booking.total_cost() == pytest.approx(570.0)

    def test_cost_does_not_change_when_a_duplicate_is_rejected(
            self, booking, lui_duplicate):
        with pytest.raises(DuplicatePassengerError):
            booking.add_passenger(lui_duplicate)
        assert booking.total_cost() == pytest.approx(285.0)

    def test_cost_uses_the_business_ticket_price(self, lui, sam,
                                                 scheduled_flight,
                                                 business_ticket):
        business_booking = Booking('BK0006', '2026-10-31', [lui, sam],
                                   scheduled_flight, business_ticket)
        # 2 x 615.
        assert business_booking.total_cost() == pytest.approx(1230.0)


class TestBookingEquals:
    def test_same_reference_is_equal(self, booking, sam, scheduled_flight,
                                     business_ticket):
        same_reference = Booking('BK0001', '2026-11-01', [sam],
                                 scheduled_flight, business_ticket)
        assert booking.equals(same_reference)

    def test_different_reference_is_not_equal(self, booking, group_booking):
        assert not booking.equals(group_booking)

    def test_booking_equals_itself(self, booking):
        assert booking.equals(booking)

    def test_reference_text_is_not_equal_to_a_booking(self, booking):
        assert not booking.equals('BK0001')

    def test_none_is_not_equal_to_a_booking(self, booking):
        assert not booking.equals(None)


class TestBookingString:
    def test_string_shows_reference_status_flight_date_and_names(
            self, group_booking):
        assert str(group_booking) == (
            'Booking BK0002 (pending) on QF401, booked 2026-10-31: '
            'Lui, Sam')

    def test_string_shows_the_new_status(self, booking):
        booking.confirm_booking()
        assert '(confirmed)' in str(booking)
