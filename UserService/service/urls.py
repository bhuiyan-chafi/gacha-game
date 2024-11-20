from django.urls import path, include
from . import views

# Define player and admin routes
player = [
    path('list/', views.listPlayersFromUserService),
    path('create/', views.createPlayerInUserService),
    path('<int:id>/details/', views.playerDetailsFromUserService),
    path('<int:id>/delete/', views.deletePlayerFromUserService),
]

admin = [
    path('list/', views.listAdminsFromUserService),
    path('create/', views.createAdminInUserService),
    path('<int:id>/details/', views.adminDetailsFromUserService),
    path('<int:id>/delete/', views.deleteAdminFromUserService),
]

# Define the main urlpatterns
urlpatterns = [
    path('player/', include(player)),
    path('admin/', include(admin)),
]
