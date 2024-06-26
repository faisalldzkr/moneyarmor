from django.urls import path
from . import views

urlpatterns = [
    path('percobaan/', views.percobaan, name=''),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('login/register/', views.registrasi, name='regis'),
    path('login/register/verifikasi-otp/', views.reg_verify_otp, name='reg_verify_otp'),
    path('login/lupa-password/', views.forgotpw, name='forgotpw'),
    path('login/lupa-password/verifikasi-otp/', views.pass_verify_otp, name='pass_verify_otp'),
    path('login/lupa-password/reset-password/', views.reset_password, name='reset_password'),
    path('beranda/', views.beranda, name='beranda'),
    path('alokasi-dana/', views.alokasi, name='alokasi'),
    path('alokasi-dana/70-20-10/', views.dana702010, name='70-20-10'),
    path('alokasi-dana/50-30-20/', views.dana503020, name='50-30-20'),
    path('langganan/', views.langganan, name='langganan'),
    path('robo-chat/', views.robochat, name='robochat'),
    path('data-diri/', views.datadiri, name='data-diri'),
    path('save-income-category/', views.save_income_category, name='save_income_category'),
    path('income-form', views.income_form, name='income_form'),
    path('display-data/', views.display_data, name='display_data'),
    path('get-categories/', views.get_categories, name='get_categories'),
    path('delete-income-data/', views.delete_income_data, name='delete_income_data'),
    path('simpan_transaksi/', views.simpan_transaksi, name='simpan_transaksi'),
    path('ambil_transaksi/', views.ambil_transaksi, name='ambil_transaksi'),
]
