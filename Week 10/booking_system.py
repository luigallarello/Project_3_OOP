import datetime

from booking import Booking
from exceptions import (BookingNotFoundError, BookingSystemError,
                        EmptyBookingError, FlightFullError,
                        FlightNotBookableError, FlightNotFoundError,
                        PassengerNotRegisteredError, WrongObjectTypeError)
from flight import Flight
from passenger import Passenger
from ticket import Ticket

# flights in these states can still take bookings
_BOOKABLE_STATUSES = {'scheduled', 'delayed'}


class BookingSystem:
    BOOKING_PREFIX = 'BK'

    def __init__(self):
        # flights keyed by flight number, passengers by passport number,
        # bookings by booking reference
        self.__flights = {}
        self.__bookings = {}
        self.__passengers = {}
        self.__cancelled_bookings = set()
        self.__count = 1
        # messages from every request that failed and was handled
        self.__error_log = []

    # ------------------------------------------------------------------
    # Core operations. These raise a custom exception as soon as a rule
    # is broken, before anything is changed.
    # ------------------------------------------------------------------
    def add_flight(self, flight):
        if not isinstance(flight, Flight):
            raise WrongObjectTypeError('Flight', flight)
        self.__flights[flight.get_flight_number()] = flight

    def register_passenger(self, passenger):
        if not isinstance(passenger, Passenger):
            raise WrongObjectTypeError('Passenger', passenger)
        self.__passengers[passenger.get_passport_number()] = passenger

    def get_flight(self, flight_number):
        flight = self.__flights.get(flight_number)
        if flight is None:
            raise FlightNotFoundError(flight_number)
        return flight

    def get_booking(self, booking_reference):
        # Only text can be a reference. Checking first also stops things
        # like a list from breaking the dictionary lookup.
        if not isinstance(booking_reference, str):
            raise BookingNotFoundError(booking_reference)
        booking = self.__bookings.get(booking_reference)
        if booking is None:
            raise BookingNotFoundError(booking_reference)
        return booking

    def create_booking(self, passengers, flight, ticket):
        # lets you pass in a single passenger as well as a list
        if isinstance(passengers, Passenger):
            passengers = [passengers]

        if len(passengers) == 0:
            raise EmptyBookingError()

        for passenger in passengers:
            self.__check_registered(passenger)

        if not isinstance(ticket, Ticket):
            raise WrongObjectTypeError('Ticket', ticket)

        self.__check_bookable(flight)
        self.__check_seats(flight, len(passengers))

        # Every check has passed, so it's now safe to change the system.
        # e.g. BK0001, BK0002...
        reference = f'{self.BOOKING_PREFIX}{self.__count:04d}'
        booking_date = str(datetime.date.today())

        new_booking = Booking(reference, booking_date, passengers,
                              flight, ticket)
        self.__bookings[reference] = new_booking

        self.__count += 1
        return new_booking

    def add_passenger_to_booking(self, booking_reference, passenger):
        booking = self.get_booking(booking_reference)
        self.__check_registered(passenger)
        # The extra person needs a seat on the same flight.
        self.__check_seats(booking.get_flight(), 1)
        booking.add_passenger(passenger)
        return booking

    def cancel_booking(self, booking_reference):
        booking = self.get_booking(booking_reference)
        # The booking decides if it can be cancelled, for example not
        # once the flight has departed. If it can't, it raises and the
        # line below never runs, so the seat isn't given back.
        booking.cancel_booking()
        self.__cancelled_bookings.add(booking_reference)
        return booking

    def seats_booked(self, flight):
        total = 0
        for reference, booking in self.__bookings.items():
            # cancelled bookings give their seats back
            if reference in self.__cancelled_bookings:
                continue
            booked_number = booking.get_flight().get_flight_number()
            if booked_number == flight.get_flight_number():
                total += len(booking.get_passengers())
        return total

    def get_available_flights(self):
        available = []
        for flight in self.__flights.values():
            if flight.get_status() not in _BOOKABLE_STATUSES:
                continue
            # skip flights that are already full
            if self.seats_booked(flight) < flight.get_capacity():
                available.append(flight)
        return available

    # ------------------------------------------------------------------
    # Requests. These are the safe versions used by the program: they
    # try the core operation, and if it raises a booking error they
    # report it and return None so the program can carry on.
    # ------------------------------------------------------------------
    def request_booking(self, passengers, flight, ticket):
        try:
            new_booking = self.create_booking(passengers, flight, ticket)
        except BookingSystemError as error:
            self.__report_failure('create booking', error)
            return None
        print(f'Created {new_booking}')
        return new_booking

    def request_add_passenger(self, booking_reference, passenger):
        try:
            booking = self.add_passenger_to_booking(booking_reference,
                                                    passenger)
        except BookingSystemError as error:
            self.__report_failure('add passenger', error)
            return None
        print(f'Added {passenger.get_name()} to {booking_reference}')
        return booking

    def request_confirmation(self, booking_reference):
        try:
            booking = self.get_booking(booking_reference)
            booking.confirm_booking()
        except BookingSystemError as error:
            self.__report_failure('confirm booking', error)
            return None
        print(f'Confirmed {booking_reference}')
        return booking

    def request_cancellation(self, booking_reference):
        try:
            booking = self.cancel_booking(booking_reference)
        except BookingSystemError as error:
            self.__report_failure('cancel booking', error)
            return None
        print(f'Cancelled {booking_reference}')
        return booking

    def request_flight_status_change(self, flight_number, status):
        try:
            flight = self.get_flight(flight_number)
            flight.set_status(status)
        except BookingSystemError as error:
            self.__report_failure('update flight', error)
            return None
        print(f'{flight_number} is now {status}')
        return flight

    def get_error_log(self):
        # A copy, so the log can't be changed from outside.
        return list(self.__error_log)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def __report_failure(self, action, error):
        message = f'Could not {action}: {error}'
        self.__error_log.append(message)
        print(message)

    def __check_registered(self, passenger):
        if not isinstance(passenger, Passenger):
            raise WrongObjectTypeError('Passenger', passenger)
        if passenger.get_passport_number() not in self.__passengers:
            raise PassengerNotRegisteredError(passenger)

    def __check_bookable(self, flight):
        if not isinstance(flight, Flight):
            raise WrongObjectTypeError('Flight', flight)
        # get_flight raises if the system doesn't know this flight
        self.get_flight(flight.get_flight_number())
        if flight.get_status() not in _BOOKABLE_STATUSES:
            raise FlightNotBookableError(flight.get_flight_number(),
                                         flight.get_status())

    def __check_seats(self, flight, seats_requested):
        # make sure the whole group fits, not just one person
        seats_left = flight.get_capacity() - self.seats_booked(flight)
        if seats_requested > seats_left:
            raise FlightFullError(flight.get_flight_number(),
                                  seats_requested, seats_left)

    def __str__(self):
        return (f'Booking system: {len(self.__flights)} flight(s), '
                f'{len(self.__passengers)} passenger(s), '
                f'{len(self.__bookings)} booking(s), '
                f'{len(self.__cancelled_bookings)} cancelled')
