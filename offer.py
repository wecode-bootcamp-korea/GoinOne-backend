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
