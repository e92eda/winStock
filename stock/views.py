from django.views import generic
from .forms import InquiryForm, StockCreateForm
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from django.shortcuts import get_object_or_404

from .models import Stock

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
    paginate_by = 2

    def get_queryset(self):
        stocks = Stock.objects.filter(user=self.request.user).order_by('-created_at')
        return stocks


class StockDetailView(LoginRequiredMixin,  generic.DetailView): #,OnlyYouMixin,
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
        stock.save()
        messages.success(self.request, '日記を作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "日記の作成に失敗しました。")
        return super().form_invalid(form)


class StockUpdateView(LoginRequiredMixin, generic.UpdateView):
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


class StockDeleteView(LoginRequiredMixin,  generic.DeleteView): #OnlyYouMixin,
    model = Stock
    template_name = 'stock_delete.html'
    success_url = reverse_lazy('stock:stock_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "日記を削除しました。")
        return super().delete(request, *args, **kwargs)
