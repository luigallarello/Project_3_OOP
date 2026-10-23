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
        return self.base_fare + self.__checked_bag_count * 35

    def baggage_allowance(self):
        return f'You have {self.__checked_bag_count} x 23 kg checked bags'



Ticket_1 = EconomyTicket(2325.22, 2)


Ticket_1.calculate_price()