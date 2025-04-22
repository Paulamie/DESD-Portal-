from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone



# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)  # Hash password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(email, first_name, last_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="student_management_users",  # Fix conflict
        blank=True
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="student_management_users_permissions",  # Fix conflict
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def id(self):
        return self.user_id

class Community(models.Model):
    is_approved = models.BooleanField(default=False)
    community_id = models.AutoField(primary_key=True)
    com_leader = models.CharField(max_length=255)
    community_name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        db_table = "Community"

    def __str__(self):
        return self.community_name
    
class Interest(models.Model):
    interest_id = models.AutoField(primary_key=True)
    interest_name = models.CharField(max_length=100)

    class Meta:
        db_table = "Interest"

    def __str__(self):
        return self.interest_name


class Society(models.Model):
    society_id = models.AutoField(primary_key=True)
    soc_leader = models.CharField(max_length=255)
    society_name = models.CharField(max_length=100)
    society_location = models.CharField(max_length=255)
    description = models.TextField()
    event_info = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now) 
    interests = models.ManyToManyField('Interest', related_name='societies')



    class Meta:
        db_table = "Societies"

    def __str__(self):
        return self.society_name


class Event(models.Model):
    is_approved = models.BooleanField(default=False)
    event_id = models.AutoField(primary_key=True) 
    event_name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    info = models.TextField()
    community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, blank=True)
    society = models.ForeignKey(Society, on_delete=models.SET_NULL, null=True, blank=True)
    
    LOCATION_CHOICES = [
        ('Online', 'Online'),
        ('On-Campus', 'On-Campus'),
        ]
    location_type = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='On-Campus')
    actual_location = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "Event"

    def __str__(self):
        return f"{self.event_name} ({self.location_type})"

class EventDetails(models.Model):
    event_details_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_id')  
    class Meta:
        db_table = "event_details"
        
    def __str__(self):
        return self.event_details_id

    
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
        db_table= "CommunityRequest"

    def __str__(self):
        return self.community_name

from django.conf import settings
from django.db import models

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


class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, to_field='user_id')
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    content = models.TextField()
    visibility = models.CharField(max_length=10, choices=[('private', 'Private'), ('public', 'Public')], default='public')

    def __str__(self):
        return f"Post by {self.user.email} - {self.content[:30]}"
    






# class Club(models.Model):
# this is not needed it is the societies one 
#     name = models.CharField(max_length=100)
#     description = models.TextField()

#     def __str__(self):
#         return self.name


# class UserProfile(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     course = models.CharField(max_length=100, blank=True, null=True)
#     bio = models.TextField(blank=True, null=True)
#     profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
#     interests = models.ManyToManyField(Interest, blank=True) 
#     clubs = models.ManyToManyField(Club, blank=True) refer to the socieites model 
#     communities = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, blank=True)

#     def __str__(self):
#         return self.user.email


# class Friendship(models.Model):
#     id = models.AutoField(primary_key=True)
#     # user one foreign key and referenced it 
#     user = models.ForeignKey(User, on_delete=models.CASCADE,  to_field='user_id')
#     friends = models.ManyToManyField(use the model, related_name="friend_of")

#     def __str__(self):
#         return f"{self.user.email}'s friends"