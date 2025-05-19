from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("list_new", views.list_new, name="list_new"),
    path("listing/<int:item_id>", views.listing, name="listing"),
    path("listing/<int:item_id>/watchlist/", views.toggle_watchlist, name="toggle_watchlist"),
    path("mywatchlist", views.mywatchlist,name="mywatchlist"),
    path("listing/<int:item_id>/bidding", views.bidding, name="bidding"),
    path("listing/<int:item_id>/close_deal", views.close_deal, name="close_deal"),
    path("sold/",views.sold, name ="sold"),
    path("won/",views.won, name ="won"),
    path("listing/<int:item_id>/comment", views.comment, name="comment"),
    path("category/<str:category_name>", views.category, name="category")
]
