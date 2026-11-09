from exceptions import (BookingStateError, DuplicatePassengerError,
                        WrongObjectTypeError)
from flight import Flight
from passenger import Passenger


class Booking:
    """A group of passengers booked on one flight with one ticket type.

    A booking starts as pending, can be confirmed, and can be cancelled
    until its flight departs. The booking's own status is the only record
    of whether it's cancelled.
    """

    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'

    def __init__(self, booking_reference, booking_date, passengers,
                 flight, ticket):
        self.__booking_reference = booking_reference
        self.__booking_date = booking_date
        self.__status = Booking.PENDING
        # A list keeps passengers in the order they were booked, and one
        # booking can cover a whole group. It's copied so later changes to
        # the caller's list don't affect the booking.
        self.__passengers = list(passengers)
        self.__flight = flight
        self.__ticket = ticket

    def get_booking_reference(self):
        return self.__booking_reference

    def get_status(self):
        return self.__status

    def is_cancelled(self):
        return self.__status == Booking.CANCELLED

    def get_passengers(self):
        # Return a copy so the list can't be changed from outside.
        return list(self.__passengers)

    def add_passenger(self, passenger):
        # Every check happens before the list is touched, so a failed add
        # leaves the booking exactly as it was.
        if not isinstance(passenger, Passenger):
            raise WrongObjectTypeError('Passenger', passenger)
        if self.is_cancelled():
            raise BookingStateError(self.__booking_reference,
                                    'changed', 'it has been cancelled')
        # Don't add the same person twice.
        for existing in self.__passengers:
            if existing.equals(passenger):
                raise DuplicatePassengerError(passenger,
                                              self.__booking_reference)
        self.__passengers.append(passenger)
        return True

    def get_flight(self):
        return self.__flight

    def confirm_booking(self):
        # Only a pending booking can be confirmed.
        if self.__status != Booking.PENDING:
            raise BookingStateError(self.__booking_reference, 'confirmed',
                                    f'it is already {self.__status}')
        # A booking can't be confirmed for a flight that won't fly.
        if not self.__flight.is_bookable():
            raise BookingStateError(
                self.__booking_reference, 'confirmed',
                f'flight {self.__flight.get_flight_number()} is not flying '
                f'({self.__flight.get_status()})')
        self.__status = Booking.CONFIRMED
        return True

    def cancel_booking(self):
        if self.is_cancelled():
            raise BookingStateError(self.__booking_reference, 'cancelled',
                                    'it is already cancelled')
        # Once the flight has left it's too late to cancel.
        if self.__flight.get_status() == Flight.DEPARTED:
            raise BookingStateError(
                self.__booking_reference, 'cancelled',
                f'flight {self.__flight.get_flight_number()} has already '
                f'departed')
        self.__status = Booking.CANCELLED
        return True

    def total_cost(self):
        # Each passenger needs their own seat, so the ticket price is
        # charged once per person. calculate_price() works for both
        # ticket types.
        return self.__ticket.calculate_price() * len(self.__passengers)

    def __str__(self):
        names = ', '.join(p.get_name() for p in self.__passengers)
        return (f'Booking {self.__booking_reference} ({self.__status}) '
                f'on {self.__flight.get_flight_number()}, '
                f'booked {self.__booking_date}: {names}')
