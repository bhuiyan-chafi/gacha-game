from django.urls import path, include
from . import views

auction_gachas = [
    path('place/', views.placeGachaForAuction,
         name='place-gacha-for-auction'),
    path('<int:auction_id>/list/', views.listAllGachasOnAuction,
         name='list-auction-gachas'),
    path('<int:auction_gacha_id>/details/',
         views.auctionGachaDetails, name='auction-gacha-details'),
    path('<int:auction_gacha_id>/player/<int:player_id>/bid/',
         views.bidForGacha, name='bid-for-gacha'),
    path('<int:auction_gacha_id>/bids/',
         views.listAllBids, name='list-all-bids'),
    path('bids/winner/',
         views.gachaWinner, name='auction-gacha-winner'),
]

urlpatterns = [
    path('list/', views.listAuctions, name='list-auctions'),
    path('create/', views.createAuction, name='create-auction'),
    path('<int:id>/details/', views.auctionDetails, name='auction-details'),
    path('gachas/', include(auction_gachas))
]
