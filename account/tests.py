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


class SignUp(TestCase):
    def setUp(self):
        Account.objects.create(
            email    = "test1234@gmail.com",
            password = "test12341234!"
        )

    def tearDown(self):
        Account.objects.all().delete()
    
    def test_signup_success(self):
        client = Client()

        account = {
            "email"    : "test4321@gmail.com",
            "password" : "AAtest12341234!"
        }

        response = client.post("/account/signup", json.dumps(account), content_type = "application/json")
        self.assertEqual(response.status_code, 200)
    
    def test_sign_exists_email(self):
        client = Client()

        account = {
            "email"    : "test1234@gmail.com",
            "password" : "AAtest12341234!"
        }

        response = client.post("/account/signup", json.dumps(account), content_type = "application/json")
        self.assertEqual(response.status_code, 400)   
        self.assertEqual(response.json(), {"message" : "EXISTS_EMAIL"})

    def test_signup_invalid_email(self):
        client = Client()

        account = {
            "email"    : "test4321gmail.com",
            "password" : "test12341234!"
        }

        response = client.post("/account/signup", json.dumps(account), content_type = "application/json")
        self.assertEqual(response.status_code, 400)

    def test_signup_invalid_char(self):
        client = Client()

        account = {
            "email"    : "!!!!!est4321@gmail.com",
            "password" : "AAtest12341234!"
        }

        response = client.post("/account/signup", json.dumps(account), content_type = "application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message" : "INVALID_CHAR"})


    def test_signup_invalid_password(self):
        client = Client()

        account = {
            "email"    : "test4321@gmail.com",
            "password" : "12345 6789"
        }

        response = client.post("/account/signup", json.dumps(account), content_type = "application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "INVALID_PASSWORD"})
    
    def test_signup_invalid_key(self):
        client = Client()

        account = {
            "id"    : "test4321@gmail.com",
            "password" : "AAtest12341234!"
        }

        response = client.post("/account/signup", json.dumps(account), content_type = "application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message" : "INVALID_KEY"})
    
class SignIn(TestCase):
    def setUp(self):
        password = bcrypt.hashpw("Test12341234!".encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8")
        Account.objects.create(
            email     = "test1234@gmail.com",
            password  = password,
            is_active = True
        )

    def tearDown(self):
        Account.objects.all().delete()

    def test_signin_success(self):
        account = {
            "email" : "test1234@gmail.com",
            "password" : "Test12341234!"
        }
 
        client = Client()

        response = client.post("/account/signin", json.dumps(account), content_type="application/json")
        token    = jwt.encode({"email" : account["email"]}, SECRET_KEY["secret"], SECRET_KEY["algorithm"]).decode("UTF-8")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"Authorization" : token})

    def test_signin_invalid_email(self):
        account = {
            "email" : "test123455@gmail.com",
            "password" : "test12341234!"
        }
 
        client = Client()

        response = client.post("/account/signin", json.dumps(account), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_signin_invalid_char(self):
        account = {
            "email" : "tes!!!!!!@gmail.com",
            "password" : "test12341234!"
        }
 
        client = Client()

        response = client.post("/account/signin", json.dumps(account), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_signin_invalid_password(self):
        account = {
            "email" : "test1234@gmail.com",
            "password" : "test12341234!!!"
        }
 
        client = Client()

        response = client.post("/account/signin", json.dumps(account), content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_signin_invalid_key(self):
        account = {
            "id" : "test1234@gmail.com",
            "password" : "test12341234!!!"
        }
 
        client = Client()

        response = client.post("/account/signin", json.dumps(account), content_type="application/json")

        self.assertEqual(response.status_code, 400)       
        self.assertEqual(response.json(), {"message" : "INVALID_KEY"})


class Active(TestCase):
    def setUp(self):
        password = bcrypt.hashpw("Test12341234!".encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8")
        user = Account.objects.create(
                email    = "test1234@gmail.com",
                password = password
        )

    def tearDown(self):
        Account.objects.all().delete()

    def test_email_auth_success(self):
        user = Account.objects.get(email = 'test1234@gmail.com')

        client = Client()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        response = client.get(f"/account/activate/{uidb64}/{token}")

        uid  = force_text(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
  
        self.assertEqual(response.status_code, 302)       

    def test_email_auth_fail(self):
        user = Account.objects.get(email = 'test1234@gmail.com')

        client = Client()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = "1234"

        response = client.get(f"/account/activate/{uidb64}/{token}")

        uid  = force_text(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)

        self.assertEqual(response.status_code, 400)
            

class BalanceView(TestCase):
    def setUp(self):
        password = bcrypt.hashpw("Test12341234!".encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8")
        user = Account.objects.create(
            id               = 1,
            email            = "test1234@gmail.com",
            password         = password,
            is_active        = True,
            currency_balance = 100000000
        )
        Currency.objects.create(
            id               = 1,
            code             = 'krw',
            name             = '원화',
            is_active        = True,
            is_base_currency = True
        )

        Item.objects.create(
            id               = 1,
			currency_id      = Currency.objects.get(id=1).id,
			code 			 = 'BTC',
			name 			 = '비트코인',
            is_active        = True,
			price_unit       = 1,
			amount_unit      = 1,
        )

        AccountItem.objects.create(
            id           = 1,
			account_id   = Account.objects.get(id=1).id,
			item_id      = Item.objects.get(id=1).id,
			amount       = 1,
        )

        Price.objects.create(
            id           = 1,
			item_id      = Item.objects.get(id=1).id,
			currency_id  = Currency.objects.get(id=1).id,
			trade_price  = 1000,
        )

        Trade.objects.create(
            id           = 1,
			item_id      = Item.objects.get(id=1).id,
			buyer_id     = Account.objects.get(id=1).id,
			amount       = 1,
			trade_price  = 100
        )

    def tearDown(self):
        Account.objects.all().delete()

    def test_balance_view_success(self):
        user = {
            'email' : "test1234@gmail.com"
        }
                
        client = Client()

        token = jwt.encode({"email" : user['email']}, SECRET_KEY["secret"], SECRET_KEY["algorithm"]).decode("UTF-8")
        header = {'HTTP_Authorization' : token}

        response = client.get('/account/balance', **header)

        TestCase.maxDiff = None
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'balance': [{
                'amount': '1.00000000',
                'avg_buy_price': '100.000000000000',
                'buy_price': '100.00000000000000000000',
                'change_price': '900.00000000000000000000',
                'change_rate': '900',
                'name': 'BTC',
                'now_price': '1000.0000000000000000'}],
            'total_asset': {
                'currency_balance': '100000000.00000000',
                'item_balance': '1000.0000000000000000',
                'total_buy_price': '100.00000000000000000000',
                'total_change_price': '900.00000000000000000000',
                'total_change_rate': '900'}
            })

    def test_balance_view_invalid_user(self):
        user = {
            'email' : "test1234@gmail.com"
        }
                
        client = Client()

        token = jwt.encode({"email" : user['email']}, SECRET_KEY["secret"], SECRET_KEY["algorithm"]).decode("UTF-8")
        header = {'HTTP_Authorization' : '1234'}

        response = client.get('/account/balance', **header)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message" : "INVALID_USER"})
