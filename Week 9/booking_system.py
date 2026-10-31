import datetime

from booking import Booking
from flight import Flight
from passenger import Passenger

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

    def get_count(self):
        return self.__count

    def add_flight(self, flight):
        if isinstance(flight, Flight):
            self.__flights[flight.get_flight_number()] = flight

    def register_passenger(self, passenger):
        if isinstance(passenger, Passenger):
            self.__passengers[passenger.get_passport_number()] = passenger

    def create_booking(self, passengers, flight, ticket):
        # lets you pass in a single passenger as well as a list
        if isinstance(passengers, Passenger):
            passengers = [passengers]

        if len(passengers) == 0:
            return None

        for passenger in passengers:
            if passenger.get_passport_number() not in self.__passengers:
                return None

        if flight.get_flight_number() not in self.__flights:
            return None

        if flight.get_status() not in _BOOKABLE_STATUSES:
            return None

        # make sure the whole group fits, not just one person
        seats_left = flight.get_capacity() - self.seats_booked(flight)
        if len(passengers) > seats_left:
            return None

        # e.g. BK0001, BK0002...
        reference = f'{self.BOOKING_PREFIX}{self.__count:04d}'
        booking_date = str(datetime.date.today())

        new_booking = Booking(reference, booking_date, passengers,
                              flight, ticket)
        self.__bookings[reference] = new_booking

        self.__count += 1
        return new_booking

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

    def cancel_booking(self, booking_reference):
        if not isinstance(booking_reference, str):
            return None

        booking = self.__bookings.get(booking_reference)
        if booking is None:
            return None

        # The booking decides if it can be cancelled, for example not
        # once the flight has departed. The system just keeps track.
        if not booking.cancel_booking():
            return None
        self.__cancelled_bookings.add(booking_reference)
        return booking

    def get_available_flights(self):
        available = []
        for flight in self.__flights.values():
            if flight.get_status() not in _BOOKABLE_STATUSES:
                continue
            # skip flights that are already full
            if self.seats_booked(flight) < flight.get_capacity():
                available.append(flight)
        return available

    def __str__(self):
        return (f'Booking system: {len(self.__flights)} flight(s), '
                f'{len(self.__passengers)} passenger(s), '
                f'{len(self.__bookings)} booking(s), '
                f'{len(self.__cancelled_bookings)} cancelled')


# quick test, only runs when this file is run directly
if __name__ == '__main__':
    from economy_ticket import EconomyTicket

    system = BookingSystem()
    passenger_1 = Passenger('Lui', 'lui@email.com', 'PA123456')
    passenger_2 = Passenger('Sam', 'sam@email.com', 'PB654321')
    passenger_3 = Passenger('Alex', 'alex@email.com', 'PC111222')
    small_flight = Flight('QF401', 'SYD', 'MEL', '10:00', 2, 'scheduled')
    cancelled_flight = Flight('QF500', 'SYD', 'BNE', '12:00', 100,
                              'cancelled')

    for passenger in (passenger_1, passenger_2, passenger_3):
        system.register_passenger(passenger)
    system.add_flight(small_flight)
    system.add_flight(cancelled_flight)
    ticket_1 = EconomyTicket(250.0, 1)

    # group booking fills the 2 seats
    booking_1 = system.create_booking([passenger_1, passenger_2],
                                      small_flight, ticket_1)
    print(booking_1)

    # flight is full and the other one is cancelled, so both give None
    print(system.create_booking(passenger_3, small_flight, ticket_1))
    print(system.create_booking(passenger_3, cancelled_flight, ticket_1))
    print([str(f) for f in system.get_available_flights()])

    # cancelling frees the seats back up
    system.cancel_booking('BK0001')
    print(system.create_booking(passenger_3, small_flight, ticket_1))
    print(system)
