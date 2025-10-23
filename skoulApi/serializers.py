from rest_framework import serializers
from .models import CustomUser
from .models import *
from .services import *

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) 
    # userdetail = UserDetailSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = ('id','last_name', 'first_name', 'username', 'email', 'password', 'date_joined','role')
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate_email(self, value):
        """
        Valider que l'email est unique
        """
        # Si c'est une mise à jour, exclure l'utilisateur actuel de la vérification
        if self.instance:
            if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("Un compte existe déjà avec cet email.")
        else:
            # Si c'est une création, vérifier simplement l'existence
            if CustomUser.objects.filter(email=value).exists():
                raise serializers.ValidationError("Un compte existe déjà avec cet email.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)  # hachage sécurisé
        user.save()
        
        # Envoyer l'email de bienvenue avec les identifiants
        if password and user.email:
            try:
                send_welcome_email(user, password)
            except Exception as e:
                # On continue même si l'email échoue, pour ne pas bloquer la création
                print(f"Erreur lors de l'envoi de l'email de bienvenue: {e}")
        
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # hachage sécurisé
        instance.save()
        return instance
    

class RoleSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()
    
        
class LevelClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelClass
        fields = '__all__'
        
        
class ClassesSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    level_name = serializers.SerializerMethodField()
    students_detail = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)

    class Meta:
        model = Classes
        fields = ['id', 'name', 'teacher', 'teacher_name', 'level_name','level', 'created_at', 'student_count', 'students_detail']
        extra_kwargs = {
            'teacher': {'write_only': False, 'required': False}
        }
    
    def create(self, validated_data):
        """
        Créer une classe et envoyer un email au professeur si assigné
        """
        classe = super().create(validated_data)
        
        # Créer une liste de diffusion pour cette classe
        DiffusionList.objects.create(name=classe.name)
        
        # Envoyer un email au professeur si assigné
        if classe.teacher and classe.teacher.email:
            try:
                send_teacher_class_assignment_email(classe.teacher, classe, is_new_assignment=True)
            except Exception as e:
                # On continue même si l'email échoue
                print(f"Erreur lors de l'envoi de l'email au professeur: {e}")
        
        return classe
    
    def update(self, instance, validated_data):
        """
        Mettre à jour une classe et envoyer un email si le professeur change
        """
        old_teacher = instance.teacher
        old_name = instance.name
        new_teacher = validated_data.get('teacher', instance.teacher)
        new_name = validated_data.get('name', instance.name)
        
        # Mettre à jour la classe
        classe = super().update(instance, validated_data)
        
        # Si le nom de la classe a changé, mettre à jour la liste de diffusion
        if old_name != new_name:
            try:
                # Chercher la liste de diffusion avec l'ancien nom
                diffusion_list = DiffusionList.objects.filter(name=old_name).first()
                if diffusion_list:
                    # Mettre à jour le nom de la liste de diffusion
                    diffusion_list.name = new_name
                    diffusion_list.save()
                else:
                    # Si la liste n'existe pas, la créer
                    DiffusionList.objects.create(name=new_name)
            except Exception as e:
                print(f"Erreur lors de la mise à jour de la liste de diffusion: {e}")
        
        # Si le professeur a changé et qu'il y a un nouveau professeur
        if old_teacher != new_teacher and new_teacher and new_teacher.email:
            try:
                send_teacher_class_assignment_email(new_teacher, classe, is_new_assignment=False)
            except Exception as e:
                # On continue même si l'email échoue
                print(f"Erreur lors de l'envoi de l'email au nouveau professeur: {e}")
        
        return classe
    
    def get_teacher_name(self, obj):
        return obj.teacher.username if obj.teacher else "Aucun"

    def get_student_count(self, obj):
        return AffectationStudents.objects.filter(classroom=obj).count()
    
    def get_level_name(self, obj):
        return obj.level.name if obj.level else None
    
    def get_students_detail(self, obj):
        affectations = AffectationStudents.objects.filter(classroom=obj)
        return AffectationStudentSerializer(affectations, many=True).data
        
class AffectationStudentSerializer(serializers.ModelSerializer):
    student_username = serializers.SerializerMethodField()
    student_full_name = serializers.SerializerMethodField()
    class Meta:
        model = AffectationStudents
        fields = '__all__'
    
    def create(self, validated_data):
        """
        Créer une affectation et envoyer un email à l'étudiant
        """
        affectation = super().create(validated_data)
        
        # Envoyer un email à l'étudiant
        if affectation.student and affectation.student.email:
            try:
                send_student_class_assignment_email(
                    affectation.student, 
                    affectation.classroom, 
                    is_new_assignment=True
                )
            except Exception as e:
                # On continue même si l'email échoue
                print(f"Erreur lors de l'envoi de l'email à l'étudiant: {e}")
        
        return affectation
    
    def update(self, instance, validated_data):
        """
        Mettre à jour une affectation et envoyer un email si la classe change
        """
        old_classroom = instance.classroom
        new_classroom = validated_data.get('classroom', instance.classroom)
        
        # Mettre à jour l'affectation
        affectation = super().update(instance, validated_data)
        
        # Si la classe a changé, envoyer un email de réaffectation
        if old_classroom != new_classroom and affectation.student and affectation.student.email:
            try:
                send_student_class_assignment_email(
                    affectation.student, 
                    new_classroom, 
                    is_new_assignment=False
                )
            except Exception as e:
                # On continue même si l'email échoue
                print(f"Erreur lors de l'envoi de l'email de réaffectation à l'étudiant: {e}")
        
        return affectation
        
    def get_student_username(self, obj):
        return obj.student.username

    def get_student_full_name(self, obj):
        first_name = obj.student.first_name or ""
        last_name = obj.student.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        return full_name if full_name else obj.student.username
        
class DiffusionListSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    email_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CustomUser.objects.all(),
        source='email',
        write_only=True
    )

    class Meta:
        model = DiffusionList
        fields = ['id', 'name', 'email', 'email_ids']

    def get_email(self, obj):
        return [user.email for user in obj.email.all()]

        
        

class SendMailSerializer(serializers.ModelSerializer):
    sent_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)
    class Meta:
        model = EmailSendModel
        fields = ['id', 'subject', 'message', 'from_email', 'to_email', 'sent_at', 'criticality', 'diffusion_list']

class UserEmailSerializer(serializers.ModelSerializer):
    sent_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)
    diffusion_list_name = serializers.SerializerMethodField()

    class Meta:
        model = EmailSendModel
        fields = ['id', 'subject', 'message', 'from_email', 'to_email', 'sent_at', 'criticality', 'diffusion_list', 'diffusion_list_name']

    def get_diffusion_list_name(self, obj):
        return obj.diffusion_list.name if obj.diffusion_list else None

class APILogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = APILogEntry
        fields = '__all__'
        
        
        


class CourseSerializer(serializers.ModelSerializer):
    level_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)
    classes_count = serializers.SerializerMethodField()
    classes = serializers.SerializerMethodField()

    class Meta:
        model = Courses
        fields = ['id', 'name', 'level', 'level_name', 'meeting_link', 'descriptions', 'pdf', 'created_at', 'classes_count', 'classes']
        extra_kwargs = {
            'pdf': {'required': False, 'allow_null': True}
        }
    
    def update(self, instance, validated_data):
        """
        Mise à jour du cours en conservant le PDF existant si aucun nouveau n'est fourni
        """
        # Si 'pdf' n'est pas dans validated_data ou est None, on garde l'ancien PDF
        if 'pdf' not in validated_data or validated_data.get('pdf') is None:
            validated_data.pop('pdf', None)  # Retirer 'pdf' pour ne pas l'écraser
        
        # Mettre à jour le cours avec les autres champs
        return super().update(instance, validated_data)

    def get_level_name(self, obj):
        return obj.level.name if obj.level else None

    def get_classes_count(self, obj):
        """Retourne le nombre de classes auxquelles ce cours a été affecté"""
        return CoursAffectation.objects.filter(course=obj).values('classroom').distinct().count()

    def get_classes(self, obj):
        """Retourne la liste des classes auxquelles ce cours a été affecté avec leurs détails"""
        # Récupérer les IDs des classes distinctes
        classroom_ids = CoursAffectation.objects.filter(course=obj).values_list('classroom_id', flat=True).distinct()
        
        # Récupérer les classes avec leurs détails
        from .models import Classes
        classes = Classes.objects.filter(id__in=classroom_ids).select_related('level', 'teacher')
        
        classes_data = []
        for classroom in classes:
            teacher_name = None
            if classroom.teacher:
                first_name = classroom.teacher.first_name or ""
                last_name = classroom.teacher.last_name or ""
                teacher_name = f"{first_name} {last_name}".strip()
                if not teacher_name:
                    teacher_name = classroom.teacher.username
            
            classes_data.append({
                'id': classroom.id,
                'name': classroom.name,
                'level_id': classroom.level.id if classroom.level else None,
                'level_name': classroom.level.name if classroom.level else None,
                'teacher_id': classroom.teacher.id if classroom.teacher else None,
                'teacher_name': teacher_name,
                'created_at': classroom.created_at.strftime("%d/%m/%Y") if classroom.created_at else None
            })
        
        return classes_data



class CourseAffectationSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)

    class Meta:
        model = CoursAffectation
        fields = ['id', 'course', 'course_name', 'classroom', 'class_name', 'created_at']

    def get_course_name(self, obj):
        return obj.course.name

    def get_class_name(self, obj):
        return obj.classroom.name

class UserDetailsSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    class_info = serializers.SerializerMethodField()
    test_results = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'class_info', 'test_results', 'student_count']

    def get_role(self, obj):
        return obj.role if obj.role else "Aucun rôle"
    
    def get_student_count(self, obj):
        # Si l'utilisateur est enseignant, on compte les élèves de sa classe
        classroom = Classes.objects.filter(teacher=obj).first()
        if classroom:
            return AffectationStudents.objects.filter(classroom=classroom).count()
        return 0


    def get_class_info(self, obj):
        aff = AffectationStudents.objects.filter(student=obj).first()
        if aff:
            teacher_name = None
            if aff.classroom.teacher:
                first_name = aff.classroom.teacher.first_name or ""
                last_name = aff.classroom.teacher.last_name or ""
                teacher_name = f"{first_name} {last_name}".strip()
                if not teacher_name:
                    teacher_name = aff.classroom.teacher.username
            
            return {
                'class_name': aff.classroom.name,
                'level': aff.classroom.level.name,
                'teacher_name': teacher_name,
                'created_at': aff.classroom.created_at.strftime("%d/%m/%Y") if aff.classroom.created_at else None
            }
        return None

    def get_test_results(self, obj):
        results = ResultHomework.objects.filter(student=obj).order_by('-created_at')
        return [{
            'id': result.id,
            'homework_name': result.homework.name if result.homework else None,
            'result': result.result,
            'observation': result.observation,
            'created_at': result.created_at.strftime("%d/%m/%Y %H:%M") if result.created_at else None
        } for result in results]


class StudentCompleteInfoSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    class_info = serializers.SerializerMethodField()
    test_results = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    total_tests = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    recent_results = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'class_info', 'test_results', 'average_score', 
            'total_tests', 'courses', 'recent_results'
        ]

    def get_role(self, obj):
        return obj.role if obj.role else "Aucun rôle"

    def get_class_info(self, obj):
        aff = AffectationStudents.objects.filter(student=obj).first()
        if aff:
            teacher_name = None
            if aff.classroom.teacher:
                first_name = aff.classroom.teacher.first_name or ""
                last_name = aff.classroom.teacher.last_name or ""
                teacher_name = f"{first_name} {last_name}".strip()
                if not teacher_name:
                    teacher_name = aff.classroom.teacher.username
            
            return {
                'class_id': aff.classroom.id,
                'class_name': aff.classroom.name,
                'level_id': aff.classroom.level.id,
                'level_name': aff.classroom.level.name,
                'teacher_id': aff.classroom.teacher.id if aff.classroom.teacher else None,
                'teacher_name': teacher_name,
                'created_at': aff.classroom.created_at.strftime("%d/%m/%Y") if aff.classroom.created_at else None
            }
        return None

    def get_test_results(self, obj):
        results = ResultHomework.objects.filter(student=obj).order_by('-created_at')
        return [{
            'id': result.id,
            'homework_name': result.homework.name if result.homework else None,
            'result': result.result,
            'observation': result.observation,
            'created_at': result.created_at.strftime("%d/%m/%Y %H:%M") if result.created_at else None
        } for result in results]

    def get_average_score(self, obj):
        results = ResultHomework.objects.filter(student=obj)
        if not results:
            return 0
        
        total_score = 0
        for result in results:
            total_score += result.result
        
        return round(total_score / len(results), 2)

    def get_total_tests(self, obj):
        return ResultHomework.objects.filter(student=obj).count()

    def get_courses(self, obj):
        # Récupérer les cours affectés à la classe de l'étudiant
        aff = AffectationStudents.objects.filter(student=obj).first()
        if not aff:
            return []
        
        course_affectations = CoursAffectation.objects.filter(classroom=aff.classroom)
        return [{
            'id': ca.course.id,
            'name': ca.course.name,
            'description': ca.course.descriptions,
            'level': ca.course.level.name,
            'meeting_link': ca.course.meeting_link,
            'pdf_url': ca.course.pdf.url if ca.course.pdf else None,
            'date': ca.created_at.strftime("%d/%m/%Y") if ca.created_at else None
        } for ca in course_affectations]

    def get_recent_results(self, obj):
        # Récupérer les 5 derniers résultats de devoirs
        results = ResultHomework.objects.filter(student=obj).order_by('-created_at')[:5]
        return [{
            'homework_name': result.homework.name if result.homework else None,
            'result': result.result,
            'observation': result.observation,
            'date': result.created_at.strftime("%d/%m/%Y") if result.created_at else None
        } for result in results]
    
    
class HomeworkSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    level_name = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    scheduled_date_formatted = serializers.SerializerMethodField()
    end_date_formatted = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    target_students_count = serializers.SerializerMethodField()
    
    # Statistiques automatiques
    average_score = serializers.SerializerMethodField()
    submitted_count = serializers.SerializerMethodField()
    submission_rate = serializers.SerializerMethodField()
    highest_score = serializers.SerializerMethodField()
    lowest_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Homework
        fields = [
            'id', 'name', 'description', 'form_link', 'created_at', 'created_at_formatted',
            'course', 'course_name', 'classes', 'class_name', 'level', 'level_name',
            'scheduled_date', 'scheduled_date_formatted', 'is_scheduled', 'is_sent',
            'student', 'student_name', 'end_date', 'end_date_formatted', 'is_individual',
            'is_available', 'target_students_count',
            # Statistiques
            'average_score', 'submitted_count', 'submission_rate', 'highest_score', 'lowest_score',
        ]
    
    def create(self, validated_data):
        """
        Créer un devoir et gérer l'envoi immédiat ou planifié
        """
        # Déterminer si c'est un devoir individuel
        student = validated_data.get('student')
        if student:
            validated_data['is_individual'] = True
        
        homework = super().create(validated_data)
        
        # Si le devoir est planifié, ne pas envoyer immédiatement
        if homework.is_scheduled and homework.scheduled_date:
            # Le devoir sera envoyé par la tâche Celery
            target = f"étudiant {homework.student.username}" if homework.is_individual else "classe"
            print(f"Devoir '{homework.name}' planifié pour le {homework.scheduled_date} ({target})")
        else:
            # Envoyer immédiatement un email
            try:
                send_homework_assignment_email(homework)
                # Marquer comme envoyé si l'envoi immédiat réussit
                homework.is_sent = True
                homework.save()
            except Exception as e:
                # On continue même si l'email échoue
                print(f"Erreur lors de l'envoi des emails de devoir: {e}")
        
        return homework
    
    def get_course_name(self, obj):
        return obj.course.name if obj.course else None
    
    def get_class_name(self, obj):
        return obj.classes.name if obj.classes else None
    
    def get_level_name(self, obj):
        return obj.level.name if obj.level else None
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%d/%m/%Y %H:%M") if obj.created_at else None
    
    def get_scheduled_date_formatted(self, obj):
        return obj.scheduled_date.strftime("%d/%m/%Y %H:%M") if obj.scheduled_date else None
    
    def get_end_date_formatted(self, obj):
        return obj.end_date.strftime("%d/%m/%Y %H:%M") if obj.end_date else None
    
    def get_student_name(self, obj):
        if obj.student:
            first_name = obj.student.first_name or ""
            last_name = obj.student.last_name or ""
            full_name = f"{first_name} {last_name}".strip()
            return full_name if full_name else obj.student.username
        return None
    
    def get_is_available(self, obj):
        return obj.is_available
    
    def get_target_students_count(self, obj):
        return len(obj.target_students)
    
    def get_average_score(self, obj):
        """Calcule la moyenne générale du devoir"""
        from .models import ResultHomework
        results = ResultHomework.objects.filter(homework=obj)
        
        if not results.exists():
            return None
        
        total = sum(result.result for result in results)
        average = total / results.count()
        return round(average, 2)
    
    def get_submitted_count(self, obj):
        """Compte le nombre d'élèves ayant rendu le devoir"""
        from .models import ResultHomework
        return ResultHomework.objects.filter(homework=obj).count()
    
    def get_submission_rate(self, obj):
        """Calcule le taux de soumission en pourcentage"""
        total_students = len(obj.target_students)
        if total_students == 0:
            return 0
        
        from .models import ResultHomework
        submitted = ResultHomework.objects.filter(homework=obj).count()
        rate = (submitted / total_students) * 100
        return round(rate, 2)
    
    def get_highest_score(self, obj):
        """Retourne la meilleure note du devoir"""
        from .models import ResultHomework
        results = ResultHomework.objects.filter(homework=obj)
        
        if not results.exists():
            return None
        
        return max(result.result for result in results)
    
    def get_lowest_score(self, obj):
        """Retourne la note la plus basse du devoir"""
        from .models import ResultHomework
        results = ResultHomework.objects.filter(homework=obj)
        
        if not results.exists():
            return None
        
        return min(result.result for result in results)

        
class ResultHomeworkSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_email = serializers.SerializerMethodField()
    homework_name = serializers.SerializerMethodField()
    homework_description = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()
    classes_name = serializers.SerializerMethodField()
    level_name = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ResultHomework
        fields = [
            'id', 'student', 'student_name', 'student_email', 'class_name', 'classes_name',
            'homework', 'homework_name', 'homework_description', 'course_name', 'level_name',
            'result', 'observation', 'created_at', 'created_at_formatted'
        ]
        extra_kwargs = {
            'class_name': {'required': False, 'allow_null': True}
        }
    
    def create(self, validated_data):
        """
        Créer un résultat de devoir et envoyer un email à l'étudiant
        La classe est automatiquement déduite de l'affectation de l'étudiant
        """
        student = validated_data.get('student')
        
        # Si la classe n'est pas fournie, la récupérer automatiquement depuis l'affectation
        if 'class_name' not in validated_data or validated_data.get('class_name') is None:
            try:
                affectation = AffectationStudents.objects.get(student=student)
                validated_data['class_name'] = affectation.classroom
            except AffectationStudents.DoesNotExist:
                raise serializers.ValidationError({
                    "student": "Cet étudiant n'est affecté à aucune classe. Veuillez d'abord l'affecter à une classe."
                })
        
        result_homework = super().create(validated_data)
        
        # Envoyer un email à l'étudiant
        try:
            send_homework_result_email(result_homework)
        except Exception as e:
            # On continue même si l'email échoue
            print(f"Erreur lors de l'envoi de l'email de note: {e}")
        
        return result_homework
    
    def update(self, instance, validated_data):
        """
        Mettre à jour un résultat de devoir et envoyer un email si la note change
        """
        old_result = instance.result
        new_result = validated_data.get('result', instance.result)
        
        # Mettre à jour le résultat
        result_homework = super().update(instance, validated_data)
        
        # Si la note a changé, envoyer un email
        if old_result != new_result:
            try:
                send_homework_result_email(result_homework)
            except Exception as e:
                # On continue même si l'email échoue
                print(f"Erreur lors de l'envoi de l'email de mise à jour de note: {e}")
        
        return result_homework
    
    def get_student_name(self, obj):
        if obj.student:
            first_name = obj.student.first_name or ""
            last_name = obj.student.last_name or ""
            full_name = f"{first_name} {last_name}".strip()
            return full_name if full_name else obj.student.username
        return None
    
    def get_student_email(self, obj):
        return obj.student.email if obj.student else None
    
    def get_homework_name(self, obj):
        return obj.homework.name if obj.homework else None
    
    def get_homework_description(self, obj):
        return obj.homework.description if obj.homework else None
    
    def get_course_name(self, obj):
        return obj.homework.course.name if obj.homework and obj.homework.course else None
    
    def get_classes_name(self, obj):
        return obj.class_name.name if obj.class_name else None
    
    def get_level_name(self, obj):
        return obj.class_name.level.name if obj.class_name and obj.class_name.level else None
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%d/%m/%Y %H:%M") if obj.created_at else None