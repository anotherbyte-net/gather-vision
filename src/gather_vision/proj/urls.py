"""gather-vision URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib.auth import views as auth_views
from django.urls import include, path
from django_distill import distill_path
from gather_vision.proj import views, settings, admin


urlpatterns = [
    path(
        "admin/password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "admin/doc/",
        include("django.contrib.admindocs.urls"),
    ),
    path(
        "admin/",
        admin.admin_site.urls,
    ),
    path(
        "electricity",
        include("gather_vision.apps.electricity.urls", namespace="electricity"),
    ),
    path(
        "legislatures",
        include("gather_vision.apps.legislatures.urls", namespace="legislatures"),
    ),
    path(
        "music",
        include("gather_vision.apps.music.urls", namespace="music"),
    ),
    path(
        "transport",
        include("gather_vision.apps.transport.urls", namespace="transport"),
    ),
    path(
        "water",
        include("gather_vision.apps.water.urls", namespace="water"),
    ),
    path(
        "explore",
        include("gather_vision.apps.explore.urls", namespace="explore"),
    ),
    distill_path(
        "",
        views.HomePageView.as_view(),
        name="index",
    ),
]

if settings.USE_DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns.append(
        path(
            "__debug__/",
            include(debug_toolbar.urls),
        )
    )
