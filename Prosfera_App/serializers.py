from rest_framework import serializers
from .models import Payement_Offrande, Prevoir

# Sérialiseur pour Payement_Offrande
class PayementOffrandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payement_Offrande
        fields = ['nom_offrande', 'departement', 'montant', 'date_payement', 'annee']

# Sérialiseur pour Prevoir
class PrevoirSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prevoir
        fields = ['descript_prevision', 'montant_prevus', 'annee_prevus']