import logging
import io
import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render

import csv
from django.http import HttpResponse, HttpResponseForbidden

from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from django import forms
from .forms import InquiryForm, StockCreateForm, ChoiceForm, CSVUploadForm
from .models import Stock, Trade, Company, Order
from . import stockChart, myMailRead

# グラフ作成
import matplotlib

# バックエンドを指定
matplotlib.use('Agg')

logger = logging.getLogger(__name__)


class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        # URLに埋め込まれた主キーから日記データを1件取得。取得できなかった場合は404エラー
        stock = get_object_or_404(Stock, pk=self.kwargs['pk'])
        # ログインユーザーと日記の作成ユーザーを比較し、異なればraise_exceptionの設定に従う=>すべてOK
        # return self.request.user == stock.user
        return True


class IndexView(generic.TemplateView):
    template_name = "index.html"


class InquiryView(generic.FormView):
    template_name = "inquiry.html"
    form_class = InquiryForm

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'メッセージを送信しました。')
        logger.info('Inquiry sent by {}'.format(form.cleaned_data['name']))
        return super().form_valid(form)


class StockListView(LoginRequiredMixin, generic.ListView):
    model = Stock
    template_name = 'stock_list.html'
    paginate_by = 10

    def get_queryset(self):
        stocks = Stock.objects.order_by('-created_at')  # filter(user=self.request.user).
        #stocks = Stock.objects.order_by('-symbol')  # filter(user=self.request.user).
        # for stock in stocks:
        #     if stock.symbolAlias == '' or stock.symbolAlias == None:
        #         stock.symbolDisp = stock.symbolName
        #     else:
        #         stock.symbolDisp = stock.symbolAlias
        for stock in stocks:
            if Company.objects.filter(symbol=stock.symbol).exists():
                stock.symbolDisp = Company.objects.get(symbol=stock.symbol).symbolAlias
            else:
                stock.symbolDisp = "****" + str(stock.symbol)

        return stocks


class TradeListView(LoginRequiredMixin, generic.ListView):
    model = Trade
    template_name = 'trade_list.html'
    paginate_by = 10

    def get_queryset(self):
#
        tranMailFolder = "/Users/kunieda/Dropbox/StockExecute/tranMail/*.txt"
        stockMail= myMailRead.StockMail()

        # fromMailText = stockMail.getFromMailSave(tranMailFolder)

        # self.saveTradeMail(fromMailText)        # Convert to Trade and save the results.

        try:
            symbolForDisplay = self.kwargs['pk']  # Requestの後に、pK（この場合表示すべき銘柄Symbol）がついている場合
            trades = Trade.objects.filter(symbol=symbolForDisplay).order_by(
                '-created_at')  # .filter(user=self.request.user)        return trades

        except:  # Requestの後に、pK がついていない場合
            trades = Trade.objects.order_by('-created_at')  # .filter(user=self.request.user)        return trades

        return trades

    def get_success_url(self):
        return reverse_lazy('stock:stock_detail', kwargs={'pk': self.object.pk})

    def saveTradeMail(self, fromMailText):        # Convert to Trade and save the results.
        # iD の連番生成のため、datetimeを元に、３桁追加して作成、元々はcsvファイルからの読み込みの場合だが、整合性をとる
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        now = datetime.datetime.now(JST)
        dtimestring = now.strftime('%Y%m%d %H%M%S')
        # sellBuy = {'売り': 1, '買い': 2}
        lcount = 0
        for result in fromMailText:

            if '売り' in result['sellbuy']:
                side = 1
            else:
                side = 2

            symbolSerach = result['symbol']
            try:
                stockMatch = Stock.objects.get(symbol=symbolSerach)
            except Exception as e:  # Muched stock does not exist
                print(f'Error!! {symbolSerach} :Corresponding Stock does not exits. {e} ')

                stockMatch = Stock(symbol=symbolSerach, symbolName=row[0] + '*',
                                   user_id=1)  # So, this is dummy., user_id=1
                stockMatch.save()

            aTrade = Trade(ExecutionDay=result['tdate'].replace('/', '-'),
                # ExchangeName =row[2],
                symbolName = result['symbolName'],
                symbol=result['symbol'],
                Side= side,
                Qty=result['qty'], Price= result['price'],
                # Valuation=row[8], PointUse=row[9],
                # Commission=row[10], ProfitLoss=row[12], stock_record=stockMatch, user_id=1,
                stock_record=stockMatch,
                user_id=1,
                id=dtimestring + f'{lcount:03}'  # 年から秒までと、0埋めで3文字)       #AccountType=row[11],
            )
            # ないデータ：　DeliveryDay=,
            aTrade.save()       # Databaseに保存

            lcount += 1

class OrderListView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'order_list.html'
    paginate_by = 10

    def get_queryset(self):
#
        # tranMailFolder = "/Users/kunieda/Dropbox/StockExecute/tranMail/*.txt"
        # stockMail= myMailRead.StockMail()

        # fromMailText = stockMail.getFromMailSave(tranMailFolder)

        # self.saveorderMail(fromMailText)        # Convert to Trade and save the results.

        try:
            symbolForDisplay = self.kwargs['pk']  # Requestの後に、pK（この場合表示すべき銘柄Symbol）がついている場合
            orders = Order.objects.filter(symbol=symbolForDisplay).order_by(
                '-created_at')  # .filter(user=self.request.user)        return orders

        except:  # Requestの後に、pK がついていない場合
            orders = Order.objects.order_by('-created_at')  # .filter(user=self.request.user)        return orders

        return orders

class StockCreateView(LoginRequiredMixin, generic.CreateView):
    model = Stock
    template_name = 'stock_create.html'
    form_class = StockCreateForm
    success_url = reverse_lazy('stock:stock_list')

    def form_valid(self, form):
        stock = form.save(commit=False)
        stock.user = self.request.user
        stock.save_stocks()
        messages.success(self.request, 'Stockデータを作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Stockデータの作成に失敗しました。")
        return super().form_invalid(form)


class StockUpdateView(LoginRequiredMixin, OnlyYouMixin, generic.UpdateView):
    model = Stock
    template_name = 'stock_update.html'
    form_class = StockCreateForm

    def get_success_url(self):
        return reverse_lazy('stock:stock_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, '日記を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "日記の更新に失敗しました。")
        return super().form_invalid(form)


class StockDeleteView(LoginRequiredMixin, OnlyYouMixin, generic.DeleteView):
    model = Stock
    template_name = 'stock_delete.html'
    success_url = reverse_lazy('stock:stock_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "日記を削除しました。")
        return super().delete(request, *args, **kwargs)


class StockImportView(LoginRequiredMixin, generic.FormView):
    template_name = 'stock_import.html'
    success_url = reverse_lazy('stock:stock_list')
    form_class = CSVUploadForm

    def form_valid(self, form):
        form.save_stocks()
        # return redirect('app:index')
        return super().form_valid(form)


class TradeImportView(LoginRequiredMixin, generic.FormView):    # Kabu Station CSV file read
    template_name = 'trade_import.html'
    success_url = reverse_lazy('stock:trade_list')
    form_class = CSVUploadForm

    def form_valid(self, form):
        form.save_trades()
        return super().form_valid(form)


# def tradeMailImport(request):   # Import from the mail text.
#     tranMailFolder = "/Users/kunieda/Dropbox/StockExecute/tranMail/*.txt"
#     stockMail= myMailRead.StockMail()
#     results = stockMail.getFromMailSave(tranMailFolder)
#     print (results)




def stock_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="posts.csv"'
    # HttpResponseオブジェクトはファイルっぽいオブジェクトなので、csv.writerにそのまま渡せます。
    writer = csv.writer(response)

    writer.writerow(Stock.exportListHeader())  # Header write
    for post in Stock.objects.all():
        writer.writerow(post.exportList())
    return response


# チャート表示
def get_svg(request, pk):
    astock = Stock.objects.get(pk=pk)

    stockC = stockChart.StockChart(display=True)

    stockC.stockLoad(pk + '.T', period_type=astock.period_type, period=astock.period)

    # Trade data to show

    trades = Trade.objects.filter(symbol=pk).order_by(
        '-created_at')  # .filter(user=self.request.user)

    # arrowList = [(t.ExecutionDay, t.price)for t in trades] #, t.Side, t.Qty
    arrowList = []
    for t in trades:
        arrowList.append({'x': t.ExecutionDay, 'y': t.Price, 'side': t.Side, 'qty': t.Qty})

    titleText = f"Display period: {astock.period} {astock.period_type}"
    fig = stockC.stockFigure(arrow=arrowList, title=titleText)

    # SVG 形式体系
    buf = io.BytesIO()
    fig.savefig(buf, format='svg', bbox_inches='tight')
    svg = buf.getvalue()

    buf.close()

    response = HttpResponse(svg, content_type='image/svg+xml')
    return response


def stock_detail_pre(request, pk): # Show the previous stock
    # ipk = int (pk)
   # preStock = theStock.get_previous_by_created_at()

    try:
        theStock = Stock.objects.get(pk=pk)
        ordered_objects = Stock.objects.order_by('symbol')
        preStock = ordered_objects.filter(symbol__lt=theStock.symbol).last()  #前のSymbol順を取得
    except:
        return redirect('stock:stock_detail', pk=pk)

    ppk = preStock.pk
    return redirect('stock:stock_detail', pk=ppk)

def stock_detail_post(request, pk):      # Show the next stock
    try:
        theStock = Stock.objects.get(pk=pk)
        ordered_objects = Stock.objects.order_by('symbol')
        preStock = ordered_objects.filter(symbol__gt=theStock.symbol).first()  #前のSymbol順を取得
    except:
        return redirect('stock:stock_detail', pk=pk)

    ppk = preStock.pk
    return redirect('stock:stock_detail', pk=ppk)

def trade_delete(request):
    Trade.objects.all().delete()  # データベースから全て消去

    return redirect('/trade-list/')


class StockDetailView(generic.FormView): # 最初の入り口

    def get(self, request, *args, **kwargs):
        view = StockDetailOriginalView.as_view()    #GetならOriginalViewへ
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = StockDetailFormView.as_view()        #PostならFormViewへ
        return view(request, *args, **kwargs)


class StockDetailOriginalView(LoginRequiredMixin, OnlyYouMixin, generic.DetailView):
    model = Stock
    template_name = "stock_detail.html"
    # trades = Trade.objects.order_by(
    # '-created_at')  #         return trades

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        given_period = f"{context['object'].period} {context['object'].period_type}"
        context['form'] = ChoiceForm(initial={'selected_period': given_period})

        symbolForDisplay =context['object'].symbol
        trades = Trade.objects.filter(symbol=symbolForDisplay).order_by('-created_at')  #         return trades
        # context['trade_list'] = trades
        # 追加したいコンテキスト情報(取得したコンテキスト情報のキーのリストを設定)
        # addList = []
        tradeBalance = 0    # Trade balance of each Stock
        for atrd in trades:
            if atrd.Side == 1:      # Sell
                tradeBalance += atrd.Valuation
            elif atrd.Side == 2:    # Buy
                tradeBalance -= atrd.Valuation
            else:
                raise ValueError("Trade Side error!")
            atrd.Balance = tradeBalance
            # addList.append(tradeBalance)      # Make list for data transfer

        # コンテキスト情報のキーを追加
        context['trade_list'] = trades

        return context


class StockDetailFormView(SingleObjectMixin, FormView):
    form_class = ChoiceForm
    model = Stock
    template_name = "stock_detail.html"

    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()

        try:
            selected_choice = request.POST['selected_period']
        except (KeyError, selected_choice.DoesNotExist):
            # Redisplay the question voting form.
            return render(request, 'stock_detail.html', {
                # 'question': question,
                'error_message': "You didn't select a choice.",
            })
        else:
            # Store given period, period_type to the database
            pk = kwargs['pk']
            astock = Stock.objects.get(pk=pk)

            foundPosition = selected_choice.find(' ')     #get the first comporneto of selected_choice.
            astock.period = selected_choice[:foundPosition]
            astock.period_type = selected_choice[foundPosition+1:]     #get the rest.
            astock.save()

            return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('stock:stock_detail', kwargs={'pk': self.object.pk})


