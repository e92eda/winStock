from django.contrib import admin

from .models import Stock, Trade


admin.site.register(Stock)
admin.site.register(Trade)

