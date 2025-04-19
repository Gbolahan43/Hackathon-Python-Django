from django.contrib import admin
from .models import Challenge, UserChallenge


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'docker_image', 'start_port', 'end_port', 'point')
    search_fields = ('name', 'docker_image')
    list_filter = ('point',)  # Optional: helpful if you have varying challenge points
    ordering = ('name',)
    empty_value_display = '-empty-'
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'point')
        }),
        ('Docker Config', {
            'fields': ('docker_image', 'docker_port', 'start_port', 'end_port')
        }),
        ('Security', {
            'fields': ('flag',)
        }),
    )


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'container_id', 'port', 'no_of_attempt', 'is_solved')
    search_fields = ('user__username', 'challenge__name')
    list_filter = ('is_solved', 'challenge')
    ordering = ('user',)
    empty_value_display = '-empty-'
    readonly_fields = ('no_of_attempt', 'container_id')  # assuming these shouldn't be modified manually

    fieldsets = (
        (None, {
            'fields': ('user', 'challenge')
        }),
        ('Container Info', {
            'fields': ('container_id', 'port')
        }),
        ('Progress', {
            'fields': ('no_of_attempt', 'is_solved')
        }),
    )
