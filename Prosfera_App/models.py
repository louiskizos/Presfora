import uuid
from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers
# Create your models here.



class Groupe_Offrandes(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    num_ordre = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description_recette = models.CharField(max_length=100)
    
    def __str__(self):
        return self.description_recette

class Sorte_Offrande(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descript_recette = models.ForeignKey(Groupe_Offrandes, on_delete=models.CASCADE)
    num_compte = models.IntegerField(max_length=15)
    nom_offrande = models.TextField(max_length=50)
    
    def __str__(self):
        return self.nom_offrande
    

class Payement_Offrande(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom_offrande = models.ForeignKey(Sorte_Offrande, on_delete=models.CASCADE)
    departement = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    date_payement = models.DateField()
    annee = models.IntegerField()
    
    

class CompteArgent(models.Model) :
    
    nom = models.CharField(max_length=100)
    solde = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) :
        return self.nom

class Groupe_Previsions(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    num_ordre = models.CharField(max_length=100)
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    description_prevision = models.CharField(max_length=100)
    
    def __str__(self):
        return self.description_prevision


class Sorte_Prevision(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descript_prevision = models.ForeignKey(Groupe_Previsions, on_delete=models.CASCADE)
    num_compte = models.IntegerField(max_length=15)
    nom_prevision = models.TextField(max_length=50)
    
    def __str__(self):
        return self.nom_prevision
    
class Prevoir(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descript_prevision = models.ForeignKey(Sorte_Prevision, on_delete=models.CASCADE)
    montant_prevus = models.IntegerField(max_length=15)
    annee_prevus = models.IntegerField(max_length=8)
    
    def __str__(self):
        return self.descript_prevision
    
    
class PayementOffrandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payement_Offrande
        fields = ['nom_offrande', 'departement', 'montant', 'date_payement', 'annee']
        
class PrevoirSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prevoir
        fields = ['descript_prevision', 'montant_prevus', 'annee_prevus']