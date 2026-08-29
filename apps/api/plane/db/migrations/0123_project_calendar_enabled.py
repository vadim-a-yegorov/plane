from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0122_alter_draftissue_assignees_alter_issue_assignees_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="calendar_enabled",
            field=models.BooleanField(default=False),
        ),
    ]
