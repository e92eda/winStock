import logging
import io

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
from .models import Stock, Trade
from . import stockChart

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
        # ログインユーザーと日記の作成ユーザーを比較し、異なればraise_exceptionの設定に従う
        return self.request.user == stock.user


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
        for stock in stocks:
            if stock.SymbolAlias == '':
                stock.SymbolDisp = stock.SymbolName
            else:
                stock.SymbolDisp = stock.SymbolAlias

        return stocks


class TradeListView(LoginRequiredMixin, generic.ListView):
    model = Trade
    template_name = 'trade_list.html'
    paginate_by = 10

    def get_queryset(self):
        try:
            symbolForDisplay = self.kwargs['pk']  # Requestの後に、pK（この場合表示すべき銘柄Symbol）がついている場合
            trades = Trade.objects.filter(Symbol=symbolForDisplay).order_by(
                '-created_at')  # .filter(user=self.request.user)        return trades

        except:  # Requestの後に、pK がついていない場合
            trades = Trade.objects.order_by('-created_at')  # .filter(user=self.request.user)        return trades

        return trades

    def get_success_url(self):
        return reverse_lazy('stock:stock_detail', kwargs={'pk': self.object.pk})


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


class TradeImportView(LoginRequiredMixin, generic.FormView):
    template_name = 'trade_import.html'
    success_url = reverse_lazy('stock:trade_list')
    form_class = CSVUploadForm

    def form_valid(self, form):
        form.save_trades()
        return super().form_valid(form)


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

    trades = Trade.objects.filter(Symbol=pk).order_by(
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


def stock_detail_pre(request, pk):      # Show the previous stock
    theStock = Stock.objects.get(pk=pk)
    try:
        preStock = theStock.get_previous_by_created_at()
    except:
        return redirect('stock:stock_detail', pk=pk)

    ppk = preStock.pk
    return redirect('stock:stock_detail', pk=ppk)

def stock_detail_post(request, pk):      # Show the next stock
    theStock = Stock.objects.get(pk=pk)
    try:
        preStock = theStock.get_next_by_created_at()
    except:
        return redirect('stock:stock_detail', pk=pk)

    ppk = preStock.pk
    return redirect('stock:stock_detail', pk=ppk)

def trade_delete(request):
    Trade.objects.all().delete()  # データベースから全て消去

    return redirect('/trade-list/')


class StockDetailView(generic.FormView):

    def get(self, request, *args, **kwargs):
        view = StockDetailOriginalView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = StockDetailFormView.as_view()
        return view(request, *args, **kwargs)


class StockDetailOriginalView(LoginRequiredMixin, OnlyYouMixin, generic.DetailView):
    model = Stock
    template_name = "stock_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ChoiceForm()
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


