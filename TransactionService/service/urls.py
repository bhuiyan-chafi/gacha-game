from django.urls import path
from . import views

urlpatterns = [
    path('player/<int:player_id>/all/',
         views.playerGameCurrencyTransactions, name='player-transaction'),
    path('player/<int:player_id>/purchase/game-currency/',
         views.playerGameCurrencyPurchase, name='player-game-currency-purchase'),
    path('auction/winner/declare/', views.declareAuctionWinner,
         name='declare-auction-winner'),
]
