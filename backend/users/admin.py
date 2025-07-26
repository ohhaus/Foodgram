from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Регистрация в админке пользователя."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('last_login', 'date_joined')
    list_display_links = ('id', 'username', 'email')
    list_per_page = 20
    fieldsets = (
        (
            'Основная информация',
            {
                'fields': (
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'password',
                )
            },
        ),
        (
            'Права доступа',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
