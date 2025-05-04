from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings

# === Custom User Manager ===
class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(email, first_name, last_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# === Custom User Model ===
class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    full_name = models.CharField(max_length=255, blank=True)
    course = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)

    # Friends system
    friends = models.ManyToManyField("self", symmetrical=True, blank=True)

    # Interests (used for friend/society matching)
    interests = models.ManyToManyField('Interest', blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="student_management_users",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="student_management_users_permissions",
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


    @property
    def id(self):
        return self.user_id



# === Interest ===
class Interest(models.Model):
    interest_id = models.AutoField(primary_key=True)
    interest_name = models.CharField(max_length=100)

    class Meta:
        db_table = "Interest"

    def __str__(self):
        return self.interest_name
# === Community ===
class Community(models.Model):
    is_approved = models.BooleanField(default=False)
    community_id = models.AutoField(primary_key=True)
    com_leader = models.CharField(max_length=255)
    community_name = models.CharField(max_length=100)
    description = models.TextField()
    purpose = models.TextField(blank=True, null=True)
    interests = models.ManyToManyField(Interest, blank=True) 

    class Meta:
        db_table = "Community"

    def __str__(self):
        return self.community_name
    
# === Society (with members + is_approved + is_featured) ===
class Society(models.Model):
    society_id = models.AutoField(primary_key=True)
    soc_leader = models.CharField(max_length=255)
    society_name = models.CharField(max_length=100)
    society_location = models.CharField(max_length=255)
    description = models.TextField()
    event_info = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    interests = models.ManyToManyField('Interest', related_name='societies')
    members = models.ManyToManyField(User, related_name='joined_societies', blank=True)

    class Meta:
        db_table = "Societies"

    def __str__(self):
        return self.society_name

class SocietyJoinRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    society = models.ForeignKey('Society', on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='reviewed_society_requests', on_delete=models.SET_NULL)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'society')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.society.society_name} ({self.status})"
    

    
# === Event ===
class Event(models.Model):
    is_approved = models.BooleanField(default=False)
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=100)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='event_requests'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    info = models.TextField()
    community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, blank=True)
    society = models.ForeignKey(Society, on_delete=models.SET_NULL, null=True, blank=True)
    required_materials= models.TextField(null=True, blank=True)

    LOCATION_CHOICES = [
        ('Online', 'Online'),
        ('On-Campus', 'On-Campus'),
    ]


    location_type = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='On-Campus')
    actual_location = models.CharField(max_length=255, blank=True, null=True)
    maximum_capacity = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = "Event"

    def __str__(self):
        return f"{self.event_name} ({self.location_type})"

# === EventDetails ===
class EventDetails(models.Model):
    event_details_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_id')
    can_book = models.BooleanField(default=True)


    class Meta:
        db_table = "event_details"

    def __str__(self):
        return str(self.event_details_id)

# === CommunityRequest ===
class CommunityRequest(models.Model):
    community_name = models.CharField(max_length=255)
    description = models.TextField()
    purpose = models.TextField()
    requester = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_id')
    interests = models.ManyToManyField(Interest)
    status = models.CharField(max_length=10, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, related_name='reviewed_requests', on_delete=models.SET_NULL)

    class Meta:
        db_table = "CommunityRequest"

    def __str__(self):
        return self.community_name

# === UpdateRequest ===
class UpdateRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='update_requests')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_update_requests')
    field_to_update = models.CharField(max_length=100)
    old_value = models.CharField(max_length=100, blank=True, null=True)
    new_value = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')])
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='update_requests/', null=True, blank=True)

    def __str__(self):
        return self.field_to_update

# === Post ===
class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_id')
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    content = models.TextField()
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends'),
        ('community', 'Community'),
        ('club', 'Club'),
        ('society', 'Society'),
    ]

    # ... other fields ...
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='public'
    )
   

    def __str__(self):
        return f"Post by {self.user.email} - {self.content[:30]}"
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} on Post {self.post.post_id}"


# === CommunityMembership ===
class CommunityMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'community')

    def __str__(self):
        return f"{self.user.get_full_name()} -> {self.community.community_name}"



class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50, 
        choices=[
            ('info', 'Info'), 
            ('success', 'Success'), 
            ('warning', 'Warning'), 
            ('error', 'Error')
        ],
        default='info'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.user.get_full_name()}: {self.message[:30]}'

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE, to_field='user_id')
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE, to_field='user_id')
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "FriendRequest"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.from_user.get_full_name()} ➤ {self.to_user.get_full_name()} ({self.status})"

class Friendship(models.Model):
    user = models.ForeignKey(User, related_name='friendships', on_delete=models.CASCADE, to_field='user_id')
    friend = models.ForeignKey(User, related_name='friends_with', on_delete=models.CASCADE, to_field='user_id')
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        db_table = "Friendship"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} ♥ {self.friend.get_full_name()}"
