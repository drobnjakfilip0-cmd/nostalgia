from django.urls import path

from . import views

app_name = 'item'

urlpatterns=[
    path('', views.items, name='items'),
    path('<int:pk>/', views.detail, name='detail'),
    path('seller/<int:pk>/', views.seller, name='seller'),
    path('new/', views.new, name='new'),
    path('<int:pk>/delete', views.delete, name='delete'),
    path('<int:pk>/edit', views.edit, name='edit'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='favorite'),
    path("<int:pk>/buy/", views.buy_now, name="buy_now")
]