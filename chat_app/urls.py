from django.urls import path
from . import views

app_name = 'chat_app'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/message/', views.chat_message, name='chat_message'),
    path('api/index/', views.index_page, name='index_page'),
]