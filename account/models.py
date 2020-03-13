from django.db       import models
from exchange.models import Item

class Account(models.Model):
    name         = models.CharField(max_length=50, null=True)
    password     = models.CharField(max_length=400)
    email        = models.EmailField(max_length=200, unique=True)
    nickname     = models.CharField(max_length=50, null=True)
    bank         = models.CharField(max_length=50, null=True)
    bank_account = models.CharField(max_length=200, null=True)
    address      = models.CharField(max_length=500, null=True)
    created_at   = models.DateTimeField(auto_now_add=True, null=True)
    updated_at   = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'accounts'

class Offer(models.Model):
    account        = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    price          = models.DecimalField(max_digits=16, decimal_places=8)
    origin_amount  = models.DecimalField(max_digits=16, decimal_places=8)
    remined_amount = models.DecimalField(max_digits=16, decimal_places=8)
    buy            = models.BooleanField(default=False)
    sell           = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)  

    class Meta:
        db_table = 'offers'

class Trade(models.Model):
    item       = models.ForeignKey(Item, on_delete=models.CASCADE)
    buyer      = models.ForeignKey(Account, related_name='buyer', on_delete=models.SET_NULL, null=True)
    seller     = models.ForeignKey(Account, related_name='seller', on_delete=models.SET_NULL, null=True)
    offer      = models.ForeignKey(Offer, on_delete=models.CASCADE, null=True)
    amount     = models.DecimalField(max_digits=16, decimal_places=8)
    price_unit = models.DecimalField(max_digits=16, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = 'trade'


