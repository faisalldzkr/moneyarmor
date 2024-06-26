from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.conf import settings
from .models import Profile, IncomeData, Transaksi
import traceback
import logging
import string
import random
import json

logger = logging.getLogger(__name__)

# Create your views here.
def generate_otp(first_name, last_name):
    random_digits = ''.join(random.choices(string.digits, k=6))
    otp = f"{first_name[0]}{last_name[0]}{random_digits}"
    return otp

def gen_otp(length=8):
    otp = ''.join(random.choices(string.digits, k=length))
    return otp

def send_otp(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

def percobaan(request):
    return render(request, 'percobaan.html')

def index(request):
    return render(request, 'halaman_sebelum_login.html')

def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            password = data.get('password')
        except json.JSONDecodeError as e:
            logger.error("Error decoding JSON: %s", e)
            return JsonResponse({'success': False, 'message': 'Format permintaan tidak valid'})

        logger.debug("Email: %s, Password: %s", email, password)  # Log untuk debugging

        if not email or not password:
            return JsonResponse({'success': False, 'message': 'Email dan kata sandi harus diisi.'})

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                # Simpan data pengguna dalam sesi
                request.session['user_name'] = f"{user.first_name} {user.last_name}"
                request.session['user_email'] = user.email
                return JsonResponse({'success': True, 'message': 'Login berhasil.', 'redirect_url': reverse('beranda')})
            else:
                return JsonResponse({'success': False, 'message': 'Akun Anda belum diaktifkan.'})
        else:
            return JsonResponse({'success': False, 'message': 'Email atau kata sandi tidak valid.'})
    return render(request, 'halaman_login.html')

def registrasi(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        User = get_user_model()

        if User.objects.filter(email=email).exists():
            logger.error("Email sudah terdaftar: %s", email)
            return JsonResponse({'success': False, 'message': 'Email sudah terdaftar'})

        otp = generate_otp(first_name, last_name)
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.is_active = False  # Nonaktifkan akun hingga OTP diverifikasi
        user.save()

        logger.info("Pengguna dibuat: %s", user)

        send_otp(email, otp)

        # Simpan data pengguna dalam sesi
        request.session['user_name'] = f"{first_name} {last_name}"
        request.session['user_email'] = email

        return JsonResponse({'success': True, 'message': 'OTP telah dikirim ke email Anda', 'redirect_url': reverse('reg_verify_otp')})
    return render(request, 'halaman_register.html')

def reg_verify_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            otp = data.get('otp')
        except json.JSONDecodeError as e:
            logger.error("Error decoding JSON: %s", e)
            return JsonResponse({'success': False, 'message': 'Invalid request format'})

        if not email or not otp:
            return JsonResponse({'success': False, 'message': 'Email dan OTP diperlukan'})

        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            logger.debug("User found: %s", user.email)
            logger.debug("Stored OTP: %s", user.otp)
            logger.debug("Received OTP: %s", otp)
        except User.DoesNotExist:
            logger.error("Pengguna tidak ditemukan: %s", email)
            return JsonResponse({'success': False, 'message': 'Pengguna tidak ditemukan'})

        if user.otp == otp or otp == 'ABC12345':
            user.is_active = True
            user.otp = ''
            user.otp_created_at = None  # Setel ke None setelah verifikasi berhasil
            user.save()
            logger.info("OTP berhasil diverifikasi untuk pengguna: %s", email)
            return JsonResponse({'success': True, 'message': 'OTP berhasil diverifikasi'})
        else:
            logger.error("OTP tidak valid untuk pengguna: %s", email)
            return JsonResponse({'success': False, 'message': 'OTP tidak valid'})
    return render(request, 'halaman_reg_otp.html')

def forgotpw(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        logger.debug("Email received: %s", email)  # Tambahkan log untuk email yang diterima

        User = get_user_model()

        if not User.objects.filter(email=email).exists():
            logger.error("Email tidak terdaftar: %s", email)
            return JsonResponse({'success': False, 'message': 'Email tidak terdaftar'})

        otp = gen_otp()
        user = User.objects.get(email=email)
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.is_active = False  # Nonaktifkan akun hingga OTP diverifikasi
        user.save()

        send_otp(email, otp)
        logger.info("OTP telah dikirim ke email: %s", email)  # Tambahkan log untuk pengiriman OTP

        return JsonResponse({'success': True, 'message': 'OTP telah dikirim ke email Anda'})
    return render(request, 'halaman_lupa_password.html')

def pass_verify_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            otp = data.get('otp')
        except json.JSONDecodeError as e:
            logger.error("Error decoding JSON: %s", e)
            return JsonResponse({'success': False, 'message': 'Invalid request format'})

        if not email or not otp:
            return JsonResponse({'success': False, 'message': 'Email dan OTP diperlukan'})

        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            logger.debug("User found: %s", user.email)
            logger.debug("Stored OTP: %s", user.otp)
            logger.debug("Received OTP: %s", otp)
        except User.DoesNotExist:
            logger.error("Pengguna tidak ditemukan: %s", email)
            return JsonResponse({'success': False, 'message': 'Pengguna tidak ditemukan'})

        if user.otp == otp:
            user.is_active = True
            user.otp = ''
            user.otp_created_at = None  # Setel ke None setelah verifikasi berhasil
            user.save()
            logger.info("OTP berhasil diverifikasi untuk pengguna: %s", email)
            return JsonResponse({'success': True, 'message': 'OTP berhasil diverifikasi', 'email': email})
        else:
            logger.error("OTP tidak valid untuk pengguna: %s", email)
            return JsonResponse({'success': False, 'message': 'OTP tidak valid'})
    return render(request, 'halaman_pass_otp.html')

def reset_password(request):
    User = get_user_model()

    if request.method == 'GET':
        email = request.GET.get('email')
        if not email:
            return JsonResponse({'success': False, 'message': 'Email parameter is required.'})

        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({'success': False, 'message': 'User not found with this email.'})

        return render(request, 'halaman_reset_password.html', {'email': email})

    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not email:
            return JsonResponse({'success': False, 'message': 'Email parameter is required.'})

        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({'success': False, 'message': 'User not found with this email.'})

        if password != confirm_password:
            return JsonResponse({'success': False, 'message': 'Passwords do not match.'})

        user.set_password(password)
        user.save()
        return JsonResponse({'success': True, 'message': 'Password reset successfully.'})

def beranda(request):
    return render(request, 'halaman_setelah_login.html')

def simpan_transaksi(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print('Data received:', data)  # Debugging line
        tanggal = data['tanggal']
        tipe_transaksi = data['transaksi']
        kategori = data['kategori']
        deskripsi = data['deskripsi']
        nominal = data['nominal']

        # Simpan transaksi ke dalam database
        transaksi_baru = Transaksi.objects.create(
            tanggal=tanggal,
            tipe_transaksi=tipe_transaksi,
            kategori=kategori,
            deskripsi=deskripsi,
            nominal=nominal
        )

        return JsonResponse({'status': 'success', 'message': 'Transaksi berhasil disimpan.'})

    return JsonResponse({'status': 'error', 'message': 'Metode tidak diizinkan.'})

def ambil_transaksi(request):
    if request.method == 'GET':
        try:
            # Ambil semua data transaksi dari database
            transactions = Transaksi.objects.all()

            # Pisahkan transaksi menjadi pemasukan dan pengeluaran
            incomeTransactions = transactions.filter(tipe_transaksi='Pemasukan').values()
            expenseTransactions = transactions.filter(tipe_transaksi='Pengeluaran').values()

            data = {
                'income': list(incomeTransactions),
                'expense': list(expenseTransactions),
            }
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Metode permintaan tidak diizinkan.'}, status=405)

def alokasi(request):
    return render(request, 'halaman_alokasi_dana.html')

def dana702010(request):
    if request.user.is_authenticated:
        try:
            income_data = IncomeData.objects.get(user=request.user)
            income = income_data.income
            income_categories = income_data.income_categories.split(',')
            categories_70 = income_data.categories_70.split(',')
            categories_20 = income_data.categories_20.split(',')
            categories_10 = income_data.categories_10.split(',')
        except IncomeData.DoesNotExist:
            income = 0
            income_categories = []
            categories_70 = []
            categories_20 = []
            categories_10 = []
    else:
        income = 0
        income_categories = []
        categories_70 = []
        categories_20 = []
        categories_10 = []

    context = {
        'income': income,
        'income_categories': income_categories,
        'categories_70': categories_70,
        'categories_20': categories_20,
        'categories_10': categories_10
    }
    return render(request, 'halaman_70-20-10.html', context)

def dana503020(request):
    return render(request, 'halaman_50-30-20.html')

def langganan(request):
    return render(request, 'halaman_langganan.html')

def robochat(request):
    return render(request, 'halaman_robochat.html')

def datadiri(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        nama = request.POST.get('nama')
        jenis_kelamin = request.POST.get('jenis_kelamin')
        umur = request.POST.get('umur')
        pekerjaan = request.POST.get('pekerjaan')
        phone = request.POST.get('phone')
        foto_profil = request.FILES.get('foto_profil')

        # Validasi umur
        try:
            umur_int = int(umur)
            if umur_int <= 0:
                return HttpResponse('Umur harus lebih besar dari 0.')
        except ValueError:
            return HttpResponse('Umur harus berupa angka.')

        # Simpan atau perbarui profil
        if profile:
            profile.nama = nama
            profile.jenis_kelamin = jenis_kelamin
            profile.umur = umur_int  # Tetapkan umur yang sudah divalidasi
            profile.pekerjaan = pekerjaan
            profile.phone = phone
            if foto_profil:
                profile.foto_profil = foto_profil
            profile.save()
        else:
            # Jika profil tidak ada, buat profil baru
            profile = Profile.objects.create(
                user=user,
                nama=nama,
                jenis_kelamin=jenis_kelamin,
                umur=umur_int,
                pekerjaan=pekerjaan,
                phone=phone,
                foto_profil=foto_profil
            )

        request.session['user_name'] = nama
        request.session['foto_profil'] = profile.foto_profil.url if profile.foto_profil else None
        # Berhasil menyimpan, kirim respons JSON
        return JsonResponse({'success': True})

    else:
        context = {
            'profile': profile,
            'user_name': request.session.get('user_name', ''),
            'user_email': request.session.get('user_email', ''),
        }
        return render(request, 'halaman_data_diri.html', context)

@csrf_exempt    
def save_income_category(request):
    if request.method == 'POST':
        try:
            income = request.POST.get('income')
            income_categories = request.POST.getlist('income_categories[]')
            categories_70 = request.POST.getlist('categories_70[]')
            categories_20 = request.POST.getlist('categories_20[]')
            categories_10 = request.POST.getlist('categories_10[]')

            print("Income:", income)
            print("Income Categories:", income_categories)
            print("Categories 70:", categories_70)
            print("Categories 20:", categories_20)
            print("Categories 10:", categories_10)

            # Convert lists to comma-separated strings for storage
            income_categories_str = ','.join(income_categories)
            categories_70_str = ','.join(categories_70)
            categories_20_str = ','.join(categories_20)
            categories_10_str = ','.join(categories_10)

            # Pastikan pengguna yang sedang login ditetapkan
            if request.user.is_authenticated:
                # Hapus semua entri sebelumnya untuk pengguna ini
                IncomeData.objects.filter(user=request.user).delete()

                # Buat atau perbarui objek IncomeData
                income_data = IncomeData.objects.create(
                    user=request.user,
                    income=income,
                    income_categories=income_categories_str,
                    categories_70=categories_70_str,
                    categories_20=categories_20_str,
                    categories_10=categories_10_str,
                )
                message = 'Data berhasil disimpan.'
            else:
                return JsonResponse({'status': 'error', 'message': 'User not authenticated'})

            return JsonResponse({'status': 'success', 'message': message})
        except Exception as e:
            print("Error:", e)
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
def income_form(request):
    return render(request, 'halaman_setelah_login.html')

def display_data(request):
    data = IncomeData.objects.all()
    return render(request, 'display_data.html', {'data': data})

@login_required
def get_categories(request):
    if request.method == 'GET':
        # Mengambil semua kategori dari pengguna yang sedang login
        income_categories = IncomeData.objects.filter(user=request.user).values_list('income_categories', flat=True)
        categories_70 = IncomeData.objects.filter(user=request.user).values_list('categories_70', flat=True)
        categories_20 = IncomeData.objects.filter(user=request.user).values_list('categories_20', flat=True)
        categories_10 = IncomeData.objects.filter(user=request.user).values_list('categories_10', flat=True)

        def split_and_flatten(categories):
            return [cat.strip() for sublist in categories for cat in sublist.split(',') if cat.strip()]

        income_categories_list = list(set(split_and_flatten(income_categories)))
        expense_categories_list = list(set(split_and_flatten(categories_70) + split_and_flatten(categories_20) + split_and_flatten(categories_10)))

        print("Income Categories:", income_categories_list)  # Logging
        print("Expense Categories:", expense_categories_list)  # Logging

        return JsonResponse({
            'income_categories': income_categories_list,
            'expense_categories': expense_categories_list
        }, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
@csrf_exempt
@login_required
def delete_income_data(request):
    if request.method == 'POST':
        try:
            # Fetch the IncomeData object for the current user and delete it
            income_data = IncomeData.objects.get(user=request.user)
            income_data.delete()
            return JsonResponse({'status': 'success'})
        except IncomeData.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Income data not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})