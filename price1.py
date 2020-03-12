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


coin_list       = ['ETC', 'ATOM']
coin_list2      = {'ETC' : 3, 'ATOM' : 5} 
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