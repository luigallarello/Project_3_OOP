from ticket import Ticket


class EconomyTicket(Ticket):
    def __init__(self, base_fare, checked_bag_count):
        super().__init__(base_fare)
        self.__checked_bag_count = checked_bag_count

    def get_checked_bag_count(self):
        return self.__checked_bag_count

    def set_checked_bag_count(self, checked_bag_count):
        if isinstance(checked_bag_count, int):
            self.__checked_bag_count = checked_bag_count

    def calculate_price(self):
        # economy pays $35 for every checked bag
        return self.base_fare + self.__checked_bag_count * 35

    def baggage_allowance(self):
        return f'You have {self.__checked_bag_count} x 23 kg checked bags'

    def __str__(self):
        return (f'Economy ticket: ${self.calculate_price():.2f}, '
                f'{self.__checked_bag_count} checked bag(s)')


# quick test, only runs when this file is run directly
if __name__ == '__main__':
    ticket_1 = EconomyTicket(2325.22, 2)
    print(ticket_1.calculate_price())
    print(ticket_1.baggage_allowance())
    print(ticket_1)
