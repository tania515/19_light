
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('', views.product_list, name='product_list'),
    # path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
]