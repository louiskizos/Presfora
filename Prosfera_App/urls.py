from django.urls import path
from .views import *
from . import views

app_name = "app"
urlpatterns = [
   
    path('', homePage, name='Acceuil'),
    
    path('accounts/login/', loginPage, name='login'),
    path('createAccount', createAccount, name='createAccount'),
    path('CreationUser', CreateUser, name='CreationUser'), #Creation
    path('Change_Password', change_password , name='Change_Password'),
    path('Connexion', connecterUser, name='Connexion'),
    path('Profil', profil, name='Profil'),
    path('Deconnexion', logout, name='Deconnexion'),
    path('Modification', updatePassword, name='Modification'),

    ############ GROUPE OFFRANDES ######################
    path('Groupe_Offrandes', groupeOffrandePage, name='Groupe_Offrandes'),
    path('CreateGroupe', CreateGroupe, name='CreateGroupe'),
    path('Groupe_offrande_data', Groupe_Data, name='Groupe_offrande_data'),
    path('Supprimer_Groupe_Offrande/<uuid:id>/', Supprimmer_Groupe_Offrande, name='Supprimer_Groupe_Offrande'),
    path('Modifier/<uuid:id>/', update_groupe_offrandes, name='Modifier'),
    path('Modifier_Groupe_Offrande/<uuid:id>/', updateGroupeOffrandes, name='Modifier_Groupe_Offrande'),
    path('Pagination_Search_Groupe_Offrande', Pagination_Search_Groupe_Offrande, name='Pagination_Search_Groupe_Offrande'),
    ########### SORTE DES OFFRANDES ########################
    path('Sorte_offrandes', sorte_offrandePage, name='Sorte_offrandes'),
    path('Sorte2_offrandes', sorte_offrandePage2, name='Sorte2_offrandes'),
    path('Minenfant', minenfantPage, name='Minenfant'),
    path('SorteOffrandes', CreateSorteOffrande, name='SorteOffrandes'),
    path('SorteOffrandes_2', CreateSorteOffrande_2, name='SorteOffrandes_2'),
    path('Supprimer_Sorte_Offrande/<uuid:id>/', Supprimmer_Sorte_Offrande, name='Supprimer_Sorte_Offrande'),
    path('Data_offrande', dataOffrandePage, name='Data_offrande'),
    
    ############ GROUPE DES PREVISIONS ###############################
    path('Groupe_Prevision', groupe_previsonPage, name='Groupe_Prevision'),
    path('Create_Groupe_Prevision', CreateGroupe_Prevision, name='Create_Groupe_Prevision'),
    path('Groupe_Prevision_Data', Groupe_Prevision_Data, name='Groupe_Prevision_Data'),
    path('Supprimer_Groupe_Prevision/<uuid:id>/', Supprimmer_Groupe_Prevision, name='Supprimer_Groupe_Prevision'),
    path('Modifier_PrevisionPage/<uuid:id>/', update_groupe_previsions, name='Modifier_PrevisionPage'),
    path('Modifier_Groupe_Prevision/<uuid:id>/', updateGroupePrevision, name='Modifier_Groupe_Prevision'),
    ########### PREVOIR ################################
    
    path('Prevoir', prevoirPage, name='Prevoir'),
    path('Create_Prevision', CreatePrevision, name='Create_Prevision'),
    path('Sorte_Prevision_Data', Sorte_Prevision_Data, name='Sorte_Prevision_Data'),
    
    
    ########### PAYEMENT DES OFFRANDES #########################
    path('Payement_Offrande', payementOffrandePage, name='Payement_Offrande'),
    path('Formulaire_Payement/<uuid:id>/', payementformulairePage, name='Formulaire_Payement'),
    path('Payement', payement, name='Payement'),
    path('Payement_Offrande_Data',Payement_Offrande_Data, name='Payement_Offrande_Data'),
    
    ################ Depense   #########################
    path('Formulaire_Depense/<uuid:id>/', depensePage, name='Depense'),
    path('Decaisser', depenser, name='Decaisser'),
    path('Depense_data', depense_data, name='Depense_data'),
    path('Sortie_data', Sortie_Data, name='Sortie_data'),
    
    ################ AHADI   ##########################
    path('Souscrire_Ahadi', souscrire_ahadi_Page, name='Souscrire_Ahadi'),
    path('Payement_Ahadi', payement_ahadi_Page, name='Payement_Ahadi'),
    path('Formulaire_Ahadi/<uuid:id>/', ahadiformulairePage, name='Formulaire_Ahadi'),
    path('Souscrire', souscrire, name='Souscrire'),
    path('Liste_souscription', liste_souscription, name='Liste_souscription'),
    path('Details/<uuid:id>/', detailPage, name='Details'),
    path('Formulaire_Ahadi_Payement/<uuid:id>/', Formulaire_Ahadi_Payement, name='Formulaire_Ahadi_Payement'),
    path('Payement_ahadi', payement_ahadi, name='Payement_ahadi'),
    path('Payement_ahadi_data', data_payement_ahadi, name='Payement_ahadi_data'),
    ############## Recu #########################
    path('Recu/<uuid:id>/', recuPage, name='Recu'),
    path('Recu_ahadi/<uuid:id>/', recuPage, name='Recu'),
    path('Recu_data', recu_dataPage, name='Recu_data'),
    path('Bon_Sortie/<str:nom>/', bonSortiePage, name='Bon_Sortie'),
    path('Bilan', bilan, name='Bilan'),
    ############# Rapport PDF #####################
    path('Recu_pdf/<uuid:pdf_id>/', recu_pdf, name='Recu_pdf'),
    path('Bon_sorti_pdf/<uuid:pdf_id>/', bon_sorti_pdf, name='generate_sorti_pdf'),
    path('Livre_Caisse', livre_de_caisse, name='Livre_Caisse'),
    path('Bilan_pdf', bilan_pdf, name='Bilan_pdf'),
    path('test', Pagination_Search_Groupe_Offrande, name='test'),
    #################### DATA API #######################
    path('api/presfora-data/', views.get_presfora_data, name='get_presfora_data'),
    

]