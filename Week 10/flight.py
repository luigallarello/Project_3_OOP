_VALID_STATUSES = {'scheduled', 'delayed', 'departed', 'cancelled'}


class Flight:
    def __init__(self, flight_number, origin, destination, departure_time,
                 capacity, status):
        self.__flight_number = flight_number
        self.__origin = origin
        self.__destination = destination
        self.__departure_time = departure_time
        self.__capacity = capacity
        # Default to scheduled in case the status passed in isn't valid.
        self.__status = 'scheduled'
        self.set_status(status)

    def get_flight_number(self):
        return self.__flight_number

    def get_capacity(self):
        return self.__capacity

    def get_status(self):
        return self.__status

    def set_status(self, status):
        if status in _VALID_STATUSES:
            self.__status = status
        else:
            print(f'Invalid flight status: {status}')

    def __str__(self):
        return (f'{self.__flight_number}: {self.__origin} -> '
                f'{self.__destination} at {self.__departure_time} '
                f'({self.__status}, {self.__capacity} seats)')
