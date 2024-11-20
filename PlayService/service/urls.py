from django.urls import path
from . import views

urlpatterns = [
    path('roll-to-win/', views.rollToWinGacha, name='roll-to-win'),
    path('direct-purchase/', views.createPlayerGachaByPurchase,
         name='direct-purchase'),
    path('player/<int:player_id>/collection/',
         views.playerGachaCollections, name='player-collection'),
    path('player/collection/<int:collection_id>/',
         views.playerGachaCollectionDetails, name='player-collection-details'),
]
