from django.contrib import admin
from myapp.models import User, IncomeData, Transaksi

# Register your models here.
@admin.register(IncomeData)
class IncomeDataAdmin(admin.ModelAdmin):
    list_display = ('income', 'created_at')
admin.site.register(User)
admin.site.register(Transaksi)