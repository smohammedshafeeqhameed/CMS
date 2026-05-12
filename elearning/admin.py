from django.contrib import admin
from .models import MaterialCategory, LearningMaterial, MaterialAccess

@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name']

@admin.register(LearningMaterial)
class LearningMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'category', 'uploaded_by', 'access_level', 'download_count', 'is_active', 'uploaded_at']
    list_filter = ['is_active', 'access_level', 'category', 'uploaded_at']
    search_fields = ['title', 'subject__name', 'uploaded_by__username']
    raw_id_fields = ['subject', 'category', 'uploaded_by']
    readonly_fields = ['download_count', 'uploaded_at', 'updated_at']

@admin.register(MaterialAccess)
class MaterialAccessAdmin(admin.ModelAdmin):
    list_display = ['material', 'student', 'action', 'accessed_at']
    list_filter = ['action', 'accessed_at']
    search_fields = ['student__username', 'material__title']
    raw_id_fields = ['material', 'student']
    readonly_fields = ['accessed_at']
