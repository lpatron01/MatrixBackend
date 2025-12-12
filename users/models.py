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
        LISI = "Licence en Ingénierie des Systèmes Informatiques", "Licence en Ingénierie des Systèmes Informatiques"
        LGMI = "Licence en Génie Mécanique", "Licence en Génie Mécanique"
        LGE = "Licence en Génie énergétique", "Licence en Génie énergétique"
        LEEA = "Licence en électronique électrotechnique & Automatique", "Licence en électronique électrotechnique & Automatique"
        MRDS = "Master Recherche en data science", "Master Recherche en data science"
        MRAII = "Master Recherche en Automatique & Informatique Industrielle", "Master Recherche en Automatique & Informatique Industrielle"
        MPCI = "Master Professionnel en Commandes des Systémes Industriels", "Master Professionnel en Commandes des Systémes Industriels"
        MPGMSI = "Master Professionnel en Gestion de Maintenance des Systémes Industriels", "Master Professionnel en Gestion de Maintenance des Systémes Industriels"
        MPGM = "Master Professionnel en génie mécanique", "Master Professionnel en génie mécanique"

    email = models.EmailField(unique=True)
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
    cin = models.IntegerField(unique=True, null=True, blank=True)
    diploma = models.CharField(
        max_length=80,
        choices=DiplomaChoices.choices,
        help_text="Diplôme obtenu par l'utilisateur.",
    )
    date_of_birth = models.DateField(blank=True, null=True) 
    place_of_birth = models.CharField(max_length=150, blank=True) 
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


class EducationHistory(models.Model):
    class Grade(models.TextChoices):
        FIRST_YEAR = "1ere", "1ère année"
        SECOND_YEAR = "2eme", "2ème année"
        THIRD_YEAR = "3eme", "3ème année"

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
    specialty = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)
    session = models.CharField(max_length=20, choices=Session.choices)
    result = models.CharField(max_length=20, choices=Result.choices)

    class Meta:
        ordering = ("-academic_year",)
        verbose_name_plural = "Education histories"

    def __str__(self):
        return f"{self.student} - {self.class_name} ({self.academic_year})"



