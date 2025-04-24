from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.contrib import messages
from .models import CommunityRequest, Event, Community, Society, Interest, UpdateRequest, CommunityMembership
from django.core.files.base import ContentFile
from .models import SocietyJoinRequest





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

    modeladmin.message_user(request, "✅ Selected community requests were approved and communities created.", messages.SUCCESS)


def reject_community_request(modeladmin, request, queryset):
    queryset.update(status='rejected', reviewed_at=timezone.now(), reviewed_by=request.user)
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
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'start_time', 'end_time', 'location_type', 'is_approved')
    search_fields = ('event_name',)

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
    from django.core.files.base import ContentFile
    import os

    for obj in queryset:
        obj.status = 'approved'
        obj.reviewed_at = timezone.now()
        obj.reviewed_by = request.user

        user = obj.user
        field = obj.field_to_update.lower()

        if field == 'name':
            full_name = obj.new_value.strip().split(' ', 1)
            user.first_name = full_name[0]
            user.last_name = full_name[1] if len(full_name) > 1 else ''

        elif field == 'course':
            user.course = obj.new_value

        elif field == 'profile_picture' and obj.profile_picture:
            filename = os.path.basename(obj.profile_picture.name)
            print(f"🖼 Saving profile picture {filename} to user {user.email}")

            try:
                obj.profile_picture.open() 
                user.profile_picture.save(
                    filename,
                    ContentFile(obj.profile_picture.read()),
                    save=True
                )
                print(f"✅ Profile picture saved successfully.")
            except Exception as e:
                print(f"❌ Error saving profile picture: {e}")

        user.save()
        obj.save()

    modeladmin.message_user(request, "✅ Selected profile updates were approved.", messages.SUCCESS)


def reject_update_request(modeladmin, request, queryset):
    queryset.update(status='rejected', reviewed_at=timezone.now(), reviewed_by=request.user)
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
    modeladmin.message_user(request, "✅ Selected society join requests approved.", messages.SUCCESS)

def reject_society_join_request(modeladmin, request, queryset):
    queryset.update(status='rejected', reviewed_by=request.user, reviewed_at=timezone.now())
    modeladmin.message_user(request, "❌ Selected society join requests rejected.", messages.ERROR)

@admin.register(SocietyJoinRequest)
class SocietyJoinRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'society', 'reason', 'status', 'created_at', 'reviewed_by', 'reviewed_at')
    list_filter = ('status', 'society')
    search_fields = ('user__first_name', 'user__last_name', 'society__society_name')
    actions = [approve_society_join_request, reject_society_join_request]
