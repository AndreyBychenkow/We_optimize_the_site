# Generated by Django 5.1.2 on 2024-11-05 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0019_remove_comment_likes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Картинка'),
        ),
    ]