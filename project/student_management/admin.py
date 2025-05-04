from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.contrib import messages
from .models import CommunityRequest, Event, Community, Society, Interest, UpdateRequest, CommunityMembership
from django.core.files.base import ContentFile
from .models import SocietyJoinRequest
from .models import Notification
import os
from .models import Comment

# Helper function for creating notifications in admin
def create_notification(user, message, notification_type='info'):
    Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
    )


def approve_community_request(modeladmin, request, queryset):
    for req in queryset:
        req.status = 'approved'
        req.reviewed_at = timezone.now()
        req.reviewed_by = request.user
        req.save()

        # Only create if a Community doesn't already exist
        if not Community.objects.filter(community_name=req.community_name).exists():
            Community.objects.create(
                community_name=req.community_name,
                description=req.description,
                purpose=req.purpose,
                com_leader=req.requester.get_full_name(),
                is_approved=True
            )

        create_notification(req.requester, f"Your community request for '{req.community_name}' has been approved!", 'error')


    modeladmin.message_user(request, "✅ Selected community requests were approved and communities created.", messages.SUCCESS)



def reject_community_request(modeladmin, request, queryset):
    queryset.update(status='rejected', reviewed_at=timezone.now(), reviewed_by=request.user)

    # Create a notification for the user
    for req in queryset:

        create_notification(req.requester, f"Your community request for '{req.community_name}' has been rejected.", 'success')

        
    modeladmin.message_user(request, "❌ Selected community requests were rejected.", messages.ERROR)



approve_community_request.short_description = "Approve selected requests"
reject_community_request.short_description = "Reject selected requests"

# CommunityRequest Admin Configuration
class CommunityRequestAdmin(admin.ModelAdmin):
    list_display = ('community_name', 'requester', 'status', 'created_at', 'reviewed_at')
    actions = [approve_community_request, reject_community_request]  # Add actions here

# Register the model
admin.site.register(CommunityRequest, CommunityRequestAdmin)

# Community Admin Configuration
@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('community_name', 'com_leader', 'is_approved')
    search_fields = ('community_name',)

# Event Admin Configuration

def approve_event_request(modeladmin, request, queryset):
    for event in queryset:
        event.is_approved = True
        event.save()

        if hasattr(event, 'requester') and event.requester:
            create_notification(event.requester, f"Your event '{event.event_name}' has been approved!", 'success')

    modeladmin.message_user(request, "✅ Selected events approved.", messages.SUCCESS)

def reject_event_request(modeladmin, request, queryset):
    for event in queryset:
        event.is_approved = False
        event.save()

        if hasattr(event, 'requester') and event.requester:
            create_notification(event.requester, f"Your event '{event.event_name}' has been rejected.", 'error')

    modeladmin.message_user(request, "❌ Selected events rejected.", messages.ERROR)

approve_event_request.short_description = "Approve selected events"
reject_event_request.short_description = "Reject selected events"

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'start_time', 'end_time', 'location_type', 'is_approved')
    search_fields = ('event_name',)
    actions = [approve_event_request, reject_event_request]

# Society Admin Configuration
@admin.register(Society)
class SocietyAdmin(admin.ModelAdmin):
    list_display = ('society_name', 'soc_leader', 'society_location')
    search_fields = ('society_name',)

# Interest Admin Configuration
@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('interest_name',)


def approve_update_request(modeladmin, request, queryset):
    for obj in queryset:
        obj.status = 'approved'
        obj.reviewed_at = timezone.now()
        obj.reviewed_by = request.user

        user = obj.user
        field = obj.field_to_update.lower()

        try:
            if field == 'name':
                parts = obj.new_value.strip().split(' ', 1)
                user.first_name = parts[0]
                user.last_name = parts[1] if len(parts) > 1 else ''
            elif field == 'course':
                user.course = obj.new_value
            elif field == 'bio':
                user.bio = obj.new_value
            elif field == 'date_of_birth':
                from datetime import datetime
                try:
                    user.date_of_birth = datetime.strptime(obj.new_value, "%Y-%m-%d").date()
                except ValueError:
                    messages.error(request, f"Invalid date format for {user.email}. Use YYYY-MM-DD.")
                    continue
            elif field == 'gender':
                user.gender = obj.new_value
            elif field == 'facebook':
                user.facebook = obj.new_value
            elif field == 'twitter':
                user.twitter = obj.new_value
            elif field == 'instagram':
                user.instagram = obj.new_value
            elif field == 'profile_picture' and obj.profile_picture:
                filename = os.path.basename(obj.profile_picture.name)
                obj.profile_picture.open()
                user.profile_picture.save(
                    filename,
                    ContentFile(obj.profile_picture.read()),
                    save=True
                )
            else:
                continue  # skip unknown fields

            user.save()
            obj.save()

            create_notification(
                user,
                f"Your profile update request for '{obj.field_to_update}' has been approved!",
                'success'
            )

        except Exception as e:
            messages.error(request, f"❌ Failed to apply update for {user.email}: {str(e)}")

    modeladmin.message_user(request, "✅ Selected profile updates were approved.", messages.SUCCESS)




def reject_update_request(modeladmin, request, queryset):
    queryset.update(status='rejected', reviewed_at=timezone.now(), reviewed_by=request.user)

    # Create a notification for the user
    for obj in queryset:

        create_notification(obj.user, f"Your profile update request for '{obj.field_to_update}' has been rejected.", 'error')


        

    modeladmin.message_user(request, "❌ Selected profile updates were rejected.", messages.ERROR)



approve_update_request.short_description = "Approve selected update requests"
reject_update_request.short_description = "Reject selected update requests"


@admin.register(UpdateRequest)
class UpdateRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'field_to_update', 'old_value', 'new_value', 'status', 'created_at', 'reviewed_at']
    list_filter = ['status', 'field_to_update']
    actions = [approve_update_request, reject_update_request]

@admin.register(CommunityMembership)
class CommunityMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'community', 'joined_at')
    list_filter = ('community',)
    search_fields = ('user__first_name', 'user__last_name', 'community__community_name')

# --- Society Join Request Actions ---
def approve_society_join_request(modeladmin, request, queryset):
    for join_req in queryset:
        join_req.status = 'approved'
        join_req.reviewed_by = request.user
        join_req.reviewed_at = timezone.now()
        join_req.society.members.add(join_req.user)
        join_req.save()

        # Create a notification for the user

        create_notification(join_req.user, f"Your join request to the society '{join_req.society.society_name}' has been approved!", 'success')



    modeladmin.message_user(request, "✅ Selected society join requests approved.", messages.SUCCESS)


def reject_society_join_request(modeladmin, request, queryset):
    queryset.update(status='rejected', reviewed_by=request.user, reviewed_at=timezone.now())

    # Create a notification for the user
    for join_req in queryset:

        create_notification(join_req.user, f"Your join request to the society '{join_req.society.society_name}' has been rejected.", 'error')

        

    modeladmin.message_user(request, "❌ Selected society join requests rejected.", messages.ERROR)


@admin.register(SocietyJoinRequest)
class SocietyJoinRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'society', 'reason', 'status', 'created_at', 'reviewed_by', 'reviewed_at')
    list_filter = ('status', 'society')
    search_fields = ('user__first_name', 'user__last_name', 'society__society_name')
    actions = [approve_society_join_request, reject_society_join_request]

#comment's section
admin.site.register(Comment)