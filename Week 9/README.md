# Project_3_OOP


22/10:
Today the passenger class is being written up. It includes three attributes: name, email and passport number. All of these are private and should be processed as strings. Each of the attributes have getters and setters and there is one additional method called 'equals'.

equals() defines value equality for Passenger. Two objects represent the same passenger if their passport numbers match, regardless of whether they are in the same object of memory.

28/10 Workshop 9-1: Code review with Billy:
Todays code review billy went over my uml design with all of my proposed methods etc. He noted I didn't need dunder and magic methods in my uml. He also noted that a booking can hold multiple passengers rather than just one, and my current booking only stores one passenger. He noted a few relationship changes on the uml as well, in specific the passenger -> bookingsystem and booking system to booking. This is because the booking system creates the booking but is listed as the wrong relationship.