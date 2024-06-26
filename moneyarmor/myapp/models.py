from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
class User(AbstractUser):
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name='myapp_user_set',
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        verbose_name=('groups'),
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='myapp_user_permissions_set',
        blank=True,
        help_text=('Specific permissions for this user.'),
        verbose_name=('user permissions'),
    )

    def __str__(self):
        return self.email

class IncomeData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income = models.FloatField()
    income_categories = models.TextField()
    categories_70 = models.TextField()
    categories_20 = models.TextField()
    categories_10 = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"IncomeData {self.id} for user {self.user.username}"
    
User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100)
    jenis_kelamin = models.CharField(max_length=20)
    umur = models.PositiveIntegerField()
    pekerjaan = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    foto_profil = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Transaksi(models.Model):
    TIPETRANSAKSI_CHOICES = [
        ('Pemasukan', 'Pemasukan'),
        ('Pengeluaran', 'Pengeluaran'),
    ]

    KATEGORI_CHOICES = [
        ('Pemasukan', 'Pemasukan'),
        ('Kebutuhan', 'Kebutuhan'),
        ('Tabungan', 'Tabungan'),
        ('Keinginan', 'Keinginan'),
    ]

    tanggal = models.DateField()
    tipe_transaksi = models.CharField(max_length=20, choices=TIPETRANSAKSI_CHOICES)
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES)
    deskripsi = models.TextField()
    nominal = models.DecimalField(max_digits=15, decimal_places=0)  # Ubah decimal_places sesuai kebutuhan

    def __str__(self):
        return f"{self.tanggal} - {self.tipe_transaksi} - {self.kategori} - {self.nominal}"