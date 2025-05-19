from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from decimal import Decimal

from .models import User, Listing, WatchList, Bid, Comment

class NewListingForm(forms.Form):
    title = forms.CharField(
        max_length=64,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder':'Enter the name of your item'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows':2,
            'placeholder':'Enter description of your item'
        })
    )
    starting_bid = forms.DecimalField(
        max_digits=20, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class':'form-control',
            'min':0
        })
    )
    image = forms.ImageField(
        required=False
    )
    category = forms.ChoiceField(
        required=False,
        choices=[('','Select a category(optional)')] + Listing.CATEGORY_CHOICES
    )

class BidForm(forms.Form):
    price = forms.DecimalField(
        max_digits=20,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class':'form-control',
            'min':0
        })
    )

class CommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows':3,
            'placeholder':'Please enter your comment here.'
        })
    )

def index(request):
    active_listings = Listing.objects.filter(is_closed=False)
    categories = Listing.objects.filter(is_closed=False).exclude(category__isnull=True).exclude(category="").values_list('category', flat=True).distinct()

    return render(request, "auctions/index.html", {
        "active_listings":active_listings,
        "categories":categories
    })

def category(request, category_name):
    active_listings = Listing.objects.filter(is_closed=False, category=category_name)
    categories = Listing.objects.filter(is_closed=False).exclude(category__isnull=True).exclude(category="").values_list('category', flat=True).distinct()
    return render(request, "auctions/index.html", {
        "active_listings":active_listings,
        "categories":categories
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def list_new(request):
    if request.method == "POST":
        form = NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = Listing(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                starting_bid=form.cleaned_data["starting_bid"],
                image=form.cleaned_data["image"],
                category=form.cleaned_data["category"],
                seller=request.user
            )
            listing.save()
            return HttpResponseRedirect(reverse("index"))
 
    else:
        new_list_form = NewListingForm()
        return render(request, "auctions/list_new.html",{
        "new_list_form":new_list_form
    })

@login_required
def listing(request,item_id):
    item = Listing.objects.get(pk=item_id)
    user = request.user
    in_watchlist = WatchList.objects.filter(user=user,item=item).exists()
    comments = Comment.objects.filter(item=item)
    if Bid.objects.filter(item = item).exists():
        bid_price = Bid.objects.filter(item=item).order_by('-price').first()
    else:
        bid_price=item.starting_bid
    
    if item.is_closed and user == item.winner:
        return render(request, "auctions/listing.html", {
            "item":item,
            "message":"You won the bid.",
            "comments":comments
        })
    elif item.is_closed:
        return render(request,"auctions/listing.html", {
            "item":item,
            "message":"Item Sold",
            "comments":comments
        })

    bidform = BidForm()
    commentform = CommentForm()
    return render(request, "auctions/listing.html",{
        "item":item,
        "in_watchlist":in_watchlist,
        "bidform" : bidform,
        "bid_price":bid_price,
        "commentform":commentform,
        "comments":comments
    })

@login_required
def toggle_watchlist(request, item_id):
    if request.method == "POST":
        user = request.user
        item = Listing.objects.get(pk = item_id)
        watch, created = WatchList.objects.get_or_create(user=user, item=item)
        if not created:
            watch.delete()
        return HttpResponseRedirect(reverse("index"))


@login_required
def mywatchlist(request):
    watch_items = WatchList.objects.filter(user = request.user)
    return render(request, "auctions/mywatchlist.html", {
        "watch_items":watch_items
    })

@login_required
def bidding(request, item_id):
    if request.method == "POST":
        user = request.user
        item = Listing.objects.get(pk = item_id)
        bid_price = Decimal(request.POST["price"])
        in_watchlist = WatchList.objects.filter(user=user,item=item).exists()
        bidform = BidForm()
        if Bid.objects.filter(item = item).exists():
            current_price = Bid.objects.filter(item=item).order_by('-price').first().price
            if bid_price <= current_price:
                return render(request, "auctions/listing.html", {
                    "item":item,
                    "in_watchlist":in_watchlist,
                    "bidform" : bidform,
                    "bid_price":current_price,
                    "message":"Bid price must be higher than current price."
                })
        else:
            if bid_price < item.starting_bid:
                return render(request, "auctions/listing.html", {
                    "item":item,
                    "in_watchlist":in_watchlist,
                    "bidform" : bidform,
                    "bid_price":item.starting_bid,
                    "message":"Bid price can't be lower than starting bid price."
                })
        Bid.objects.create(item=item, user=user, price=bid_price)
        return HttpResponseRedirect(reverse("listing", args=[item_id]))

@login_required
def close_deal(request, item_id):
    if request.method == "POST":
        user = request.user
        item = Listing.objects.get(pk = item_id)
        if Bid.objects.filter(item=item).exists():
            winner = Bid.objects.filter(item=item).order_by('-price').first().user
            item.is_closed = True
            item.winner = winner
            item.save()
            return render(request,"auctions/sold.html", {
            "item":item
            })
        else:
            in_watchlist = WatchList.objects.filter(user=user,item=item).exists()
            bid_price=item.starting_bid

            bidform = BidForm()
            return render(request, "auctions/listing.html", {
                "item":item,
                "in_watchlist":in_watchlist,
                "bidform" : bidform,
                "bid_price":bid_price,
                "message":"No one placed a bid yet."
            })

@login_required
def sold(request):
    user=request.user
    sold_items = Listing.objects.filter(seller=user, is_closed=True)
    return render(request,"auctions/sold.html",{
        "sold_items":sold_items
    })

@login_required
def won(request):
    user = request.user
    won_items = Listing.objects.filter(winner=user, is_closed=True)
    return render(request,"auctions/won.html", {
        "won_items":won_items
    })

@login_required
def comment(request, item_id):
    if request.method == "POST":
        user = request.user
        item = Listing.objects.get(pk = item_id)
        comment = request.POST["comment"]
        Comment.objects.create(user=user,item=item,comment=comment)
        return HttpResponseRedirect(reverse("listing", args=[item_id]))


