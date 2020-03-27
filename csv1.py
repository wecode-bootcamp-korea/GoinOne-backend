import csv
import os
import re
import jwt
import json
import bcrypt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coinone.settings")

import django

django.setup()

from account.models  import *
from exchange.models import *

'''
account
'''
# CSV_PATH = '/Users/wave/Desktop/2nd_project/2nd_project_csv/account.csv'
# 
# with open(CSV_PATH, newline='') as csvfile:
	# data_reader = csv.DictReader(csvfile)
	# for row in data_reader:
		# print(row)
		# Account.objects.create(
			# email     = row['email'],
			# password  = bcrypt.hashpw(row['password'].encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8"),
# 
		# )
'''
currency
'''
CSV_PATH = '/Users/wave/Desktop/2nd_project/2nd_project_csv/currency.csv'

with open(CSV_PATH, newline='') as csvfile:
	data_reader = csv.DictReader(csvfile)
	for row in data_reader:
		print(row)
		Currency.objects.create(
			code 		     = row['code'],
			name 		     = row['name'],
            is_active 		 = row['is_active'],
			is_base_currency = row['is_base_currency']
		)

'''
item
'''
CSV_PATH = '/Users/wave/Desktop/2nd_project/2nd_project_csv/item.csv'

with open(CSV_PATH, newline='') as csvfile:
	data_reader = csv.DictReader(csvfile)
	for row in data_reader:
		print(row)
		Item.objects.create(
			currency_id      = row['currency_id'],
			code 			 = row['code'],
			name 			 = row['name'],
            is_active        = row['is_active'],
			price_unit       = row['price_unit'],
			amount_unit      = row['amount_unit']
		)

'''
account_item
'''
CSV_PATH = '/Users/wave/Desktop/2nd_project/2nd_project_csv/account_item.csv'

with open(CSV_PATH, newline='') as csvfile:
	data_reader = csv.DictReader(csvfile)
	for row in data_reader:
		print(row)
		AccountItem.objects.create(
			account_id   = row['account_id'],
			item_id      = row['item_id'],
			amount       = row['amount']
		)


'''
price
'''
CSV_PATH = '/Users/wave/Desktop/2nd_project/2nd_project_csv/price.csv'

with open(CSV_PATH, newline='') as csvfile:
	data_reader = csv.DictReader(csvfile)
	for row in data_reader:
		print(row)
		Price.objects.create(
			item_id      = row['item_id'],
			currency_id  = row['currency_id'],
			trade_price  = row['trade_price'],
			created_at   = row['created_at']
		)

'''
offer
'''
CSV_PATH = '/Users/wave/Desktop/2nd_project/2nd_project_csv/offer.csv'

with open(CSV_PATH, newline='') as csvfile:
	data_reader = csv.DictReader(csvfile)
	for row in data_reader:
		print(row)
		Offer.objects.create(
			account_id      = row['account_id'],
			item_id         = row['item_id'],
			price           = row['price'],
			origin_amount   = row['origin_amount'],
			remained_amount = row['remained_amount'],
			is_buy          = row['is_buy'],
			is_sell         = row['is_sell'],
			created_at      = row['created_at']
		)


'''
trade
'''
CSV_PATH = '/Users/wave/Desktop/2nd_project/2nd_project_csv/trade.csv'

with open(CSV_PATH, newline='') as csvfile:
	data_reader = csv.DictReader(csvfile)
	for row in data_reader:
		print(row)
		Trade.objects.create(
			item_id      = row['item_id'],
			buyer_id     = row['buyer'],
			seller_id    = row['seller'],
			offer_id     = row['offer'],
			amount       = row['amount'],
			trade_price  = row['trade_price'],
			created_at   = row['created_at']
		)


'''
report
'''

coin_list       = ['BTC', 'ETH', 'ETC', 'XRP', 'ATOM']
coin_list2      = {'BTC' : 1, 'ETH' : 2, 'ETC' : 3, 'XRP' : 4, 'ATOM' : 5} 
time_units      = ['days', 'weeks']
minutes_units   = [1, 3, 5, 15, 30, 60, 240] 


for coin in coin_list:
	for time_unit in time_units:
		CSV_PATH = f'/Users/wave/Desktop/2nd_project/2nd_project_csv/{coin}_KRW_{time_unit}.csv'

		with open(CSV_PATH, newline='') as csvfile:
			data_reader = csv.DictReader(csvfile)
			for row in data_reader:
				print(row)
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
	for minutes_unit in minutes_units:
		CSV_PATH = f'/Users/wave/Desktop/2nd_project/2nd_project_csv/{coin}_KRW_{minutes_unit}min.csv'

		with open(CSV_PATH, newline='') as csvfile:
			data_reader = csv.DictReader(csvfile)
			for row in data_reader:
				print(row)
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