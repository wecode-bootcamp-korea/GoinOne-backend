import json
import jwt
import bcrypt

from account.models     import Account
from my_settings        import SECRET_KEY
from .utils             import Login_Check, validate_password, validate_special_char
from unittest.mock      import patch, MagicMock

from django.test        import TestCase, Client
from django.http        import JsonResponse,HttpResponse

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
            email    = "test1234@gmail.com",
            password = password
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
        self.assertEqual(response.json(), {"access_token" : token})

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

