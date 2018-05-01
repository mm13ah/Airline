"""Airline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from API.views import findflight, bookflight, paymentmethods, payforbooking, finalizebooking, bookingstatus, cancelbooking

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/findflight/', findflight),
    path('api/bookflight/', bookflight),
    path('api/paymentmethods/', paymentmethods),
    path('api/payforbooking/', payforbooking),
    path('api/finalizebooking/', finalizebooking),
    path('api/bookingstatus/', bookingstatus),
    path('api/cancelbooking/', cancelbooking),
]
