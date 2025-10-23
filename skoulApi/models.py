from django.db import models
from django.contrib.auth.models import AbstractUser


# ==========================
# UTILISATEUR PERSONNALISÉ
# ==========================
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Administrateur"),
        ("teacher", "Enseignant"),
        ("student", "Étudiant"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    
    # Forcer l'unicité de l'email
    email = models.EmailField(unique=True, blank=False, null=False)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    class Meta:
        # Configuration supplémentaire pour l'unicité
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_user_email')
        ]

class LevelClass(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Classes(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "teacher"}
    )
    level = models.ForeignKey(LevelClass, on_delete=models.CASCADE, related_name="classes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.level.name}"


class AffectationStudents(models.Model):
    classroom = models.ForeignKey(Classes, on_delete=models.CASCADE)
    student = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "student"}
    )

    def __str__(self):
        return f"{self.student.username} -> {self.classroom.name}"



class DiffusionList(models.Model):
    name = models.CharField(max_length=50)
    email = models.ManyToManyField(CustomUser)

    def __str__(self):
        return self.name


class EmailSendModel(models.Model):
    subject = models.CharField(max_length=250)
    message = models.TextField()
    from_email = models.EmailField()
    to_email = models.EmailField(blank=True, null=True)  # optionnel si on envoie en masse
    diffusion_list = models.ForeignKey(DiffusionList, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    criticality = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.from_email} -> {self.to_email}"



class APILogEntry(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    path = models.CharField(max_length=500)  # L'URL appelée
    method = models.CharField(max_length=10)  # GET, POST, PUT, DELETE
    status_code = models.IntegerField()  # 200, 404, 500...
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request_body = models.TextField(null=True, blank=True)  # Corps envoyé par l'utilisateur
    duration = models.FloatField(help_text="Durée de la requête en secondes")
    created_at = models.DateTimeField(auto_now_add=True)  # Date/heure où la requête a été faite

    def __str__(self):
        return f"{self.method} {self.path} ({self.status_code})"


# ==========================
# TESTS / QUESTIONS / REPONSES
# # ==========================
# class Test(models.Model):
#     name = models.CharField(max_length=50)
#     classes = models.ForeignKey(Classes, on_delete=models.CASCADE)
#     question_number = models.IntegerField()
#     level = models.ForeignKey(LevelClass, on_delete=models.CASCADE)


# class Categorie(models.Model):
#     name = models.CharField(max_length=100)
#     descriptions = models.CharField(max_length=255)

#     def __str__(self):
#         return self.name


# class Responses(models.Model):
#     name = models.CharField(max_length=30)
#     categories = models.ForeignKey(Categorie, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.name


# class Questions(models.Model):
#     name = models.CharField(max_length=100)
#     categories = models.ForeignKey(Categorie, on_delete=models.CASCADE)
#     question = models.CharField(max_length=250)
#     response = models.ForeignKey(Responses, on_delete=models.CASCADE)
#     points = models.IntegerField()


# ==========================
# COURS
# ==========================
class Courses(models.Model):
    name = models.CharField(max_length=100)
    level = models.ForeignKey(LevelClass, on_delete=models.CASCADE)
    meeting_link = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    descriptions = models.CharField(max_length=500)
    pdf = models.FileField(upload_to="Cours/", null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.level.name})"


class CoursAffectation(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classes, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.name} -> {self.classroom.name} ({self.created_at})"


# ==========================
# REPONSES AUX TESTS
# ==========================
# class StudentAnswer(models.Model):
#     student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={"role": "student"})
#     test = models.ForeignKey(Test, on_delete=models.CASCADE)
#     question = models.ForeignKey(Questions, on_delete=models.CASCADE)
#     selected_response = models.ForeignKey(Responses, on_delete=models.CASCADE)
#     is_correct = models.BooleanField(default=False)


# class TestResult(models.Model):
#     student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={"role": "student"})
#     test = models.ForeignKey(Test, on_delete=models.CASCADE)
#     score = models.IntegerField()
#     total = models.IntegerField()
#     date_taken = models.DateTimeField(auto_now_add=True)


# ==========================
# DEVOIRS
# ==========================
class Homework(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    form_link = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    classes = models.ForeignKey(Classes, on_delete=models.CASCADE)
    level = models.ForeignKey(LevelClass, on_delete=models.CASCADE)
    
    # Champs pour la planification
    scheduled_date = models.DateTimeField(null=True, blank=True, help_text="Date et heure d'envoi planifiée")
    is_scheduled = models.BooleanField(default=False, help_text="Indique si le devoir est planifié pour un envoi différé")
    is_sent = models.BooleanField(default=False, help_text="Indique si le devoir a été envoyé aux étudiants")
    
    # Nouveaux champs pour les fonctionnalités avancées
    student = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        limit_choices_to={"role": "student"},
        help_text="Étudiant spécifique (pour devoirs individuels, ex: étudiant malade)"
    )
    end_date = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Date et heure de fin de disponibilité du devoir"
    )
    is_individual = models.BooleanField(
        default=False, 
        help_text="Indique si le devoir est destiné à un étudiant spécifique"
    )
    end_notification_sent = models.BooleanField(
        default=False,
        help_text="Indique si la notification de dépublication a été envoyée"
    )

    def __str__(self):
        if self.is_individual and self.student:
            return f"{self.name} (Individuel - {self.student.username})"
        return self.name
    
    @property
    def is_available(self):
        """Vérifie si le devoir est encore disponible (pas expiré)"""
        if not self.end_date:
            return True
        from django.utils import timezone
        return timezone.now() <= self.end_date
    
    @property
    def target_students(self):
        """Retourne la liste des étudiants ciblés par ce devoir"""
        if self.is_individual and self.student:
            return [self.student]
        else:
            # Retourner tous les étudiants de la classe
            from .models import AffectationStudents
            affectations = AffectationStudents.objects.filter(classroom=self.classes)
            return [aff.student for aff in affectations]


class ResultHomework(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={"role": "student"})
    class_name = models.ForeignKey(Classes, on_delete=models.CASCADE)
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    result = models.IntegerField()
    observation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.homework.name}"
