_VALID_STATUSES = {'scheduled', 'delayed', 'departed', 'cancelled'}


class Flight:
    def __init__(self, flight_number, origin, destination, departure_time,
                 capacity, status):
        self.__flight_number = flight_number
        self.__origin = origin
        self.__destination = destination
        self.__departure_time = departure_time
        self.__capacity = capacity
        # default to scheduled in case the status passed in isn't valid
        self.__status = 'scheduled'
        self.set_status(status)

    def get_flight_number(self):
        return self.__flight_number

    def set_flight_number(self, flight_number):
        if isinstance(flight_number, str):
            self.__flight_number = flight_number
        else:
            print('Please assign a proper flight number.')

    flight_number = property(get_flight_number, set_flight_number)

    def get_origin(self):
        return self.__origin

    def set_origin(self, origin):
        if isinstance(origin, str):
            self.__origin = origin

    origin = property(get_origin, set_origin)

    def get_destination(self):
        return self.__destination

    def set_destination(self, destination):
        if isinstance(destination, str):
            self.__destination = destination

    destination = property(get_destination, set_destination)

    def get_departure_time(self):
        return self.__departure_time

    def set_departure_time(self, departure_time):
        if isinstance(departure_time, str):
            self.__departure_time = departure_time

    departure_time = property(get_departure_time, set_departure_time)

    def get_capacity(self):
        return self.__capacity

    def set_capacity(self, capacity):
        if isinstance(capacity, int):
            self.__capacity = capacity
        else:
            print('Invalid capacity')

    capacity = property(get_capacity, set_capacity)

    def get_status(self):
        return self.__status

    def set_status(self, status):
        if status in _VALID_STATUSES:
            self.__status = status
        else:
            print(f'Invalid flight status: {status}')

    status = property(get_status, set_status)

    def __str__(self):
        return (f'{self.__flight_number}: {self.__origin} -> '
                f'{self.__destination} at {self.__departure_time} '
                f'({self.__status}, {self.__capacity} seats)')


# quick test, only runs when this file is run directly
if __name__ == '__main__':
    flight_1 = Flight('QF401', 'SYD', 'MEL', '10:00', 180, 'scheduled')
    print(flight_1)
    flight_1.set_status('delayed')
    print(flight_1)
    flight_1.set_status('boarding')
    print(flight_1)
