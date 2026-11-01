class Passenger:
    def __init__(self, name, email, passport_number):
        self.__name = name
        self.__email = email
        self.__passport_number = passport_number

    def get_name(self):
        return self.__name

    def get_passport_number(self):
        return self.__passport_number

    def equals(self, other):
        if not isinstance(other, Passenger):
            return False
        # Same passport means same person, even if they're separate objects.
        return self.__passport_number == other.get_passport_number()

    def __str__(self):
        return (f'{self.__name} ({self.__email}), '
                f'passport {self.__passport_number}')
