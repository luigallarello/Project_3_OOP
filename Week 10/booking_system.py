import datetime

from booking import Booking
from business_ticket import BusinessTicket
from economy_ticket import EconomyTicket
from exceptions import (BookingNotFoundError, BookingSystemError,
                        DuplicateFlightError, EmptyBookingError,
                        FlightFullError, FlightNotBookableError,
                        FlightNotFoundError, PassengerNotRegisteredError,
                        WrongObjectTypeError)
from flight import Flight
from passenger import Passenger
from ticket import Ticket


class BookingSystem:
    """Keeps track of flights, passengers and bookings, and makes bookings.

    The core methods raise a custom exception as soon as a rule is broken.
    The request_ methods call them, catch any booking error, report it and
    return None so the program can carry on.
    """

    BOOKING_PREFIX = 'BK'

    def __init__(self):
        # Dictionaries give a quick lookup by each object's unique key:
        # flight number, passport number and booking reference.
        self.__flights = {}
        self.__bookings = {}
        self.__passengers = {}
        self.__count = 1
        # A list keeps every handled error message in the order it
        # happened.
        self.__error_log = []

    # ------------------------------------------------------------------
    # Core operations. These raise a custom exception as soon as a rule
    # is broken, before anything is changed.
    # ------------------------------------------------------------------
    def add_flight(self, flight):
        if not isinstance(flight, Flight):
            raise WrongObjectTypeError('Flight', flight)
        # Replacing a flight would leave its bookings pointing at the old
        # one, so each flight number can only be added once.
        if flight.get_flight_number() in self.__flights:
            raise DuplicateFlightError(flight.get_flight_number())
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
        # A single passenger is accepted as well as a list of them.
        if isinstance(passengers, Passenger):
            passengers = [passengers]
        if not isinstance(passengers, list):
            raise WrongObjectTypeError('list of Passengers', passengers)
        if len(passengers) == 0:
            raise EmptyBookingError()

        for passenger in passengers:
            self.__check_registered(passenger)

        if not isinstance(ticket, Ticket):
            raise WrongObjectTypeError('Ticket', ticket)

        self.__check_bookable(flight)
        self.__check_seats(flight, len(passengers))

        # Every check has passed, so it's now safe to change the system.
        # References count up from BK0001.
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
        # The booking decides if it can be cancelled and raises if it
        # can't, for example once the flight has departed.
        booking.cancel_booking()
        return booking

    def seats_booked(self, flight):
        if not isinstance(flight, Flight):
            raise WrongObjectTypeError('Flight', flight)
        total = 0
        for booking in self.__bookings.values():
            # The booking's own status is checked, so a booking cancelled
            # from anywhere gives its seats back.
            if booking.is_cancelled():
                continue
            booked_number = booking.get_flight().get_flight_number()
            if booked_number == flight.get_flight_number():
                total += len(booking.get_passengers())
        return total

    def get_available_flights(self):
        available = []
        for flight in self.__flights.values():
            # Flights that won't fly or are already full are skipped.
            if not flight.is_bookable():
                continue
            if self.seats_booked(flight) < flight.get_capacity():
                available.append(flight)
        return available

    # ------------------------------------------------------------------
    # Requests. These are the safe versions used by the program. Each one
    # tries a core operation, and if it raises a booking error the error
    # is reported and None is returned so the program can carry on.
    # ------------------------------------------------------------------
    def request_new_flight(self, flight_number, origin, destination,
                           departure_time, capacity, status):
        # The Flight constructor raises if the capacity or status is
        # invalid, so the program never holds a broken flight.
        try:
            flight = Flight(flight_number, origin, destination,
                            departure_time, capacity, status)
        except BookingSystemError as error:
            self.__report_failure('create flight', error)
            return None
        print(f'Created flight {flight_number}')
        return flight

    def request_new_passenger(self, name, email, passport_number):
        try:
            passenger = Passenger(name, email, passport_number)
        except BookingSystemError as error:
            self.__report_failure('create passenger', error)
            return None
        print(f'Created passenger {name}')
        return passenger

    def request_new_economy_ticket(self, base_fare, checked_bag_count):
        try:
            ticket = EconomyTicket(base_fare, checked_bag_count)
        except BookingSystemError as error:
            self.__report_failure('create economy ticket', error)
            return None
        print(f'Created {ticket}')
        return ticket

    def request_new_business_ticket(self, base_fare, lounge_access,
                                    checked_bag_count):
        try:
            ticket = BusinessTicket(base_fare, lounge_access,
                                    checked_bag_count)
        except BookingSystemError as error:
            self.__report_failure('create business ticket', error)
            return None
        print(f'Created {ticket}')
        return ticket

    def request_add_flight(self, flight):
        try:
            self.add_flight(flight)
        except BookingSystemError as error:
            self.__report_failure('add flight', error)
            return None
        print(f'Added flight {flight.get_flight_number()}')
        return flight

    def request_register_passenger(self, passenger):
        try:
            self.register_passenger(passenger)
        except BookingSystemError as error:
            self.__report_failure('register passenger', error)
            return None
        print(f'Registered {passenger.get_name()}')
        return passenger

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
    # Private helpers used by the methods above.
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
        # This raises if the system doesn't know the flight.
        self.get_flight(flight.get_flight_number())
        if not flight.is_bookable():
            raise FlightNotBookableError(flight.get_flight_number(),
                                         flight.get_status())

    def __check_seats(self, flight, seats_requested):
        # The whole group has to fit, not just one person.
        seats_left = flight.get_capacity() - self.seats_booked(flight)
        if seats_requested > seats_left:
            raise FlightFullError(flight.get_flight_number(),
                                  seats_requested, seats_left)

    def __str__(self):
        cancelled = sum(1 for booking in self.__bookings.values()
                        if booking.is_cancelled())
        return (f'Booking system: {len(self.__flights)} flight(s), '
                f'{len(self.__passengers)} passenger(s), '
                f'{len(self.__bookings)} booking(s), '
                f'{cancelled} cancelled')
