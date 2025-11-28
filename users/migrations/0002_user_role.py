from django.db import migrations, models


def set_default_role(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(role="").update(role="student")


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("student", "Étudiant"),
                    ("teacher", "Enseignant"),
                    ("administrator", "Responsable Administratif"),
                    ("club_manager", "Gestionnaire de Club"),
                ],
                default="student",
                help_text="Profil fonctionnel tel que défini dans le cahier des charges.",
                max_length=32,
            ),
        ),
        migrations.RunPython(set_default_role, migrations.RunPython.noop),
    ]

