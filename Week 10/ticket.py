from abc import ABC, abstractmethod

from exceptions import InvalidFareError

# Both ticket types charge the same fee for a paid checked bag.
BAG_FEE = 35.0


# Abstract, so you have to make an EconomyTicket or BusinessTicket instead.
class Ticket(ABC):
    def __init__(self, base_fare):
        # set_base_fare raises before anything is stored, so a ticket with
        # a bad fare is never created.
        self.__base_fare = 0.0
        self.set_base_fare(base_fare)

    def get_base_fare(self):
        return self.__base_fare

    def set_base_fare(self, base_fare):
        # Whole numbers are fine too, they're stored as floats.
        is_number = (isinstance(base_fare, (int, float))
                     and not isinstance(base_fare, bool))
        if not is_number or base_fare < 0:
            raise InvalidFareError(base_fare)
        self.__base_fare = float(base_fare)

    @abstractmethod
    def calculate_price(self):
        """Work out the full price, each ticket type does this itself."""

    @abstractmethod
    def baggage_allowance(self):
        """Describe the checked baggage this ticket includes."""
