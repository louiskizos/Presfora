
from django.shortcuts import  render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Sum
from Prosfera_App.models import *
from django.contrib.auth import login, update_session_auth_hash
from django.core.paginator import Paginator
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.contrib import messages
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, OuterRef, Subquery
import re
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A5
from num2words import num2words
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.http import HttpResponse, FileResponse
import random
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import Payement_Offrande, Prevoir
from django.db.models import Q


# Create your views here.


def loginPage(request):
    page = 'login/login.html'
    return render(request, page)


def createAccount(request):
    page = 'login/create_account.html'
    return render(request, page)

@login_required
def updatePassword(request):
    
    page = 'login/change_password.html'
    return render(request, page)

@login_required
def profil(request):
    
    page = 'login/profil_user.html'
    return render(request, page)

#LogOut
@login_required
def logout(request):
    auth.logout(request)
    return redirect('app:login')


#Connexion session

def connecterUser(request):
    
    if request.method == 'POST':
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Rechercher l'utilisateur par email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        
        # Authentifier l'utilisateur
        if user and user.check_password(password):
            login(request, user)
            return redirect('app:Acceuil')
        
        else:
            message_erreur = "Désolé, veuillez vérifier vos informations"
            return render(request, 'login/login.html', {'message_erreur': message_erreur})
        
    return render(request, 'login/login.html')

#Create user


def CreateUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Vérification du format de l'email
        try:
            validate_email(email)
        except ValidationError:
            message_erreur = "L'email est invalide."
            return render(request, 'login/create_account.html', {'message_erreur': message_erreur})
        
        # Vérification si l'utilisateur existe déjà par email
        if User.objects.filter(email=email).exists():
            message_erreur = "L'adresse email'utilisateur existe déjà"
            return render(request, 'login/create_account.html', {'message_erreur': message_erreur})
        
        if User.objects.filter(username=username).exists():
            message_erreur = "La fontion de l'utilisateur existe déjà"
            return render(request, 'login/create_account.html', {'message_erreur': message_erreur})
        
        # Vérifier si le nombre d'utilisateurs est déjà 2
        if User.objects.count() >= 4:
            message_erreur = "Le nombre d'utilisateurs est limité à 3."
            return render(request, 'login/create_account.html', {'message_erreur': message_erreur})
        
        else:
            # Création de l'utilisateur
            utilisateur = User(
                username=username,
                email=email
            )
            utilisateur.set_password(password)  # Sécurise le mot de passe
            utilisateur.save()  # Sauvegarde dans la base de données

            return redirect('app:login')  # Redirige vers la page de connexion après l'inscription
    else:
        return render(request, '/logincreate_account.html')



def change_password(request):
    
    if request.method == 'POST':
        
        # Récupérer les données du formulaire
        ancien_mdp = request.POST.get('ancien_mdp')
        nouveau_mdp = request.POST.get('nouveau_mdp')
        confirm_mdp = request.POST.get('confirm_mdp')

        # Vérification de l'ancien mot de passe
        user = request.user  # On récupère l'utilisateur actuellement connecté
        if not user.check_password(ancien_mdp):  # Vérifier si l'ancien mot de passe est correct
            messages.error(request, "L'ancien mot de passe est erroné.")
            return render(request, 'login/change_password.html')
        
        # Vérifier si les nouveaux mots de passe sont identiques
        if nouveau_mdp != confirm_mdp:
            message_erreur = "Les mots de passe ne sont pas identiques."
            return render(request, 'login/change_password.html',{'message_erreur': message_erreur} )
        
        # Vérification si le nouveau mot de passe respecte des conditions (facultatif)
        if len(nouveau_mdp) < 8:  # Exemple : le mot de passe doit avoir au moins 8 caractères
            message_erreur = "Le nouveau mot de passe doit comporter au moins 8 caractères."
            return render(request, 'login/change_password.html', {'message_erreur': message_erreur})
        # Vérification du format du nouveau mot de passe
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        
        if not re.match(password_pattern, nouveau_mdp):
            message_erreur = "Le mot de passe doit contenir au moins : une lettre majuscule, une lettre minuscule, un chiffre et un symbole spécial."
            return render(request, 'login/change_password.html', {'message_erreur': message_erreur})
        # Mise à jour du mot de passe de l'utilisateur
        user.set_password(nouveau_mdp)
        user.save()

        # On met à jour la session pour que l'utilisateur reste connecté après la modification du mot de passe
        update_session_auth_hash(request, user)

        messages_success = "Votre mot de passe a été modifié avec succès."
        return render(request, 'login/change_password.html', {'messages_success': messages_success})  # Rediriger vers la page du profil ou une autre page

    return render(request, 'login/change_password.html')

        
        
        
# fin fin

############## ACCEUIL ###############################
def arrondir(val):
    return val.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


@login_required
def homePage(request):
    
    
    if request.user.is_authenticated:
        
        soldes = Payement_Offrande.objects.filter(type_payement="Entree").aggregate(total=Sum('montant'))['total']
        
        soldes = Decimal(soldes) if soldes is not None else Decimal(0.0)
        depense = Payement_Offrande.objects.filter(type_payement="Sortie").aggregate(total=Sum('montant'))['total']
        depense = Decimal(depense) if depense is not None else Decimal(0.0)
        reste = soldes - depense
        montant_prevu = Prevoir.objects.aggregate(total=Sum('montant_prevus'))['total']
        montant_prevu = Decimal(montant_prevu) if montant_prevu is not None else Decimal(0.0)
        total = (soldes + depense + montant_prevu)
        if total == 0:
                pourcentage_solde = Decimal('0.00')
                pourcentage_depense = Decimal('0.00')
                pourcentage_prevision = Decimal('0.00')
        else:
                pourcentage_solde = arrondir((soldes / total) * 100)
                pourcentage_depense = arrondir((depense / total) * 100)
                pourcentage_prevision = arrondir((montant_prevu / total) * 100)

        data_filter = EtatBesoin.objects.filter(validation_pasteur=False)
        data_etat_count = data_filter.count()
        
        data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
        #data_filtered_caisse = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
        data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
        data_etat_counter = data_filtered.count()

        context = {
            'Soldes': reste,
            'encaissement': soldes,
            'depense': depense,
            'Montant_prevu': montant_prevu,
            'pourcentage_solde' : pourcentage_solde,
            'pourcentage_depense' : pourcentage_depense,
            'pourcentage_prevision' : pourcentage_prevision,
            'data_etat_count_P': data_etat_count,
            'data_etat_count_C': data_etat_counter,
            'data_etat_besoin_false': data_filter,
            'data_etat_besoin_true': data_filtered,
            'data_etat_besoin_true': data_filtered,
        }
        
        page = 'statistic/statistique.html'
        return render(request, page, context)
    else:
        return redirect('app:login')

############### SORTE DES OFFRANDES ########################
@login_required
def sorte_offrandePage(request):
    
    groupe_offrandes =  Groupe_Offrandes.objects.all()[:4]
    
    context = {
        'groupe_offrandes' : groupe_offrandes
    }
    
    page = 'sorte_offrandes/sorte_offrandes.html'
    return render(request, page, context)

@login_required
def sorte_offrandePage2(request):
    
    groupe_offrandes =  Groupe_Offrandes.objects.all()[4:]
    
    context = {
        'groupe_offrandes' : groupe_offrandes
    }
    
    page = 'sorte_offrandes/sorte_offrandes_2.html'
    return render(request, page, context)


@login_required
def Supprimmer_Sorte_Offrande(request, id):
    
    # Récupération de l'objet Groupe_Offrandes ou 404 si non trouvé
    sorte_offrande = Sorte_Offrande.objects.get(id=id)
    
    # Vérifier si ce groupe d'offrande est utilisé dans le modèle Sorte_Offrande
    if Payement_Offrande.objects.filter(nom_offrande=sorte_offrande).exists():
        # Si un ou plusieurs Sorte_Offrande sont liés à ce groupe, empêcher la suppression
        messages.error(request, "Impossible de supprimer cette sorte d'offrande, car elle est déjà utilisé dans un autre cas de payement !")
        return redirect("app:Data_offrande")
        
    # Si aucune sorte d'offrande n'est liée, procéder à la suppression
    sorte_offrande.delete()

    return redirect("app:Data_offrande")

@login_required
def minenfantPage(request):
    
    page = 'minenfant.html'
    return render(request, page)


def CreateSorteOffrande(request):
    
    
    if request.method == 'POST':
        # Récupérer les valeurs envoyées par le formulaire
        descript_recette_id = request.POST.get('descript_recette')  # L'ID de la recette
        num_compte = request.POST.get('num_compte')
        nom_offrande = request.POST.get('nom_offrande')
        
        groupe_offrandes =  Groupe_Offrandes.objects.all()[:4]
        
        if descript_recette_id == "#":
            
            message_erreur = "Le groupe des offrandes est vide !"
            context = {
                'message_erreur': message_erreur,
                'groupe_offrandes' : groupe_offrandes
                }
            return render(request, 'sorte_offrandes/sorte_offrandes.html', context)
        
        
        try:
            # Vérifier si l'ID de la recette existe dans la base de données
            descript_recette = Groupe_Offrandes.objects.get(id=descript_recette_id)
            
        except Groupe_Offrandes.DoesNotExist:
            message_erreur = "La description spécifiée n'existe pas."
            context = {
                'message_erreur': message_erreur,
                'groupe_offrandes' : groupe_offrandes
                }
            return render(request, 'sorte_offrandes/sorte_offrandes.html', context)

        if Sorte_Offrande.objects.filter(num_compte=num_compte).exists():
            message_erreur = "Le numéro du compte existe déjà !"
            context = {
                'message_erreur': message_erreur,
                'groupe_offrandes' : groupe_offrandes
                }
            return render(request, 'sorte_offrandes/sorte_offrandes.html', context)
        
        # Vérification si le numéro de compte existe déjà
        
        
        if Sorte_Offrande.objects.filter(nom_offrande=nom_offrande).exists():
            message_erreur = "Le nom de l'offrande existe déjà !"
            context = {
                'message_erreur': message_erreur,
                'groupe_offrandes' : groupe_offrandes
                }
            return render(request, 'sorte_offrandes/sorte_offrandes.html', context)

        
        # Création de l'enregistrement
        sorte_offrande = Sorte_Offrande(
            descript_recette=descript_recette,  # Assigner l'objet Recette_Budget ici
            num_compte=num_compte,
            nom_offrande=nom_offrande
        )
        
        # Sauvegarde de l'enregistrement
        sorte_offrande.save()
        message_succes = "Enregistrement réussi avec succès !"
        context = {
                'message_succes': message_succes,
                'groupe_offrandes' : groupe_offrandes
                }
        return render(request, 'sorte_offrandes/sorte_offrandes.html', context)
    
    else:
        message_erreur = "Échec d'enregistrement !"
        return render(request, 'sorte_offrandes/sorte_offrandes.html', {'message_erreur': message_erreur, 'sorte_offrandes' : groupe_offrandes})


def CreateSorteOffrande_2(request):
    
    
    if request.method == 'POST':
        # Récupérer les valeurs envoyées par le formulaire
        descript_recette_id = request.POST.get('descript_recette')  # L'ID de la recette
        num_compte = request.POST.get('num_compte')
        nom_offrande = request.POST.get('nom_offrande')
        
        groupe_offrandes =  Groupe_Offrandes.objects.all()[4:]
        try:
            # Vérifier si l'ID de la recette existe dans la base de données
            descript_recette = Groupe_Offrandes.objects.get(id=descript_recette_id)
        except Groupe_Offrandes.DoesNotExist:
            message_erreur = "La description spécifiée n'existe pas."
            context = {
                'message_erreur': message_erreur,
                'groupe_offrandes' : groupe_offrandes
                }
            return render(request, 'sorte_offrandes/sorte_offrandes_2.html', context)

        # Vérification si le numéro de compte existe déjà
        if Sorte_Offrande.objects.filter(num_compte=num_compte).exists():
            message_erreur = "Le numéro du compte existe déjà !"
            context = {
                'message_erreur': message_erreur,
                'groupe_offrandes' : groupe_offrandes
                }
            return render(request, 'sorte_offrandes/sorte_offrandes_2.html', context)
        
        if Sorte_Offrande.objects.filter(nom_offrande=nom_offrande).exists():
            message_erreur = "Le nom de l'offrande existe déjà !"
            context = {
                'message_erreur': message_erreur,
                'groupe_offrandes' : groupe_offrandes
                }
            return render(request, 'sorte_offrandes/sorte_offrandes_2.html', context)

        
        # Création de l'enregistrement
        sorte_offrande = Sorte_Offrande(
            descript_recette=descript_recette,  # Assigner l'objet Recette_Budget ici
            num_compte=num_compte,
            nom_offrande=nom_offrande
        )
        
        # Sauvegarde de l'enregistrement
        sorte_offrande.save()
        message_succes = "Enregistrement réussi avec succès !"
        context = {
                'message_succes': message_succes,
                'groupe_offrandes' : groupe_offrandes
                }
        return render(request, 'sorte_offrandes/sorte_offrandes_2.html', context)
    
    else:
        message_erreur = "Échec d'enregistrement !"
        return render(request, 'sorte_offrandes/sorte_offrandes_2.html', {'message_erreur': message_erreur, 'sorte_offrandes' : groupe_offrandes})

@login_required
def dataOffrandePage(request):
    # Récupération des objets Sorte_Offrande
    data = Sorte_Offrande.objects.all()

    # Paginer les objets (5 éléments par page)
    paginator = Paginator(data, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculer un numéro d'ordre dynamique pour chaque objet sur la page
    for index, objet in enumerate(page_obj, start=1):  # `start=1` commence l'index à 1
        objet.numero_ordre = index  # Assigner le numéro d'ordre à chaque objet

    # Passer les objets à la template
    context = {
        'data': page_obj
    }

    # Rendre la page avec les données paginées et numérotées
    return render(request, 'sorte_offrandes/offrandes_data.html', context)


#### Fin


########### GROUPE DES OFFRANDES #########################
@login_required
def groupeOffrandePage(request):
    
    groupe_offrandes = User.objects.all()
    context = {
        'groupe_offrande' : groupe_offrandes
    }
    page = 'groupe_offrandes/groupe_offrandes.html'
    return render(request, page, context)




@login_required
def CreateGroupe(request):
    
    if request.method == 'POST':
        
        # Récupérer les valeurs envoyées par le formulaire
        user_id = request.POST.get('user')  # L'ID de la recette
        num_ordre = request.POST.get('num_ordre')
        description_recette = request.POST.get('description_recette')
        
        sorte_offrandes =  Sorte_Offrande.objects.all()
        
        try:
            # Vérifier si l'ID de la recette existe dans la base de données
            id_user = User.objects.get(id=user_id)
            
        except User.DoesNotExist:
            message_erreur = "L'utilisateur spécifié n'existe pas."
            return render(request, 'groupe_offrandes/groupe_offrandes.html', {'message_erreur': message_erreur})

        # Vérification si le numéro de compte existe déjà
        if Groupe_Offrandes.objects.filter(description_recette=description_recette).exists():
            message_erreur = "Le nom du groupe d'offrandes existe déjà !"
            return render(request, 'groupe_offrandes/groupe_offrandes.html', {'message_erreur': message_erreur,'sorte_offrande' : sorte_offrandes })

        if Groupe_Offrandes.objects.filter(num_ordre=num_ordre).exists():
            message_erreur = "Le numero du groupe d'offrandes existe déjà !"
            return render(request, 'groupe_offrandes/groupe_offrandes.html', {'message_erreur': message_erreur,'sorte_offrande' : sorte_offrandes })

        
        # Création de l'enregistrement
        recette_budget = Groupe_Offrandes(
            description_recette=description_recette,  # Assigner l'objet Recette_Budget ici
            num_ordre = num_ordre,
            user=id_user,
           
        )
        
        # Sauvegarde de l'enregistrement
        recette_budget.save()
        message_succes = "Enregistrement réussi avec succès !"
        return render(request, 'groupe_offrandes/groupe_offrandes.html', {'message_succes': message_succes, 'sorte_offrande' : sorte_offrandes})
    
    else:
        message_erreur = "Échec d'enregistrement !"
        return render(request, 'groupe_offrandes/groupe_offrandes.html', {'message_erreur': message_erreur, 'sorte_offrande' : sorte_offrandes})


@login_required
def Supprimmer_Groupe_Offrande(request, id):
    
    # Récupération de l'objet Groupe_Offrandes ou 404 si non trouvé
    groupe_offrande = Groupe_Offrandes.objects.get(id=id, user=request.user)
    
    # Vérifier si ce groupe d'offrande est utilisé dans le modèle Sorte_Offrande
    if Sorte_Offrande.objects.filter(descript_recette=groupe_offrande).exists():
        # Si un ou plusieurs Sorte_Offrande sont liés à ce groupe, empêcher la suppression
        messages.error(request, "Impossible de supprimer ce groupe d'offrande, car il est déjà utilisé dans une sorte d'offrande.")
        return redirect("app:Groupe_offrande_data")
        
    # Si aucune sorte d'offrande n'est liée, procéder à la suppression
    groupe_offrande.delete()

    return redirect("app:Groupe_offrande_data")



def update_groupe_offrandes(request, id):

    data = Groupe_Offrandes.objects.get(id=id)

    context = {'groupe_offrandes' : data}
    page = 'groupe_offrandes/update_groupe_offrandes.html'
    
    return render(request, page, context)


login_required
def updateGroupeOffrandes(request, id):

    if request.method == 'POST':
        
        num_ordre = request.POST['num_ordre']
        description_recette = request.POST['description_recette']
        
        data_groupe = Groupe_Offrandes.objects.get(id=id)
        
        data_groupe.num_ordre  = num_ordre
        data_groupe.description_recette = description_recette
        data_groupe.save()
        return redirect('app:Groupe_offrande_data')


@login_required
def recherche_groupe_offrande(request):
    # Initialisation du queryset de base
    groupes_offrande_list = Groupe_Offrandes.objects.filter(user=request.user)
    
    # Récupérer le terme de recherche depuis la requête GET
    search_query = request.GET.get('q', '')  # Par défaut, s'il n'y a pas de recherche, on utilise une chaîne vide
    
    # Si un terme de recherche est fourni, on filtre les objets
    if search_query:
        groupes_offrande_list = groupes_offrande_list.filter(description_recette__icontains=search_query)
        
    # Pagination
    paginator = Paginator(groupes_offrande_list, 5)  # Afficher 10 éléments par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'search_query': search_query  # Passer le terme de recherche pour qu'il apparaisse dans le formulaire
    }
    return render(request, 'groupe_offrandes/pagination.html', context)
  



@login_required
def Pagination_Search_Groupe_Offrande(request):
    # Récupérer tous les objets Groupe_Offrandes pour l'utilisateur connecté
    groupes_offrande_list = Groupe_Offrandes.objects.filter(user=request.user)
    search_query = request.GET.get('q', '')
    
    if search_query:
        groupes_offrande_list = groupes_offrande_list.filter(description_recette__icontains=search_query)
    
    # Pagination : afficher 10 objets par page
    paginator = Paginator(groupes_offrande_list, 5)
    
    # Récupérer le numéro de la page depuis la requête GET
    page_number = request.GET.get('page')
    
    # Obtenir la page actuelle
    page_obj = paginator.get_page(page_number)

    return render(request, 'groupe_offrandes/pagination.html', {'page_obj': page_obj})



@login_required
def Groupe_Data(request): 
    
    # Filtrage des objets Recette_Budget pour l'utilisateur connecté
    #groupe_offrande = Groupe_Offrandes.objects.count() 
    nombre_id = 10  # Par exemple, ou un autre nombre selon votre logique
    range_list = list(range(1, nombre_id + 1))

    data = Groupe_Offrandes.objects.all()
    #groupes_offrande_list = Sorte_Offrande.objects.filter(user=request.user)
    paginator = Paginator(data, 5)  # Afficher 10 éléments par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'groupe_offrandes' : page_obj,
        'range_list' : range_list
    }
    page = 'groupe_offrandes/data_groupe_offrandes.html'
    
    # Rendu de la page
    return render(request, page, context)


######################### GROUPE DES PREVISIONS #####################
@login_required
def groupe_previsonPage(request):
    
    page = 'prevision/groupe_prevision.html'
    return render(request, page)

@login_required
def CreateGroupe_Prevision(request):
    
    if request.method == 'POST':
       
        num_ordre = request.POST.get('num_ordre')
        description_prevision = request.POST.get('description_prevision')
       
        if Groupe_Previsions.objects.filter(num_ordre=num_ordre).exists():
            message_erreur = "Le numero du groupe du prevision existe déjà !"
            return render(request, 'prevision/groupe_prevision.html', {'message_erreur': message_erreur })

        if Groupe_Previsions.objects.filter(description_prevision=description_prevision).exists():
            message_erreur = "Le nom du groupe du prevision existe déjà !"
            return render(request, 'prevision/groupe_prevision.html', {'message_erreur': message_erreur })

        # Création de l'enregistrement
        prevision = Groupe_Previsions(
            
            num_ordre = num_ordre,
            description_prevision=description_prevision           
        )
        
        # Sauvegarde de l'enregistrement
        prevision.save()
        message_succes = "Enregistrement réussi avec succès !"
        return render(request, 'prevision/groupe_prevision.html', {'message_succes': message_succes })
    
    else:
        message_erreur = "Échec d'enregistrement !"
        return render(request, 'prevision/groupe_prevision.html', {'message_erreur': message_erreur})

@login_required
def Supprimmer_Groupe_Prevision(request, id):
    
    
    
    # Récupération de l'objet Groupe_Offrandes ou 404 si non trouvé
    groupe_prevision = Groupe_Previsions.objects.get(id=id)
    
    # Vérifier si ce groupe d'offrande est utilisé dans le modèle Sorte_Offrande
    if Prevoir.objects.filter(descript_prevision=groupe_prevision).exists():
        # Si un ou plusieurs Sorte_Offrande sont liés à ce groupe, empêcher la suppression
        messages.error(request, "Impossible de supprimer ce groupe de prevision, car il est déjà utilisé dans une sorte de pprevision.")
        return redirect("app:Groupe_Prevision_Data")
        
    # Si aucune sorte d'offrande n'est liée, procéder à la suppression
    groupe_prevision.delete()

    return redirect("app:Groupe_Prevision_Data")



@login_required
def  Groupe_Prevision_Data(request): 
    
    nombre_id = 10  # Par exemple, ou un autre nombre selon votre logique
    range_list = list(range(1, nombre_id + 1))

    data = Groupe_Previsions.objects.all()
    #groupes_offrande_list = Sorte_Offrande.objects.filter(user=request.user)
    paginator = Paginator(data, 5)  # Afficher 10 éléments par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'groupe_previsions' : page_obj,
        'range_list' : range_list
    }
    page = 'prevision/data_groupe_prevision.html'
    
    # Rendu de la page
    return render(request, page, context)


def update_groupe_previsions(request, id):

    data = Groupe_Previsions.objects.get(id=id)
    
    context = {'groupe_previsions' : data}
    page = 'prevision/update_groupe_previsions.html'
    
    return render(request, page, context)


@login_required
def updateGroupePrevision(request, id):

    if request.method == 'POST':
        
        num_ordre = request.POST['num_ordre']
        
        
        try:
            
            data_groupe = Groupe_Previsions.objects.get(id=id)
            
            if data_groupe.num_ordre != num_ordre :
                
                data_groupe.num_ordre = num_ordre
                data_groupe.save()
            
            
            return redirect('app:Groupe_Prevision_Data')

        except Groupe_Previsions.DoesNotExist:
            
            return redirect('app:Groupe_Prevision_Data')  # Ou une autre action selon ton besoin

   
    return redirect('app:Groupe_Prevision_Data')

############## SORTE DES PREVISIONS #####################

@login_required
def prevoirPage(request):
    current_date = datetime.now()
 
   # formatted_date = current_date.strftime('%d-%m-%Y')
    formatted_anne = current_date.strftime('%Y')
    data = Groupe_Previsions.objects.all()
    context = {
        'data' : data,
        'data_prevu' : formatted_anne
    }
    page = 'prevoir/formulaire_prevoir.html'
    return render(request, page, context)



@login_required
def CreatePrevision(request):
    
    
    if request.method == 'POST':
        # Récupérer les valeurs envoyées par le formulaire
        descript_prevision = request.POST.get('descript_prevision')  # L'ID de la recette
        num_compte = request.POST.get('num_compte')
        nom_prevision = request.POST.get('nom_prevision')
        annee_prevus = request.POST.get('annee_prevus')
        montant_prevus = request.POST.get('montant_prevus')
        
        
        groupe_previsions =  Groupe_Previsions.objects.all()
        
        current_date = datetime.now()
        formatted_anne = current_date.strftime('%Y')
        
        if descript_prevision == "#":
            
            message_erreur = "Le groupe des previsions est vide !"
            context = {
                'message_erreur': message_erreur,
                'data' : groupe_previsions,
                'data_prevu' : formatted_anne
                }
            return render(request, 'prevoir/formulaire_prevoir.html', context)
        
        
        try:
            # Vérifier si l'ID de la recette existe dans la base de données
            descript_prevision = Groupe_Previsions.objects.get(id=descript_prevision)
            
        except Groupe_Previsions.DoesNotExist:
            message_erreur = "La description spécifiée n'existe pas."
            context = {
                'message_erreur': message_erreur,
                'data' : groupe_previsions
                }
            return render(request, 'prevoir/formulaire_prevoir.html', context)

        if Prevoir.objects.filter(num_compte=num_compte).exists():
            message_erreur = "Le numéro du compte existe déjà !"
            context = {
                'message_erreur': message_erreur,
                'data' : groupe_previsions,
                'data_prevu' : formatted_anne
                }
            return render(request, 'prevoir/formulaire_prevoir.html', context)
        
        # Vérification si le numéro de compte existe déjà
        
        
        if Prevoir.objects.filter(nom_prevision=nom_prevision).exists():
            message_erreur = "Le nom de la prevision existe déjà !"
            context = {
                'message_erreur': message_erreur,
                'data' : groupe_previsions,
                'data_prevu' : formatted_anne
                }
            return render(request, 'prevoir/formulaire_prevoir.html', context)

        
        # Création de l'enregistrement
        prevision = Prevoir(
            descript_prevision=descript_prevision,  # Assigner l'objet Recette_Budget ici
            num_compte=num_compte,
            montant_prevus=montant_prevus,
            nom_prevision=nom_prevision,
            annee_prevus = annee_prevus
        )
        
        # Sauvegarde de l'enregistrement
        prevision.save()
        message_succes = "Enregistrement réussi avec succès !"
        context = {
                'message_succes': message_succes,
                'data' : groupe_previsions,
                'data_prevu' : formatted_anne
                }
        return render(request, 'prevoir/formulaire_prevoir.html', context)
    
    else:
        message_erreur = "Échec d'enregistrement !"
        return render(request, 'prevoir/formulaire_prevoir.html', {'message_erreur': message_erreur, 'data' : groupe_previsions})



@login_required
def  Sorte_Prevision_Data(request): 
    
    nombre_id = 10  
    range_list = list(range(1, nombre_id + 1))

    data = Prevoir.objects.all()
    
    paginator = Paginator(data, 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'data' : page_obj,
        'range_list' : range_list
    }
    page = 'prevoir/prevision_data.html'
    
    # Rendu de la page
    return render(request, page, context)

############## PAYEMENT DES OFFRANDES ###################

@login_required
def payementOffrandePage(request):

    search_query = request.GET.get('q', '').strip()

    data = Sorte_Offrande.objects.exclude(
        descript_recette__description_recette="Engagement des adhérents"
    )

    
    if search_query:
        
        mots = search_query.split()
        query = Q()
        for mot in mots:
            query &= Q(nom_offrande__icontains=mot)

        data = data.filter(query)

  
    paginator = Paginator(data, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    start_index = page_obj.start_index()
    for index, objet in enumerate(page_obj, start=start_index):
        objet.numero_ordre = index

    context = {
        'data': page_obj,
        'search_query': search_query,
    }

    return render(request, 'payement_offrande/payement_offrandes.html', context)


@login_required
def payementformulairePage(request, id):
    
    current_date = datetime.now()
 
    formatted_date = current_date.strftime('%d-%m-%Y')
    formatted_anne = current_date.strftime('%Y')
    data = Sorte_Offrande.objects.get(id=id)
    
    context = {
        'data' : data,
        'date_paiement' : formatted_date,
        'annee_paiement' : formatted_anne,
        }
    page = 'payement_offrande/formulaire_payement.html'
    return render(request, page, context )



@login_required
def payement(request):
    
    if request.method == 'POST':
        
        
        nom_offrande_id = request.POST.get('nom_offrande')  
        departement = request.POST.get('departement')
        type_payement = "Entree"
        montant = request.POST.get('montant')
        montant_lettre = num2words(montant, lang='fr', to='currency', currency='USD')
        motif = request.POST.get('motif')
        date_payement = request.POST.get('date_payement')
        annee = request.POST.get('annee')
        
        
        try:
            
            nom_offrande = Sorte_Offrande.objects.get(id=nom_offrande_id)
        except Sorte_Offrande.DoesNotExist:
            message_erreur = "Le nom d'offrande spécifiée n'existe pas."
            context = {'message_erreur': message_erreur}
            return render(request, 'payement_offrande/formulaire_payement.html', context)
        
        
        try:
            montant = Decimal(montant)
        except (ValueError,):
            message_erreur = "Le montant n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'payement_offrande/formulaire_payement.html', context)
        
        
        try:
            annee = int(annee)
        except ValueError:
            message_erreur = "L'année n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'payement_offrande/formulaire_payement.html', context)
        
        
        try:
            date_payement = datetime.strptime(date_payement, '%d-%m-%Y').date()
        except ValueError:
            message_erreur = "La date de paiement n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'payement_offrande/formulaire_payement.html', context)
        
        
        payement_offrande = Payement_Offrande(
            nom_offrande=nom_offrande,  
            departement=departement,
            type_payement=type_payement,
            montant=montant,
            montant_lettre=montant_lettre,
            motif = motif,
            date_payement=date_payement,
            annee=annee
        )
        
        
        payement_offrande.save()
        message_succes = "Paiement réussi avec succès !"
        context = {'message_succes': message_succes}
        return render(request, 'payement_offrande/formulaire_payement.html', context)
    
    else:
        message_erreur = "Échec du paiement !"
        return render(request, 'payement_offrande/formulaire_payement.html', {'message_erreur': message_erreur})

@login_required
def  Payement_Offrande_Data(request): 

    
    data = Payement_Offrande.objects.all()

    
    paginator = Paginator(data, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for index, objet in enumerate(page_obj, start=1):
        objet.numero_ordre = index 

    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filteredFalse.count()

    context = {
        'data': page_obj,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }

    
    return render(request, 'payement_offrande/data_payement_offrande.html', context)


def editer_payement(request, id):

    try:
        data = Payement_Offrande.objects.get(id=id, )
        
    except Payement_Offrande.DoesNotExist:
        return render(request, '404.html', status=404)

    
    context = {
        'payement' : data,
        
        }
    return render(request, 'payement_offrande/editer_payement_offrandes.html', context)

def modification_payement(request, id):

    payement = get_object_or_404(Payement_Offrande, id=id)

    if request.method == 'POST':
        departement = request.POST.get('departement')
        montant = request.POST.get('montant')
        motif = request.POST.get('motif')

        # Mise à jour
        payement.departement = departement
        payement.montant = montant
        payement.motif = motif
        payement.save()

        return redirect('app:Recu_data')
    
    return render(request, 'payement_offrande/editer_payement_offrandes.html', {'payement': payement})


############# DEPENSE ####################
def depensePage(request, solde):

    current_date = datetime.now()
    formatted_date = current_date.strftime('%d-%m-%Y')
    formatted_annee = current_date.strftime('%Y')

    etat_not_id = request.POST.get('etat_not_id') or request.GET.get('etat_not_id')

    etat_obj = None
    if etat_not_id:
        etat_obj = get_object_or_404(EtatBesoin, id=etat_not_id)


    queryset = Payement_Offrande.objects.filter(type_payement="Entree")

    depense_list = (
        queryset
        .values('nom_offrande__nom_offrande', 'nom_offrande__num_compte', 'nom_offrande_id')
        .annotate(total_montant=Sum('montant'))
        .order_by('nom_offrande__nom_offrande')
    )

    data = depense_list.filter(total_montant=solde).first() if depense_list else None
    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filteredFalse.count()


    context = {
        'data': data,
        'date_paiement': formatted_date,
        'annee_paiement': formatted_annee,
        'etat_not_id': etat_not_id,
        'etat_obj': etat_obj,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }

    return render(request, 'depense/formulaire_depense.html', context)



def depenser(request):
    if request.method == 'POST':
        nom_offrande_id = request.POST.get('nom_offrande')
        departement = request.POST.get('departement')
        type_payement = "Sortie"
        montant = request.POST.get('montant')
        etat_montant = request.POST.get('etat_montant')
        motif = request.POST.get('motif')
        date_payement = request.POST.get('date_payement')
        annee = request.POST.get('annee')
        solde = request.POST.get('solde')
        validation_caisse = True
        etat_not_id = request.POST.get('etat_not_id')

        current_date = datetime.now()
        formatted_date = current_date.strftime('%d-%m-%Y')
        formatted_anne = current_date.strftime('%Y')

        data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
        data_etat_counter = data_filtered.count()
        data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
        data_etat_counter_P = data_filteredFalse.count()

        etat_obj = None
        if etat_not_id:
            etat_obj = get_object_or_404(EtatBesoin, id=etat_not_id)

        try:
            nom_offrande = Sorte_Offrande.objects.get(id=nom_offrande_id)
        except Sorte_Offrande.DoesNotExist:
            return render(request, 'depense/formulaire_depense.html', {
                'message_erreur': "Le nom d'offrande spécifié n'existe pas.",
                'date_paiement': formatted_date,
                'annee_paiement': formatted_anne,
                'etat_not_id': etat_not_id,
                'etat_obj': etat_obj,
                'data_etat_count_C': data_etat_counter,
                'data_etat_besoin_true': data_filtered,
                'data_etat_besoin_false': data_filteredFalse,
                'data_etat_count_P': data_etat_counter_P,
            })

        try:
            montant = Decimal(montant)
        except (ValueError, InvalidOperation):
            return render(request, 'depense/formulaire_depense.html', {
                'message_erreur': "Le montant n'est pas valide.",
                'date_paiement': formatted_date,
                'etat_not_id': etat_not_id,
                'etat_obj': etat_obj,
                'data_etat_count_C': data_etat_counter,
                'data_etat_besoin_true': data_filtered,
                'data_etat_besoin_false': data_filteredFalse,
                'data_etat_count_P': data_etat_counter_P,
            })

        try:
            etat_montant = Decimal(etat_montant)
        except (ValueError, InvalidOperation):
            return render(request, 'depense/formulaire_depense.html', {
                'message_erreur': "Le montant n'est pas valide.",
                'etat_not_id': etat_not_id,
                'etat_obj': etat_obj,
                'data_etat_count_C': data_etat_counter,
                'data_etat_besoin_true': data_filtered,
                'data_etat_besoin_false': data_filteredFalse,
                'data_etat_count_P': data_etat_counter_P,
            })

        try:
            solde = Decimal(solde)
        except (ValueError, InvalidOperation):
            return render(request, 'depense/formulaire_depense.html', {
                'message_erreur': "Le solde n'est pas valide.",
                'date_paiement': formatted_date,
                'etat_not_id': etat_not_id,
                'etat_obj': etat_obj,
                'data_etat_count_C': data_etat_counter,
                'data_etat_besoin_true': data_filtered,
                'data_etat_besoin_false': data_filteredFalse,
                'data_etat_count_P': data_etat_counter_P,
            })

        try:
            annee = int(annee)
        except ValueError:
            return render(request, 'depense/formulaire_depense.html', {
                'message_erreur': "L'année n'est pas valide.",
                'date_paiement': formatted_date,
                'etat_not_id': etat_not_id,
                'etat_obj': etat_obj,
                'data_etat_count_C': data_etat_counter,
                'data_etat_besoin_true': data_filtered,
                'data_etat_besoin_false': data_filteredFalse,
                'data_etat_count_P': data_etat_counter_P,
            })

        try:
            date_payement = datetime.strptime(date_payement, '%d-%m-%Y').date()
        except ValueError:
            return render(request, 'depense/formulaire_depense.html', {
                'message_erreur': "La date de paiement n'est pas valide.",
                'etat_not_id': etat_not_id,
                'etat_obj': etat_obj,
                'data_etat_count_C': data_etat_counter,
                'data_etat_besoin_true': data_filtered,
                'data_etat_besoin_false': data_filteredFalse,
                'data_etat_count_P': data_etat_counter_P,
            })

        # Ici tu peux continuer avec la logique de création de la dépense si tout est valide
        # if isinstance(date_payement, str):
        #     try:
        #         date_payement = datetime.strptime(date_payement, '%Y-%m-%d').date()
        #     except ValueError:
        #         return render(request, 'depense/formulaire_depense.html', {
        #             'message_erreur': "La date de paiement n'est pas valide.",
        #             'data_etat_count_C': data_etat_counter,
        #             'data_etat_besoin_true': data_filtered,
        #             'data_etat_besoin_false': data_filteredFalse,
        #             'data_etat_count_P': data_etat_counter_P,
        #         })

        if montant > solde:
            return render(request, 'depense/formulaire_depense.html', {
                'message_erreur': "Le montant dépasse le solde disponible.",
                'date_paiement': formatted_date,

        'etat_not_id': etat_not_id,
        'etat_obj': etat_obj,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
        
            })
        
        
        if montant > etat_montant:
            return render(request, 'depense/formulaire_depense.html', {
                'message_erreur': "Le montant dépasse l'état de besoin.",
                'date_paiement': formatted_date,

        'etat_not_id': etat_not_id,
        'etat_obj': etat_obj,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
        
            })

        montant_lettre = num2words(montant, lang='fr', to='currency', currency='USD')

        decaisser_offrande = Payement_Offrande(
            nom_offrande=nom_offrande,
            departement=departement,
            type_payement=type_payement,
            montant=montant,
            montant_lettre=montant_lettre,
            motif=motif,
            date_payement=date_payement,
            annee=annee
        )
        decaisser_offrande.save()
        etat_obj.validation_caisse = validation_caisse
        etat_obj.save()

        return redirect('app:Depense_data')

    return render(request, 'depense/formulaire_depense.html')



@login_required
def depense_data(request):
    search_query = request.GET.get('q', '').strip()

    entrees = Payement_Offrande.objects.filter(type_payement="Entree")
    sorties = Payement_Offrande.objects.filter(type_payement="Sortie")

    if search_query:
        entrees = entrees.filter(nom_offrande__nom_offrande__icontains=search_query)
        sorties = sorties.filter(nom_offrande__nom_offrande__icontains=search_query)

    total_entree = entrees.values(
        'nom_offrande__nom_offrande',
        'nom_offrande__num_compte',
        'nom_offrande_id'
    ).annotate(
        total_montant=Sum('montant')
    )

    total_sortie = sorties.values(
        'nom_offrande_id'
    ).annotate(
        total_montant_depense=Sum('montant')
    )

    depenses_map = {item['nom_offrande_id']: item['total_montant_depense'] for item in total_sortie}

    resultat = []
    for item in total_entree:
        offrande_id = item['nom_offrande_id']
        montant_sortie = depenses_map.get(offrande_id, 0)
        solde = item['total_montant'] - montant_sortie
        resultat.append({
            'nom_offrande__nom_offrande': item['nom_offrande__nom_offrande'],
            'nom_offrande__num_compte': item['nom_offrande__num_compte'],
            'solde': solde,
            'total_montant': item['total_montant'],
            'total_montant_depense': montant_sortie,
            'nom_offrande_id': offrande_id,
        })

    paginator = Paginator(resultat, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    start_index = page_obj.start_index()
    for index, obj in enumerate(page_obj, start=start_index):
        obj['numero_ordre'] = index

    data_filtered_true = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter_C = data_filtered_true.count()

    data_filtered_false = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filtered_false.count()

    etat_not_id = request.POST.get('etat_not_id') if request.method == 'POST' else None

    context = {
        'data': page_obj,
        'search_query': search_query,
        'data_etat_besoin_true': data_filtered_true,
        'data_etat_besoin_false': data_filtered_false,
        'data_etat_count_C': data_etat_counter_C,
        'data_etat_count_P': data_etat_counter_P,
        'etat_not_id': etat_not_id,
    }

    return render(request, 'depense/data_depense.html', context)


@login_required
def Sortie_Data(request):
    
    data = Payement_Offrande.objects.filter(type_payement="Sortie").order_by('date_payement')

    paginator = Paginator(data, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filteredFalse.count()

    context = {
        'data': page_obj,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }

    
    return render(request, 'depense/sortie_data.html', context)


def bonSortiePage(request, nom):

    
    try:
        nom_beneficiaire_cible = nom  # Utilisez la variable 'nom' de votre requête initiale
        
        data = Payement_Offrande.objects.filter(departement=nom_beneficiaire_cible)
        random_nombre = random.randint(1000, 9999)
        total_montant = sum([item.montant for item in data], Decimal(0))
        montant_en_lettre = num2words(total_montant, lang='fr').capitalize()

        context = {
            'data' : data, 
            'rand' : random_nombre,
            'total_montant': total_montant,
            'montant_en_lettre': montant_en_lettre,
            
            }
        
        page = 'rapport/bon_sortie.html'
        return render(request, page, context)
        
    except ObjectDoesNotExist: # type: ignore
        # Gérer le cas où aucun objet Depense n'est trouvé pour ce nom
        context = {'error_message': f"Aucune dépense trouvée pour le bénéficiaire '{nom}'."}
        page = 'rapport/bon_sortie.html'  # Vous pouvez créer une page d'erreur spécifique
        return render(request, page, context)

def editer_depense(request, id):

    data = Payement_Offrande.objects.get(id=id)
    
    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filteredFalse.count()


    context = {
        'data': data,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }

    return render(request, 'depense/editer_depense.html', context)

#################### AHADI #######################

@login_required
def souscrire_ahadi_Page(request):

    search_query = request.GET.get('q', '').strip()

    
    data = Sorte_Offrande.objects.filter(
        descript_recette__description_recette__icontains="Engagement des adhérents"
    )

    
    if search_query:
        data = data.filter(nom_offrande__icontains=search_query)

    # Pagination
    paginator = Paginator(data, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    
    start_index = page_obj.start_index()
    for index, objet in enumerate(page_obj, start=start_index):
        objet.numero_ordre = index

    context = {
        'data': page_obj,
        'search_query': search_query,
    }

    return render(request, 'ahadi/souscrire_ahadi.html', context)


@login_required
def payement_ahadi_Page(request):
    
    search_query = request.GET.get('q', '').strip()

    data = Ahadi.objects.all()


    
    if search_query:
        
        mots = search_query.split()
        query = Q()
        for mot in mots:
            query &= Q(nom_postnom__icontains=mot)

        data = data.filter(query)

  
    paginator = Paginator(data, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    start_index = page_obj.start_index()
    for index, objet in enumerate(page_obj, start=start_index):
        objet.numero_ordre = index


    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filtered.count()


    context = {
        'data': page_obj,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        'search_query': search_query,
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }
    return render(request, 'ahadi/liste_ahadi_doit_payer.html', context)



@login_required
def ahadiformulairePage(request, id):
    
    current_date = datetime.now()
    
    
    formatted_date = current_date.strftime('%d-%m-%Y')
    formatted_anne = current_date.strftime('%Y')
    data = Sorte_Offrande.objects.get(id=id)
    
    context = {
        'data' : data,
        'date_paiement' : formatted_date,
        'annee_paiement' : formatted_anne,
        }
    page = 'ahadi/formulaire_ahadi.html'
    return render(request, page, context )

@login_required
def detailPage(request, id):

  
    data2 = get_object_or_404(Ahadi, id=id)
    data = Payement_Offrande.objects.filter(nom_offrande=data2.nom_offrande)
    
    # Calcul des sommes cumulées
    cumulative_sums = []
    current_sum = 0

    for item in data:
        
        current_sum += item.montant or 0
        cumulative_sums.append(current_sum)

    
    processed_data = []
    for i, item in enumerate(data):
        processed_data.append({
            'op': item,
            'cumulative_sum': cumulative_sums[i]
        })
    difference = data2.montant - data.first().montant if data.exists() else 0

    context = {
        'data': processed_data,
        'ahadi': data2,
        'reste': difference
    }
    return render(request, 'ahadi/detail.html', context)

@login_required
def formulaire_ahadi_payement(request, id):
    
    current_date = datetime.now()
    
    # Tu peux aussi formater la date selon ton besoin
    formatted_date = current_date.strftime('%d-%m-%Y')
    formatted_anne = current_date.strftime('%Y')
    
    try:
        data = Ahadi.objects.get(id=id, )
    except Ahadi.DoesNotExist:
        return render(request, '404.html', status=404)

    
    context = {
        'data' : data,
        'date_paiement' : formatted_date,
        'annee_paiement' : formatted_anne,
        }
    page = 'ahadi/formulaire_payement_ahadi.html'
    return render(request, page, context )



@login_required
def payement_ahadi(request):
    
    if request.method == 'POST':
        
        # Récupérer les valeurs envoyées par le formulaire
        nom_offrande_id = request.POST.get('nom_offrande')  # L'ID de la recette
        departement = request.POST.get('departement')
        type_payement = "Entree"
        montant = request.POST.get('montant')
        montant_lettre = num2words(montant, lang='fr', to='currency', currency='USD')
        motif = request.POST.get('motif')
        date_payement = request.POST.get('date_payement')
        annee = request.POST.get('annee')
        
        # Validation des données
        try:
            # Vérifier si l'ID de la recette existe dans la base de données
            nom_offrande = Sorte_Offrande.objects.get(id=nom_offrande_id)
        except Sorte_Offrande.DoesNotExist:
            message_erreur = "Le nom d'offrande spécifiée n'existe pas."
            context = {'message_erreur': message_erreur}
            return render(request, 'ahadi/formulaire_payement_ahadi.html', context)
        
        # Vérification du montant (doit être un nombre décimal)
        try:
            montant = Decimal(montant)
        except (ValueError,):
            message_erreur = "Le montant n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'ahadi/formulaire_payement_ahadi.html', context)
        
        # Vérification de l'année (doit être un entier)
        try:
            annee = int(annee)
        except ValueError:
            message_erreur = "L'année n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'ahadi/formulaire_payement_ahadi.html', context)
        
        # Vérifier la date de paiement (assurez-vous qu'elle est dans un format valide)
        try:
            date_payement = datetime.strptime(date_payement, '%d-%m-%Y').date()
        except ValueError:
            message_erreur = "La date de paiement n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'ahadi/formulaire_payement_ahadi.html', context)
        
        # Création de l'enregistrement
        payement_offrande = Payement_Offrande(
            nom_offrande=nom_offrande,  # Assigner l'objet Sorte_Offrande ici
            departement=departement,
            montant=montant,
            type_payement=type_payement,
            montant_lettre=montant_lettre,
            motif = motif,
            date_payement=date_payement,
            annee=annee
        )
        
        # Sauvegarde de l'enregistrement
        payement_offrande.save()
        message_succes = "Paiement réussi avec succès !"
        context = {'message_succes': message_succes}
        return render(request, 'ahadi/formulaire_payement_ahadi.html', context)
    
    else:
        message_erreur = "Échec du paiement !"
        return render(request, 'ahadi/formulaire_payement_ahadi.html', {'message_erreur': message_erreur})


@login_required
def souscrire(request):
    
    if request.method == 'POST':
        
        # Récupérer les valeurs envoyées par le formulaire
        nom_offrande_id = request.POST.get('nom_offrande')  # L'ID de la recette
        nom_postnom = request.POST.get('nom_postnom')
        montant = request.POST.get('montant')
        montant_lettre = num2words(montant, lang='fr', to='currency', currency='USD')
        motif = request.POST.get('motif')
        date_ahadi = request.POST.get('date_ahadi')
        annee = request.POST.get('annee')
        
        # Validation des données
        try:
            # Vérifier si l'ID de la recette existe dans la base de données
            nom_offrande = Sorte_Offrande.objects.get(id=nom_offrande_id)
        except Sorte_Offrande.DoesNotExist:
            message_erreur = "Le nom d'offrande spécifiée n'existe pas."
            context = {'message_erreur': message_erreur}
            return render(request, 'ahadi/formulaire_ahadi.html', context)
        
        # Vérification du montant (doit être un nombre décimal)
        try:
            montant = Decimal(montant)
        except (ValueError,):
            message_erreur = "Le montant n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'ahadi/formulaire_ahadi.html', context)
        
        # Vérification de l'année (doit être un entier)
        try:
            annee = int(annee)
        except ValueError:
            message_erreur = "L'année n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'ahadi/formulaire_ahadi.html', context)
        
        # Vérifier la date de paiement (assurez-vous qu'elle est dans un format valide)
        try:
            date_ahadi = datetime.strptime(date_ahadi, '%d-%m-%Y').date()
        except ValueError:
            message_erreur = "La date de paiement n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'ahadi/formulaire_ahadi.html', context)
        
        # Création de l'enregistrement
        souscription_ahadi = Ahadi(
            nom_offrande=nom_offrande,  # Assigner l'objet Sorte_Offrande ici
            nom_postnom=nom_postnom,
            montant=montant,
            montant_lettre=montant_lettre,
            motif = motif,
            date_ahadi=date_ahadi,
            annee=annee
        )
        
        # Sauvegarde de l'enregistrement
        souscription_ahadi.save()
        message_succes = "Souscription réussie avec succès !"
        context = {'message_succes': message_succes}
        return render(request, 'ahadi/formulaire_ahadi.html', context)
    
    else:
        message_erreur = "Échec de la souscription !"
        return render(request, 'ahadi/formulaire_ahadi.html', {'message_erreur': message_erreur})

@login_required
def data_payement_ahadi(request):
      
    #data = Payement_Offrande.objects.all()



    search_query = request.GET.get('q', '').strip()

    
    #data = Payement_Offrande.objects.exclude(nom_offrande__descript_recette__description_recette="Engagement des adhérents")
    data = Payement_Offrande.objects.filter(nom_offrande__descript_recette__description_recette="Engagement des adhérents")


    
    if search_query:
        
        mots = search_query.split()
        query = Q()
        for mot in mots:
            query &= Q(departement__icontains=mot)

        data = data.filter(query)

  
    paginator = Paginator(data, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    start_index = page_obj.start_index()
    for index, objet in enumerate(page_obj, start=start_index):
        objet.numero_ordre = index

    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filtered.count()


    context = {
        'data': page_obj,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        'search_query': search_query,
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }
    page = 'ahadi/payement_ahadi_data.html'
    return render(request, page, context )



@login_required
def liberation_ahadi(request):

    search_query = request.GET.get('q', '')

    engagements = Ahadi.objects.all()

    if search_query:
        engagements = engagements.filter(nom_postnom__icontains=search_query)

    
    paiements = Payement_Offrande.objects.filter(
        type_payement="Entree",
        nom_offrande=OuterRef('nom_offrande'),
        departement=OuterRef('nom_postnom'), 
        nom_offrande__descript_recette__description_recette="Engagement des adhérents"
    ).values('nom_offrande', 'departement').annotate(
        total_paye=Sum('montant')
    ).values('total_paye')

    
    engagements = engagements.annotate(
        total_paye=Subquery(paiements, output_field=models.DecimalField(max_digits=15, decimal_places=2)),
    )

    
    for e in engagements:
        e.reste = (e.montant or 0) - (e.total_paye or 0)
        

    
    paginator = Paginator(engagements, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    start_index = page_obj.start_index()
    for index, obj in enumerate(page_obj, start=start_index):
        obj.numero_ordre = index


    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filteredFalse.count()

    context = {
        'data': page_obj,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }
    return render(request, 'ahadi/liberation_ahadi.html', context)


def editer_souscription_ahadi(request, id):

    
    current_date = datetime.now()

    formatted_date = current_date.strftime('%d-%m-%Y')
    formatted_anne = current_date.strftime('%Y')
    
    try:
        data = Ahadi.objects.get(id=id, )
        
    except Ahadi.DoesNotExist:
        return render(request, '404.html', status=404)

    
    context = {
        'data' : data,
        'date_paiement' : formatted_date,
        'annee_paiement' : formatted_anne,
        }
    return render(request, 'ahadi/editer_souscription_ahadi.html', context)


def editer_payement_ahadi(request, id):

    try:
        data = Payement_Offrande.objects.get(id=id, )
        
    except Payement_Offrande.DoesNotExist:
        return render(request, '404.html', status=404)

    
    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filtered.count()


    context = {
        'payement': data,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }
    return render(request, 'ahadi/editer_payement_ahadi.html', context)



def modifier_ahadi_payement(request, id):

    payement = get_object_or_404(Payement_Offrande, id=id)

    if request.method == 'POST':
        departement = request.POST.get('departement')
        montant = request.POST.get('montant')
        motif = request.POST.get('motif')

        # Mise à jour
        payement.departement = departement
        payement.montant = montant
        payement.motif = motif
        payement.save()

        return redirect('app:Payement_ahadi_data')
    return render(request, 'payement_offrande/editer_payement_ahadi.html', {'payement': payement})

    

####################### FIN Ahadi #########################

def recuPage(request, id):
    
    data = Payement_Offrande.objects.get(id=id)
    random_nombre = random.randint(1000, 9999)
    context = {'data' : data, 'rand' : random_nombre}
    page = 'rapport/recu.html'
    return render(request, page, context )


def recu_dataPage(request):
      
    #data = Payement_Offrande.objects.all()
    search_query = request.GET.get('q', '').strip()

    
    data = Payement_Offrande.objects.exclude(nom_offrande__descript_recette__description_recette="Engagement des adhérents")


    
    if search_query:
        
        mots = search_query.split()
        query = Q()
        for mot in mots:
            query &= Q(departement__icontains=mot)

        data = data.filter(query)

  
    paginator = Paginator(data, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    start_index = page_obj.start_index()
    for index, objet in enumerate(page_obj, start=start_index):
        objet.numero_ordre = index


   
    context = {
        'data': page_obj,
        'search_query': search_query,
    }

    page = 'rapport/recu_data.html'
    return render(request, page, context )

################## ETAT DE BESOIN ###################

@login_required
def etatBsesionformulairePage(request):
    
    page = 'etat_besoin/etat_besoin.html'
    
    current_date = datetime.now()
    
    
    formatted_date = current_date.strftime('%d-%m-%Y')
    #formatted_anne = current_date.strftime('%Y')
   
    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filtered.count()


    context = {
        'data': formatted_date,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }
    return render(request, page, context )


@login_required
def etatBsesionformulaireData(request):
    
    page = 'etat_besoin/etat_besoin_data.html'
    
    
    data = EtatBesoin.objects.all()


    paginator = Paginator(data, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    start_index = page_obj.start_index()
    for i, obj in enumerate(page_obj, start=start_index):
        obj.numero_ordre = i 

    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filteredFalse.count()

    context = {
        'data': page_obj,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }
    return render(request, page, context)



@login_required
def notificat_etat_besoinPage(request, id):


    try:
        data = EtatBesoin.objects.get(id=id)
    except EtatBesoin.DoesNotExist:
        messages.error(request, "Cette demande n'existe pas.")
        return redirect("app:Etat_Besoin")  
    
    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_filtered_caisse = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filteredFalse.count()

    context = {
        'data': data,
        'data_etat_besoin_caisse': data_filtered_caisse,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }

    return render(request, 'etat_besoin/validation_pasteur.html', context)


@login_required
def soumettre_etat_besoin(request):
    if request.method == 'POST':
        
        service = request.POST.get('service')
        designation = request.POST.get('designation')
        montant = request.POST.get('montant')
        quantite = request.POST.get('quantite')
        motif = request.POST.get('motif')
        date_etat_besoin = request.POST.get('date_etat_besoin')
        
        
        try:
            montant = Decimal(montant)
        except (ValueError,):
            message_erreur = "Le montant n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'etat_besoin/etat_besoin_form.html', context)
        
        
        try:
            date_etat_besoin = datetime.strptime(date_etat_besoin, '%d-%m-%Y').date()
        except ValueError:
            message_erreur = "La date de l'état de besoin n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'etat_besoin/etat_besoin.html', context)
    
        try:
            etat_besoin = EtatBesoin(
                service=service,
                montant=montant,
                designation=designation,
                quantite=quantite,
                motif=motif,
                date_etat_besoin=date_etat_besoin,
                validation_pasteur=False, 
                validation_caisse=False,  
            )
            
            etat_besoin.save()
            #message_succes = "L'état de besoin a été créé avec succès !"
            #context = {'message_succes': message_succes}
            return redirect('app:Etat_Besoin_Data')
        
        except Exception as e:
            message_erreur = f"Une erreur est survenue : {e}"
            context = {'message_erreur': message_erreur}
            return render(request, 'etat_besoin/etat_besoin.html', context)
    
    else:
        
        return render(request, 'etat_besoin/etat_besoin.html')
    

def valider_etatBesoin(request, id):

    if request.method == 'POST':
        
        
        validation_pasteur = request.POST['validation_pasteur']
        #commentaire_pasteur = request.POST['commentaire_pasteur']
        
        try:
            
            data = EtatBesoin.objects.get(id=id)
            data.validation_pasteur = validation_pasteur
        
            data.save()
            
            
            return redirect('app:Etat_Besoin_Data')

        except EtatBesoin.DoesNotExist:
            
            return redirect('app:Etat_Besoin_Data')

   
    return redirect('app:Etat_Besoin_Data')
    


#################### RAPPORT PDF ##########################


def custom_404(request, exception):
    return render(request, 'et.html', {}, status=404)


############ DATA POUR LES GRAPHIQUES ##############

@api_view(['GET'])
def get_presfora_data(request):

    
    payement_entree = Payement_Offrande.objects.exclude(type_payement='Entreenom_offrande')\
        .values('annee').annotate(total_payement=Sum('montant')).order_by('annee')

    # Sorties
    payement_sortie = Payement_Offrande.objects.filter(type_payement='Sortie')\
        .values('annee').annotate(total_depense=Sum('montant')).order_by('annee')

    
    previsions = Prevoir.objects.values('annee_prevus')\
        .annotate(total_prevision=Sum('montant_prevus')).order_by('annee_prevus')


    payements_data = [{"annee": p['annee'], "total_payement": p['total_payement']} for p in payement_entree]
    depenses_data = [{"annee": p['annee'], "total_depense": p['total_depense']} for p in payement_sortie]
    previsions_data = [{"annee_prevus": p['annee_prevus'], "total_prevision": p['total_prevision']} for p in previsions]

    
    labels = sorted(list(set(
        [p['annee'] for p in payement_entree] +
        [p['annee'] for p in payement_sortie] +
        [p['annee_prevus'] for p in previsions]
    )))

    data = {
        'labels': labels,
        'datasets': [
            {
                'label': "Solde total",
                'lineTension': 0.3,
                'backgroundColor': "rgba(78, 115, 223, 0.05)",
                'borderColor': "rgba(78, 115, 223, 1)",
                'pointRadius': 3,
                'pointBackgroundColor': "rgba(78, 115, 223, 1)",
                'pointBorderColor': "rgba(78, 115, 223, 1)",
                'pointHoverRadius': 3,
                'pointHoverBackgroundColor': "rgba(78, 115, 223, 1)",
                'pointHoverBorderColor': "rgba(78, 115, 223, 1)",
                'pointHitRadius': 10,
                'pointBorderWidth': 2,
                'data': [next((item['total_payement'] for item in payements_data if item['annee'] == label), 0) for label in labels],
            },
            {
                'label': "Dépense totale",
                'lineTension': 0.3,
                'backgroundColor': "rgba(78, 115, 223, 0.05)",
                'borderColor': "rgb(211, 16, 81)",
                'pointRadius': 3,
                'pointBackgroundColor': "rgb(211, 16, 81)",
                'pointBorderColor': "rgb(211, 16, 81)",
                'pointHoverRadius': 3,
                'pointHoverBackgroundColor': "rgb(211, 16, 81)",
                'pointHoverBorderColor': "rgb(211, 16, 81)",
                'pointHitRadius': 10,
                'pointBorderWidth': 2,
                'data': [next((item['total_depense'] for item in depenses_data if item['annee'] == label), 0) for label in labels],
            },
            {
                'label': "Prévision totale",
                'lineTension': 0.3,
                'backgroundColor': "rgba(78, 115, 223, 0.05)",
                'borderColor': "#858796",
                'pointRadius': 3,
                'pointBackgroundColor': "#858796",
                'pointBorderColor': "#858796",
                'pointHoverRadius': 3,
                'pointHoverBackgroundColor': "#858796",
                'pointHoverBorderColor': "#858796",
                'pointHitRadius': 10,
                'pointBorderWidth': 2,
                'data': [next((item['total_prevision'] for item in previsions_data if item['annee_prevus'] == label), 0) for label in labels],
            },
        ]
    }

    return Response(data)


@api_view(['GET'])
def get_presfora_data_proucentage(request):
    # Récupération des données
    soldes = Payement_Offrande.objects.filter(type_payement="Entree").aggregate(total=Sum('montant'))['total']
    soldes = Decimal(soldes) if soldes is not None else Decimal(0.0)

    depense = Payement_Offrande.objects.filter(type_payement="Sortie").aggregate(total=Sum('montant'))['total']
    depense = Decimal(depense) if depense is not None else Decimal(0.0)

    montant_prevu = Prevoir.objects.aggregate(total=Sum('montant_prevus'))['total']
    montant_prevu = Decimal(montant_prevu) if montant_prevu is not None else Decimal(0.0)

    total = soldes + depense + montant_prevu

    if total == 0:
        pourcentage_solde = Decimal('0.00')
        pourcentage_depense = Decimal('0.00')
        pourcentage_prevision = Decimal('0.00')
    else:
        pourcentage_solde = arrondir((soldes / total) * 100)
        pourcentage_depense = arrondir((depense / total) * 100)
        pourcentage_prevision = arrondir((montant_prevu / total) * 100)

    
    data = {
        'pourcentage_solde': float(pourcentage_solde),
        'pourcentage_depense': float(pourcentage_depense),
        'pourcentage_prevision': float(pourcentage_prevision),
    }

    return Response(data)



################## PDF #########################

def recu_pdf(request,pdf_id):
    
    try:
        data = Payement_Offrande.objects.get(id=pdf_id)
        num_alea = random.randint(1000,9999)
    except Payement_Offrande.DoesNotExist:
        return HttpResponse("Payement_Offrande ne pas la", status=404)  # Gestion de l'erreur si l'objet n'existe pas

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A5))
    width, height = landscape(A5)

    # Ajout du logo (assurez-vous que le chemin est correct)
    logo_path = "static/img/logo.png"
    try:
        p.drawImage(logo_path, 50, height - 80, width=60, height=60, mask='auto')
    except Exception as e:
        print(f"Error loading logo: {e}") #gestion d'erreur si le logo n'est pas trouvé.

    # Informations générales
    p.setFont("Helvetica", 12)
    p.drawString(130, height - 30, "ECC/3ème C.B.C.A")
    p.drawString(130, height - 50, "Département : FINANCE")  # Assurez-vous que c'est correct
    p.drawString(130, height - 70, "Institution : BP 495 GOMA")

    # Montant en haut à droite
    p.setFont("Helvetica-Bold", 12)
    p.drawString(width - 150, height - 50, f"{data.montant}$")
    en_lettre = num2words(data.montant, lang='fr', to='currency', currency='USD')  
    montant_lettre = en_lettre

    # Titre du reçu (générer un numéro de reçu unique)
    receipt_number = f"{num_alea}/CBCA/{datetime.now().year}"  # Exemple de numéro de reçu
    p.setFont("Helvetica-Bold", 16)
    p.drawString(220, height - 130, f"REÇU N° {receipt_number}")

    # Détails du reçu
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 170, f"Reçu de : Louis")  # Assurez-vous que c'est correct
    p.drawString(50, height - 190, f"Montant (en lettres) : {montant_lettre}") #fonction à créer pour convertir le montant en lettres.
    p.drawString(50, height - 210, f"Motif du paiement : {data.motif}")

    # Section Caisse
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 250, "La caisse")

    # Date et validation centrées
    p.setFont("Helvetica", 12)
    date_text = f"Date : {data.date_payement}"
    pour_versement_text = "Pour versement"
    date_x = width - 180
    pour_versement_x = date_x + (len(date_text) - len(pour_versement_text)) * 2  # Ajustement pour centrage

    p.drawString(date_x, height - 250, date_text)
    p.drawString(pour_versement_x, height - 270, pour_versement_text)

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"recu de {data.departement}.pdf")

@login_required
def bilan(request):
    from django.db.models import Q

    query = request.GET.get('q', '').strip().lower()

    prevision_qs = Prevoir.objects.select_related('descript_prevision')
    paiement_qs = Payement_Offrande.objects.select_related('nom_offrande')

    if query:
        prevision_qs = prevision_qs.filter(
            Q(nom_prevision__icontains=query) |
            Q(annee_prevus__icontains=query)
        )

        paiement_qs = paiement_qs.filter(
            Q(nom_offrande__nom_offrande__icontains=query) |
            Q(date_payement__icontains=query)
        )

    grouped = (
        prevision_qs
        .values(
            'descript_prevision__num_ordre',
            'descript_prevision__description_prevision',
            'annee_prevus'
        )
        .annotate(total_prevus=Sum('montant_prevus'))
        .order_by('descript_prevision__num_ordre', 'annee_prevus')
    )

    combined_data = []
    for group in grouped:
        num_ordre = group['descript_prevision__num_ordre']
        annee = group['annee_prevus']

        related_data = prevision_qs.filter(
            descript_prevision__num_ordre=num_ordre,
            annee_prevus=annee
        ).values('nom_prevision', 'num_compte', 'montant_prevus')

        pay_qs_filtered = paiement_qs.filter(
            nom_offrande__descript_recette__num_ordre=num_ordre,
            annee=annee
        )

        pay_grouped = pay_qs_filtered.values(
            'nom_offrande__num_compte',
            'nom_offrande__nom_offrande'
        ).annotate(
            total_recette=Sum('montant', filter=Q(type_payement='Entree')),
            total_depense=Sum('montant', filter=Q(type_payement='Sortie')),
        )

        prevision_list = [{
            'libelle': item['nom_prevision'],
            'num_compte': item['num_compte'],
            'recette': '-',
            'depense': '-',
            'prevision': item['montant_prevus'],
        } for item in related_data]

        paiement_list = [{
            'libelle': item['nom_offrande__nom_offrande'],
            'num_compte': item['nom_offrande__num_compte'],
            'recette': item['total_recette'] or '-',
            'depense': item['total_depense'] or '-',
            'prevision': '-',
        } for item in pay_grouped]

        lignes_fusionnees = prevision_list + paiement_list

        total_recettes = sum(
            [p['recette'] if p['recette'] != '-' else 0 for p in paiement_list], Decimal(0)
        )
        total_depenses = sum(
            [p['depense'] if p['depense'] != '-' else 0 for p in paiement_list], Decimal(0)
        )

        combined_data.append({
            'num_ordre': num_ordre,
            'description_prevision': group['descript_prevision__description_prevision'],
            'annee_prevus': annee,
            'total_prevus': group['total_prevus'] or 0,
            'total_recettes': total_recettes,
            'total_depenses': total_depenses,
            'lignes': lignes_fusionnees
        })

    paginator = Paginator(combined_data, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for i, item in enumerate(page_obj, start=page_obj.start_index()):
        item['numero_ordre'] = i

    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filteredFalse.count()

    context = {
        'data': page_obj,
        'search_query': query,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }

    return render(request, 'rapport/bilan.html', context)

def livre_de_caisse(request):

    #data = Payement_Offrande.objects.all()
    

    search_query = request.GET.get('q', '').strip()

    
    #data = Payement_Offrande.objects.exclude(nom_offrande__descript_recette__description_recette="Engagement des adhérents")

    data_queryset = Payement_Offrande.objects.all().order_by('nom_offrande')
    
    if search_query:
        
        mots = search_query.split()
        query = Q()
        for mot in mots:
            query &= Q(date_payement__icontains=mot)

        data_queryset = data_queryset.filter(query)


    # Calcul des sommes cumulées
    cumulative_sums = []
    current_sum = 0

    for item in data_queryset:
        if item.type_payement == 'Sortie':
            current_sum -= item.montant or 0
        else:
            current_sum += item.montant or 0
        cumulative_sums.append(current_sum)

    # Préparer les données traitées avec somme cumulative
    processed_data = []
    for i, item in enumerate(data_queryset):
        processed_data.append({
            'op': item,
            'cumulative_sum': cumulative_sums[i]
        })

    # Pagination des données traitées (5 éléments par page)
    paginator = Paginator(processed_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    data_filtered = EtatBesoin.objects.filter(validation_pasteur=True, validation_caisse=False)
    data_etat_counter = data_filtered.count()

    data_filteredFalse = EtatBesoin.objects.filter(validation_pasteur=False)
    data_etat_counter_P = data_filteredFalse.count()

    context = {
        'data': page_obj,
        'data_etat_count_C': data_etat_counter,
        'data_etat_besoin_true': data_filtered,
        'data_etat_besoin_false': data_filteredFalse,
        'data_etat_count_P': data_etat_counter_P,
    }

    return render(request, 'rapport/livre_caisse.html', context)


def bon_sorti_pdf(request, pdf_id):
    try:
        data = Payement_Offrande.objects.get(id=pdf_id)
        num_alea = random.randint(1000,9999)
    except Payement_Offrande.DoesNotExist:
        return HttpResponse("Pas de donnée sur les dépenses", status=404)

    # Initialisation du buffer et du canvas PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A5))
    width, height = landscape(A5)
    
    # Logo avec fond opaque
    logo_path = "static/img/logo.png"  # Vérifie si le chemin est correct
    p.drawImage(logo_path, 50, height - 80, width=60, height=60, mask='auto')
    
    # Informations générales
    p.setFont("Helvetica", 12)
    p.drawString(120, height - 30, "ECC/3ème C.B.C.A")
    p.drawString(120, height - 50, "Département : FINANCE")
    p.drawString(120, height - 70, "Institution : EGLISE CBCA/KATOYI")
    p.drawString(120, height - 90, "BP : 495 GOMA")
    
    # Montant en haut à droite
    p.setFont("Helvetica-Bold", 12)
    p.drawString(width - 160, height - 50, f"Date : {data.date_payement}")
    
    # Titre du reçu
    p.setFont("Helvetica-Bold", 16)
    p.drawString(width / 2 - 150, height - 120, f"BON DE SORTIE DE CAISSE N° {num_alea}/CBCA/{datetime.now().year}")
    
    en_lettre = num2words(data.montant, lang='fr', to='currency', currency='USD')  
    montant_lettre = en_lettre
    # Détails du reçu
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 150, f"Nom du bénéficiaire : {data.departement}")
    p.drawString(50, height - 170, f"Montant (en lettres) : {montant_lettre}")
    p.drawString(50, height - 190, f"Motif du paiement : {data.motif}")
    
    # Tableau avec Table et TableStyle
    table_data = [
        ['Numéro du compte', 'Description', 'Montant'],  # En-têtes
        [data.nom_offrande.num_compte, data.nom_offrande, data.montant]  # Valeurs
    ]
    
    # Créer l'objet Table
    table = Table(table_data, colWidths=[160, 160, 160], rowHeights=30)
    
    # Appliquer le style au tableau
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fond des en-têtes
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Couleur du texte des en-têtes
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alignement du texte
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Police des en-têtes
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding pour les en-têtes
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Fond des lignes
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Bordures des cellules
    ])
    table.setStyle(style)
    
    # Positionner le tableau sur la page (en bas du bloc de texte)
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, height - 220 - 50)  # Ajuste la position du tableau
    
    # Section Caisse
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 310, "Trésorier / RPS / EVARES / Comptable.Sce")

    p.setFont("Helvetica", 12)
    p.drawString(320, height - 310, 'Pour acquit')

    # Date et validation centrées
    p.setFont("Helvetica", 12)
    date_text = f"Caissier"
    date_x = width - 120   
    p.drawString(date_x, height - 310, date_text)
   
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Bon_de_sortie_{data.departement}.pdf")




@login_required
def bilan_pdf(request):
    try:
        grouped = (
            Prevoir.objects
            .values(
                'descript_prevision__num_ordre',
                'descript_prevision__description_prevision',
                'annee_prevus'
            )
            .annotate(total_prevus=Sum('montant_prevus'))
            .order_by('descript_prevision__num_ordre', 'annee_prevus')
        )

        data_2 = Prevoir.objects.select_related('descript_prevision').all()

        combined_data = []
        for group in grouped:
            related_data = data_2.filter(
                descript_prevision__num_ordre=group['descript_prevision__num_ordre'],
                annee_prevus=group['annee_prevus']
            )
            combined_data.append({
                'num_ordre': group['descript_prevision__num_ordre'],
                'description_prevision': group['descript_prevision__description_prevision'],
                'annee_prevus': group['annee_prevus'],
                'total_prevus': group['total_prevus'],
                'related_data': related_data
            })

    except Prevoir.DoesNotExist:
        return HttpResponse("Pas de donnée sur la prévision", status=404)

    # Création du PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleH = styles["Heading1"]
    

    logo_path = "static/img/logo.png"  # Assure-toi que ce chemin est accessible (voir remarques ci-dessous)
    logo = Image(logo_path, width=60, height=60)
    elements.append(logo)

    # En-tête général
    elements.append(Paragraph("ECC/3ème C.B.C.A - Département FINANCE", styleN))
    elements.append(Paragraph("Institution : EGLISE CBCA/KATOYI", styleN))
    elements.append(Paragraph("BP : 495 GOMA", styleN))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"BILAN DES PREVISIONS - {datetime.now().strftime('%d/%m/%Y')}", styleH))
    elements.append(Spacer(1, 20))

    # Tableau
    table_data = [['N°', 'LES OFFRANDES', 'N° DE COMPTE', 'PREVISION']]  # En-tête

    for bloc in combined_data:
        # Ligne regroupée
        table_data.append([
            '-',
            bloc['description_prevision'],
            bloc['num_ordre'],
            f"{bloc['total_prevus']}"
        ])

        for item in bloc['related_data']:
            table_data.append([
                '-',
                item.nom_prevision,
                item.num_compte,
                f"{item.montant_prevus}"
            ])

    # Table object
    table = Table(table_data, colWidths=[80, 200, 100, 100], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 40))

    # Signatures
    elements.append(Paragraph("Trésorier / RPS / EVARES / Comptable.Sce", styleN))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Pour acquit", styleN))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Caissier", styleN))

    # Génération finale du document
    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="bilan_previsions.pdf")



def num_lettre():
    num = 12.4
    en_lettre = num2words(num, lang='fr', to='currency', currency='USD')
    print(en_lettre)
    
    return HttpResponse()