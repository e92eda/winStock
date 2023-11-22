from accounts.models import CustomUser
from django.db import models

class Company(models.Model):
    symbol = models.IntegerField(db_column='Symbol', primary_key=True, default=0,)  # Field name made lowercase.
    symbolAlias = models.CharField(db_column='SymbolAlias',default="", verbose_name='Alias', max_length=12, blank=True,null=True)
    symbolName = models.CharField(db_column='SymbolName', verbose_name='Stock name', max_length=40, blank=True,null=True)  # Field name made lowercase.


#  Stock database 定義
class Stock(models.Model):
    """Stockモデル"""
    executionid = models.CharField(db_column='ExecutionID', max_length=15, blank=True,
                                   null=True)  # Field name made lowercase.
    accounttype = models.CharField(db_column='AccountType', max_length=1, blank=True,
                                   null=True)  # Field name made lowercase.
    symbol = models.IntegerField(db_column='symbol', primary_key=True,  default=0,)  # Field name made lowercase.
    symbolName = models.CharField(db_column='symbolName', verbose_name='Stock name', max_length=15, blank=True,null=True)  # Field name made lowercase.
    exchange = models.CharField(db_column='Exchange', max_length=1, blank=True, null=True)  # Field name made lowercase.
    exchangename = models.CharField(db_column='ExchangeName', max_length=15, blank=True,
                                    null=True)  # Field name made lowercase.
    price = models.DecimalField(db_column='Price', max_digits=12, decimal_places=1, blank=True,
                                null=True)  # Field name made lowercase.
    leavesqty = models.DecimalField(db_column='LeavesQty', max_digits=12, decimal_places=1, blank=True,
                                    null=True)  # Field name made lowercase.
    holdqty = models.DecimalField(db_column='HoldQty', max_digits=12, decimal_places=1, blank=True,
                                  null=True)  # Field name made lowercase.
    side = models.CharField(db_column='Side', max_length=1, blank=True, null=True)  # Field name made lowercase.
    currentprice = models.DecimalField(db_column='CurrentPrice', max_digits=12, decimal_places=1, blank=True,
                                       null=True)  # Field name made lowercase.
    valuation = models.DecimalField(db_column='Valuation', max_digits=12, decimal_places=1, blank=True,
                                    null=True)  # Field name made lowercase.
    profitloss = models.DecimalField(db_column='ProfitLoss', max_digits=12, decimal_places=1, blank=True,
                                     null=True)  # Field name made lowercase.
    profitlossrate = models.DecimalField(db_column='ProfitLossRate', max_digits=12, decimal_places=1, blank=True,
                                         null=True)  # Field name made lowercase.

    #company = models.ForeignKey(Company, on_delete=models.CASCADE, to_field='symbol', default="")
    #symbolAlias = models.CharField(default="", verbose_name='Alias', max_length=40, blank=True,null=True)
    symbolDisp = models.CharField(verbose_name='sName', max_length=40, blank=True,null=True)

    comment = models.TextField(verbose_name='コメント', blank=True, null=True)
    # user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.PROTECT, blank=True, null=True)
    user_id = models.IntegerField(default=1)
    title = models.CharField(verbose_name='タイトル', max_length=40, blank=True, null=True)

    photo1 = models.ImageField(verbose_name='写真1', blank=True, null=True)
    photo2 = models.ImageField(verbose_name='写真2', blank=True, null=True)
    photo3 = models.ImageField(verbose_name='写真3', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True, blank=True, null=True)

    holding = models.BooleanField(default=False)  # Stock hold or not.
    period = models.IntegerField(default=7)
    period_type = models.CharField(default='day', verbose_name='期間表示タイプ', max_length=10)

    # def __init__(self):
    #     super().__init__()
    #     # self.SymbolAlias = self.symbolName
        # print(self.SymbolAlias, "True name:",self.symbolName)

    class Meta:
        verbose_name_plural = 'Stock'

    # @classmethod
    # def getStock(cls, pk):



    @classmethod
    def exportListHeader(cls):
        return (['ExecutionID', 'AccountType', 'symbol', 'symbolName', 'Exchange',
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

class Order(models.Model):
    """Orderモデル  注文約定照会　Kabu ステーション　API　"""
    ID = models.CharField(primary_key=True, max_length=25, default='')
    State = models.SmallIntegerField(null=True)         #OrderStateと同一
    OrderState = models.SmallIntegerField(null=True)    #Stateと同一である
    OrdType = models.SmallIntegerField(null=True)
    RecvTime = models.DateTimeField(null=True)
    Symbol = models.IntegerField(default=0)
    SymbolName = models.CharField(null=True, verbose_name='タイトル', max_length=40)
    Exchange = models.CharField(db_column='Exchange', max_length=1, blank=True, null=True)  # Field name made lowercase.
    ExchangeName = models.CharField(db_column='ExchangeName', max_length=15, blank=True,
                                    null=True)
    Price = models.DecimalField(null=True, decimal_places=1, max_digits=10)
    OrderQty = models.IntegerField(null=True)
    CumQty = models.IntegerField(null=True)
    Side = models.SmallIntegerField(null=True)
    AccountType = models.SmallIntegerField(null=True)
    DelivType = models.SmallIntegerField(null=True)
    ExpireDay = models.DateField(null=True)

    comment = models.TextField(verbose_name='コメント', blank=True, null=True)

    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Order'

    def __str__(self):
        return self.ID



#  Trade database 定義
class Trade(models.Model):
    """Tradeモデル  売買履歴　CSVファイル読み込み。該当するAPIはない模様　"""
    id = models.CharField(primary_key=True, max_length=20, default='')
    stock_record = models.ForeignKey(Stock, on_delete=models.PROTECT,
        related_name="Stock_record", default="111")     # Relation to Stock model
    ExecutionDay = models.DateField(null=True)
    DeliveryDay = models.DateField(null=True)
    Exchange = models.IntegerField(null=True)

    ExchangeName = models.CharField(max_length=6, default=0, null=True)
    symbol = models.IntegerField(default=0)
    symbolName = models.CharField(null=True, verbose_name='タイトル', max_length=40)
    Side = models.IntegerField(null=True)
    Qty = models.IntegerField(null=True)
    Price = models.DecimalField(null=True, decimal_places=1, max_digits=10)

    Valuation = models.DecimalField(null=True, decimal_places=0, max_digits=10)
    PointUse = models.BooleanField(default=False,null=True)
    Commission = models.DecimalField(null=True, decimal_places=1, max_digits=6)
    AccountType = models.IntegerField(null=True)
    ProfitLoss = models.DecimalField(null=True, decimal_places=0, max_digits=10)
    Balance = models.DecimalField(null=True, decimal_places=0, max_digits=10)

    # CurrentPrice = models.DecimalField(null=True, decimal_places=0, max_digits=10)

    comment = models.TextField(verbose_name='コメント', blank=True, null=True)
    # user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.PROTECT)

    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True, null=True)


    class Meta:
        verbose_name_plural = 'Trade'

    def __str__(self):
        return self.id



# class FigPeriodChoice(models.Model):
# # To choose period to show in the chart. Store for each stock.
#     periodDay = models.IntegerField(default=7)
