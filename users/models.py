from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom manager where email is the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        STUDENT = "student", "Étudiant"
        TEACHER = "teacher", "Enseignant"
        ADMINISTRATOR = "administrator", "Responsable Administratif"
        CLUB_MANAGER = "club_manager", "Gestionnaire de Club"

    class DiplomaChoices(models.TextChoices):
        LISI = "Licence en Ingénierie des Systèmes Informatiques", "إجازة في هندسة أنظمة المعلومات"
        LGMI = "Licence en Génie Mécanique", "إجازة في الهندسة الميكانيكية"
        LGE = "Licence en Génie énergétique", "إجازة في الهندسة الطاقية"
        LEEA = "Licence en électronique électrotechnique & Automatique", "إجازة في الإلكترونيات الكهرتقنية والآلية"
        MRDS = "Master Recherche en data science", "ماجستير بحث في علوم البيانات"
        MRAII = "Master Recherche en Automatique & Informatique Industrielle", "ماجستير بحث في الآلية والحوسبة الصناعية"
        MPCI = "Master Professionnel en Commandes des Systémes Industriels", "ماجستير مهني في قيادة الأنظمة الصناعية"
        MPGMSI = "Master Professionnel en Gestion de Maintenance des Systémes Industriels", "ماجستير مهني في إدارة صيانة الأنظمة الصناعية"
        MPGM = "Master Professionnel en génie mécanique", "ماجستير مهني في الهندسة الميكانيكية"

        @classmethod
        def get_diploma_display_by_language(cls, diploma_value, language):
            """Get diploma display based on language"""
            french_names = {
                cls.LISI.value: "Licence en Ingénierie des Systèmes Informatiques",
                cls.LGMI.value: "Licence en Génie Mécanique",
                cls.LGE.value: "Licence en Génie énergétique",
                cls.LEEA.value: "Licence en électronique électrotechnique & Automatique",
                cls.MRDS.value: "Master Recherche en data science",
                cls.MRAII.value: "Master Recherche en Automatique & Informatique Industrielle",
                cls.MPCI.value: "Master Professionnel en Commandes des Systémes Industriels",
                cls.MPGMSI.value: "Master Professionnel en Gestion de Maintenance des Systémes Industriels",
                cls.MPGM.value: "Master Professionnel en génie mécanique",
            }

            arabic_names = {
                cls.LISI.value: "إجازة في هندسة أنظمة المعلومات",
                cls.LGMI.value: "إجازة في الهندسة الميكانيكية",
                cls.LGE.value: "إجازة في الهندسة الطاقية",
                cls.LEEA.value: "إجازة في الإلكترونيات الكهرتقنية والآلية",
                cls.MRDS.value: "ماجستير بحث في علوم البيانات",
                cls.MRAII.value: "ماجستير بحث في الآلية والحوسبة الصناعية",
                cls.MPCI.value: "ماجستير مهني في قيادة الأنظمة الصناعية",
                cls.MPGMSI.value: "ماجستير مهني في إدارة صيانة الأنظمة الصناعية",
                cls.MPGM.value: "ماجستير مهني في الهندسة الميكانيكية",
            }

            if language == 'ar':
                return arabic_names.get(diploma_value, diploma_value)
            else:  # Default to French
                return french_names.get(diploma_value, diploma_value)

    email = models.EmailField(unique=True)
    cin = models.IntegerField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    first_name_arabic = models.CharField(max_length=150, blank=True)
    last_name_arabic = models.CharField(max_length=150, blank=True)
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text="Profil fonctionnel tel que défini dans le cahier des charges.",
    )

    diploma = models.CharField(
        max_length=80,
        choices=DiplomaChoices.choices,
        help_text="Diplôme obtenu par l'utilisateur.",
    )
    date_of_birth = models.DateField(blank=True, null=True) 
    place_of_birth = models.CharField(max_length=150, blank=True)
    place_of_birth_arabic = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ("-date_joined",)

    def __str__(self):
        return self.email

    def add_education_history(self, academic_year, registration_id, grade, specialty, class_name, session, result):
        if self.role != self.Role.STUDENT:
            raise ValueError("Only students can have education history.")
        return self.education_histories.create(
            academic_year=academic_year,
            registration_id=registration_id,
            grade=grade,
            specialty=specialty,
            class_name=class_name,
            session=session,
            result=result,
        )


class EducationHistory(models.Model):
    class Grade(models.TextChoices):
        FIRST_YEAR = "1", "Première année"
        SECOND_YEAR = "2", "Deuxième année"
        THIRD_YEAR = "3", "Troisième année"

        @classmethod
        def get_grade_display_by_language(cls, grade_value, language):
            """Get grade display based on language"""
            french_names = {
                cls.FIRST_YEAR.value: "Première année",
                cls.SECOND_YEAR.value: "Deuxième année",
                cls.THIRD_YEAR.value: "Troisième année",
            }

            arabic_names = {
                cls.FIRST_YEAR.value: "السنة الأولى",
                cls.SECOND_YEAR.value: "السنة الثانية",
                cls.THIRD_YEAR.value: "السنة الثالثة",
            }

            if language == 'ar':
                return arabic_names.get(grade_value, grade_value)
            else:  # Default to French
                return french_names.get(grade_value, grade_value)

    class Session(models.TextChoices):
        PRINCIPALE = "principale", "Principale"
        CONTROLE = "controle", "Contrôle"

    class Result(models.TextChoices):
        TRES_BIEN = "tres_bien", "Très Bien"
        BIEN = "bien", "Bien"
        ASSEZ_BIEN = "assez_bien", "Assez Bien"
        PASSABLE = "passable", "Passable"
        AJOURNE = "ajourne", "Ajourné"

    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="education_histories",
        limit_choices_to={'role': User.Role.STUDENT}
    )
    academic_year = models.CharField(max_length=9, help_text="Ex: 2023-2024")
    registration_id = models.IntegerField()
    grade = models.CharField(max_length=10, choices=Grade.choices)
    specialty = models.CharField(max_length=100,default="Tronc Commun")
    class_name = models.CharField(max_length=50)
    session = models.CharField(max_length=20, choices=Session.choices)
    result = models.CharField(max_length=20, choices=Result.choices)

    class Meta:
        ordering = ("-academic_year",)
        verbose_name_plural = "Education histories"

    def __str__(self):
        return f"{self.student} - {self.class_name} ({self.academic_year})"



