from abc import ABC, abstractmethod

# Both ticket types charge the same fee for a paid checked bag.
BAG_FEE = 35.0


# Abstract, so you have to make an EconomyTicket or BusinessTicket instead.
class Ticket(ABC):
    def __init__(self, base_fare):
        self.__base_fare = 0.0
        self.set_base_fare(base_fare)

    def get_base_fare(self):
        return self.__base_fare

    def set_base_fare(self, base_fare):
        # Whole numbers are fine too, they're stored as floats.
        is_number = (isinstance(base_fare, (int, float))
                     and not isinstance(base_fare, bool))
        if is_number and base_fare >= 0:
            self.__base_fare = float(base_fare)
        else:
            print(f'Invalid base fare: {base_fare}')

    @abstractmethod
    def calculate_price(self):
        """Work out the full price, each ticket type does this itself."""

    @abstractmethod
    def baggage_allowance(self):
        """Describe the checked baggage this ticket includes."""
