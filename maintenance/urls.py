from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('demo/<str:role>/', views.demo_login, name='demo_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('complaints/new/', views.complaint_create, name='complaint_create'),
    path('complaints/<str:ticket_id>/', views.complaint_detail, name='complaint_detail'),

    # API
    path('api/complaints/<str:ticket_id>/status/', views.api_update_status, name='api_update_status'),
    path('api/complaints/<str:ticket_id>/assign/', views.api_assign_technician, name='api_assign_technician'),
    path('api/complaints/<str:ticket_id>/rate/', views.api_rate_complaint, name='api_rate_complaint'),
    path('api/complaints/<str:ticket_id>/comment/', views.api_add_comment, name='api_add_comment'),
    path('api/complaints/<str:ticket_id>/urgency/', views.api_update_urgency, name='api_update_urgency'),
]
