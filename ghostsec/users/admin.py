from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'get_skill_level_with_badge', 
        'challenges_completed', 'reputation_points', 'is_active', 
        'account_status'
    )
    list_filter = (
        'is_active', 'is_staff', 'is_superuser', 'skill_level',
        'two_factor_enabled', 'security_questions_set'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('last_login', 'date_joined', 'last_active')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'bio', 'avatar'),
        }),
        (_('Platform Progress'), {
            'fields': (
                'skill_level', 'experience_points', 'challenges_completed',
                'contributions', 'reputation_points', 'badges'
            ),
        }),
        (_('Security'), {
            'fields': (
                'two_factor_enabled', 'security_questions_set',
                'last_security_check', 'last_password_change',
                'failed_login_attempts', 'account_locked_until'
            ),
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'last_active'),
        }),
    )
    
    def get_skill_level_with_badge(self, obj):
        """Display skill level with a colored badge."""
        colors = {
            0: '#6c757d',  # Gray for Beginner
            1: '#28a745',  # Green for Novice
            2: '#17a2b8',  # Cyan for Intermediate
            3: '#007bff',  # Blue for Advanced
            4: '#ffc107',  # Yellow for Expert
            5: '#dc3545',  # Red for Master
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.skill_level, '#6c757d'),
            obj.get_skill_level_display()
        )
    get_skill_level_with_badge.short_description = 'Skill Level'
    
    def account_status(self, obj):
        """Display account status with color-coded indicator."""
        if not obj.is_active:
            return format_html(
                '<span style="color: #dc3545;">❌ Inactive</span>'
            )
        if obj.is_account_locked():
            return format_html(
                '<span style="color: #ffc107;">🔒 Locked</span>'
            )
        if obj.two_factor_enabled:
            return format_html(
                '<span style="color: #28a745;">✅ Secured</span>'
            )
        return format_html(
            '<span style="color: #17a2b8;">✓ Active</span>'
        )
    account_status.short_description = 'Status'
