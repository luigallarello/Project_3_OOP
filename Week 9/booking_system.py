from flight import Flight
from passenger import Passenger
from booking import Booking
import datetime


class BookingSystem ():
    BOOKING_PREFIX = 'BK'
    def __init__(self):
        self.__flights = {}
        self.__bookings = {}
        self.__passengers = {}
        self.__cancelled_bookings = set()
        self.__count = 1

    def get_count(self):
        return self.__count

    def add_flight(self, flight):
        if isinstance(flight, Flight):
            self.__flights[flight.get_flight_number()] = flight



    def register_passenger(self, passenger):
        if isinstance(passenger, Passenger):
            self.__passengers[passenger.get_passport_number()] = passenger


    def create_booking(self, passengers, flight, ticket):
        # Accept one passenger or a list of passengers
        if isinstance(passengers, Passenger):
            passengers = [passengers]

        if len(passengers) == 0:
            return None

        for passenger in passengers:
            if passenger.get_passport_number() not in self.__passengers:
                return None

        if flight.get_flight_number() not in self.__flights:
            return None

        # Can't book a flight that is cancelled or has already left
        if flight.get_status() in ('cancelled', 'departed'):
            return None

        # Not enough seats left for everyone on this booking
        if self.seats_booked(flight) + len(passengers) > flight.get_capacity():
            return None

        reference = f'{self.BOOKING_PREFIX}{self.__count:04d}'
        booking_date = str(datetime.date.today())

        new_booking = Booking(reference, booking_date, passengers, flight, ticket)
        self.__bookings[reference] = new_booking

        self.__count += 1
        return new_booking


    def seats_booked(self, flight):
        # Count passengers on this flight, ignoring cancelled bookings
        total = 0
        for reference, booking in self.__bookings.items():
            if reference in self.__cancelled_bookings:
                continue
            if booking.get_flight().get_flight_number() == flight.get_flight_number():
                total += len(booking.get_passengers())
        return total


    def cancel_booking(self, booking_reference):
        # 1. booking_reference not a str -> return None (or raise TypeError).

        # 2. Look it up in self.__bookings (not self.__passengers).
        #    Not found -> return None.

        # 3. Already in self.__cancelled_bookings -> return None.

        # 4. Tell the booking to cancel itself: booking.cancel_booking()
        #    (the Booking owns its own status).

        # 5. Add booking_reference to self.__cancelled_bookings.

        # 6. Return the cancelled booking.
        pass


    def get_available_flights(self):
        # 1. Loop over self.__flights.values().

        # 2. Keep flights whose status is 'scheduled' or 'delayed'
        #    (not 'cancelled' or 'departed').

        # 3. Return them as a list (UML says list[Flight], not the dict).
        return list(self.__flights.values())

    # Optional helpers (add to UML if you keep them):
    # def find_booking(self, booking_reference) -> Booking | None
    # def get_bookings_for_passenger(self, passport_number) -> list[Booking]
