from exceptions import (FlightStatusChangeError, InvalidCapacityError,
                        InvalidFlightStatusError)


class Flight:
    """A scheduled flight with a fixed number of seats and a status."""

    SCHEDULED = 'scheduled'
    DELAYED = 'delayed'
    DEPARTED = 'departed'
    CANCELLED = 'cancelled'
    VALID_STATUSES = {SCHEDULED, DELAYED, DEPARTED, CANCELLED}
    # Only these flights can still take or confirm bookings.
    BOOKABLE_STATUSES = {SCHEDULED, DELAYED}
    # Once a flight reaches one of these, its status can't change again.
    FINAL_STATUSES = {DEPARTED, CANCELLED}

    def __init__(self, flight_number, origin, destination, departure_time,
                 capacity, status):
        is_whole_number = (isinstance(capacity, int)
                           and not isinstance(capacity, bool))
        if not is_whole_number or capacity < 0:
            raise InvalidCapacityError(capacity)
        self.__flight_number = flight_number
        self.__origin = origin
        self.__destination = destination
        self.__departure_time = departure_time
        self.__capacity = capacity
        # Every flight starts as scheduled, then set_status checks the
        # real status. It raises on a bad one, so an invalid flight is
        # never created.
        self.__status = Flight.SCHEDULED
        self.set_status(status)

    def get_flight_number(self):
        return self.__flight_number

    def get_capacity(self):
        return self.__capacity

    def get_status(self):
        return self.__status

    def set_status(self, status):
        if status not in Flight.VALID_STATUSES:
            raise InvalidFlightStatusError(status, Flight.VALID_STATUSES)
        # A flight that has left or been cancelled can't come back.
        if self.__status in Flight.FINAL_STATUSES and status != self.__status:
            raise FlightStatusChangeError(self.__flight_number,
                                          self.__status, status)
        self.__status = status

    def is_bookable(self):
        return self.__status in Flight.BOOKABLE_STATUSES

    def __str__(self):
        return (f'{self.__flight_number}: {self.__origin} -> '
                f'{self.__destination} at {self.__departure_time} '
                f'({self.__status}, {self.__capacity} seats)')
