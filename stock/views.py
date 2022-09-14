import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import get_object_or_404

from .forms import InquiryForm, StockCreateForm
from .models import Stock, Trade

import csv
from django.http import HttpResponse

#グラフ作成
import matplotlib
#バックエンドを指定
matplotlib.use('Agg')

import io


from .forms import CSVUploadForm

from . import stockChart

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
        stocks = Stock.objects.filter(user=self.request.user).order_by('-created_at')
        return stocks


class TradeListView(LoginRequiredMixin, generic.ListView):
    model = Trade
    template_name = 'trade_list.html'
    paginate_by = 10

    def get_queryset(self):
        trades = Trade.objects.filter(user=self.request.user).order_by('-created_at')
        return trades


class StockDetailView(LoginRequiredMixin, OnlyYouMixin, generic.DetailView):
    model = Stock
    template_name = 'stock_detail.html'


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


# class StockImportView(LoginRequiredMixin, generic.ListView):

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

    stockC = stockChart.StockChart(display=True)

    stockC.stockLoad(pk + '.T')
    fig = stockC.stockFigure()

    # fig.savefig("img.png")

    buf = io.BytesIO()
    fig.savefig(buf, format='svg', bbox_inches='tight')
    svg = buf.getvalue()

    buf.close()

    response = HttpResponse(svg, content_type='image/svg+xml')
    return response
