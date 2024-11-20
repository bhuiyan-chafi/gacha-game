from django.urls import path
from . import views

urlpatterns = [
    # PlayService Endpoints
    path('play-service/roll-to-win/', views.rollToWinGacha, name='roll-to-win'),
    path('play-service/direct-purchase/', views.createPlayerGachaByPurchase, name='direct-purchase'),
    path('play-service/player/<int:player_id>/collection/', views.playerGachaCollections, name='player-collection'),
    path('play-service/player/collection/<int:collection_id>/', views.playerGachaCollectionDetails, name='player-collection-details'),

    # AuctionService Endpoints
    path('auction-service/auction/list/', views.listAuctions, name='list-auctions'),
    path('auction-service/auction/create/', views.createAuction, name='create-auction'),
    path('auction-service/auction/<int:id>/details/', views.auctionDetails, name='auction-details'),
    path('auction-service/gachas/place/', views.placeGachaForAuction, name='place-gacha-for-auction'),
    path('auction-service/gachas/<int:auction_id>/list/', views.listAllGachasOnAuction, name='list-gachas-on-auction'),
    path('auction-service/gachas/<int:auction_gacha_id>/details/', views.auctionGachaDetails, name='auction-gacha-details'),
    path('auction-service/gachas/<int:auction_gacha_id>/player/<int:player_id>/bid/', views.bidForGacha, name='bid-for-gacha'),
    path('auction-service/gachas/<int:auction_gacha_id>/bids/', views.listAllBids, name='list-all-bids'),
    path('auction-service/gachas/<int:auction_gacha_id>/bids/winner/', views.gachaWinner, name='gacha-winner'),

    # TransactionService Endpoints
    path('transaction-service/player/<int:player_id>/all/', views.playerGameCurrencyTransactions, name='player-transaction'),
    path('transaction-service/player/<int:player_id>/purchase/game-currency/', views.playerGameCurrencyPurchase, name='player-game-currency-purchase'),
    path('transaction-service/auction/winner/declare/', views.declareAuctionWinner, name='declare-auction-winner'),
]