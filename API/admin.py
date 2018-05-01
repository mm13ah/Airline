from django.contrib import admin
from .models import Aircraft, Airport, Flight, Booking, Passenger, Payment_provider, Invoice

admin.site.register(Aircraft)
admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(Booking)
admin.site.register(Passenger)
admin.site.register(Payment_provider)
admin.site.register(Invoice)
