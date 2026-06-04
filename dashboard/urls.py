from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns=[
    path('', views.index, name='index'),
    path('user/<int:user_id>/', views.user_items, name='user_items')
    
]