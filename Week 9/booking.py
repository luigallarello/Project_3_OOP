from passenger import Passenger
from flight import Flight
from ticket import Ticket

VALID_STATUSES = {'pending', 'confirmed', 'cancelled'}


class Booking():
    def __init__(self, booking_reference, booking_date, passengers, flight, ticket):
        # 1. Check passengers / flight / ticket are the right types
        #    (isinstance against Passenger, Flight, Ticket) -> raise TypeError.
        self.__booking_reference = booking_reference
        self.__booking_date = booking_date
        self.__status = 'pending'   # every new booking starts as pending
        self.__passengers = list(passengers)   # a booking can hold several passengers
        self.__flight = flight
        self.__ticket = ticket


    def get_booking_reference(self):
        return self.__booking_reference

    def set_booking_reference(self, booking_reference):
        if isinstance(booking_reference, str):
            self.__booking_reference = booking_reference
        else:
            return f'{booking_reference} is not a valid booking reference, please enter again.'

    booking_reference = property(get_booking_reference, set_booking_reference)


    def get_booking_date(self):
        return self.__booking_date

    def get_status(self):
        return self.__status

    def get_passengers(self):
        return list(self.__passengers)

    def add_passenger(self, passenger):
        if not isinstance(passenger, Passenger):
            return False
        for existing in self.__passengers:
            if existing.equals(passenger):
                return False
        self.__passengers.append(passenger)
        return True

    def get_flight(self):
        return self.__flight

    def get_ticket(self):
        return self.__ticket


    def confirm_booking(self):
        # 1. Only a 'pending' booking can be confirmed.
        #    Already confirmed or cancelled -> raise ValueError.

        # 2. (Optional) Flight must still be bookable:
        #    flight status 'cancelled' or 'departed' -> raise ValueError.

        # 3. Set self.__status = 'confirmed'.
        pass

    def cancel_booking(self):
        # 1. Already 'cancelled' -> raise ValueError (can't cancel twice).

        # 2. (Optional) Flight already 'departed' -> raise ValueError.

        # 3. Set self.__status = 'cancelled'.
        pass

    def total_cost(self):
        # 1. Ask the ticket for its price: self.__ticket.calculate_price()
        #    (polymorphism - works for Economy and Business tickets).

        # 2. Multiply by the number of passengers: len(self.__passengers).

        # 3. Return the total as a float.
        pass

    def equals(self, other):
        # 1. other is not a Booking -> return False.

        # 2. Two bookings are the same if their booking references match
        #    (same idea as Passenger.equals with passport numbers).
        pass
