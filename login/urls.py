from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('registrar', views.registrar, name='registrar'),
    path('login', views.inicio_sesion, name='inicio_sesion'),
    path('registro', views.registro, name='registro'),
    path('logout', views.logout, name='logout'),
    path('cambiar_pass', views.cambiar_pass, name='cambiar_pass'),
    path('recuperar/', views.recuperar, name='recuperar'),
    #Patrones de Viajes
    path('add_trip', views.add_trip, name="add_trip"),
    path('join_plan', views.join_plan, name="join_plan"),
    path('show_trip', views.show_trip, name="show_trip"),
]
