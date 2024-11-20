from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.listAuctions, name='list-auctions'),
    path('create/', views.createAuction, name='create-auction'),
    path('<int:id>/details/', views.auctionDetails, name='auction-details'),
    # Additional Auction Gacha URLs for bidding services
    path('gachas/place/', views.placeGachaForAuction,
         name='place-gacha-for-auction'),
    path('gachas/<int:auction_id>/list/',
         views.listAllGachasOnAuction, name='list-gachas-on-auction'),
    path('gachas/<int:auction_gacha_id>/details/',
         views.auctionGachaDetails, name='auction-gacha-details'),
    path('gachas/<int:auction_gacha_id>/player/<int:player_id>/bid/',
         views.bidForGacha, name='bid-for-gacha'),
    path('gachas/<int:auction_gacha_id>/bids/',
         views.listAllBids, name='list-all-bids'),
    path('gachas/<int:auction_gacha_id>/bids/winner/',
         views.gachaWinner, name='gacha-winner'),
]
