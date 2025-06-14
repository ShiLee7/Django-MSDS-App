# Generated by Django 5.1.3 on 2024-11-29 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0017_remove_msds_description_of_first_aid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='msds',
            name='aid_eye',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Necessary measures for eye contact as route of exposure'),
        ),
        migrations.AlterField(
            model_name='msds',
            name='aid_inges',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Necessary measures for ingestion as route of exposure'),
        ),
        migrations.AlterField(
            model_name='msds',
            name='aid_inhal',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Necessary measures for inhalation as route of exposure'),
        ),
        migrations.AlterField(
            model_name='msds',
            name='aid_skin',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Necessary measures for skin contact as route of exposure'),
        ),
        migrations.AlterField(
            model_name='msds',
            name='symp_eye',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Most important symptoms/effects, acute and delayed for eye contact as route of exposure'),
        ),
        migrations.AlterField(
            model_name='msds',
            name='symp_inges',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Most important symptoms/effects, acute and delayed for ingestion as route of exposure'),
        ),
        migrations.AlterField(
            model_name='msds',
            name='symp_inhal',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Most important symptoms/effects, acute and delayed for inhalation as route of exposure'),
        ),
        migrations.AlterField(
            model_name='msds',
            name='symp_skin',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Most important symptoms/effects, acute and delayed for skin contact as route of exposure'),
        ),
    ]
