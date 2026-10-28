
_VALID_STATUSES = {'scheduled', 'delayed', 'departed', 'cancelled'}


class Flight():
    def __init__(self, flight_number, origin, destination, departure_time, capacity, status):
        self.__flight_number = flight_number
        self.__origin = origin
        self.__destination = destination
        self.__departure_time = departure_time
        self.__capacity = capacity
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

    def set_origin(self,origin):
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
        if status not in _VALID_STATUSES:
            raise ValueError(f'Invalid flight status: {status}')
        self.__status = status

    status = property(get_status, set_status)

