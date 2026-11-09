from abc import ABC, abstractmethod

from exceptions import InvalidBaggageError, InvalidFareError

# Both ticket types charge the same fee for a paid checked bag.
BAG_FEE = 35.0
BAG_WEIGHT_KG = 23


class Ticket(ABC):
    """The shared parts of every ticket: a base fare and checked bags.

    Ticket is abstract, so an EconomyTicket or BusinessTicket has to be
    made instead. Each type sets its own name and bag limit and works out
    its own price.
    """

    TICKET_TYPE = 'Ticket'
    # None means there's no upper limit on checked bags.
    MAX_CHECKED_BAGS = None

    def __init__(self, base_fare, checked_bag_count):
        # Both setters raise before anything is stored, so a ticket with a
        # bad fare or bag count is never created.
        self.__base_fare = 0.0
        self.__checked_bag_count = 0
        self.set_base_fare(base_fare)
        self.set_checked_bag_count(checked_bag_count)

    def get_base_fare(self):
        return self.__base_fare

    def set_base_fare(self, base_fare):
        # Whole numbers are fine too, they're stored as floats. True and
        # False count as numbers in Python, so they're ruled out on their
        # own.
        is_number = (isinstance(base_fare, (int, float))
                     and not isinstance(base_fare, bool))
        if not is_number or base_fare < 0:
            raise InvalidFareError(base_fare)
        self.__base_fare = float(base_fare)

    def get_checked_bag_count(self):
        return self.__checked_bag_count

    def set_checked_bag_count(self, checked_bag_count):
        is_whole_number = (isinstance(checked_bag_count, int)
                           and not isinstance(checked_bag_count, bool))
        is_valid = is_whole_number and checked_bag_count >= 0
        if is_valid and self.MAX_CHECKED_BAGS is not None:
            is_valid = checked_bag_count <= self.MAX_CHECKED_BAGS
        if not is_valid:
            # Raise before changing anything so the old count is kept.
            raise InvalidBaggageError(self.TICKET_TYPE, checked_bag_count,
                                      self.MAX_CHECKED_BAGS)
        self.__checked_bag_count = checked_bag_count

    @abstractmethod
    def calculate_price(self):
        """Work out the full price, each ticket type does this itself."""

    @abstractmethod
    def baggage_allowance(self):
        """Describe the checked baggage this ticket includes."""
