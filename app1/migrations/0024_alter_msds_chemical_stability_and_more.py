# Generated by Django 5.1.3 on 2024-12-10 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0023_alter_msds_phys'),
    ]

    operations = [
        migrations.AlterField(
            model_name='msds',
            name='chemical_stability',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='msds',
            name='conditions_to_avoid',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='msds',
            name='hazardous_decomposition_products',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='msds',
            name='incompatible_materials',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='msds',
            name='information_on_toxicological_effects',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='msds',
            name='possibility_of_hazardous_reactions',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='msds',
            name='reactivity',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='msds',
            name='substance_or_mixture',
            field=models.CharField(blank=True, choices=[('substance', 'Substance'), ('mixture', 'Mixture')], max_length=10, null=True),
        ),
    ]
