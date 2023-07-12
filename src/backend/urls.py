from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from companies.views import CompanyViewSet
from conversations.views import init_conversation, play_the_middle_man, ConversationViewSet, VendorViewSet
from users.views import LoginView, LogoutView, UserPasswordResetViewSet, UserViewSet


router = routers.DefaultRouter()

# user related, i.e. reset passwords
router.register('passwordreset', UserPasswordResetViewSet, basename='passwordreset')

# Custom views
router.register('companies', CompanyViewSet, basename='companies')
router.register('vendors', VendorViewSet, basename='vendors')
router.register('users', UserViewSet)
router.register('conversations', ConversationViewSet, basename="conversations")

urlpatterns = [
    # Twilio webhook
    path('init_conversation', init_conversation, name='init_conversation'),
    path('play_the_middle_man', play_the_middle_man, name='play_the_middle_man'),

    # Stripe webhook
    # path('stripe/webhook/', webhooks.handler_all, name="djstripe-webhook"),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),

    # Our URLS
    path('api/', include(router.urls)),

    # TODO: Add these auth endpoints to api docs, like password reset ??
    path('api/auth/login/', LoginView.as_view(), name="rest_login"),
    path('api/auth/logout/', LogoutView.as_view(), name="rest_logout"),

    # Django built in
    path('admin/', admin.site.urls),
]


if settings.DEBUG:  # pragma: no cover
    # Static files for local dev, so we don't have to collectstatic and such
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Django debug toolbar
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

# If we're being served on Heroku, we're on `django/` prefix, so prefix
# all urls with that
if settings.SETTINGS_MODULE == 'settings.heroku':
    urlpatterns = [path('django/', include(urlpatterns))]
