from passenger import Passenger

VALID_STATUSES = {'pending', 'confirmed', 'cancelled'}


class Booking:
    def __init__(self, booking_reference, booking_date, passengers,
                 flight, ticket):
        self.__booking_reference = booking_reference
        self.__booking_date = booking_date
        self.__status = 'pending'
        # list so one booking can cover a group
        self.__passengers = list(passengers)
        self.__flight = flight
        self.__ticket = ticket

    def get_booking_reference(self):
        return self.__booking_reference

    def set_booking_reference(self, booking_reference):
        if isinstance(booking_reference, str):
            self.__booking_reference = booking_reference
        else:
            return (f'{booking_reference} is not a valid booking reference, '
                    'please enter again.')

    booking_reference = property(get_booking_reference,
                                 set_booking_reference)

    def get_booking_date(self):
        return self.__booking_date

    def get_status(self):
        return self.__status

    def get_passengers(self):
        # return a copy so the list can't be changed from outside
        return list(self.__passengers)

    def add_passenger(self, passenger):
        if not isinstance(passenger, Passenger):
            return False
        # don't add the same person twice
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
        # Only a pending booking can be confirmed.
        if self.__status != 'pending':
            return False
        # A booking can't be confirmed for a flight that won't fly.
        if self.__flight.get_status() in ('cancelled', 'departed'):
            return False
        self.__status = 'confirmed'
        return True

    def cancel_booking(self):
        if self.__status == 'cancelled':
            return False
        # Once the flight has left it's too late to cancel.
        if self.__flight.get_status() == 'departed':
            return False
        self.__status = 'cancelled'
        return True

    def total_cost(self):
        # Each passenger needs their own seat, so the ticket price is
        # charged once per person. calculate_price() works for both
        # ticket types.
        return self.__ticket.calculate_price() * len(self.__passengers)

    def equals(self, other):
        if not isinstance(other, Booking):
            return False
        # Booking references are unique, so matching references means
        # it's the same booking.
        return self.__booking_reference == other.get_booking_reference()

    def __str__(self):
        names = ', '.join(p.get_name() for p in self.__passengers)
        return (f'Booking {self.__booking_reference} ({self.__status}) '
                f'on {self.__flight.get_flight_number()}, '
                f'booked {self.__booking_date}: {names}')


# quick test, only runs when this file is run directly
if __name__ == '__main__':
    from economy_ticket import EconomyTicket
    from flight import Flight

    flight_1 = Flight('QF401', 'SYD', 'MEL', '10:00', 180, 'scheduled')
    passenger_1 = Passenger('Lui', 'lui@email.com', 'PA123456')
    passenger_2 = Passenger('Sam', 'sam@email.com', 'PB654321')
    ticket_1 = EconomyTicket(250.0, 1)

    booking_1 = Booking('BK0001', '2026-10-29', [passenger_1],
                        flight_1, ticket_1)
    print(booking_1)
    print(booking_1.add_passenger(passenger_2))
    print(booking_1.add_passenger(passenger_2))   # already on it
    print(booking_1)

    # 2 passengers x (250 + 35 for 1 bag) = 570
    print(booking_1.total_cost())

    print(booking_1.confirm_booking())
    print(booking_1.confirm_booking())   # already confirmed
    print(booking_1.cancel_booking())
    print(booking_1.cancel_booking())    # already cancelled
    print(booking_1)

    booking_2 = Booking('BK0001', '2026-10-30', [passenger_2],
                        flight_1, ticket_1)
    booking_3 = Booking('BK0002', '2026-10-30', [passenger_2],
                        flight_1, ticket_1)
    print(booking_1.equals(booking_2))   # same reference
    print(booking_1.equals(booking_3))

    # A booking on a departed flight can't be confirmed or cancelled.
    departed_flight = Flight('QF9', 'SYD', 'PER', '06:00', 100, 'departed')
    late_booking = Booking('BK0003', '2026-10-30', [passenger_1],
                           departed_flight, ticket_1)
    print(late_booking.confirm_booking())
    print(late_booking.cancel_booking())
