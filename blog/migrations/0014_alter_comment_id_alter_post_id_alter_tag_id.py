# Generated by Django 5.1.2 on 2024-10-27 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_alter_comment_id_alter_post_id_alter_tag_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='post',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='tag',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]