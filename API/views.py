from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Aircraft, Airport, Flight, Booking, Passenger, Payment_provider, Invoice
from datetime import timedelta, datetime
import requests
import json
import random
from threading import Timer

#Function that deletes booking if still on hold
def deletebooking(booking):
    if booking.status == 'ON HOLD':
        booking.delete()

#Function that updates travlled bookings
def checkiftravelled():
    bookings = Booking.objects.filter(status='CONFIRMED')
    date = datetime.now()
    for booking in bookings:
        if date > booking.flight.dep_datetime :
            booking.status = 'TRAVELLED'
            booking.save()

def findflight(request): #GET request
    if request.method != 'GET': #If method not GET return 405 METHOD NOT ALLOWED
        return HttpResponse('Must be GET method', status=405)
    else:
        try:
            #Get the JSON payload
            json_data = request.read().decode('utf-8')
            data = json.loads(json_data)
        except:
            return HttpResponse('Payload must be in JSON format', status=415)

        #Get details from the payload
        dep_airport = data['dep_airport']
        dest_airport = data['dest_airport']
        dep_date = data['dep_date']
        num_passengers = data['num_passengers']
        is_flex = data['is_flex']

        #Get available flights - if is_flex is true check in range of date +- a day
        if is_flex == True or is_flex == 'True': #Check if formatted as a string on client end
            date = timezone.make_aware(datetime.strptime(dep_date, '%Y-%m-%d'), timezone.get_default_timezone()) #Add default timezone
            start_date = str(date - timedelta(days=1)).split()[0] #Subtract a day from start_date
            end_date = str(date + timedelta(days=2)).split()[0] #Add two days to end date (has to cover more than 24hrs later)
            matching_flights = Flight.objects.filter(dep_airport__contains=dep_airport,
                dest_airport__contains=dest_airport, dep_datetime__range=(start_date, end_date)).values('pk', 'flight_num', 'dep_airport',
                'dest_airport', 'dep_datetime', 'arr_datetime', 'duration', 'price', 'aircraft')
        else:
            matching_flights = Flight.objects.filter(dep_airport__contains=dep_airport,
                dest_airport__contains=dest_airport, dep_datetime__contains=dep_date).values('pk', 'flight_num', 'dep_airport',
                'dest_airport', 'dep_datetime', 'arr_datetime', 'duration', 'price', 'aircraft')

        #Get timezones of dep_airport and dest_airport
        dep_timezone = Airport.objects.get(airport_name__contains=dep_airport).time_zone
        dest_timezone = Airport.objects.get(airport_name__contains=dest_airport).time_zone

        flight_list = []
        for matching_flight in matching_flights:
            booked_seats = 0
            bookings = Booking.objects.filter(flight=matching_flight['pk'],status__in=['CONFIRMED','ON HOLD']) #Get all bookings for that flight that are on hold or confirmed

            for booking in bookings: #Sum total number of seats booked
                booked_seats += booking.num_seats_booked

            #Check there are enough seats on the flight
            if not booked_seats + num_passengers > Aircraft.objects.get(pk=matching_flight['aircraft']).num_seats:
                flight = { 'flight_id' : matching_flight['pk'], 'flight_num' : matching_flight['flight_num'], 'dep_airport' : matching_flight['dep_airport'],
                            'dest_airport' : matching_flight['dest_airport'], 'dep_date': str(matching_flight['dep_datetime']) + ' ' + dep_timezone,
                            'arr_date' : str(matching_flight['arr_datetime']) + ' ' + dest_timezone, 'duration' : matching_flight['duration'], 'price' : matching_flight['price'] }
                flight_list.append(flight)

        payload = { 'flights' : flight_list }
        payload = json.dumps(payload, default=str) #default=str allows serializing of datetimes

        #If flights available, return 200 OK response and flight JSON payload
        if len(flight_list) != 0:
            return HttpResponse(payload, content_type='application/json', status=200)

        #Else return 503 SERVICE UNAVAILABLE response
        else:
            return HttpResponse('No flights available', status=503)


@csrf_exempt
def bookflight(request): #POST request
    if request.method != 'POST': #If method not POST return 405 METHOD NOT ALLOWED
        return HttpResponse('Must be POST method', status=405)
    else:
        try:
            #Convert from JSON
            json_data = request.read().decode('utf-8')
            data = json.loads(json_data)

        except:
            return HttpResponse('Payload must be in JSON format', status=415)

        #Get flight_id, passenger details and num_passengers
        flight_id = data['flight_id']
        passengers = data['passengers']
        num_passengers = len(passengers)

        #Create separate arrays to store passenger details - used to link passengers and booking (many-to-many)
        first_names = []
        surnames = []
        emails = []
        phones = []

        #Check to see if there is space available
        booked_seats = 0
        bookings = Booking.objects.filter(flight=flight_id,status__in=['CONFIRMED','ON HOLD']) #Get all bookings for that flight that are on hold or confirmed
        flight = Flight.objects.get(pk=flight_id) #Get flight details

        for booking in bookings: #Sum total number of seats booked
            booked_seats += booking.num_seats_booked

        #If no seats available return 503 UNAVAILABLE
        if booked_seats + num_passengers > flight.aircraft.num_seats:
            return HttpResponse('No seats available', status=503)
        #If seats available create booking
        else:
            for i in range(0, num_passengers): #Create/get passenger objects in/from database
                Passenger.objects.get_or_create(first_name=passengers[i]['first_name'], surname=passengers[i]['surname'],
                                                email=passengers[i]['email'], phone=passengers[i]['phone'])
                first_names.append(passengers[i]['first_name'])
                surnames.append(passengers[i]['surname'])
                emails.append(passengers[i]['email'])
                phones.append(passengers[i]['phone'])

            #Get list of passengers in this booking
            passengers = Passenger.objects.filter(first_name__in=first_names, surname__in=surnames, email__in=emails, phone__in=phones)
            passengers = list(passengers)

            #Create a (unique) booking number - randomness it less likely to be guessed
            random.seed()
            booking_num = 'AH' + str(flight_id) + str(len(Booking.objects.all())+1) + str(random.randint(0,99))

            #Create the booking and add the passengers details
            created_booking = Booking(booking_num=booking_num, flight=flight, num_seats_booked=num_passengers)
            created_booking.save()
            created_booking.passengers.add(*passengers)

            #Get the total price and status
            seat_price = Flight.objects.get(pk=flight_id).price
            tot_price = num_passengers*seat_price
            status = created_booking.status

            #Create JSON payload containing booking details
            booking_details = { 'booking_num' : booking_num, 'booking_status' : status, 'tot_price' : str(tot_price) }
            booking_details = json.dumps(booking_details)

            #Delete booking after a certain time if still ON HOLD
            t = Timer(created_booking.time.total_seconds(), deletebooking, args=[created_booking])
            t.start()

            #Return booking details and 201 CREATED
            return HttpResponse(booking_details, content_type='application/json', status=201)


def paymentmethods(request): #GET request
    if request.method != 'GET': #If method not GET return 405 METHOD NOT ALLOWED
        return HttpResponse('Must be GET method', status=405)
    else:
        #Get payment providers from database
        pay_provider_list = []
        pay_providers = Payment_provider.objects.all().values('pk', 'name')
        for pay_provider in pay_providers:
            provider = { 'pay_provider_id' : pay_provider['pk'], 'pay_provider_name' : pay_provider['name'] }
            pay_provider_list.append(provider)

        payload = { 'pay_providers' : pay_provider_list }
        payload = json.dumps(payload)

        #Return payment methods and 200 OK if list not empty
        if len(pay_provider_list) != 0:
            return HttpResponse(payload, content_type='application/json', status=200)
        else: #If no providers in database, return 503 SERVICE UNAVAILABLE response
            return HttpResponse('No payment service providers available', status=503)


@csrf_exempt
def payforbooking(request): #POST request
    if request.method != 'POST': #If method not POST return 405 METHOD NOT ALLOWED
        return HttpResponse('Must be POST method', status=405)
    else:
        try: #Convert from JSON
            json_data = request.read().decode('utf-8')
            data = json.loads(json_data)
        except: #If not in JSON format return 415 UNSUPPORTED MEDIA TYPE
            return HttpResponse('Payload must be in JSON format', status=415)

        #Get pay_provider_id, invoice_id, booking_num
        booking_num = data['booking_num']
        pay_provider_id = data['pay_provider_id']

        try: #Get pay_provider details from database
            payment_provider = Payment_provider.objects.get(pk=pay_provider_id)
        except: #If payment provider not found in database return 404 NOT FOUND
            return HttpResponse('Payment provider not found, ensure you have entered the correct id', status=404)

        url = payment_provider.web_address
        account_num = payment_provider.account_num
        username = payment_provider.username
        password = payment_provider.password

        #Create payload and login to payment provider (urlencoded format not JSON)
        payload = { 'username' : username, 'password' : password }
        try:
            s = requests.Session()
            r = s.post(url + '/api/login/', data=payload)

            if r.status_code != 200: #Check if login successful
                return HttpResponse('Could not establish connection to payment service provider', status=503)

            else:
                #Create invoice
                try:
                    booking = Booking.objects.get(booking_num=booking_num)
                    amount = str(booking.num_seats_booked*booking.flight.price)
                    payload = { 'account_num' : account_num, 'client_ref_num' : booking_num, 'amount' : amount }
                    r = s.post(url + 'api/createinvoice/', json=payload, headers={'Content-type': 'application/json'})
                    print(r.status_code, r.text)

                    if r.status_code != 201: #Check invoice has been created
                        return HttpResponse('Could not establish connection to payment service provider', status=503)
                    else:
                        #Read data back from payment provider
                        data = r.json()
                        payprovider_ref_num = data['payprovider_ref_num']
                        stamp_code = data['stamp_code']

                        #Add invoice to database
                        invoice = Invoice.objects.create(air_reference_num=booking_num, pay_reference_num=payprovider_ref_num,
                                                    booking_num=booking_num, amount=amount, paid=False, stamp=stamp_code)

                        #Logout of payment provider
                        r = s.post(url + '/api/logout/')

                        #Create JSON payload to return to the client
                        payload = { 'pay_provider_id' : pay_provider_id, 'invoice_id' : payprovider_ref_num, 'booking_num': booking_num, 'url' : url}
                        payload = json.dumps(payload)

                        #Return payload and 201 CREATED
                        return HttpResponse(payload, content_type='application/json', status=201)
                except:
                    return HttpResponse('Booking not found. Your booking may have been deleted if it was on hold for too long', status=404)
        except:
            return HttpResponse('Could not establish connection to payment service provider', status=503)


@csrf_exempt
def finalizebooking(request): #POST request
    if request.method != 'POST': #If method not POST return 405 METHOD NOT ALLOWED
        return HttpResponse('Must be GET POST method', status=405)
    else:
        try: #Get JSON data and convert
            json_data = request.read().decode('utf-8')
            data = json.loads(json_data)
        except: #If not in JSON format return 415 UNSUPPORTED MEDIA TYPE
            return HttpResponse('Payload must be in JSON format', status=415)

        #Get booking_num, pay_provider_id and stamp
        booking_num = data['booking_num']
        pay_provider_id = data['pay_provider_id']
        stamp = data['stamp']

        try: #Lookup booking and invoice in database
            booking = Booking.objects.get(booking_num=booking_num)
            invoice = Invoice.objects.get(booking_num=booking_num)
        except: #If booking can't be found in database return 404 NOT FOUND
            return HttpResponse('Booking not found', status=404)

        #Check if given stamp matches stamp in database
        if stamp != invoice.stamp:
            return HttpResponse('Electronic stamp does not match', status=503)
        else: #If given stamp matches stamp in database

            #Change booking status to CONFIRMED and invoice paid to True
            booking.status='CONFIRMED'
            invoice.paid=True

            #Save to database
            booking.save()
            invoice.save()

            #Create JSON payload to be returned to client
            payload = { 'booking_num' : booking_num, 'booking_status' : booking.status }
            payload = json.dumps(payload)

            #Return payload and 201 CREATED
            return HttpResponse(payload, content_type='application/json', status=201)


def bookingstatus(request): #GET request

    #Update all previous bookings
    checkiftravelled()

    if request.method != 'GET': #If method not GET return 405 METHOD NOT ALLOWED
        return HttpResponse(status=405)
    else:
        try:
            #Get JSON data and convert
            json_data = request.read().decode('utf-8')
            data = json.loads(json_data)
        except: #If not in JSON format return 415 UNSUPPORTED MEDIA TYPE
            return HttpResponse('Payload must be in JSON format', status=415)

        #Get booking_num
        booking_num = data['booking_num']

        try: #Lookup booking in database and get details
            booking = Booking.objects.get(booking_num=booking_num)
        except: #If booking can't be found in database return 404 NOT FOUND
            return HttpResponse('Booking not found. Your booking may have been deleted if it was on hold for too long', status=404)

        #Get booking details
        booking_status = booking.status
        flight_num = booking.flight.flight_num
        dep_airport = booking.flight.dep_airport
        dest_airport = booking.flight.dest_airport
        dep_timezone = Airport.objects.get(airport_name__contains=dep_airport).time_zone
        dest_timezone = Airport.objects.get(airport_name__contains=dest_airport).time_zone
        dep_datetime = str(booking.flight.dep_datetime) + ' ' + dep_timezone
        arr_datetime = str(booking.flight.arr_datetime) + ' ' + dest_timezone
        duration = booking.flight.duration



        #Create JSON payload to be returned to user
        payload = { 'booking_num' : booking_num, 'booking_status' : booking_status, 'flight_num' : flight_num,
                    'dep_airport' : dep_airport, 'dest_airport' : dest_airport, 'dep_datetime' : dep_datetime,
                    'arr_datetime' : arr_datetime, 'duration' : duration }
        payload = json.dumps(payload, default=str)

        #Return payload and 200 OK
        return HttpResponse(payload, content_type='application/json', status=200)

@csrf_exempt
def cancelbooking(request): #POST request
    if request.method != 'POST': #If method not GET return 405 METHOD NOT ALLOWED
        return HttpResponse(status=405)
    else:
        try: #Get JSON data and convert
            json_data = request.read().decode('utf-8')
            data = json.loads(json_data)
        except: #If not in JSON format return 415 UNSUPPORTED MEDIA TYPE
            return HttpResponse('Payload must be in JSON format', status=415)

        #Get booking_num
        booking_num = data['booking_num']

        try: #Lookup booking in database and get details
            booking = Booking.objects.get(booking_num=booking_num)
        except: #If booking can't be found in database return 404 NOT FOUND
            return HttpResponse('Booking not found. Your booking may have been deleted if it was on hold for too long', status=404)

        #Change booking status to cancelled and save to database
        booking.status = 'CANCELLED'
        booking.save()

        payload = { 'booking_num' : booking.booking_num, 'booking_status': booking.status }
        payload = json.dumps(payload)

        #If successful return 201 CREATED
        return HttpResponse(payload, content_type='application/json', status=201)
