BOOKING_NO = 'BK0001'

from flight import Flight
from passenger import Passenger
from booking import Booking


class BookingSystem ():
    def __init__(self):
        self.__flights = {}
        self.__bookings = {}
        self.__passengers = {}
        self.__cancelled_bookings = set()

    def add_flight(self, flight):
        if isinstance(flight, Flight):
            self.__flights.update(flight)



    def register_passenger(self, passenger):
        if isinstance(passenger, Passenger):
            self.__passengers.update(passenger)


    def create_booking(self, passenger, flight, ticket):
        # 1. Passenger not registered (key not in
        #    self.__passengers) -> raise.

        # 2. Flight not in this system, or not available
        #    (check its status) -> raise.

        # 3. (Optional) Flight full -> raise.

        # 4. Build the reference: prefix + padded counter.

        # 5. Today's date from datetime, as a string to
        #    match booking_date: str in your UML.

        # 6. Create the Booking. Its constructor may also
        #    raise (e.g. the isinstance check on ticket).

        # 7. Store it in self.__bookings.

        # 8. Counter += 1.

        # 9. Return the booking.

    def cancel_booking(self, booking_reference):
        pass

    def get_available_flights(self):
        

    



