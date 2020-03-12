from django.urls import path, include

urlpatterns = [
    path('account', include('account.urls')),
    path('exchange', include('exchange.urls'))
]
