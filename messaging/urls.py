from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.InboxView.as_view(), name='inbox'),
    path('start/<int:listing_id>/', views.StartConversationView.as_view(), name='start'),
    path('thread/<int:listing_id>/<int:other_user_id>/', views.ConversationThreadView.as_view(), name='thread'),
    path('thread/<int:listing_id>/<int:other_user_id>/poll/', views.PollMessagesView.as_view(), name='poll'),
]
