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
            } for report in Report.objects.filter(item_id = item_id, unit = unit)]
            
            return JsonResponse({"data" : report_data}, status=200)
        except KeyError:
            return HttpResponse(status=200)


class ExchangeView(View):
    def get(self, request, item):
        try:
            today           = timezone.localtime(timezone.now())
            yesterday       = today.today() - timedelta(days=1)
            today_price     = Price.objects.filter(created_at__year = today.year, created_at__month = today.month, created_at__day = today.day)
            yesterday_price = Price.objects.filter(created_at__year = yesterday.year, created_at__month = yesterday.month, created_at__day = yesterday.day)
            sell_price_list = [offer['price'] for offer in Offer.objects.filter(item_id=item, is_sell=True, is_active=True).values('price').distinct().order_by('price').reverse()]
            buy_price_list  = [offer['price'] for offer in Offer.objects.filter(item_id=item, is_buy=True, is_active=True).values('price').distinct().order_by('price').reverse()]

            item_list = [{
                "name"                : item.name,
                "code"                : item.code,
                "now_price"           : Price.objects.filter(item_id = item).latest('created_at').trade_price,
                "yesterday_max_price" : today_price.filter(item_id=item).aggregate(trade_price=Avg('trade_price'))["trade_price"],
                "today_max_price"     : today_price.filter(item_id=item).aggregate(trade_price=Max('trade_price'))["trade_price"],
                "today_min_price"     : today_price.filter(item_id=item).aggregate(trade_price=Min('trade_price'))["trade_price"],
                "24_trade_volume"     : sum([price_data.trade_price for price_data in today_price.filter(item_id=item)]),
                "price_unit"          : item.price_unit,
                "amount_unit"         : item.amount_unit
            } for item in Item.objects.all()]

            trade_list = [{
                "time"    : trade.created_at,
                "price"   : trade.trade_price,
                "amount"  : trade.amount,
                "is_buy"  : trade.offer.is_buy,
                "is_sell" : trade.offer.is_sell,
            } for trade in Trade.objects.filter(item_id = item).order_by('created_at').reverse()]

            offer_sell_list = [{
                "price"     : sell_price,
                "amount"    : sum([offer.remained_amount for offer in Offer.objects.filter(price=sell_price)]),
            } for sell_price in sell_price_list]

            offer_buy_list = [{
                "price"     : buy_price,
                "amount"    : sum([offer.remained_amount for offer in Offer.objects.filter(price=buy_price)]),
            } for buy_price in buy_price_list]
                    
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
    def post(self, request, option):
        try:
            with transaction.atomic():
                data = json.loads(request.body)

                amount_data = Decimal(data["amount"])
                price_data  = Decimal(data["price"])

                if option == 'sell':
                    print('=========================== sell ===========================')
                    account_item = AccountItem.objects.get(account_id = request.user, item_id = data['item'])
                    # 고객 코인 잔고 확인
                    if amount_data <= account_item.amount:

                        # Offer 테이블에 해당 가격으로 주문이 올라온게 있sms지 확인
                        if Offer.objects.filter(price = price_data, item_id = data['item'], is_buy=True, is_active=True).exists():

                            #Offer 테이블에 올라온 총 주문 수량이 더 많음
                            if amount_data <= sum([offer.remained_amount for offer in Offer.objects.filter(price=price_data, is_buy=True, is_active=True, item_id = data['item'])]):

                                for offer in Offer.objects.filter(price=price_data, is_buy = True, is_active=True, item_id = data['item']):
                                    # offer 테이블에 구매하기 팔기 원하는 양보다 많은 수의 코인을 가지고 있을 경우
                                    if amount_data < offer.remained_amount:
                                        print('a')

                                        # 판매자 코인 잔고 반영
                                        user_item         = AccountItem.objects.get(account_id = request.user, item_id = data['item'])
                                        user_item.amount -= amount_data

                                        if user_item.amount == 0:
                                            user_item.delete()
                                        else:
                                            user_item.save()
    
                                        # 구매자 코인 잔고 반영
                                        if AccountItem.objects.filter(account_id = offer.account_id, item_id = data['item']).exists():
                                            account_item         = AccountItem.objects.get(account_id = offer.account_id, item_id = data['item'])
                                            account_item.amount += amount_data
                                            account_item.save()
                                        else:
                                            AccountItem(
                                                item_id    = data['item'],
                                                account_id = offer.account_id,
                                                amount     = amount_data
                                            ).save()

                                        # 구매자 원화 잔고 반영
                                        user = Account.objects.get(id=offer.account_id)
                                        user.currency_balance -= amount_data * price_data

                                        if user_item.amount == 0:
                                            user_item.delete()
                                        else:
                                            user_item.save()
                                        
                                        # 판매자 원화 잔고 반영
                                        user = Account.objects.get(id=request.user)
                                        user.currency_balance += amount_data * price_data
                                        user.save()

                                        # 거래 내역 생성                               
                                        Trade(
                                            item_id     = offer.item_id,
                                            buyer_id    = offer.account_id,
                                            seller_id   = request.user,
                                            trade_price = offer.price,
                                            offer_id    = offer.id,
                                            amount      = amount_data,
                                        ).save()

                                        offer.remained_amount -= amount_data
                                        offer.save()

                                        print('b')

                                        return JsonResponse({"message" : "SUCCESS"}, status=200)

                                    # offer 테이블에 구매하기 원하는 양보다 적은 수의 코인을 가지고 있을 경우 
                                    # amount_data 수량이 0이되면 200 OK                             
                                    if amount_data >= offer.remained_amount:
                                        print('c')

                                        # 판매자 코인 잔고 반영
                                        user_item         = AccountItem.objects.get(account_id = request.user, item_id = data['item'])
                                        user_item.amount -= offer.remained_amount

                                        if user_item.amount == 0:
                                            user_item.delete()
                                        else:
                                            user_item.save()
    
                                        # 구매자 코인 잔고 반영
                                        if AccountItem.objects.filter(account_id = offer.account_id, item_id = data['item']).exists():
                                            account_item         = AccountItem.objects.get(account_id = offer.account_id, item_id = data['item'])
                                            account_item.amount += offer.remained_amount
                                            account_item.save()
                                        else:
                                            AccountItem(
                                                item_id    = data['item'],
                                                account_id = offer.account_id,
                                                amount     = offer.remained_amount
                                            ).save()

                                        # 구매자 원화 잔고 반영
                                        user = Account.objects.get(id=offer.account_id)
                                        user.currency_balance -= offer.remained_amount * price_data
                                        user.save()

                                        # 판매자 원화 잔고 반영
                                        user = Account.objects.get(id=request.user)
                                        user.currency_balance += offer.remained_amount * price_data
                                        user.save()

                                        # 거래 내역 생성
                                        Trade(
                                            item_id     = offer.item_id,
                                            buyer_id    = offer.account_id, 
                                            seller_id   = request.user,
                                            trade_price = offer.price,
                                            offer_id    = offer.id,
                                            amount      = offer.remained_amount
                                        ).save()

                                        amount_data -= offer.remained_amount

                                        offer.remained_amount = 0
                                        offer.is_active = False
                                        offer.save()

                                        print('d')

                            #Offer 테이블에 올라온 총 주문 수량이 더 적음       
                            else:
                                for offer in Offer.objects.filter(price=price_data, is_buy = True, is_active=True, item_id = data['item']):
                                    if Offer.objects.filter(price=price_data, is_buy = True, is_active=True, item_id = data['item']).exists():

                                        # 판매자 코인 잔고 반영
                                        user_item         = AccountItem.objects.get(account_id = request.user, item_id = data['item'])
                                        user_item.amount -= offer.remained_amount

                                        if user_item.amount == 0:
                                            user_item.delete()
                                        else:
                                            user_item.save()
    
                                        # 구매자 코인 잔고 반영
                                        if AccountItem.objects.filter(account_id = offer.account_id, item_id = data['item']).exists():
                                            account_item         = AccountItem.objects.get(account_id = offer.account_id, item_id = data['item'])
                                            account_item.amount += offer.remained_amount
                                            account_item.save()
                                        else:
                                            AccountItem(
                                                item_id    = data['item'],
                                                account_id = offer.account_id,
                                                amount     = offer.remained_amount
                                            ).save()

                                        # 구매자 원화 잔고 반영
                                        user = Account.objects.get(id=offer.account_id)
                                        user.currency_balance -= offer.remained_amount * price_data
                                        user.save()

                                        # 판매자 원화 잔고 반영
                                        user = Account.objects.get(id=request.user)
                                        user.currency_balance += offer.remained_amount * price_data
                                        user.save()                      
                                        
                                        # 거래 내역 생성
                                        Trade(
                                            item_id     = offer.item_id,
                                            buyer_id    = offer.account_id, 
                                            seller_id   = request.user,  
                                            trade_price = offer.price,
                                            offer_id    = offer.id,
                                            amount      = offer.remained_amount
                                        ).save()

                                        amount_data -= offer.remained_amount

                                        # 주문 테이블에 저장된 수량 수정
                                        offer.remained_amount = 0
                                        offer.is_active = False
                                        offer.save()

                                # 주문표에 있는 수량 모두 소진 시 주문표에 남은 수량 저장
                                Offer(
                                    account_id      = request.user,
                                    item_id         = data['item'],
                                    price           = price_data,
                                    origin_amount   = amount_data,
                                    remained_amount = amount_data,
                                    is_sell         = True
                                ).save()

                                print('f')

                                return JsonResponse({"message" : "ADD_OFFER_YOUR_REMAINED_AMOUNT"})

                        # 가격 매칭이 안되었을 시 offer에 주문 저장 
                        else:
                            print('g')
                            Offer(
                                account_id      = request.user,
                                item_id         = data['item'],
                                price           = price_data,
                                origin_amount   = amount_data,
                                remained_amount = amount_data,
                                is_sell         = True
                            ).save()

                            return JsonResponse({"message" : "ADD_OFFER"}, status=200)

                    return JsonResponse({"message" : "CHECK_YOUR_BALANCE"}, status=400)

                if option == 'buy':
                    print('=========================== buy ===========================')
                    # 고객 잔고 확인

                    if amount_data * price_data <= Account.objects.get(id = request.user).currency_balance: 
                        # offer 테이블에 해당 가격이 있는지 확인
                        print(Offer.objects.filter(price = price_data, item_id = data['item'] ,is_sell=True, is_active=True).exists())

                        if Offer.objects.filter(price = price_data, item_id = data['item'] ,is_sell=True, is_active=True).exists():                        
                            # 구매하기 원하는 수량이 offer 있는 양보다 적음 (구매하기 충분한 양)

                            if amount_data <= sum([offer.remained_amount for offer in Offer.objects.filter(price=price_data, is_sell = True, is_active=True, item_id = data['item'])]):

                                # 구매하기 원하는 수량이 offer 있는 양보다 적음 (구매하기 충분한 양)
                                for offer in Offer.objects.filter(price=price_data, is_sell = True, is_active=True, item_id = data['item']):
                                    # offer 테이블에 구매하기 원하는 양보다 많은 수의 코인을 가지고 있을 경우

                                    if amount_data < offer.remained_amount:
                                        print('1')

                                        # 판매자 코인 잔고 반영
                                        user_item         = AccountItem.objects.get(account_id = offer.account_id, item_id = data['item'])
                                        user_item.amount -= amount_data

                                        if user_item.amount == 0:
                                            user_item.delete()
                                        else:
                                            user_item.save()
    
                                        # 구매자 코인 잔고 반영
                                        if AccountItem.objects.filter(account_id = request.user, item_id = data['item']).exists():
                                            account_item         = AccountItem.objects.get(account_id = request.user, item_id = data['item'])
                                            account_item.amount += amount_data
                                            account_item.save()
                                        else:
                                            AccountItem(
                                                item_id    = data['item'],
                                                account_id = request.user,
                                                amount     = amount_data
                                            ).save()

                                        # 판매자 원화 잔고 반영
                                        user = Account.objects.get(id = offer.account_id)
                                        user.currency_balance += amount_data * price_data
                                        user.save()

                                        # 구매자 원화 잔고 반영
                                        user = Account.objects.get(id=request.user)
                                        user.currency_balance -= amount_data * price_data
                                        user.save()

                                        Trade(
                                            item_id     = offer.item_id,
                                            buyer_id    = request.user,
                                            seller_id   = offer.account_id,
                                            trade_price = offer.price,
                                            offer_id    = offer.id,
                                            amount      = offer.remained_amount,
                                        ).save()

                                        offer.remained_amount -= amount_data
                                        offer.save()

                                        print('2')

                                        return JsonResponse({"message" : "SUCCESS"}, status=200)

                                    # offer 테이블에 구매하기 원하는 양보다 적은 수의 코인을 가지고 있을 경우 
                                    # amount_data 수량이 0이되면 200 OK                             
                                    if amount_data >= offer.remained_amount:
                                        print('3')

                                        # 판매자 코인 잔고 반영
                                        user_item         = AccountItem.objects.get(account_id = offer.account_id, item_id = data['item'])
                                        user_item.amount -= offer.remained_amount

                                        if user_item.amount == 0:
                                            user_item.delete()
                                        else:
                                            user_item.save()
    
                                        # 구매자 코인 잔고 반영
                                        if AccountItem.objects.filter(account_id = request.user, item_id = data['item']).exists():
                                            account_item         = AccountItem.objects.get(account_id = request.user, item_id = data['item'])
                                            account_item.amount += offer.remained_amount
                                            account_item.save()
                                        else:
                                            AccountItem(
                                                item_id    = data['item'],
                                                account_id = request.user,
                                                amount     = offer.remained_amount
                                            ).save()

                                        # 판매자 원화 잔고 반영
                                        user = Account.objects.get(id = offer.account_id)
                                        user.currency_balance += offer.remained_amount * price_data
                                        user.save()

                                        # 구매자 원화 잔고 반영
                                        user = Account.objects.get(id=request.user)
                                        user.currency_balance -= offer.remained_amount * price_data
                                        user.save()

                                        Trade(
                                            item_id     = offer.item_id,
                                            buyer_id    = request.user,
                                            seller_id   = offer.account_id,
                                            trade_price = offer.price,
                                            offer_id    = offer.id,
                                            amount      = offer.remained_amount
                                        ).save()

                                        amount_data -= offer.remained_amount

                                        offer.remained_amount = 0
                                        offer.is_active = False
                                        offer.save()

                                        print('4')

                            # 주문 테이블에 있는 수량이 구매자가 원하는 수량 보다 적음
                            else:
                                for offer in Offer.objects.filter(price=price_data, is_sell = True, is_active=True, item_id = data['item']):
                                    if Offer.objects.filter(price=price_data, is_sell = True, is_active=True, item_id = data['item']).exists():
                                        print('5')

                                        # 판매자 코인 잔고 반영
                                        user_item         = AccountItem.objects.get(account_id = offer.account_id, item_id = data['item'])
                                        user_item.amount -= offer.remained_amount

                                        if user_item.amount == 0:
                                            user_item.delete()
                                        else:
                                            user_item.save()
    
                                        # 구매자 코인 잔고 반영                    
                                        if AccountItem.objects.filter(account_id = request.user, item_id = data['item']).exists():
                                            account_item         = AccountItem.objects.get(account_id = request.user, item_id = data['item'])
                                            account_item.amount += offer.remained_amount
                                            account_item.save()
                                        else:
                                            AccountItem(
                                                item_id    = data['item'],
                                                account_id = request.user,
                                                amount     = offer.remained_amount
                                            ).save()

                                        # 판매자 원화 잔고 반영
                                        user = Account.objects.get(id = offer.account_id)
                                        user.currency_balance += offer.remained_amount * price_data
                                        user.save()

                                        # 구매자 원화 잔고 반영
                                        user = Account.objects.get(id=request.user)
                                        user.currency_balance -= offer.remained_amount * price_data
                                        user.save()

                                        Trade(
                                            item_id     = offer.item_id,
                                            buyer_id    = request.user,
                                            seller_id   = offer.account_id,
                                            trade_price = offer.price,
                                            offer_id    = offer.id,
                                            amount      = offer.remained_amount
                                        ).save()

                                        amount_data -= offer.remained_amount

                                        offer.remained_amount = 0
                                        offer.is_active = False
                                        offer.save()

                                        print('7')
                                # 주문표에 있는 수량 모두 소진 시 주문표에 남은 수량 저장
                                print('8')
                                Offer(
                                    account_id      = request.user,
                                    item_id         = data['item'],
                                    price           = price_data,
                                    origin_amount   = amount_data,
                                    remained_amount = amount_data,
                                    is_buy          = True
                                ).save()

                                return JsonResponse({"message" : "ADD_OFFER_YOUR_REMAINED_AMOUNT"})

                        # 가격 매칭이 안되었을 시 offer에 주문 저장 
                        else:
                            print('9')
                            Offer(
                                account_id      = request.user,
                                item_id         = data['item'],
                                price           = price_data,
                                origin_amount   = amount_data,
                                remained_amount = amount_data,
                                is_buy          = True
                            ).save()
                
                            return JsonResponse({"message" : "ADD_OFFER"}, status=200)

                    return JsonResponse({"message" : "CHECK_YOUR_BALANCE"}, status=400)

                return JsonResponse({"message" : "INVALID_REQUEST"}, status=400)

        except IntegrityError:
            return JsonResponse({"message":"Try again"}, status = 400)
        except ValidationError:
            return HttpResponse(status=400)
        except AccountItem.DoesNotExist:
            return JsonResponse({"message" : "CHECK_YOUR_BALANCE"}, status=400)


class TradeCancel(View):
    @Login_Check
    def post(self, request):
        return HttpResponse(status=200)

        


