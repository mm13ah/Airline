from django.db import models
from datetime import timedelta

class Aircraft(models.Model):
    aircraft_type = models.CharField(max_length=30)
    registration_number = models.CharField(max_length=10, unique=True)
    num_seats = models.PositiveSmallIntegerField()

    def __str__(self):
        return u'%s, %s, %s'%(self.aircraft_type, self.registration_number, self.num_seats)

class Airport(models.Model):
    airport_name = models.CharField(max_length=30, unique=True)
    country = models.CharField(max_length=30)
    time_zone = models.CharField(max_length=30)

    def __str__(self):
        return u'%s, %s, %s'%(self.airport_name, self.country, self.time_zone)

class Flight(models.Model):
    flight_num = models.CharField(max_length=10)
    dep_airport = models.CharField(max_length=30)
    dest_airport = models.CharField(max_length=30)
    dep_datetime = models.DateTimeField()
    arr_datetime = models.DateTimeField()
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    duration = models.DurationField()
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return u'%s, %s, %s, %s, %s, %s, %s'%(self.flight_num, self.dep_airport, self.dest_airport, self.dep_datetime, self.arr_datetime, self.duration, self.price)

class Passenger(models.Model):
    first_name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    email = models.CharField(max_length=70)
    phone = models.CharField(max_length=12)

    def __str__(self):
        return u'%s, %s, %s, %s'%(self.first_name, self.surname, self.email, self.phone)

class Booking(models.Model):
    booking_num = models.CharField(max_length=10, unique=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    num_seats_booked = models.PositiveSmallIntegerField()
    passengers = models.ManyToManyField(Passenger)
    status = models.CharField(max_length=9, default='ON HOLD')
    time = models.DurationField(default=timedelta(minutes=30))

    def __str__(self):
        return u'%s, %s, %s, %s'%(self.booking_num, self.num_seats_booked, self.passengers.all(), self.status)

class Payment_provider(models.Model):
    name = models.CharField(max_length=30)
    web_address = models.URLField()
    account_num = models.CharField(max_length=10)
    username = models.CharField(max_length=10, default='mm13ah')
    password = models.CharField(max_length=20, default='badpassword')

    def __str__(self):
        return u'%s, %s, %s'%(self.name, self.web_address, self.account_num)

class Invoice(models.Model):
    air_reference_num = models.CharField(max_length=10, unique=True)
    pay_reference_num = models.CharField(max_length=10, unique=True)
    booking_num = models.CharField(max_length=6)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    paid = models.BooleanField()
    stamp = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return u'%s, %s, %s, %s, %s, %s'%(self.air_reference_num, self.pay_reference_num, self.booking_num, self.amount, self.paid, self.stamp)
