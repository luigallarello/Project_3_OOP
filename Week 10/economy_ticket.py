from ticket import BAG_FEE, BAG_WEIGHT_KG, Ticket


class EconomyTicket(Ticket):
    """A basic ticket where every checked bag is paid for."""

    TICKET_TYPE = 'Economy'

    def calculate_price(self):
        # Economy pays the bag fee for every checked bag.
        return self.get_base_fare() + self.get_checked_bag_count() * BAG_FEE

    def baggage_allowance(self):
        return (f'You have {self.get_checked_bag_count()} x {BAG_WEIGHT_KG} '
                f'kg checked bags')

    def __str__(self):
        return (f'Economy ticket: ${self.calculate_price():.2f}, '
                f'{self.get_checked_bag_count()} checked bag(s)')
