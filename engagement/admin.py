from django.contrib import admin

from .models import BookingRequest, ContactInquiry, Subscriber


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'preferred_date', 'preferred_time', 'status', 'created_at')
    list_filter = ('status', 'service_interest', 'preferred_date')
    search_fields = ('name', 'email', 'business_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'preferred_date'


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'inquiry_type', 'company', 'is_handled', 'submitted_at')
    list_filter = ('inquiry_type', 'is_handled', 'submitted_at')
    search_fields = ('name', 'email', 'company', 'message')
    readonly_fields = ('submitted_at',)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('name', 'email')
    readonly_fields = ('subscribed_at',)
