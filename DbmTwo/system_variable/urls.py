from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.createSystemVariable,
         name='create-system-variable'),
    path('list/', views.listSystemVariables,
         name='list-system-variables'),
    path('<int:id>/details/', views.systemVariableDetails,
         name='system-variable-details'),
]
