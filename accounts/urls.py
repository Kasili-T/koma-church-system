from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views

app_name = "accounts"

# -------------------------------
# API Router
# -------------------------------
router = DefaultRouter()
router.register(r'members', views.MemberViewSet)
router.register(r'roles', views.RoleViewSet)

# -------------------------------
# URL Patterns
# -------------------------------
urlpatterns = [
    # --------------------------------
    # Authentication
    # --------------------------------
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # --------------------------------
    # Dashboards
    # --------------------------------
    path("dashboard/", views.member_dashboard, name="dashboard"),
    path("member-dashboard/", views.member_dashboard, name="member_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
# --------------------------------
# Admin Dashboard - Extra Management
# --------------------------------
path("sermons/", views.sermons_view, name="sermons"),
path("manage-sermons/", views.manage_sermons, name="manage_sermons"),

path("media-gallery/", views.media_gallery_view, name="media_gallery"),
path("manage-media-gallery/", views.manage_media_gallery, name="manage_media_gallery"),

path("manage-news-feed/", views.manage_news_feed, name="manage_news_feed"),
path("manage-prayer-requests/", views.manage_prayer_requests, name="manage_prayer_requests"),

    # --------------------------------
    # Reports & Analytics
    # --------------------------------
    path("admin-dashboard/reports/", views.reports_analytics, name="reports_analytics"),
    path("admin-dashboard/reports/pdf/", views.reports_pdf_view, name="reports_pdf"),

    # --------------------------------
    # Profile & Account Management
    # --------------------------------
    path("profile/", views.profile_view, name="profile"),
    path("change-password/", views.change_password, name="change_password"),
    path("update-notifications/", views.update_notifications, name="update_notifications"),

    # --------------------------------
    # Donations & Finances
    # --------------------------------
    path("donations/", views.donations_view, name="donations"),
    path("contributions/", views.contributions, name="contributions"),
    path("make-donation/", views.make_donation, name="make_donation"),
    path("make-contribution/", views.make_contribution, name="make_contribution"),
    path("donations-finances/", views.donations_finances, name="donations_finances"),

    # --------------------------------
    # Attendance
    # --------------------------------
    path("attendance/", views.attendance_view, name="attendance"),

    # --------------------------------
    # Events
    # --------------------------------
    path("events/", views.events_view, name="events"),
    path("event-management/", views.event_management, name="event_management"),
    path("add-event/", views.add_event, name="add_event"),
    path("events/<int:event_id>/edit/", views.edit_event, name="edit_event"),
    path("events/<int:event_id>/delete/", views.delete_event, name="delete_event"),
    path("event-report/", views.event_report, name="event_report"),

    # --------------------------------
    # Chat & Forums
    # --------------------------------
    path("chat/", views.chat_view, name="chat"),
    path("forums/", views.forums_view, name="forums"),

    # --------------------------------
    # Admin Management
    # --------------------------------
    path("member-management/", views.member_management, name="member_management"),
    path("volunteer-management/", views.volunteer_management, name="volunteer_management"),
    path("send-notifications/", views.send_notifications, name="send_notifications"),
    path("news-feed-management/", views.news_feed_management, name="news_feed_management"),
    path("member/<int:member_id>/edit/", views.edit_member, name="edit_member"),
    path("member/<int:member_id>/delete/", views.delete_member, name="delete_member"),
    path("admin/prayer-requests/", views.admin_prayer_requests, name="admin_prayer_requests"),
    path("admin/prayer-requests/update/<int:pk>/", views.update_prayer_request, name="update_prayer_request"),
    # --------------------------------
    # News & Volunteers (CRUD)
    
    path('news-feed/create/', views.create_news_post, name='create_news_post'),
    path('news-feed/', views.news_feed, name='news_feed'),  # For listing posts
    path("news-feed/", views.news_feed, name="news_feed"),
    path("news-feed/create/", views.create_news_post, name="create_news_post"),
    path("news-feed/<int:post_id>/edit/", views.edit_news_post, name="edit_news_post"),
    path("news-feed/<int:post_id>/delete/", views.delete_news_post, name="delete_news_post"),
    path("volunteer/", views.volunteer_view, name="volunteer"),
    path("prayer-requests/", views.prayer_requests_view, name="prayer_requests"),
    path("my-attendance/", views.my_attendance_view, name="my_attendance"),
    path("admin/prayer-requests/update/<int:pk>/", views.update_prayer_request, name="update_prayer_request"),
    path('sermons/', views.sermons_view, name='sermons'),
    path('sermons/add/', views.add_sermon, name='add_sermon'),
    path('sermons/edit/<int:id>/', views.edit_sermon, name='edit_sermon'),
    path('sermons/delete/<int:id>/', views.delete_sermon, name='delete_sermon'),
    
    path('media-gallery/', views.media_gallery_list, name='media_gallery_list'),
    path('media-gallery/upload/', views.media_gallery_create, name='media_gallery_create'),
    path('media-gallery/edit/<int:id>/', views.media_gallery_edit, name='media_gallery_edit'),
    path('media-gallery/delete/<int:id>/', views.media_gallery_delete, name='media_gallery_delete'),
    path('prayer-requests/', views.prayer_requests_view, name='prayer_requests'),
    path('prayer/<int:pk>/edit/', views.prayer_edit, name='prayer_edit'),
    path('prayer/<int:pk>/delete/', views.prayer_delete, name='prayer_delete'),
    path('prayer/<int:pk>/react/', views.prayer_toggle_reaction, name='prayer_react'),
    path('admin-dashboard/news-feed/', views.admin_news_feed, name='admin_news_feed'),
    path('admin-dashboard/news-feed/create/', views.admin_create_news_post, name='admin_create_news_post'),
    path('admin/news-feed/', views.admin_news_feed, name='admin_news_feed'),
    path('admin/news-feed/create/', views.create_news_post, name='create_news_post'),







    # --------------------------------
    # Password Reset (Django Auth)
    # --------------------------------
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"),
        name="password_reset_complete",
    ),

    # --------------------------------
    # External Callbacks
    # --------------------------------
    path("mpesa-callback/", views.mpesa_callback, name="mpesa_callback"),

    # --------------------------------
    # Notifications
    # --------------------------------
    path("my-notifications/", views.my_notifications, name="my_notifications"),
    path("notifications/", views.member_notifications, name="member_notifications"),
      path("notifications/mark-read/", views.mark_notifications_read, name="mark_notifications_read"),

    # --------------------------------
    # API Routes
    # --------------------------------
    path("api/", include(router.urls)),
]
