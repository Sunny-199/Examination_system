# Generated by Django 4.0.5 on 2022-07-05 13:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0002_remove_imageanswer_image_imageanswer_image_link'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imageanswer',
            name='answer_sheet',
        ),
        migrations.AddField(
            model_name='imageanswer',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='API.topic'),
        ),
    ]
