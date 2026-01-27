from django.contrib import admin
from django.urls import path
from pastes import views

urlpatterns = [
    # Required API Routes
    path('api/healthz', views.healthz),
    path('api/pastes', views.create_paste),
    path('api/pastes/<uuid:id>', views.fetch_api),
    
    # Required HTML Route
    path('p/<uuid:id>', views.view_html),
    
    # Home (UI)
    path('', views.create_paste),
]
