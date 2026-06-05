from django.urls import path
from . import views

app_name = 'item'

urlpatterns = [
    path('',                          views.items,          name='items'),
    path('novi/',                     views.new,            name='new'),
    path('prodavac/<int:pk>/',        views.seller,         name='seller'),
    path('<slug:slug>/',              views.detail,         name='detail'),
    path('<slug:slug>/uredi',         views.edit,           name='edit'),
    path('<slug:slug>/obrisi',        views.delete,         name='delete'),
    path('<slug:slug>/favorit/',      views.toggle_favorite, name='favorite'),
    path('<slug:slug>/kupi/',         views.buy_now,        name='buy_now'),
]
