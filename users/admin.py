from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FacultyProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'department_fk', 'is_approved', 'is_staff', "attendance", "total_marks", "gpa")
    list_filter = ('role', 'is_approved', 'is_staff', 'department_fk')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'department_fk', 'phone_number', 'employee_id', 'designation', 'is_approved', 'approved_by', 'approved_at', 'attendance', 'total_marks', 'gpa')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'department_fk', 'phone_number', 'employee_id', 'designation', 'is_approved')}),
    )

@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'specialization', 'years_of_experience')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'employee_id')
    list_filter = ('specialization',)

admin.site.register(User, CustomUserAdmin)
