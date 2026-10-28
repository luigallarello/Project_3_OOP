VALID_STATUSES = pass

class Booking():
    def __init__(self, passenger, flight, ticket):
        self.__booking_reference = booking_reference
        self.__booking_date = booking_date
        self.__status = status
        self.__passenger = passenger
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

    def get_passenger(self):
        return self.__passenger

    def get_flight(self):
        return self.__flight

    def get_ticket(self):
        return self.__ticket

    def confirm_booking(self, booking_reference):
        pass

    def cancel_booking(self, booking_reference):
        pass

    def total_cost(self):
        pass

    def equals(self, Booking):
        pass

    