import re
import jwt
import json
import bcrypt

from .models                import Account, Trade
from .text                  import message
from .tokens                import account_activation_token
from .utils                 import Login_Check, validate_password, validate_special_char
from exchange.models        import Currency, Item, Price, Report, AccountItem
from my_settings            import SECRET_KEY, EMAIL

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


class SignUpView(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            validate_email(data["email"])

            if validate_special_char(data["email"]):
                return JsonResponse({"message" : "INVALID_CHAR"}, status=400)

            if validate_password(data["password"]):
                return JsonResponse({"message" : "INVALID_PASSWORD"}, status=400)

            if Account.objects.filter(email=data["email"]).exists():
                return JsonResponse({"message" : "EXISTS_EMAIL"}, status=400)

            user = Account.objects.create(
                email    = data["email"],
                password = bcrypt.hashpw(data["password"].encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8"),
            )
            user.is_active = False
            user.save()

            current_site = get_current_site(request) 
            domain       = current_site.domain
            uidb64       = urlsafe_base64_encode(force_bytes(user.pk))
            token        = account_activation_token.make_token(user)
            message_data = message(domain, uidb64, token)

            mail_title = "이메일 인증을 완료해주세요"
            mail_to    = data['email']
            email      = EmailMessage(mail_title, message_data, to=[mail_to])
            email.send()         
 
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

                    if user.is_active == True:
                        return JsonResponse({"access_token" : token}, status=200)

                    return JsonResponse({"message" : "ACCOUNT_NOT_AUTH"}, status=400)

                return HttpResponse(status=401)

            return JsonResponse({"message" : "NOT_EXISTS_MAIL"}, status=400)

        except KeyError:
            return JsonResponse({"message" : "INVALID_KEY"}, status=400)
        except ValidationError:
            return JsonResponse({"message" : "VALIDATION_ERROR"}, status=400)

class Activate(View):
    def get(self, request, uidb64, token):
        try:
            uid  = force_text(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(pk=uid)
            
            if account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()

                return redirect(EMAIL['REDIRECT_PAGE'])
        
            return JsonResponse({"message" : "AUTH FAIL"}, status=400)

        except ValidationError:
            return JsonResponse({"message" : "TYPE_ERROR"}, status=400)
        except KeyError:
            return JsonResponse({"message" : "INVALID_KEY"}, status=400)