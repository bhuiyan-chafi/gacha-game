from django.urls import path
from . import views

urlpatterns = [
    # Player Endpoints
    path('player/list/', views.listPlayers, name='gateway-list-players'),
    path('player/create/', views.createPlayer, name='gateway-create-player'),
    path('player/<int:id>/details/', views.playerDetails,
         name='gateway-player-details'),
    path('player/<int:id>/delete/', views.deletePlayer,
         name='gateway-delete-player'),

    # Admin Endpoints
    path('admin/list/', views.listAdmins, name='gateway-list-admins'),
    path('admin/create/', views.createAdmin, name='gateway-create-admin'),
    path('admin/<int:id>/details/', views.adminDetails,
         name='gateway-admin-details'),
    path('admin/<int:id>/delete/', views.deleteAdmin,
         name='gateway-delete-admin'),
    # Gacha Endpoints
    path('gacha/list/', views.listGachas, name='gateway-list-gachas'),
    path('gacha/create/', views.createGacha, name='gateway-create-gacha'),
    path('gacha/<int:id>/details/', views.gachaDetails,
         name='gateway-gacha-details'),
    path('gacha/<int:id>/delete/', views.deleteGacha,
         name='gateway-delete-gacha'),

    # System Variable Endpoints
    path('system-variables/create/', views.createSystemVariable,
         name='gateway-create-system-variable'),
    path('system-variables/list/', views.listSystemVariables,
         name='gateway-list-system-variables'),
    path('system-variables/<int:id>/details/', views.systemVariableDetails,
         name='gateway-system-variable-details'),
]
