from django.urls import path
from . import views

urlpatterns = [
    # ================= LOGIN AND LOGOUT ========================
    path('user/login/', views.loginUser, name='user-login'),
    path('user/<int:id>/logout/', views.logoutUser, name='user-logout'),
    path('token/verify/', views.verifyToken, name='verify-token'),

    # ================= CREATE | UPDATE | DELETE PLAYER/s ========================
    path('create/', views.createPlayer, name='gateway-create-player'),
    path('<int:id>/details/', views.playerDetails,
         name='gateway-player-details'),
    path('<int:id>/delete/', views.deletePlayer,
         name='gateway-delete-player'),

    # ================= SEE LIST/SINGLE GACHA ITEM ========================
    path('gacha/list/', views.listGachas, name='gateway-list-gachas'),
    path('gacha/<int:id>/details/', views.gachaDetails,
         name='gateway-gacha-details'),

    # ================= PLAY SERVICES ========================
    path('play-service/roll-to-win/', views.rollToWinGacha, name='roll-to-win'),
    path('play-service/direct-purchase/',
         views.createPlayerGachaByPurchase, name='direct-purchase'),
    path('play-service/player/<int:player_id>/collection/',
         views.playerGachaCollections, name='player-collection'),
    path('play-service/player/collection/<int:collection_id>/',
         views.playerGachaCollectionDetails, name='player-collection-details'),

    # ================= AUCTION | PLACE GACHA on AUCTION | BID FOR A GACHA ========================
    path('auction-service/auction/list/',
         views.listAuctions, name='list-auctions'),
    path('auction-service/auction/<int:id>/details/',
         views.auctionDetails, name='auction-details'),
    path('auction-service/gachas/place/',
         views.placeGachaForAuction, name='place-gacha-for-auction'),
    path('auction-service/gachas/<int:auction_id>/list/',
         views.listAllGachasOnAuction, name='list-gachas-on-auction'),
    path('auction-service/gachas/<int:auction_gacha_id>/details/',
         views.auctionGachaDetails, name='auction-gacha-details'),
    path('auction-service/gachas/<int:auction_gacha_id>/player/<int:player_id>/bid/',
         views.bidForGacha, name='bid-for-gacha'),
    path('auction-service/gachas/<int:auction_gacha_id>/bids/',
         views.listAllBids, name='list-all-bids'),

    # ================= PURCHASE RUNES AND SEE TRANSACTION DETAILS ========================
    path('transaction-service/player/<int:player_id>/all/',
         views.playerGameCurrencyTransactions, name='player-transaction'),
    path('transaction-service/player/<int:player_id>/purchase/game-currency/',
         views.playerGameCurrencyPurchase, name='player-game-currency-purchase'),
]
