import requests
import json
import ast
import sys

print('\n*******************************************************************************')
print('Welcome to mm13ah client software.')

while True: #Allows commands to be entered one after the other
    ### MAIN MENU ###
    print('\nMAIN MENU')
    print('\nPlease choose a service from the menu below: ')
    print('  1. Airlines')
    print('  2. Payment service providers')

    option = input("\nPlease enter your choice, or type 'exit' to exit: ")

    if option == '1': #AIRLINES
        #Get available airlines and print them to user
        try:
            r = requests.get('http://directory.pythonanywhere.com/api/list/', json={'company_type' : 'airline'}, headers={'Content-type': 'application/json'})

        except:
            print('Could not connect to directory. Please check your internet connection')
            sys.exit()
        company_list = r.json()['company_list']
        urls = [] #Store urls so requests can be sent
        print("\nYou have selected airlines\n\nAirlines available: ")
        for i in range(0, len(company_list)):
            print('  ' + str(i+1) + '.', company_list[i]['company_name'], ' - ', company_list[i]['url'])
            if company_list[i]['url'][-1] != '/':
                company_list[i]['url'] += '/'
            urls.append(company_list[i]['url'])
        while True:
            #Get command from user - while True allows commands to be entered one after the other
            user_command = input("\nPlease enter a command. Type 'help' to list commands, 'menu' to return to the menu or 'exit' to exit the program.\n")

            #AIRLINE COMMANDS
            if (user_command == 'findflight'):
                #Get desired flight details from user
                print('\nPlease enter flight details:')
                dep_airport = input('\n  Departure airport: ')
                dest_airport = input('  Destination airport: ')
                dep_date = input('  Departure date (YYYY-MM-DD): ')
                num_passengers = input('  Enter number of passengers: ')
                try:
                    num_passengers = int(num_passengers)
                except:
                    while type(num_passengers) != int: #Ensure num_passengers is an integer
                        try:
                            num_passengers = int(input('  Number of passengers must be an integer, please try again: '))
                        except ValueError:
                            pass
                is_flex = input('  Enter if flexible (Y/N): ').upper() #Convert to upper incase y/n is entered
                while is_flex not in ('Y', 'N'): #Ensure is_flex is Y/N
                    is_flex = input('  If flexible must be Y or N. Enter if flexible: ').upper()
                if is_flex == 'Y': #Convert is_flex to True of False
                    is_flex = True
                elif is_flex == 'N':
                    is_flex = False

                payload = { 'dep_airport' : dep_airport, 'dest_airport' : dest_airport, 'dep_date' : dep_date,
                            'num_passengers' : num_passengers, 'is_flex' : is_flex }

                #Check if user wants to find all flights or flights from a specific airline
                airline = input("Please enter the number of the airline you would like to select, or to find flights from all airlines type '*': \n")
                if airline == '*': #Find flights from all airlines
                    for url in urls: #Loop through list of airline URLs and find matching flights
                        r = requests.get(url + 'api/findflight/', json=payload, headers={'Content-type': 'application/json'})
                        if r.status_code == 200: #If successful print flights
                            print('\nFlights found from: ', url)
                            parsed = json.loads(r.text)
                            print(json.dumps(parsed, indent=4, sort_keys=False))
                        else: #If unsuccessful, return error code and reason
                            print('\nNo flights found from: ', url)
                            print('Response: ', r.status_code, r.text)
                else:
                    try: #Validate input
                        if 1 <= int(airline) <= len(urls): #Find flights from entered airline
                            airline_url = urls[int(airline)-1]
                            try:
                                r = requests.get(airline_ul + 'api/findflight/', json=payload, headers={'Content-type': 'application/json'})
                                if r.status_code == 200: #If successful print flights
                                    print('\nFlights found from: ', airline_url)
                                    parsed = json.loads(r.text)
                                    print(json.dumps(parsed, indent=4, sort_keys=False))
                                else: #If unsuccessful return error code and reason
                                    print('\nNo flights found from: ', airline_url)
                                    print('Response: ', r.status_code, r.text)
                            except:
                                print('Could not connect to the airline')
                        else:
                            print('Invalid airline, please enter a number between 1 -', len(urls), "or type '*' for all airlines")
                    except ValueError:
                        print('Invalid airline, please enter a number between 1 -', len(urls), "or type '*' for all airlines")

            elif (user_command == 'bookflight'):
                #Get airline from user
                airline = input("Please enter the number of the airline you would like to select: ")
                try: #Validate input
                    if 1 <= int(airline) <= len(urls):
                        airline_url = urls[int(airline)-1]
                        flight_id = input('  Enter flight id: ')
                        num_passengers = input('  Enter number of passengers: ')
                        try:
                            num_passengers = int(num_passengers)
                        except:
                            while type(num_passengers) != int: #Ensure num_passengers is an integer
                                try:
                                    num_passengers = int(input('  Number of passengers must be an integer, please try again: '))
                                except ValueError:
                                    pass
                        passengers = []
                        print('  Please enter details for each passenger: ')
                        for i in range(0, num_passengers): #Store details of each passenger in a dictionary
                            print('    Passenger ' + str(i+1))
                            passenger = {
                                'first_name' : input('      First name: '),
                                'surname' : input('      Surname: '),
                                'email' : input('      Email: '),
                                'phone' : input('      Phone: '),
                            }
                            passengers.append(passenger)
                        payload = { 'flight_id' : flight_id, 'passengers' : passengers }
                        try:
                            r = requests.post(airline_url + 'api/bookflight/', json=payload, headers={'Content-type': 'application/json'})
                            if r.status_code == 201: #If successful print booking details
                                print('\nBooking successful! Details: ')
                                parsed = json.loads(r.text)
                                print(json.dumps(parsed, indent=4, sort_keys=False))
                            else: #If unsuccessful return error code and reason
                                print('\nBooking unsuccessful.')
                                print('Response: ', r.status_code, r.text)
                        except:
                            print('Could not connect to the airline')
                    else:
                        print('Invalid airline, please enter a number between 1 -', len(urls))
                except ValueError:
                    print('Invalid airline, please enter a number between 1 -', len(urls))


            elif (user_command == 'paymentmethods'):
                #Get airline from user
                airline = input("Please enter the number of the airline you would like to select: ")
                try: #Validate input
                    if 1 <= int(airline) <= len(urls):
                        airline_url = urls[int(airline)-1]
                        try:
                            r = requests.get(airline_url + 'api/paymentmethods/')
                            if r.status_code == 200: #If successful print payment methods
                                print('\nPayment methods available from this airline: ')
                                parsed = json.loads(r.text)
                                print(json.dumps(parsed, indent=4, sort_keys=False))
                            else: #If unsuccessful return error code and reason
                                print('\nNo payment methods found')
                                print('Reponse: ', r.status_code, r.text)
                        except:
                            print('Could not connect to the airline')
                    else:
                        print('Invalid airline, please enter a number between 1 -', len(urls))
                except ValueError:
                    print('Invalid airline, please enter a number between 1 -', len(urls))

            elif (user_command == 'payforbooking'):
                #Get airline from user
                airline = input("Please enter the number of the airline you would like to select: ")
                try: #Validate input
                    if 1 <= int(airline) <= len(urls):
                        airline_url = urls[int(airline)-1]
                        booking_num = input('Enter booking number: ')
                        pay_provider_id = input('Enter payment provider id: ')
                        payload = { 'booking_num' : booking_num, 'pay_provider_id' : pay_provider_id }
                        try:
                            r = requests.post(airline_url + 'api/payforbooking/', json=payload, headers={'Content-type': 'application/json'})
                            if r.status_code == 201: #If successful return payment details
                                print('\nSuccess! Please make a note of the following details and proceed to payment with the payment service provider')
                                parsed = json.loads(r.text)
                                print(json.dumps(parsed, indent=4, sort_keys=False))
                            else: #If unsuccessful return error code and reason
                                print('\nPayment unsuccessful')
                                print('Response: ', r.status_code, r.text)
                        except:
                            print('Could not connect to the airline')
                    else:
                        print('Invalid airline, please enter a number between 1 -', len(urls))
                except ValueError:
                    print('Invalid airline, please enter a number between 1 -', len(urls))

            elif (user_command == 'finalizebooking'):
                #Get airline from user
                airline = input("Please enter the number of the airline you would like to select: ")
                try: #Validate input
                    if 1 <= int(airline) <= len(urls):
                        airline_url = urls[int(airline)-1]
                        booking_num = input('  Enter booking number: ')
                        pay_provider_id = input('  Enter payment provider id: ')
                        stamp = input('  Enter payment provider electronic stamp: ')
                        payload = { 'booking_num' : booking_num, 'pay_provider_id' : pay_provider_id, 'stamp' : stamp }
                        try:
                            r = requests.post(airline_url + 'api/finalizebooking/', json=payload, headers={'Content-type': 'application/json'} )
                            if r.status_code == 201: #If successful return final booking details
                                print('\nBooking finalized! Details: ')
                                parsed = json.loads(r.text)
                                print(json.dumps(parsed, indent=4, sort_keys=False))
                            else: #If unsuccessful return error code and reason
                                print('\nBooking finalization unsuccessful.')
                                print('Response: ', r.status_code, r.text)
                        except:
                            print('Could not connect to the airline')
                    else:
                        print('Invalid airline, please enter a number between 1 -', len(urls))
                except ValueError:
                    print('Invalid airline, please enter a number between 1 -', len(urls))

            elif (user_command == 'bookingstatus'):
                #Get airline from user
                airline = input("Please enter the number of the airline you would like to select: ")
                try: #Validate input
                    if 1 <= int(airline) <= len(urls):
                        airline_url = urls[int(airline)-1]
                        booking_num = input('  Enter booking number: ')
                        payload = { 'booking_num' : booking_num }
                        try:
                            r = requests.get(airline_url + 'api/bookingstatus/', json=payload, headers={'Content-type': 'application/json'})
                            if r.status_code == 200: #If successful return booking status
                                print('\nBooking status: ')
                                parsed = json.loads(r.text)
                                print(json.dumps(parsed, indent=4, sort_keys=False))
                            else: #If unsuccessful return error code and reason
                                print('\nBooking not found.')
                                print('Response: ', r.status_code, r.text)
                        except:
                            print('Could not connect to the airline')
                    else:
                        print('Invalid airline, please enter a number between 1 -', len(urls))
                except ValueError:
                    print('Invalid airline, please enter a number between 1 -', len(urls))

            elif (user_command == 'cancelbooking'):
                #Get airline from user
                airline = input("Please enter the number of the airline you would like to select: ")
                try: #Validate input
                    if 1 <= int(airline) <= len(urls):
                        airline_url = urls[int(airline)-1]
                        booking_num = input('  Enter booking number: ')
                        payload = { 'booking_num' : booking_num }
                        try:
                            r = requests.post(airline_url + 'api/cancelbooking/', json=payload, headers={'Content-type': 'application/json'})
                            if r.status_code == 201: #If successful return cancelled booking
                                print('\nSuccess, booking cancelled. Details: ')
                                parsed = json.loads(r.text)
                                print(json.dumps(parsed, indent=4, sort_keys=False))
                            else: #If unsuccessful return error code and reason
                                print('\nBooking not found.')
                                print('Response: ', r.status_code, r.text)
                        except:
                            print('Could not connect to the airline')
                    else:
                        print('Invalid airline, please enter a number between 1 -', len(urls))
                except ValueError:
                    print('Invalid airline, please enter a number between 1 -', len(urls))

            elif (user_command == 'help'):
                print('\nCommands:')
                print('  findflight -- Search for available flights')
                print('  bookflight -- Book a specific flight')
                print('  paymentmethods -- View available payment methods')
                print('  payforbooking -- Pay for a specific booking')
                print('  finalizebooking -- Finalize a booking')
                print('  bookingstatus -- Check a booking status')
                print('  cancelbooking -- Cancel a booking')
                print('  help -- Display this menu')
                print('  exit -- Exit program')

            elif (user_command == 'menu'):
                break

            elif (user_command == 'exit'):
                sys.exit()

            else:
                print("\nInvalid command. Type 'help' for options.")

    elif option == '2': #PAYMENT SERVICE PROVIDERS
        #Get available payment providers and print them to user
        try:
            r = requests.get('http://directory.pythonanywhere.com/api/list/', json={'company_type' : 'payment'}, headers={'Content-type': 'application/json'})
        except:
            print('Could not connect to directory. Please check your internet connection')
            sys.exit()
        company_list = r.json()['company_list']
        urls = [] #Store urls
        print('\nYou have selected payment service providers\n\nPlease select one from the list below:')
        for i in range(0, len(company_list)):
            if company_list[i]['url'][-1] != '/': #Append a / to url if it doesn't end in one
                company_list[i]['url'] += '/'
            print('  ' + str(i+1) + '.', company_list[i]['company_name'], ' - ', company_list[i]['url'])
            urls.append(company_list[i]['url'])
        selected_provider = input('\nPlease enter your choice: ')
        while True: #Ensure selected provider is an int range of number of payment providers
            try:
                selected_provider = int(selected_provider)
                if not 1 <= selected_provider <= len(urls):
                    raise Exception('Please enter a valid choice between 1 - ' + str(len(urls)) + ': ')
                else:
                    selected_url = urls[selected_provider-1]
                    break
            except:
                selected_provider = input('Please enter a valid choice between 1 - ' + str(len(urls)) + ': ')

        print('Company selected: ', selected_url)

        #Set logged_in to False initially
        logged_in = False

        while True:
            #Get command from user - while True allows commands to be entered one after the other
            user_command = input("\nPlease enter a command. Type 'help' to list commands, 'menu' to return to the menu or 'exit' to exit the program.\n")

            #PAYMENT SERVICE PROVIDER COMMANDS
            if (user_command == 'register'):
                #Get details from user
                first_name = input('  Enter first name: ')
                surname = input('  Enter surname: ')
                email = input('  Enter email: ')
                phone = input('  Enter phone number: ')
                username = input('  Enter username: ')
                password = input('  Enter password: ')
                customer_type = input('  Enter customer type (personal or business): ')

                #Create payload and process request
                payload = { 'first_name' : first_name, 'surname' : surname, 'email' : email, 'phone' : phone,
                            'username' : username, 'password' : password, 'customer_type' : customer_type }
                try:
                    r = requests.post(selected_url + 'api/register/', json=payload, headers={'Content-type': 'application/json'})
                    if r.status_code == 201: #If successful return welcome message
                        print(r.text)
                    else: #If unsuccessful return error code and reason
                        print(r.status_code, r.text)
                except:
                    print('Could not connect to the payment provider')

            elif (user_command == 'login'):
                #Get user details
                username = input('  Enter username: ')
                password = input('  Enter password: ')

                #Create payload and process request
                payload = { 'username' : username, 'password' : password }
                try:
                    s = requests.Session()
                    r = s.post(selected_url + 'api/login/', data=payload)

                    if r.status_code == 200: #If successful return welcome message, set logged_in to True
                        print(r.text)
                        logged_in = True
                    else: #If unsuccessful return error code and reason
                        print(r.status_code, r.text)
                except:
                    print('Could not connect to the payment provider')

            elif (user_command == 'logout'):
                if logged_in == True: #Check if logged in, process request
                    try:
                        r = s.post(selected_url + 'api/logout/')
                        if r.status_code == 200: #If successful return goodbye message, set logged_in to False
                            print(r.text)
                            logged_in = False
                        else: #If unsuccessful return error code and reason
                            print(r.status_code, r.text)
                    except:
                        print('Could not connect to the payment provider')
                else:
                    print('You are not logged in')

            elif (user_command == 'newaccount'):
                if logged_in == True: #Check if logged in, process request
                    try:
                        r = s.post(selected_url + 'api/newaccount/')
                        if r.status_code == 201: #If successful return account number
                            print(r.text)
                        else: #If unsuccessful return error code and reason
                            print(r.status_code, r.text)
                    except:
                        print('Could not connect to the payment provider')
                else:
                    print('You are not logged in')

            elif (user_command == 'deposit'):
                if logged_in == True: #Check if logged in
                #Get details from user
                    amount = ''
                    while type(amount) != float: #Verify amount is a float
                        try:
                            amount = float(input('  Enter amount: '))
                        except ValueError:
                            print('Not a valid amount')
                    account_num = input('  Enter account number: ')

                    #Create payload and process request
                    payload = { 'amount' : amount, 'account_num' : account_num }
                    try:
                        r = s.post(selected_url + 'api/deposit/', json=payload, headers={'Content-type': 'application/json'})
                        if r.status_code == 201: #If successful return account details (number and balance)
                            parsed = json.loads(r.text)
                            print(json.dumps(parsed, indent=4, sort_keys=False))
                        else: #If unsuccessful return error code and reason
                            print(r.status_code, r.text)
                    except:
                        print('Could not connect to the payment provider')
                else:
                    print('You are not logged in')

            elif (user_command == 'transfer'):
                if logged_in == True: #Check if logged in
                #Get details from user
                    amount = ''
                    while type(amount) != float: #Verify amount is a float
                        try:
                            amount = float(input('  Enter amount: '))
                        except ValueError:
                            print('Not a valid amount')
                    from_account_num = input('  Enter account number from which money should be taken: ')
                    to_account_num = input('  Enter account number to which money will be paid:  ')

                    #Create payload and process request
                    payload = { 'amount' : amount, 'from_account_num' : from_account_num, 'to_account_num' : to_account_num }
                    try:
                        r = s.post(selected_url + 'api/transfer/', json=payload, headers={'Content-type': 'application/json'})
                        if r.status_code == 201: #If successful return account details (number and balance)
                            parsed = json.loads(r.text)
                            print(json.dumps(parsed, indent=4, sort_keys=False))
                        else: #If unsuccessful return error code and reason
                            print(r.status_code, r.text)
                    except:
                        print('Could not connect to the payment provider')
                else:
                    print('You are not logged in')

            elif (user_command == 'balance'):
                if logged_in == True: #Check if logged in, process request
                    try:
                        r = s.get(selected_url + 'api/balance/', json=payload, headers={'Content-type': 'application/json'})
                        if r.status_code == 200: #If successful return all accounts and details
                            parsed = json.loads(r.text)
                            print(json.dumps(parsed, indent=4, sort_keys=False))
                        else: #If unsuccessful return error code and reason
                            print(r.status_code, r.text)
                    except:
                        print('Could not connect to the payment provider')
                else:
                    print('You are not logged in')

            elif (user_command == 'createinvoice'):
                if logged_in == True: #Check if logged in
                    #Get details from user
                    account_num = input('  Enter account number of business customer: ')
                    client_ref_num = input('  Enter payee reference number for invoice: ')
                    amount = ''
                    while type(amount) != float: #Verify amount is a float
                        try:
                            amount = float(input('  Enter amount: '))
                        except ValueError:
                            print('Not a valid amount')

                    #Create payload and process request
                    payload = { 'account_num' : account_num, 'client_ref_num' : client_ref_num, 'amount' : amount }
                    try:
                        r = s.post(selected_url + 'api/createinvoice/', json=payload, headers={'Content-type': 'application/json'})
                        if r.status_code == 201: #If successful return reference number and stamp
                            parsed = json.loads(r.text)
                            print(json.dumps(parsed, indent=4, sort_keys=False))
                        else: #If unsuccessful return error code and reason
                            print(r.status_code, r.text)
                    except:
                        print('Could not connect to the payment provider')
                else:
                    print('You are not logged in')

            elif (user_command == 'payinvoice'):
                if logged_in == True: #Check logged in
                    #Get details from user
                    payprovider_ref_num = input('  Enter payment provider reference number for invoice: ')
                    client_ref_num = input('  Enter booking number for invoice: ') #Client reference number is booking number
                    amount = ''
                    while type(amount) != float: #Verify amount is a float
                        try:
                            amount = float(input('  Enter amount: '))
                        except ValueError:
                            print('Not a valid amount')

                    #Create payload and process request
                    payload = { 'payprovider_ref_num' : payprovider_ref_num, 'client_ref_num' : client_ref_num, 'amount' : amount }
                    try:
                        r = s.post(selected_url + 'api/payinvoice/', json=payload, headers={'Content-type': 'application/json'})
                        if r.status_code == 201: #If successful return electronic stamp
                            parsed = json.loads(r.text)
                            print(json.dumps(parsed, indent=4, sort_keys=False))
                        else: #If unsuccessful return error code and reason
                            print(r.status_code, r.text)
                    except:
                        print('Could not connect to the payment provider')
                else:
                    print('You are not logged in')

            elif (user_command == 'statement'):
                if logged_in == True: #Check logged in
                    #Get account number from user
                    account_num = input('  Enter account number: ')

                    #Create payload and process request
                    payload = { 'account_num' : account_num }
                    try:
                        r = s.get(selected_url + 'api/statement/', json=payload, headers={'Content-type': 'application/json'})
                        if r.status_code == 201: #If successful return statement
                            parsed = json.loads(r.text)
                            print(json.dumps(parsed, indent=4, sort_keys=False))
                        else: #If unsuccessful return error code and reason
                            print(r.status_code, r.text)
                    except:
                        print('Could not connect to the payment provider')
                else:
                    print('You are not logged in')

            elif (user_command == 'help'):
                print('\nCommands:')
                print('  register -- Register a customer for the first time')
                print('  login -- User login')
                print('  logout -- User logout')
                print('  newaccount -- Create a new account')
                print('  deposit -- Deposit money into an account')
                print("  transfer -- Transfer money from one of the user's accounts to another")
                print('  balance -- Check the balance of all accounts')
                print('  createinvoice -- Create an invoice for a business client')
                print('  payinvoice -- Pay an invoice')
                print('  statement -- Get an account statement')
                print('  help -- Display this menu')
                print('  exit -- Exit program')

            elif (user_command == 'menu'):
                break

            elif (user_command == 'exit'):
                sys.exit()

            else:
                print("\nInvalid command. Type 'help' for options.")

    elif option == 'exit':
        sys.exit()

    else:
        print('\nInvalid option, please type 1 for airlines or 2 for payment service providers.')

    #     #DIRECTORY COMMANDS
    #     elif (user_command == 'register'):
    #         company_name = input('  Enter company name: ')
    #         company_type = input('  Enter company type (airline or payment)')
    #         url = input("  Enter address of company's website: ")
    #         company_code = input('  Enter company code: ')
    #         payload = { 'company_name' : company_name, 'company_type' : company_type, 'url' : url, 'company_code' : company_code }
    #         r = requests.post('http://directory.pythonanywhere.com/api/register/', json=payload, headers={'Content-type': 'application/json'})
    #         if r.status_code == 201:
    #             print('Success, company registered')
    #         else:
    #             print(r.status_code, r.text)
    #
    #     elif (user_command == 'list'):
    #         company_type = input('  Enter the company type: ')
    #         payload = { 'company_type' : company_type }
    #         r = requests.get('http://directory.pythonanywhere.com/api/list/', json=payload, headers={'Content-type': 'application/json'})
    #         if r.status_code == 200:
    #             parsed = json.loads(r.text)
    #             print(json.dumps(parsed, indent=4, sort_keys=False))
    #         else:
    #             print(r.status_code, r.text)
    #
    #     elif (user_command == 'unregister'):
    #         print('Service unavailable, please contact directory admin to remove company manually')
