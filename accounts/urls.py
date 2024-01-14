from django.conf import settings
from django.urls import path
from .views import signup, user_login, dashboard, add_artwork, gallery, logout_view, user_gallery, \
    user_gallery_by_user, complete_profile, purchase, delete_artwork, add_to_favorites, favorites, \
    remove_from_favorites, admin_approval, admin_approve_artwork, admin_reject_artwork, manage_images, donate_us, \
    find_your_artists, artwork_detail, search_artists, like_artwork, manage_users, edit_artwork, change_password, \
    gift_artwork, add_comment, inbox, statistics,  participate_auction
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('add_artwork/', add_artwork, name='add_artwork'),
    path('', gallery, name='gallery'),
    path('logout/', logout_view, name='logout'),
    path('user_gallery/<int:user_id>/', user_gallery, name='user_gallery'),
    path('user_gallery/<str:username>/', user_gallery_by_user, name='user_gallery'),
    path('complete_profile/', complete_profile, name='complete_profile'),
    path('purchase/<int:artwork_id>/', purchase, name='purchase'),
    path('delete_artwork/<int:artwork_id>/', delete_artwork, name='delete_artwork'),
    path('add_to_favorites/', add_to_favorites, name='add_to_favorites'),
    path('favorites/', favorites, name='favorites'),
    path('remove_from_favorites/<int:favorite_id>/', remove_from_favorites, name='remove_from_favorites'),
    path('approval/', admin_approval, name='admin_approval'),
    path('approve/<int:artwork_id>/', admin_approve_artwork, name='admin_approve_artwork'),
    path('reject/<int:artwork_id>/', admin_reject_artwork, name='admin_reject_artwork'),
    path('approval/', manage_images, name='manage_images'),
    path('delete_artwork/<int:artwork_id>/', delete_artwork, name='delete_artwork'),
    path('donate_us/', donate_us, name='donate_us'),
    path('find_your_artist/', find_your_artists, name='find_your_artist'),
    path('artwork/<int:artwork_id>/', artwork_detail, name='artwork_detail'),
    path('search_artists/', search_artists, name='search_artists'),
    path('like_artwork/<int:artwork_id>/', like_artwork, name='like_artwork'),
    path('manage_users/', manage_users, name='manage_users'),
    path('edit_artwork/<int:artwork_id>/', edit_artwork, name='edit_artwork'),
    path('<int:user_id>/password/', change_password, name='change_password'),
    path('gift_artwork/<int:artwork_id>/', gift_artwork, name='gift_artwork'),
    path('add_comment/<int:artwork_id>/', add_comment, name='add_comment'),
    path('inbox/', inbox, name='inbox'),
    path('statistics/', statistics, name='statistics'),
    path('auction/participate/<int:artwork_id>/', participate_auction, name='participate_auction'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
