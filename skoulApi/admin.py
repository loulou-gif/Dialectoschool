# skoulApi/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff", "is_active", "date_joined")
    list_filter = ("role", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Role", {"fields": ("role",)}),)

@admin.register(LevelClass)
class LevelClassAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "teacher", "created_at")
    list_filter = ("level", "teacher", "created_at")
    search_fields = ("name", "teacher__username", "teacher__first_name", "teacher__last_name")
    ordering = ("-created_at",)

@admin.register(AffectationStudents)
class AffectationStudentsAdmin(admin.ModelAdmin):
    list_display = ("student", "classroom", "student_role")
    list_filter = ("classroom__level", "classroom")
    search_fields = ("student__username", "student__first_name", "student__last_name", "classroom__name")
    
    def student_role(self, obj):
        return obj.student.role
    student_role.short_description = "Rôle étudiant"

@admin.register(DiffusionList)
class DiffusionListAdmin(admin.ModelAdmin):
    list_display = ("name", "email_count")
    search_fields = ("name",)
    filter_horizontal = ("email",)
    
    def email_count(self, obj):
        return obj.email.count()
    email_count.short_description = "Nombre d'emails"

@admin.register(EmailSendModel)
class EmailSendModelAdmin(admin.ModelAdmin):
    list_display = ("subject", "from_email", "to_email", "criticality", "sent_at", "created_at")
    list_filter = ("criticality", "sent_at", "created_at")
    search_fields = ("subject", "from_email", "to_email")
    ordering = ("-created_at",)
    readonly_fields = ("sent_at", "created_at")

@admin.register(APILogEntry)
class APILogEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "method", "path", "status_code", "duration", "created_at")
    list_filter = ("method", "status_code", "created_at")
    search_fields = ("user__username", "path")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "meeting_link", "created_at")
    list_filter = ("level", "created_at")
    search_fields = ("name", "descriptions")
    ordering = ("-created_at",)

@admin.register(CoursAffectation)
class CoursAffectationAdmin(admin.ModelAdmin):
    list_display = ("course", "classroom", "created_at")
    list_filter = ("course__level", "created_at")
    search_fields = ("course__name", "classroom__name")
    ordering = ("-created_at",)

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "classes", "level", "created_at")
    list_filter = ("level", "course", "classes", "created_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)

@admin.register(ResultHomework)
class ResultHomeworkAdmin(admin.ModelAdmin):
    list_display = ("student", "homework", "class_name", "result", "created_at")
    list_filter = ("class_name__level", "created_at")
    search_fields = ("student__username", "student__first_name", "student__last_name", "homework__name")
    ordering = ("-created_at",)

# Enregistrement du modèle CustomUser
admin.site.register(CustomUser, CustomUserAdmin)
