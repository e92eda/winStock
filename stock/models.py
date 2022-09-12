from accounts.models import CustomUser
from django.db import models


class Stock(models.Model):
    """Stockモデル"""
    # ExecutionID = models.CharField(null=True, max_length=40)
    # AccountType = models.CharField(null=True, max_length=6)
    Symbol = models.CharField(max_length=6, default='', primary_key=True)

    SymbolName = models.CharField(null=True,verbose_name='タイトル', max_length=40)
    # Exchange = models.IntegerField(null=True)
    # ExchangeName = models.CharField(null=True, max_length=40)
    # ExecutionDay = models.DateField(null=True)
    Price = models.IntegerField(null=True)
    LeavesQty = models.IntegerField(null=True)
    # HoldQty = models.IntegerField(null=True)
    # Side = models.IntegerField(null=True)
    # Expenses = models.DecimalField(null=True,decimal_places=1, max_digits=10)
    # Commission = models.DecimalField(null=True, decimal_places=1, max_digits=6)
    # CommissionTax = models.DecimalField(null=True, decimal_places=1, max_digits=6)
    # ExpireDay = models.DateField(null=True)
    # MarginTradeType = models.IntegerField(null=True)
    CurrentPrice = models.DecimalField(null=True,decimal_places=0, max_digits=10)
    Valuation = models.DecimalField(null=True,decimal_places=0, max_digits=10)
    ProfitLoss = models.DecimalField(null=True,decimal_places=0, max_digits=10)
    ProfitLossRate = models.DecimalField(null=True,decimal_places=3, max_digits=6)
    #
    comment = models.TextField(verbose_name='コメント', blank=True, null=True)
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.PROTECT)
    title = models.CharField(verbose_name='タイトル', max_length=40)
    # content = models.TextField(verbose_name='本文', blank=True, null=True)
    photo1 = models.ImageField(verbose_name='写真1', blank=True, null=True)
    photo2 = models.ImageField(verbose_name='写真2', blank=True, null=True)
    photo3 = models.ImageField(verbose_name='写真3', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    holding = models.BooleanField(default=False)       # Stock hold or not.

    class Meta:
        verbose_name_plural = 'Stock'

    @classmethod
    def exportListHeader(cls):
        return(['ExecutionID', 'AccountType', 'Symbol', 'SymbolName', 'Exchange',
                'ExchangeName', 'ExecutionDay', 'Price', 'LeavesQty', 'HoldQty', 'Side',
                'Expenses', 'Commission', 'CommissionTax', ' ExpireDay', 'MarginTradeType',
                'CurrentPrice', 'Valuation', 'ProfitLoss', 'ProfitLossRate'])

    def exportList(self):
        return ([self.ExecutionID, self.AccountType, self.Symbol, self.SymbolName, self.Exchange
            , self.ExchangeName, self.ExecutionDay, self.Price, self.LeavesQty, self.HoldQty, self.Side
            , self.Expenses, self.Commission, self.CommissionTax, self.ExpireDay, self.MarginTradeType
            , self.CurrentPrice, self.Valuation, self.ProfitLoss, self.ProfitLossRate])

    def __str__(self):
        return self.title

