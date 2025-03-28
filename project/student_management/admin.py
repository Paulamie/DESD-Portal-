from django.contrib import admin
from .models import CommunityRequest, Event, Community, Society, Interest  
from django.contrib import admin
from .models import UpdateRequest
from django.db import models
from django.utils import timezone


# Custom actions for the admin interface
def approve_community_request(modeladmin, request, queryset):
    queryset.update(status='approved')

def reject_community_request(modeladmin, request, queryset):
    queryset.update(status='rejected')

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
    queryset.update(status='approved', reviewed_at=timezone.now(), reviewed_by=request.user)

def reject_update_request(modeladmin, request, queryset):
    queryset.update(status='rejected', reviewed_at=timezone.now(), reviewed_by=request.user)



approve_update_request.short_description = "Approve selected update requests"
reject_update_request.short_description = "Reject selected update requests"

@admin.register(UpdateRequest)
class UpdateRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'field_to_update', 'old_value', 'new_value', 'status', 'created_at', 'reviewed_at')
    list_filter = ('status', 'created_at')
    actions = [approve_update_request, reject_update_request]

