from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    CATEGORY_CHOICES = [
        ('fashion', 'Fashion'),
        ('home', 'Home'),
        ('electronics', 'Electronics'),
        ('books', 'Books'),
        ('toys', 'Toys'),
        ('beauty', 'Beauty')
    ]
    
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=20, decimal_places=2)
    image = models.ImageField(upload_to='listing_images/', blank=True, null=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True
    )
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing_items")
    is_closed = models.BooleanField(default = False)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="won_auctions")

    @property
    def winning_bid(self):
        return self.bid_items.order_by('-price').first

    def __str__(self):
        return f"{self.title}"

class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlisted_by")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlist_items")
    
    class Meta:
        unique_together=('user', 'item')
    
    def __str__(self):
        return f"{self.user} added {self.item} to watchlist"

class Bid(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid_items")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    price = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} bid ${self.price} for {self.item.title} "

class Comment(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented: {self.comment}"


