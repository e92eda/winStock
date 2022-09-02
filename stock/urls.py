from django.urls import path

from . import views


app_name = 'stock'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('inquiry/', views.InquiryView.as_view(), name="inquiry"),
    path('stock-list/', views.StockListView.as_view(), name="stock_list"),
    path('stock-detail/<int:pk>/', views.StockDetailView.as_view(), name="stock_detail"),
    path('stock-create/', views.StockCreateView.as_view(), name="stock_create"),
    path('stock-update/<int:pk>/', views.StockUpdateView.as_view(), name="stock_update"),
    path('stock-delete/<int:pk>/', views.StockDeleteView.as_view(), name="stock_delete"),
]