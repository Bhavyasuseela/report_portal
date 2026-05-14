from django.urls import path
from accounts.views import (
    login_view, login_author, login_convener, login_reviewer, login_librarian, login_head,
    login_admin,
    verify_otp_view, logout_view, dashboard_redirect, register_author,
    admin_dashboard, admin_add_user, admin_edit_user, admin_delete_user, admin_toggle_active,
    admin_approve_author, admin_reject_author,
    change_password, forgot_password, reset_password_via_link,
)

urlpatterns = [
    path('', dashboard_redirect, name='dashboard'),
    path('login/', login_view, name='login'),
    path('login/author/', login_author, name='login_author'),
    path('login/convener/', login_convener, name='login_convener'),
    path('login/reviewer/', login_reviewer, name='login_reviewer'),
    path('login/librarian/', login_librarian, name='login_librarian'),
    path('login/head/', login_head, name='login_head'),
    path('login/admin/', login_admin, name='login_admin'),
    path('register/', register_author, name='register_author'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),
    path('logout/', logout_view, name='logout'),
    path('change-password/', change_password, name='change_password'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', reset_password_via_link, name='reset_password_via_link'),

    # Admin panel
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/add-user/', admin_add_user, name='admin_add_user'),
    path('admin-panel/edit-user/<int:user_id>/', admin_edit_user, name='admin_edit_user'),
    path('admin-panel/delete-user/<int:user_id>/', admin_delete_user, name='admin_delete_user'),
    path('admin-panel/toggle-active/<int:user_id>/', admin_toggle_active, name='admin_toggle_active'),
    path('admin-panel/approve-author/<int:user_id>/', admin_approve_author, name='admin_approve_author'),
    path('admin-panel/reject-author/<int:user_id>/', admin_reject_author, name='admin_reject_author'),
]
