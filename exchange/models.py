from django.db      import models

class Currency(models.Model):
    code             = models.CharField(max_length=50)
    name             = models.CharField(max_length=50)
    symbol           = models.URLField(max_length=500)
    is_active        = models.BooleanField(default=False)
    is_base_currency = models.BooleanField(default=False)

    class Meta:
        db_table = 'currencies'

class Item(models.Model):
    currency     = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True)
    account      = models.ManyToManyField('account.Account', through='AccountItem')
    code         = models.CharField(max_length=50)
    name         = models.CharField(max_length=50)
    price_unit   = models.DecimalField(max_digits=8, decimal_places=3)
    amount_unit  = models.DecimalField(max_digits=8, decimal_places=3) 
    is_active    = models.BooleanField(default=False)

    class Meta:
        db_table = 'items'

class Price(models.Model):
    item        = models.ForeignKey('Item', on_delete=models.CASCADE)
    currency    = models.ForeignKey('Currency', on_delete=models.CASCADE)
    trade_price = models.DecimalField(max_digits=20, decimal_places=8)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'price'

class Report(models.Model):
    item          = models.ForeignKey('Item', on_delete=models.CASCADE)
    currency      = models.ForeignKey('Currency', on_delete=models.CASCADE)
    opening_price = models.DecimalField(max_digits=30, decimal_places=8)
    high_price    = models.DecimalField(max_digits=30, decimal_places=8)
    low_price     = models.DecimalField(max_digits=30, decimal_places=8)
    trade_price   = models.DecimalField(max_digits=30, decimal_places=8)
    candle_price  = models.DecimalField(max_digits=30, decimal_places=8)
    candle_volume = models.DecimalField(max_digits=30, decimal_places=8)
    unit          = models.CharField(max_length=50)
    date          = models.DateTimeField(max_length=100)

    class Meta:
        db_table = 'reports'

class AccountItem(models.Model):
    item    = models.ForeignKey('Item', on_delete=models.CASCADE)
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    amount  = models.DecimalField(max_digits=30, decimal_places=8, default=0)

    class Meta:
        db_table = 'account_item'
