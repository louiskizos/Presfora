# Generated by Django 4.2.20 on 2025-03-25 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Prosfera_App', '0004_alter_payement_offrande_annee_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payement_offrande',
            name='annee',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='prevoir',
            name='annee_prevus',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='prevoir',
            name='montant_prevus',
            field=models.DecimalField(decimal_places=2, max_digits=15),
        ),
        migrations.AlterField(
            model_name='sorte_offrande',
            name='num_compte',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='sorte_prevision',
            name='num_compte',
            field=models.BigIntegerField(),
        ),
    ]
