class Passenger:
    def __init__(self, name, email, passport_number):
        self.__name = name
        self.__email = email
        self.__passport_number = passport_number

    def get_name(self):
        return self.__name

    def set_name(self, name):
        if isinstance(name, str):
            self.__name = name

    name = property(get_name, set_name)

    def get_email(self):
        return self.__email

    def set_email(self, email):
        if isinstance(email, str):
            self.__email = email

    email = property(get_email, set_email)

    def get_passport_number(self):
        return self.__passport_number

    def set_passport_number(self, passport_number):
        if isinstance(passport_number, str):
            self.__passport_number = passport_number

    passport_number = property(get_passport_number, set_passport_number)

    def equals(self, other):
        if not isinstance(other, Passenger):
            return False
        # same passport means same person, even if they're separate objects
        return self.__passport_number == other.get_passport_number()

    def __str__(self):
        return (f'{self.__name} ({self.__email}), '
                f'passport {self.__passport_number}')


# quick test, only runs when this file is run directly
if __name__ == '__main__':
    passenger_1 = Passenger('Lui', 'lui@email.com', 'PA123456')
    passenger_2 = Passenger('Lui G', 'other@email.com', 'PA123456')
    print(passenger_1)
    print(passenger_1.equals(passenger_2))
