from django.db       import models
from exchange.models import Item

class Account(models.Model):
    name             = models.CharField(max_length=50, null=True)
    password         = models.CharField(max_length=400)
    email            = models.EmailField(max_length=200, unique=True)
    nickname         = models.CharField(max_length=50, null=True)
    bank             = models.CharField(max_length=50, null=True)
    bank_account     = models.CharField(max_length=200, null=True)
    currency_balance = models.DecimalField(max_digits=20, decimal_places=8, default=10000000)
    address          = models.CharField(max_length=500, null=True)
    is_active        = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts'

class Offer(models.Model):
    account         = models.ForeignKey(Account, on_delete=models.CASCADE)
    item            = models.ForeignKey(Item, on_delete=models.CASCADE)
    price           = models.DecimalField(max_digits=16, decimal_places=8)
    origin_amount   = models.DecimalField(max_digits=16, decimal_places=8)
    remained_amount = models.DecimalField(max_digits=16, decimal_places=8)
    is_buy          = models.BooleanField(default=False)
    is_sell         = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)  

    class Meta:
        db_table = 'offers'

class Trade(models.Model):
    item        = models.ForeignKey(Item, on_delete=models.CASCADE)
    buyer       = models.ForeignKey(Account, related_name='buyer', on_delete=models.SET_NULL, null=True)
    seller      = models.ForeignKey(Account, related_name='seller', on_delete=models.SET_NULL, null=True)
    trade_price = models.DecimalField(max_digits=30, decimal_places=8)
    offer       = models.ForeignKey(Offer, on_delete=models.CASCADE, null=True)
    amount      = models.DecimalField(max_digits=16, decimal_places=8)
    created_at  = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = 'trade'