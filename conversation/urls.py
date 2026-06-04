from django.urls import path

from . import views

app_name = 'conversation'

urlpatterns = [
    path('new/<int:item_pk>/', views.new, name='new'),
    path('', views.inbox, name = 'inbox'),
    path('<int:pk>/', views.detail, name='detail'),
    path('delete/<int:pk>/', views.delete_conversation, name='delete')
]