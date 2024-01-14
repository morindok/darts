# در فایل models.py
from django.db import models
from django.contrib.auth.models import User, AbstractUser, Permission, Group
from django.db import models
from django.urls import reverse
from django.utils import timezone

# models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    national_code = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telegramID = models.CharField(max_length=30, null=True, blank=True)
    digital_wallet_address = models.CharField(max_length=250, null=True, blank=True)
    total_artistic_value = models.PositiveIntegerField(default=0, verbose_name='ارزش هنری کل')

    def calculate_artistic_value(self):
        # محاسبه ارزش هنری بر اساس آثار هنری کاربر
        artworks = Artwork.objects.filter(uploaded_by=self.user, approved=True)
        total_value = sum(artwork.price for artwork in artworks)
        return total_value



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Artwork(models.Model):
    title = models.CharField(max_length=35)
    description = models.TextField(max_length=100)
    price = models.PositiveIntegerField(default=0, max_length=10000000)
    image = models.ImageField(upload_to='public_html/media')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_by_artworks')
    approved = models.BooleanField(default=False)
    likes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name='liked_artworks', blank=True)
    comments = models.ManyToManyField(Comment, related_name='artwork_comments')
    current_bid_amount = models.PositiveIntegerField(default=0, verbose_name='مبلغ فعلی مزایده')
    current_highest_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='current_highest_bidder_artworks')


    def __str__(self):
        return self.title


def user_directory_path(instance, filename):
    # Upload to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.id}/{filename}'


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to=user_directory_path, null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='customuser_set',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name='customuser_set',
    )


# models.py


class FavoriteArt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class InboxMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    related_artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, null=True, blank=True,default='')
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender.username} to {self.receiver.username} - {self.created_at}'
