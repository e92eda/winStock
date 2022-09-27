from django.urls import path

from . import views


app_name = 'stock'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('inquiry/', views.InquiryView.as_view(), name="inquiry"),
    path('stock-list/', views.StockListView.as_view(), name="stock_list"),
    path('stock-create/', views.StockCreateView.as_view(), name="stock_create"),
    path('stock-update/<str:pk>/', views.StockUpdateView.as_view(), name="stock_update"),
    path('stock-delete/<str:pk>/', views.StockDeleteView.as_view(), name="stock_delete"),

# グラフ描画
    path('stock-detail/<str:pk>/', views.StockDetailView.as_view(), name="stock_detail"),
    path('stock-detail/<str:pk>/plot/', views.get_svg, name='plot'),
    # path('plot/', views.get_svg, name='plot'),

# Stock　データベース読み,書き込み
    path('stock-import/', views.StockImportView.as_view(), name="stock_import"),
    path('stock-export/', views.stock_export, name='stock_export'),

# Trade　データベース読み込み,削除
    path('trade-list/', views.TradeListView.as_view(), name="trade_list"),
    path('trade-list/<str:pk>/', views.TradeListView.as_view(), name="trade_list"),

    path('trade-import/', views.TradeImportView.as_view(), name="trade_import"),
    path('trade-delete/', views.trade_delete, name='trade_delete'),

# Test Radiobutton
#     path('my-test/<str:pk>/', views.MyTestView.as_view(), name="my_test"),

]
