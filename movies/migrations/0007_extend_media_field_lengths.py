# Generated manually to extend media field lengths for Cloudinary URLs

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0006_alter_movie_actors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='poster',
            field=models.ImageField(blank=True, null=True, upload_to='posters/', max_length=255),
        ),
        migrations.AlterField(
            model_name='actor',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='actors/', max_length=255),
        ),
        migrations.AlterField(
            model_name='director',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='directors/', max_length=255),
        ),
    ] 