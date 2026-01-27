from django.urls import path
from pastes import views

urlpatterns = [
    path('api/healthz', views.healthz),
    path('api/pastes', views.create_paste),
    path('api/pastes/<uuid:id>', views.fetch_api),
    path('p/<uuid:id>', views.view_html),
    path('', views.create_paste),
]
