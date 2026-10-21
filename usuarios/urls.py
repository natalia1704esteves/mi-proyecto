from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('crear-password/<str:uidb64>/<str:token>/', views.crear_password_view, name='crear_password'),
    path('reset/<str:uidb64>/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('configuracion/', views.configuracion_view, name='configuracion'),
    path('configuracion/', views.configuracion_view, name='configuracion'),
    path('configuracion/verificar-email/', views.verificar_cambio_email_view, name='verificar_cambio_email'),

]