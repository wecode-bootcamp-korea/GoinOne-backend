import re
import jwt
import json
import bcrypt

from .models                import Account, Trade
from exchange.models        import Currency, Item, Price, Report, AccountItem
from .utils                 import Login_Check, validate_password, validate_special_char
from my_settings            import SECRET_KEY
from .tokens                import account_activation_token

from django.views                   import View
from django.http                    import HttpResponse, JsonResponse
from django.core.exceptions         import ValidationError
from django.core.validators         import validate_email
from datetime                       import timedelta
from django.db.models               import Avg
from django.shortcuts               import redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http              import urlsafe_base64_encode,urlsafe_base64_decode
from django.core.mail               import EmailMessage
from django.utils.encoding          import force_bytes, force_text
from django.test                    import TestCase, Client


class Report(TestCase):
    def setUp(self):
        Account.objects.create(
            email    = "test1234@gmail.com",
            password = "test12341234!"
        )

        Report.objects.create(
			item_id       = row['item'],
			currency_id   = row['currency'],
			opening_price = row['openingPrice'],
			high_price    = row['highPrice'],
			low_price     = row['lowPrice'],
			trade_price   = row['tradePrice'],
			candle_price  = row['candle_Price'],
			candle_volume = row['candle_Volume'],
			unit          = row['unit'],
			date          = row['time']       
        )

    def tearDown(self):
        Account.objects.all().delete()