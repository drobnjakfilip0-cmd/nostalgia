from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('user/<int:user_id>/', views.user_items, name='user_items'),
    path('users/', views.users, name='users'),
    path('users/<int:user_id>/role/', views.set_user_role, name='set_user_role'),
]
