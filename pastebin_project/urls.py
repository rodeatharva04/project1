from django.urls import path
from pastes import views

urlpatterns = [
    path('api/healthz', views.health_check), # This must match the name in views.py
    path('api/pastes', views.create_paste),
    path('api/pastes/<uuid:id>', views.fetch_paste_api),
    path('p/<uuid:id>', views.fetch_paste_html),
    path('', views.create_paste), 
]