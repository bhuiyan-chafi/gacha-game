from django.urls import path
from . import views

urlpatterns = [

    # ================= TEST IF THE GATEWAY IS RUNNING ========================
    path('test/', views.gateWayOneTest, name='auth-service-test'),

    # ================= LOGIN AND LOGOUT ========================
    path('user/login/', views.loginUser, name='user-login'),
    path('user/<int:id>/logout/', views.logoutUser, name='user-logout'),

    # ================= CREATE | UPDATE | DELETE USERS ========================
    path('user/create/', views.createUser, name='auth-service-create-user'),
    path('user/list/', views.listOfUsers, name='auth-service-list-users'),
    path('user/<int:id>/details/', views.userDetails,
         name='auth-service-user-details'),
    path('user/<int:id>/delete/', views.deleteUser,
         name='auth-service-delete-user'),

    # ================= CREATE | UPDATE | DELETE ADMINS ========================
    path('admin/list/', views.listAdmins, name='gateway-list-admins'),
    path('admin/create/', views.createAdmin, name='gateway-create-admin'),
    path('admin/<int:id>/details/', views.adminDetails,
         name='gateway-admin-details'),
    path('admin/<int:id>/delete/', views.deleteAdmin,
         name='gateway-delete-admin'),

    # ================= CREATE | UPDATE | DELETE PLAYERS ========================
    path('player/list/', views.listPlayers, name='gateway-list-players'),
    path('player/<int:id>/details/', views.playerDetails,
         name='gateway-player-details'),
    path('player/<int:id>/delete/', views.deletePlayer,
         name='gateway-delete-player'),

    # ================= CREATE | UPDATE | DELETE GACHAS ========================
    path('gacha/list/', views.listGachas, name='gateway-list-gachas'),
    path('gacha/create/', views.createGacha, name='gateway-create-gacha'),
    path('gacha/<int:id>/details/', views.gachaDetails,
         name='gateway-gacha-details'),
    path('gacha/<int:id>/delete/', views.deleteGacha,
         name='gateway-delete-gacha'),

    # ================= PLAYER COLLECTION: ALL + SINGLE GACHA/S ========================
    path('play-service/player/<int:player_id>/collection/',
         views.playerGachaCollections, name='player-collection'),
    path('play-service/player/collection/<int:collection_id>/',
         views.playerGachaCollectionDetails, name='player-collection-details'),
    # ================= VIEW PLAYER TRANSACTIONS ========================
    path('transaction-service/player/<int:player_id>/all/',
         views.playerGameCurrencyTransactions, name='player-transaction'),

    # ================= CREATE | UPDATE | DELETE AUCTIONS ========================
    path('auction-service/auction/list/',
         views.listAuctions, name='list-auctions'),
    path('auction-service/auction/create/',
         views.createAuction, name='create-auction'),
    path('auction-service/auction/<int:id>/details/',
         views.auctionDetails, name='auction-details'),

    # ================= VIEW AUCTION GACHAS ========================
    path('auction-service/gachas/<int:auction_id>/list/',
         views.listAllGachasOnAuction, name='list-gachas-on-auction'),
    path('auction-service/gachas/<int:auction_gacha_id>/details/',
         views.auctionGachaDetails, name='auction-gacha-details'),

    # ================= VIEW AUCTION BIDS ========================
    path('auction-service/gachas/<int:auction_gacha_id>/bids/',
         views.listAllBids, name='list-all-bids'),

    # ================= DECLARE THE WINNER ========================
    path('auction-service/gachas/<int:auction_gacha_id>/bids/winner/',
         views.gachaWinner, name='gacha-winner'),

    # ================= Player Transactions ========================
    path('transaction-service/player/<int:player_id>/all/',
         views.playerGameCurrencyTransactions, name='player-transaction'),
]
