from django.urls import path
from . import views


urlpatterns = [
    path('list/', views.listOfGacha, name='list-gacha'),
    path('create/', views.createGacha, name='create-gacha'),
    path('<int:id>/details/', views.gachaDetails, name='gacha-details'),
    path('<int:id>/delete/', views.deleteGacha, name='delete-gacha'),
]
