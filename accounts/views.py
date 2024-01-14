from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from .forms import CustomAuthenticationForm, ArtworkForm, Artwork, UserProfileForm, UserProfileUpdateForm, \
    FavoriteArtForm, UsernameUpdateForm, PasswordChangeCustomForm, CommentForm, GiftArtworkForm

from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth.decorators import user_passes_test

from .models import UserProfile, FavoriteArt, InboxMessage


# This decorator checks if the user is an admin.
def admin_required(view_func):
    # The actual decorator using user_passes_test to verify if the user is active and a staff member.
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='login'
    )
    return actual_decorator(view_func)


# User login function
def user_login(request):
    if request.method == 'POST':
        # If the request method is POST, create a custom authentication form with the submitted data.
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # If the form is valid, extract the username and password from the cleaned data.
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Authenticate the user using the provided username and password.
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # If authentication is successful, log in the user and redirect to the dashboard.
                login(request, user)
                return redirect('dashboard')
            else:
                # If authentication fails, display an error message.
                messages.error(request, 'Your password or your username is not correct!')
    else:
        # If the request method is not POST, create an instance of the custom authentication form.
        form = CustomAuthenticationForm()

    # Render the login.html template with the form.
    return render(request, 'login.html', {'form': form})


# Custom user creation form inheriting from UserCreationForm
class CustomUserCreationForm(UserCreationForm):
    # Optional age field
    age = forms.IntegerField(required=False)

# User signup function
def signup(request):
    try:
        if request.method == 'POST':
            # If the request method is POST, create a UserCreationForm instance with the submitted data.
            form = UserCreationForm(request.POST)
            if form.is_valid():
                # If the form is valid, save the user and create a UserProfile if one doesn't exist.
                user = form.save()

                existing_profile = UserProfile.objects.filter(user=user)
                if not existing_profile:
                    UserProfile.objects.create(
                        user=user,
                    )

                return redirect('login')
            else:
                # If the form is not valid, extract and display errors.
                errors = form.errors.get_json_data()
                for field, field_errors in errors.items():
                    for error in field_errors:
                        messages.error(request, f'{field}: {error["message"]}')
        else:
            # If the request method is not POST, create an instance of the custom user creation form.
            form = CustomUserCreationForm()
        return render(request, 'signup.html', {'form': form})
    except Exception:
        # Redirect to login in case of an exception.
        return redirect('login')



# Dashboard view requiring user authentication
@login_required(login_url='login')
def dashboard(request):
    # Retrieve received messages for the logged-in user and order them by creation time.
    received_messages = InboxMessage.objects.filter(receiver=request.user).order_by('-created_at')

    # Check if there are any unread messages.
    has_unread_messages = any(not message.is_read for message in received_messages)

    # Determine if all messages are read.
    messages_are_read = not has_unread_messages

    # Retrieve the user profile for the logged-in user.
    user_profile = UserProfile.objects.get(user=request.user)

    # Check if the user is authenticated and provide the username and complete profile link accordingly.
    if request.user.is_authenticated:
        username = request.user.username
        complete_profile_link = reverse('complete_profile')
    else:
        # Display a warning message if the user is not logged in.
        messages.warning(request, 'you are not logged in')
        complete_profile_link = None

    # Render the dashboard.html template with relevant data.
    return render(request, 'dashboard.html',
                  {'complete_profile_link': complete_profile_link, 'user_profile': user_profile,
                   'has_unread_messages': has_unread_messages, 'messages_are_read': messages_are_read})



# Function to add a label to an uploaded image
def add_label_to_uploaded_image(uploaded_image, label_text):
    # Open the uploaded image using the PIL library
    image = Image.open(uploaded_image)

    # Create a drawing object for the image
    draw = ImageDraw.Draw(image)

    # Calculate the bounding box of the text to be added
    text_bbox = draw.textbbox((0, 0), label_text)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    # Calculate the position to place the text at the bottom center of the image
    text_position = ((image.width - text_width) // 2, image.height - text_height - 10)

    # Add the label text to the image
    draw.text(text_position, label_text, (255, 255, 255))

    # Save the final image
    image.save(uploaded_image.path)


# View to add artwork, requiring user authentication
@login_required(login_url='login')
def add_artwork(request):
    if request.method == 'POST':
        # If the request method is POST, create an ArtworkForm instance with the submitted data.
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            # If the form is valid, save the artwork with the logged-in user as the uploader.
            artwork = form.save(commit=False)
            artwork.uploaded_by = request.user
            artwork.save()

            # Extract the label text from the form and add it to the uploaded image.
            label_text = form.cleaned_data['label_text']
            add_label_to_uploaded_image(artwork.image, label_text)

            # Redirect to the gallery page after successfully adding artwork.
            return redirect('gallery')
    else:
        # If the request method is not POST, create an instance of the ArtworkForm.
        form = ArtworkForm()

    # Render the add_artwork.html template with the form.
    return render(request, 'add_artwork.html', {'form': form})




# View for displaying artworks in the gallery
def gallery(request):
    # Get the search query from the request parameters
    search_query = request.GET.get('search', '')

    # Filter artworks based on the title containing the search query and approved status, then order by likes
    artworks = Artwork.objects.filter(Q(title__icontains=search_query), approved=True).order_by('-likes')

    # Count the total number of users
    total_users = User.objects.count()

    # Number of artworks to display per page
    artworks_per_page = 10

    # Create a paginator for the artworks
    paginator = Paginator(artworks, artworks_per_page)

    # Get the requested page number from the request parameters
    page = request.GET.get('page', 1)

    try:
        # Get the artworks for the specified page
        artworks = paginator.page(page)
    except PageNotAnInteger:
        # If the page number is not an integer, display the first page
        artworks = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, display the last page
        artworks = paginator.page(paginator.num_pages)

    # Render the gallery.html template with the artworks and relevant information
    return render(request, 'gallery.html',
                  {'artworks': artworks, 'search_query': search_query, 'total_users': total_users})


# View to add artwork to favorites, requiring user authentication
@login_required(login_url='login')
def add_to_favorites(request):
    if request.method == 'POST':
        # If the request method is POST, create a FavoriteArtForm instance with the submitted data.
        form = FavoriteArtForm(request.POST)
        if form.is_valid():
            # If the form is valid, extract the artwork ID and create a FavoriteArt object for the user.
            artwork_id = form.cleaned_data['artwork_id']
            FavoriteArt.objects.create(user=request.user, artwork_id=artwork_id)
    # Redirect to the gallery page after adding artwork to favorites.
    return redirect('gallery')


# View to log out the user
def logout_view(request):
    # Log out the user and redirect to the login page
    logout(request)
    return redirect('login')

# View to display the gallery of a specific user by user ID
def user_gallery(request, user_id):
    user_gallery_owner = get_object_or_404(User, pk=user_id)
    artworks = Artwork.objects.filter(uploaded_by=user_gallery_owner, approved=True)

    # Check if the current user is the owner of the gallery
    is_gallery_owner = request.user == user_gallery_owner

    return render(request, 'user_gallery.html', {'artworks': artworks, 'is_gallery_owner': is_gallery_owner})


# View to display the gallery of a specific user by username
def user_gallery_by_user(request, username):
    user = get_object_or_404(User, username=username)
    artworks = Artwork.objects.filter(uploaded_by=user)
    return render(request, 'user_gallery.html', {'artworks': artworks, 'user': user})


# View to complete the user profile, requiring user authentication
@login_required(login_url='login')
def complete_profile(request):
    # Create a user profile if it doesn't exist for the current user
    if not hasattr(request.user, 'userprofile'):
        UserProfile.objects.create(user=request.user)

    # Create instances of UserProfileForm and UsernameUpdateForm
    user_profile_form = UserProfileForm(request.POST or None, instance=request.user.userprofile)
    username_update_form = UsernameUpdateForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        # If the request method is POST and both forms are valid, save the forms and redirect to the dashboard
        if user_profile_form.is_valid() and username_update_form.is_valid():
            user_profile_form.save()
            username_update_form.save()
            return redirect('dashboard')
    else:
        # If the request method is not POST, create an instance of UserProfileForm.
        form = UserProfileForm(instance=request.user.userprofile)

    # Render the complete_profile.html template with the forms.
    return render(request, 'complete_profile.html', {
        'user_profile_form': user_profile_form,
        'username_update_form': username_update_form,
    })
# View for purchasing artwork, requiring user authentication
def purchase(request, artwork_id):
    if request.user.is_authenticated:
        artwork = get_object_or_404(Artwork, id=artwork_id)

        # Prepare context data for rendering the purchase.html template
        context = {
            'artwork': artwork,
            'user_nickname': request.user.username,
            'user_telegram_id': request.user.userprofile.telegramID,
            'digital_wallet_address': request.user.userprofile.digital_wallet_address,
        }

        # Render the purchase.html template with the context data
        return render(request, 'purchase.html', context)
    else:
        # If the user is not authenticated, redirect to the login page
        return redirect('login')


# View to delete artwork, requiring user authentication
@login_required(login_url='login')
def delete_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)

    # Check if the logged-in user is the owner of the artwork
    if artwork.uploaded_by == request.user:
        artwork.delete()

    # Redirect to the user's gallery page after deleting the artwork
    return redirect('user_gallery', user_id=request.user.id)


# View to display user's favorite artworks, requiring user authentication
@login_required(login_url='login')
def favorites(request):
    # Get the favorite artworks for the logged-in user
    favorites = FavoriteArt.objects.filter(user=request.user)

    # Render the favorites.html template with the favorite artworks
    return render(request, 'favorites.html', {'favorites': favorites})

# View to remove an artwork from favorites, requiring user authentication
@login_required(login_url='login')
def remove_from_favorites(request, favorite_id):
    try:
        # Attempt to get the FavoriteArt object with the given ID
        favorite = FavoriteArt.objects.get(id=favorite_id)
        # Delete the favorite artwork
        favorite.delete()
        messages.success(request, 'Image deleted')
    except FavoriteArt.DoesNotExist:
        messages.error(request, 'Image not found')

    # Redirect to the favorites page
    return redirect('favorites')


# View for admin approval of artworks, requiring admin privileges
@admin_required
def admin_approval(request):
    # Get artworks that are not yet approved
    artworks_to_approve = Artwork.objects.filter(approved=False)

    if request.method == 'POST':
        # Check if the 'approve_btn' or 'reject_btn' is in the POST data
        if 'approve_btn' in request.POST:
            artwork_id = int(request.POST['approve_btn'])
            artwork = get_object_or_404(Artwork, id=artwork_id)
            artwork.approved = True
            artwork.save()

        elif 'reject_btn' in request.POST:
            artwork_id = int(request.POST['reject_btn'])
            artwork = get_object_or_404(Artwork, id=artwork_id)
            artwork.delete()  # Delete the artwork from the database

    # Render the approval.html template with artworks to approve
    return render(request, 'approval.html', {'artworks_to_approve': artworks_to_approve})


# View to approve artwork by admin, requiring admin privileges
@admin_required
def admin_approve_artwork(request, artwork_id):
    # Get the artwork with the given ID that is not yet approved
    artwork = get_object_or_404(Artwork, id=artwork_id, approved=False)

    # Approve the artwork
    artwork.approved = True
    artwork.save()

    # Redirect to the admin approval page
    return redirect('admin_approval')

# View to reject artwork by admin, requiring admin privileges
@admin_required
def admin_reject_artwork(request, artwork_id):
    # Get the artwork with the given ID
    artwork = get_object_or_404(Artwork, id=artwork_id)
    # Delete the artwork
    artwork.delete()
    # Redirect to the admin approval page
    return redirect('admin_approval')


# View to manage images, requiring admin privileges
@admin_required
def manage_images(request):
    # Check if the user is not an admin
    if not request.user.is_staff:
        # Render the access_denied.html template for non-admin users
        return render(request, 'access_denied.html')

    # Get all artworks
    all_artworks = Artwork.objects.all()

    # Render the approval.html template with all artworks
    return render(request, 'approval.html', {'all_artworks': all_artworks})


# View to delete artwork, requiring user authentication
@login_required
def delete_artwork(request, artwork_id):
    # Get the artwork with the given ID
    artwork = get_object_or_404(Artwork, id=artwork_id)

    # Check if the user is not an admin
    if not request.user.is_staff:
        # Redirect to the gallery page for non-admin users
        return redirect('gallery')

    # Delete the artwork
    artwork.delete()

    # Redirect to the gallery page
    return redirect('gallery')
# View to render the donate_us.html template
def donate_us(request):
    return render(request, 'donate_us.html')


# View to find artists, requiring user authentication
@login_required(login_url='login')
def find_your_artists(request):
    # Get all user profiles
    user_profiles = UserProfile.objects.all()

    # List to store users with their associated artworks
    users_with_artworks = []

    # Iterate over user profiles
    for user_profile in user_profiles:
        # Get artworks uploaded by the user
        artworks = Artwork.objects.filter(uploaded_by=user_profile.user)

        # Append user profile and artworks to the list
        users_with_artworks.append({'user_profile': user_profile, 'artworks': artworks})

    # Render the your_artists_page.html template with the list of users and artworks
    return render(request, 'your_artists_page.html', {'users_with_artworks': users_with_artworks})


# View to display details of a specific artwork
def artwork_detail(request, artwork_id):
    # Get the artwork with the given ID
    artwork = get_object_or_404(Artwork, id=artwork_id)

    # Context containing the artwork
    context = {'artwork': artwork}

    # Render the artwork_detail.html template with the artwork details
    return render(request, 'artwork_detail.html', context)

# View to search for artists based on a query
def search_artists(request):
    # Get the search query from the request's GET parameters
    search_query = request.GET.get('search_query', '')

    # Find users whose usernames contain the search query
    matching_users = User.objects.filter(username__icontains=search_query)

    # List to store users with their associated artworks
    users_with_artworks = []

    # Iterate over matching users
    for user in matching_users:
        # Get the user profile associated with the user
        user_profile = UserProfile.objects.get(user=user)

        # Get artworks uploaded by the user
        artworks = Artwork.objects.filter(uploaded_by=user)

        # Append user profile and artworks to the list
        users_with_artworks.append({'user_profile': user_profile, 'artworks': artworks})

    # Render the your_artists_page.html template with the list of users and artworks
    return render(request, 'your_artists_page.html',
                  {'users_with_artworks': users_with_artworks, 'search_query': search_query})


# View to like an artwork, requiring user authentication
@login_required(login_url='login')
def like_artwork(request, artwork_id):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Get the artwork with the given ID
        artwork = get_object_or_404(Artwork, id=artwork_id)

        # Check if the user has not already liked the artwork
        if not FavoriteArt.objects.filter(user=request.user, artwork=artwork).exists():
            # Increment the likes count of the artwork
            artwork.likes += 1
            artwork.save()

            # Create a FavoriteArt object to represent the user's like
            FavoriteArt.objects.create(user=request.user, artwork=artwork)

            # Create a notification message for the artwork owner
            like_user = request.user
            message_content = f'Your artwork "{artwork.title}" has been liked by {like_user.username}.'
            InboxMessage.objects.create(sender=like_user, receiver=artwork.uploaded_by, content=message_content)

        # Redirect to the gallery page
        return redirect('gallery')
    else:
        # Redirect to the signup page if the user is not authenticated
        return redirect('signup')


# View to manage users, requiring admin privileges
@admin_required
def manage_users(request):
    # Get all users
    users = User.objects.all()

    # Render the manage_users.html template with the list of users
    return render(request, 'manage_users.html', {'users': users})


# View to edit an artwork, requiring user authentication
@login_required(login_url='login')
def edit_artwork(request, artwork_id):
    # Get the artwork with the given ID
    artwork = get_object_or_404(Artwork, id=artwork_id)

    # Check if the request method is POST
    if request.method == 'POST':
        # Create an ArtworkForm instance with the POST data and the artwork instance
        form = ArtworkForm(request.POST, instance=artwork)

        # Check if the form is valid
        if form.is_valid():
            # Save the artwork with the updated information
            artwork = form.save(commit=False)
            artwork.approved = False
            artwork.save()

            # Redirect to the gallery page
            return redirect('gallery')
    else:
        # If the request method is not POST, create an ArtworkForm instance with the artwork instance
        form = ArtworkForm(instance=artwork)

    # Render the edit_artwork.html template with the artwork and the form
    return render(request, 'edit_artwork.html', {'artwork': artwork, 'form': form})


# View to change the password, requiring user authentication
@login_required(login_url='login')
def change_password(request, user_id):
    # Get the user with the given ID
    user = get_object_or_404(User, pk=user_id)

    # Check if the authenticated user is the owner of the profile
    if request.user != user:
        # Render an error page if the user does not have permission to change this password
        return render(request, 'error.html', {'error_message': 'You do not have permission to change this password.'})

    # Check if the request method is POST
    if request.method == 'POST':
        # Create a PasswordChangeCustomForm instance with the POST data and the user instance
        password_change_form = PasswordChangeCustomForm(user, request.POST)

        # Check if the form is valid
        if password_change_form.is_valid():
            # Save the user with the updated password
            user = password_change_form.save()

            # Update the session authentication hash
            update_session_auth_hash(request, user)

            # Display a success message
            messages.success(request, 'Password has been changed successfully.')

            # Redirect to the profile page
            return redirect('profile')
    else:
        # If the request method is not POST, create a PasswordChangeCustomForm instance with the user instance
        password_change_form = PasswordChangeCustomForm(user)

    # Render the change_password.html template with the password_change_form
    return render(request, 'change_password.html', {'password_change_form': password_change_form})


# View to gift an artwork, requiring user authentication
@login_required()
def gift_artwork(request, artwork_id):
    # Get the artwork with the given ID
    artwork = get_object_or_404(Artwork, id=artwork_id)

    # Check if the request method is POST
    if request.method == 'POST':
        # Create a GiftArtworkForm instance with the POST data
        form = GiftArtworkForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Get the authenticated user
            user_gift = request.user

            # Get the recipient from the form
            recipient = form.cleaned_data['recipient']

            # Create a new Artwork instance with the same information as the original artwork
            original_artwork = Artwork(
                title=artwork.title,
                description=artwork.description,
                price=artwork.price,
                image=artwork.image,
                uploaded_by=recipient,
                approved=artwork.approved,
                likes=artwork.likes
            )

            # Create a message content for the inbox
            message_content = f'{artwork.title}" by {user_gift.username} gifted to you!'

            # Create an InboxMessage instance for the recipient
            InboxMessage.objects.create(sender=user_gift, receiver=recipient, content=message_content)

            # Save the new artwork instance
            original_artwork.save()

            # Create a FavoriteArt instance for the recipient
            favorite_art = FavoriteArt.objects.create(user=recipient, artwork=original_artwork)

            # Delete the original artwork
            artwork.delete()

            # Redirect to the gallery page
            return redirect('gallery')
    else:
        # If the request method is not POST, create a GiftArtworkForm instance
        form = GiftArtworkForm()

    # Render the gift_artwork.html template with the form and the artwork
    return render(request, 'gift_artwork.html', {'form': form, 'artwork': artwork})


# View to add a comment to an artwork, requiring user authentication
@login_required
def add_comment(request, artwork_id):
    # Get the artwork with the given ID
    artwork = get_object_or_404(Artwork, id=artwork_id)

    # Check if the request method is POST
    if request.method == 'POST':
        # Create a CommentForm instance with the POST data
        form = CommentForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Get the authenticated user
            comment_user = request.user

            # Create a new comment instance
            comment = form.save(commit=False)
            comment.user = request.user
            comment.artwork = artwork
            comment.save()

            # Add the comment to the artwork's comments
            artwork.comments.add(comment)

            # Create a message content for the inbox
            message_content = f'A new comment has been posted for the artwork "{artwork.title}" by {comment_user.username}.'

            # Create an InboxMessage instance for the artwork owner
            InboxMessage.objects.create(sender=comment_user, receiver=artwork.uploaded_by, content=message_content)

            # Redirect to the add_comment page for the same artwork
            return redirect('add_comment', artwork_id=artwork.id)
    else:
        # If the request method is not POST, create a CommentForm instance
        form = CommentForm()

    # Render the add_comment.html template with the form and the artwork
    return render(request, 'add_comment.html', {'form': form, 'artwork': artwork})


# View to display the inbox messages, requiring user authentication
@login_required
def inbox(request):
    # Get the received messages for the authenticated user
    received_messages = InboxMessage.objects.filter(receiver=request.user).order_by('-created_at')

    # Mark all messages as read
    for message in received_messages:
        message.is_read = True
        message.save()

    # Create a context with the received messages
    context = {'received_messages': received_messages}

    # Render the inbox.html template with the context
    return render(request, 'inbox.html', context)

# Admin view to display site statistics, requiring admin privileges
@admin_required
def statistics(request):
    # Gather site statistics
    site_statistics = {
        'total_users': User.objects.count(),
        'total_artworks': Artwork.objects.count(),
        'total_artistic_value': Artwork.objects.aggregate(Sum('price'))['price__sum'] or 0,
    }

    # Gather information about artists
    artists_info = []
    artists = User.objects.filter(uploaded_by_artworks__isnull=False).distinct()
    for artist in artists:
        total_value = Artwork.objects.filter(uploaded_by=artist).aggregate(Sum('price'))['price__sum'] or 0
        artists_info.append({
            'artist_name': f'{artist.username}',
            'total_artistic_value': total_value,
        })

    # Render the statistics.html template with the gathered information
    return render(request, 'statistics.html', {'site_statistics': site_statistics, 'artists_info': artists_info})


# View to allow users to participate in an auction for a specific artwork
def participate_auction(request, artwork_id):
    # Get the artwork with the given ID
    artwork = get_object_or_404(Artwork, id=artwork_id)

    # Check if the request method is POST
    if request.method == 'POST':
        # Get the user making the offer
        user_offer = request.user

        # Get the bid amount from the POST data
        bid_amount = request.POST.get('bid_amount')

        # Get the current highest bid amount for the artwork
        auction_price = request.POST.get('auction_price', 0)

        # Check if the bid amount is a valid digit and higher than the current bid
        if bid_amount.isdigit() and int(bid_amount) > artwork.current_bid_amount:
            # Get the current highest bidder
            current_highest_bidder = artwork.current_highest_bidder

            # Update the artwork's bid information
            artwork.current_bid_amount = int(bid_amount)
            artwork.current_highest_bidder = request.user
            artwork.save()

            # Create a message content for the inbox
            message_content = f'"{artwork.title}" by {user_offer.username} has been priced at {artwork.current_bid_amount} dollars in the auction!'

            # Create an InboxMessage instance for the artwork owner
            InboxMessage.objects.create(sender=user_offer, receiver=artwork.uploaded_by, content=message_content)

            # Display a success message
            messages.success(request, 'Your bid has been successfully submitted.')

            # Redirect to the participate_auction page for the same artwork
            return redirect('participate_auction', artwork_id=artwork.id)
        else:
            # Display an error message if the bid amount is not valid or less than the current amount
            messages.error(request, 'The bid amount is not valid or less than the current amount.')

    # Render the participate_auction.html template with the artwork
    return render(request, 'participate_auction.html', {'artwork': artwork})
