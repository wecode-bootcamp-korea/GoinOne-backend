import re
import jwt
import json
import bcrypt
import time

from .models            import Currency, Item, Price, Report, AccountItem
from account.models     import Account, Trade, Offer
from account.utils      import Login_Check
                 
from django.views           import View
from django.http            import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.utils           import timezone
from datetime               import datetime, timedelta
from decimal                import Decimal
from django.db.models       import Max, Min, Avg
from django.db              import IntegrityError, transaction


class ReportVIew(View):
    def get(self, request, item_id, unit):
        try:
            Report.objects.filter(item = item_id, unit = unit)

            report_data = [{
                "item"          : report.item.code,
                "currency"      : report.currency.code,
                "opening_price" : report.opening_price,
                "high_price"    : report.high_price,
                "low_price"     : report.low_price,
                "trade_price"   : report.trade_price,
                "candle_price"  : report.candle_price,
                "candle_volume" : report.candle_volume,
                "date"          : time.mktime(report.date.timetuple()),
                "unit"          : unit
            } for report in Report.objects.filter(item_id = item_id, unit = unit).iterator()]
            
            return JsonResponse({"data" : report_data}, status=200)
        except KeyError:
            return HttpResponse(status=200)


class ExchangeView(View):
    def get(self, request, item_id):
        try:
            today           = timezone.localtime(timezone.now())
            yesterday       = today.today() - timedelta(days=1)
            today_price     = Price.objects.filter(created_at__year = today.year, created_at__month = today.month, created_at__day = today.day)
            yesterday_price = Price.objects.filter(created_at__year = yesterday.year, created_at__month = yesterday.month, created_at__day = yesterday.day)
            sell_price_list = [offer['price'] for offer in Offer.objects.filter(item_id=item_id, is_sell=True, is_active=True).values('price').distinct().order_by('price').reverse()]
            buy_price_list  = [offer['price'] for offer in Offer.objects.filter(item_id=item_id, is_buy=True, is_active=True).values('price').distinct().order_by('price').reverse()]

            item_list = [{
                "name"                : item.name,
                "code"                : item.code,
                "now_price"           : Price.objects.filter(item_id = item.id).latest('created_at').trade_price,
                "yesterday_max_price" : today_price.filter(item_id=item.id).aggregate(trade_price=Avg('trade_price'))["trade_price"],
                "today_max_price"     : today_price.filter(item_id=item.id).aggregate(trade_price=Max('trade_price'))["trade_price"],
                "today_min_price"     : today_price.filter(item_id=item.id).aggregate(trade_price=Min('trade_price'))["trade_price"],
                "24_trade_volume"     : sum([price_data.trade_price for price_data in today_price.filter(item_id=item.id)]),
                "price_unit"          : item.price_unit,
                "amount_unit"         : item.amount_unit
            } for item in Item.objects.all()]

            trade_list = [{
                "time"    : trade.created_at,
                "price"   : trade.trade_price,
                "amount"  : trade.amount,
                "is_buy"  : trade.offer.is_buy,
                "is_sell" : trade.offer.is_sell,
            } for trade in Trade.objects.filter(item_id = item_id).order_by('created_at').reverse()[0:25]]

            offer_sell_list = [{
                "price"     : sell_price,
                "amount"    : sum([offer.remained_amount for offer in Offer.objects.filter(price=sell_price, is_sell=True, is_active=True)]),
            } for sell_price in sell_price_list[0:15]]

            offer_buy_list = [{
                "price"     : buy_price,
                "amount"    : sum([offer.remained_amount for offer in Offer.objects.filter(price=buy_price, is_buy=True, is_active=True)]),
            } for buy_price in buy_price_list[0:15]]
                    
            return JsonResponse(
                {
                    "item_data"       : item_list, 
                    "trade_data"      : trade_list, 
                    "offer_sell_data" : offer_sell_list, 
                    "offer_buy_data"  : offer_buy_list
                }, status=200)

        except KeyError:
            return HttpResponse(status=400)



class TradeView(View):
    @Login_Check
    @transaction.atomic
    def post(self, request, option):

        def calc_seller_item_balance(user_id, item_id, amount):
            AccountItem.objects.get_or_create(account_id = user_id, item_id = item_id)
            user_item = AccountItem.objects.get(account_id = user_id, item_id = item_id)
            
            user_item.amount -= amount
            
            if user_item.amount == 0:
                user_item.delete()
            else:
                user_item.save()

        def calc_buyer_item_balacne(user_id, item_id, amount):
            AccountItem.objects.get_or_create(account_id = user_id, item_id = item_id)
            user_item = AccountItem.objects.get(account_id = user_id, item_id = item_id)
            
            user_item.amount += amount
            user_item.save()

        def calc_seller_currency_balance(user_id, item_id, price, amount):
            user = Account.objects.get(id = user_id)
            user.currency_balance += amount * price
            user.save()
                    
        def calc_buyer_currency_balacne(user_id, item_id, price, amount):
            user = Account.objects.get(id = user_id)
            user.currency_balance -= amount * price
            user.save()

        def create_trade_data(buyer_id, seller_id, item_id, price, offer_id, amount):
            Trade(
                buyer_id    = buyer_id,
                seller_id   = seller_id,
                item_id     = item_id,
                trade_price = price,
                offer_id    = offer_id,
                amount      = amount,
            ).save()

        def update_offer_data(offer, amount_data):
            if amount_data < offer.remained_amount:
                offer.remained_amount -= amount_data
                offer.save()               

            elif amount_data >= offer.remained_amount:
                amount_data -= offer.remained_amount

                offer.remained_amount = 0
                offer.is_active = False
                offer.save()   

            return amount_data

        def create_offer_data(option, user_id, item_id, price, amount):
            if option == 'sell':
                Offer(
                    account_id      = user_id,
                    item_id         = item_id,
                    price           = price,
                    origin_amount   = amount,
                    remained_amount = amount,
                    is_sell         = True
                ).save()
                
            elif option == 'buy':
                Offer(
                    account_id      = user_id,
                    item_id         = item_id,
                    price           = price,
                    origin_amount   = amount,
                    remained_amount = amount,
                    is_buy          = True
                ).save()    

        try:
            data = json.loads(request.body)

            amount_data = Decimal(data["amount"])
            price_data  = Decimal(data["price"])
            offers      = Offer.objects.filter(price = price_data, item_id = data['item'], is_buy=True, is_active=True)

            if option == 'sell':
                account_item = AccountItem.objects.get(account_id = request.user, item_id = data['item'])
                    
                if amount_data <= account_item.amount:

                    if not offers.exists():
                        create_offer_data(option, request.user, data['item'], price_data, amount_data)
                        return JsonResponse({"message" : "ADD_OFFER"}, status=200)

                    if amount_data <= sum([offer.remained_amount for offer in offers]):

                        for offer in offers:
                                    
                            if amount_data < offer.remained_amount:

                                calc_seller_item_balance(request.user, data['item'], amount_data)
                                calc_seller_currency_balance(request.user, data['item'], price_data, amount_data)
    
                                calc_buyer_item_balacne(offer.account_id, data['item'], amount_data)
                                calc_buyer_currency_balacne(offer.account_id, data['item'], price_data, amount_data)

                                create_trade_data(offer.account_id, request.user, offer.item_id, offer.price, offer.id, amount_data)

                                offer.remained_amount -= amount_data
                                offer.save()

                                return JsonResponse({"message" : "SUCCESS"}, status=200)
                                
                            elif amount_data == offer.remained_amount:
                                calc_seller_item_balance(request.user, data['item'], offer.remained_amount)
                                calc_seller_currency_balance(request.user, data['item'], price_data, offer.remained_amount)
    
                                calc_buyer_item_balacne(offer.account_id, data['item'], offer.remained_amount)
                                calc_buyer_currency_balacne(offer.account_id, data['item'], price_data, offer.remained_amount)

                                create_trade_data(offer.account_id, request.user, offer.item_id, offer.price, offer.id, offer.remained_amount)

                                offer.remained_amount = 0
                                offer.is_active = False
                                offer.save()

                                return JsonResponse({"message" : "SUCCESS"}, status=200)

                            elif amount_data > offer.remained_amount:
                                calc_seller_item_balance(request.user, data['item'], offer.remained_amount)
                                calc_seller_currency_balance(request.user, data['item'], price_data, offer.remained_amount)
    
                                calc_buyer_item_balacne(offer.account_id, data['item'], offer.remained_amount)
                                calc_buyer_currency_balacne(offer.account_id, data['item'], price_data, offer.remained_amount)

                                create_trade_data(offer.account_id, request.user, offer.item_id, offer.price, offer.id, offer.remained_amount)

                                amount_data -= offer.remained_amount

                                offer.remained_amount = 0
                                offer.is_active = False
                                offer.save()

                    else:
                        for offer in offers:
                            calc_seller_item_balance(request.user, data['item'], offer.remained_amount)
                            calc_seller_currency_balance(request.user, data['item'], price_data, offer.remained_amount)
    
                            calc_buyer_item_balacne(offer.account_id, data['item'], offer.remained_amount)
                            calc_buyer_currency_balacne(offer.account_id, data['item'], price_data, offer.remained_amount)

                            create_trade_data(offer.account_id, request.user, offer.item_id, offer.price, offer.id, offer.remained_amount)

                            amount_data -= offer.remained_amount

                            offer.remained_amount = 0
                            offer.is_active = False
                            offer.save()

                        create_offer_data(option, request.user, data['item'], price_data, amount_data)
                            
                        return JsonResponse({"message" : "ADD_OFFER_YOUR_REMAINED_AMOUNT"}, status=200)

                return JsonResponse({"message" : "CHECK_YOUR_BALANCE"}, status=400)

            elif option == 'buy':
                    
                offers = Offer.objects.filter(price = price_data, item_id = data['item'], is_sell=True, is_active=True)
                    
                if not offers.exists():
                    create_offer_data(option, request.user, data['item'], price_data, amount_data)
                    return JsonResponse({"message" : "ADD_OFFER"}, status=200)

                if amount_data * price_data <= Account.objects.get(id = request.user).currency_balance: 

                    if amount_data <= sum([offer.remained_amount for offer in offers]):

                        for offer in offers:

                            if amount_data < offer.remained_amount:

                                calc_seller_item_balance(offer.account_id, data['item'], amount_data)
                                calc_seller_currency_balance(offer.account_id, data['item'], price_data, amount_data)
    
                                calc_buyer_item_balacne(request.user, data['item'], amount_data)
                                calc_buyer_currency_balacne(request.user, data['item'], price_data, amount_data)

                                create_trade_data(request.user, offer.account_id, offer.item_id, offer.price, offer.id, amount_data)

                                offer.remained_amount -= amount_data
                                offer.save()

                                return JsonResponse({"message" : "SUCCESS"}, status=200)

                            elif amount_data == offer.remained_amount:
                                calc_seller_item_balance(offer.account_id, data['item'], offer.remained_amount)
                                calc_seller_currency_balance(offer.account_id, data['item'], price_data, offer.remained_amount)
    
                                calc_buyer_item_balacne(request.user, data['item'], offer.remained_amount)
                                calc_buyer_currency_balacne(request.user, data['item'], price_data, offer.remained_amount)

                                create_trade_data(request.user, offer.account_id, offer.item_id, offer.price, offer.id, offer.remained_amount)

                                offer.remained_amount = 0
                                offer.is_active = False
                                offer.save()

                                return JsonResponse({"message" : "SUCCESS"}, status=200)

                            elif amount_data > offer.remained_amount:

                                calc_seller_item_balance(offer.account_id, data['item'], offer.remained_amount)
                                calc_seller_currency_balance(offer.account_id, data['item'], price_data, offer.remained_amount)
    
                                calc_buyer_item_balacne(request.user, data['item'], offer.remained_amount)
                                calc_buyer_currency_balacne(request.user, data['item'], price_data, offer.remained_amount)

                                create_trade_data(request.user, offer.account_id, offer.item_id, offer.price, offer.id, offer.remained_amount)

                                amount_data -= offer.remained_amount

                                offer.remained_amount = 0
                                offer.is_active = False
                                offer.save()

                    else:
                        for offer in offers:
                            calc_seller_item_balance(offer.account_id, data['item'], offer.remained_amount)
                            calc_seller_currency_balance(offer.account_id, data['item'], price_data, offer.remained_amount)

                            calc_buyer_item_balacne(request.user, data['item'], offer.remained_amount)
                            calc_buyer_currency_balacne(request.user, data['item'], price_data, offer.remained_amount)
                                    
                            create_trade_data(request.user, offer.account_id, offer.item_id, offer.price, offer.id, offer.remained_amount)

                            amount_data -= offer.remained_amount

                            offer.remained_amount = 0
                            offer.is_active = False
                            offer.save()
                            
                        create_offer_data(option, request.user, data['item'], price_data, amount_data)

                        return JsonResponse({"message" : "ADD_OFFER_YOUR_REMAINED_AMOUNT"}, status=200)

                return JsonResponse({"message" : "CHECK_YOUR_BALANCE"}, status=400)

            return JsonResponse({"message" : "INVALID_REQUEST"}, status=400)

        except ValidationError:
            return HttpResponse(status=400)
        except AccountItem.DoesNotExist:
            return JsonResponse({"message" : "CHECK_YOUR_BALANCE"}, status=400)


        


