"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path,include
from projapp import views as views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('api/subscribe/', views.subscribe, name='mailchimp-subscribe'),
    path('contact/', views.contact_view, name='contact'),  # URL for the Mailchimp subscription API
    path('', views.index, name='index'),  # URL for the index view
    path('about', views.about, name='about'),  # URL for the about view
    path('contact/', views.contact, name='contact'),  # URL for the contact view
    path('bba/', views.bba, name='bba'),  # URL for the bba view
    path('bcom/', views.bcom, name='Bcom'),  # URL for the bcom view
    path('be-ece/', views.be_ece, name='BE-ECE'), 
    path('be-ece/', views.be_ece, name='BE ECE'), # URL for the BE ECE view
    path('bsc-it/', views.bsc_it, name='bscit'),  # URL for the BSc IT view
    path('data-analyst/', views.data_analyst, name='data_analyst'),  # URL for the Data Analyst view
    path('web-developer/', views.web_developer, name='web_developer'),  # URL for the Web Developer view
    path('be-it/', views.be_it, name='BE-it'),
    path('be-it/', views.be_it, name='BE it'),  # URL for the BE IT view
    path('bsc-cs/', views.bsc_cs, name='bsc-cs'),
    path('BSC_CS/', views.bsc_cs, name='BSc_CS'),  # alias # URL for the BSc CS view
    path('bcomca/', views.bcomca, name='bcomca'),  # URL for the BCom CA view
    path('be-eee/', views.be_eee, name='BE-EEE'),
    path('be-eee/', views.be_eee, name='BE EEE'),   # URL for the BE EEE view
    path('detail-page/', views.detail_page, name='detail-page'),  # URL for the detail page view
    path('listing-page/', views.listing_page, name='listing-page'),  # URL for the listing page view
    path('small/', views.small, name='small'),  # URL for the small view
    path('AIML/', views.AIML, name='AIML'),  # URL for the AIML view
    path('Cloud/', views.Cloud, name='Cloud'),  # URL for the Cloud view
    path('login/', views.login, name='login'),  # URL for the login view
    path('search/', views.search, name='search'),  # URL for the search view

    path('chat/', include('chat_app.urls')),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

