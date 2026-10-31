from abc import ABC, abstractmethod


# abstract, so you have to make an EconomyTicket or BusinessTicket instead
class Ticket(ABC):
    def __init__(self, base_fare):
        self.set_base_fare(base_fare)

    def get_base_fare(self):
        return self.__base_fare

    def set_base_fare(self, base_fare):
        if isinstance(base_fare, float):
            self.__base_fare = base_fare

    base_fare = property(get_base_fare, set_base_fare)

    # each ticket type works these out its own way
    @abstractmethod
    def calculate_price(self):
        pass

    @abstractmethod
    def baggage_allowance(self):
        pass

    # shared by both ticket types, uses their own calculate_price()
    def __str__(self):
        return (f'{type(self).__name__}: '
                f'${self.calculate_price():.2f}')


# quick test, only runs when this file is run directly
if __name__ == '__main__':
    # Ticket is abstract so this should fail
    try:
        Ticket(100.0)
    except TypeError:
        print("Can't make a plain Ticket, it's abstract")
