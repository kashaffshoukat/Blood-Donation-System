# In your donor/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView
from . import views


urlpatterns = [
    # --- Authentication Paths ---
    path('donorlogin', LoginView.as_view(template_name='donor/donorlogin.html'),name='donorlogin'),
    path('donorsignup', views.donor_signup_view,name='donorsignup'),
    
    # --- Donor Dashboard & Core Functionality ---
    path('donor-dashboard', views.donor_dashboard_view, name='donor-dashboard'),
    path('donate-blood', views.donate_blood_view, name='donate-blood'),
    path('donation-history', views.donation_history_view, name='donation-history'),
    path('make-request', views.make_request_view, name='make-request'),
    path('request-history', views.request_history_view, name='request-history'),

    # --- Donor Profile Paths ---
    path('profile', views.donor_profile_view, name='donor_profile_management'),
    path('delete-profile', views.delete_donor_profile_view, name='delete_donor_profile'),
    # FIX: Trailing slash removed to match the browser request: /search-donors
    path('search-donors', views.public_donor_search_view, name='public_donor_search'),
    # --- ADMIN PATH FOR DONOR VIEW (Required for Search) ---
    path('admin/view-donor', views.admin_view_donor_view, name='admin-view-donor'),
]