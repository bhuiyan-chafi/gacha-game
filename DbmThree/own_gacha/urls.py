from django.urls import path
from . import views

urlpatterns = [
    path('roll-to-win/', views.rollToWinGacha,
         name='create-player-gacha'),
    path('direct-purchase/',
         views.createPlayerGachaByPurchase, name='create-player-gacha-purchase'),
    path('player/<int:player_id>/collection/',
         views.playerGachaCollections, name='player-gacha-collections'),
    path('player/collection/<int:collection_id>/',
         views.playerGachaCollectionDetails, name='player-gacha-collection-details'),
]
