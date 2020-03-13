import re
import jwt
import json
import bcrypt

from .models     import Account
from .utils      import Login_Check, validate_password, validate_special_char
from my_settings import SECRET_KEY
                 
from django.views           import View
from django.http            import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class SignUpView(View):
    def post(self, request):
        data = json.loads(request.body)
    
        try:
            validate_email(data["email"])

            if validate_special_char(data["email"]):
                print("here return")
                return JsonResponse({"message" : "INVALID_CHAR"}, status=400)

            if validate_password(data["password"]):
                return JsonResponse({"message" : "INVALID_PASSWORD"}, status=400)

            if Account.objects.filter(email=data["email"]).exists():
                return JsonResponse({"message" : "EXISTS_EMAIL"}, status=400)

            Account(
                email    = data["email"],
                password = bcrypt.hashpw(data["password"].encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8")
            ).save()

            return JsonResponse({"message" : "SUCCESS"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "INVALID_KEY"}, status=400)

        except TypeError:
            return JsonResponse({"message" : "INVALID_TYPE"}, status=400)

        except ValidationError:
            return HttpResponse(status=400)

class SignInView(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            validate_email(data["email"])

            if validate_special_char(data["email"]):
                return JsonResponse({"message" : "INVALID_CHAR"}, status=400)

            if Account.objects.filter(email=data["email"]).exists():
                user = Account.objects.get(email=data["email"])

                if bcrypt.checkpw(data["password"].encode(), user.password.encode("UTF-8")):
                    token = jwt.encode({"email" : data["email"]}, SECRET_KEY["secret"], SECRET_KEY["algorithm"]).decode("UTF-8")
                    
                    return JsonResponse({"access_token" : token}, status=200)

                return HttpResponse(status=401)

            return HttpResponse(status=400)

        except KeyError:
            return JsonResponse({"message" : "INVALID_KEY"}, status=400)

        except ValidationError:
            return HttpResponse(status=400)