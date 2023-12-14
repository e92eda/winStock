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
from stock.forms import InquiryForm, StockCreateForm, ChoiceForm, CSVUploadForm
from stock.models import Stock, Trade, Company, Order
from stock import stockChart, myMailRead

# グラフ作成
import matplotlib

# バックエンドを指定
matplotlib.use('Agg')

logger = logging.getLogger(__name__)

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
