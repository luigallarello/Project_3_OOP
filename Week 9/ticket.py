from abc import ABC, abstractmethod


class Ticket(ABC):
    def __init__(self, base_fare):
        self.set_base_fare(base_fare)

    def get_base_fare(self):
        return self.__base_fare

    def set_base_fare(self, base_fare):
        if isinstance(base_fare, float):
            self.__base_fare = base_fare

    base_fare = property(get_base_fare, set_base_fare)

    @abstractmethod
    def calculate_price(self):
        pass

    @abstractmethod
    def baggage_allowance(self):
        pass

    