import decimal
from django.shortcuts import  render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Sum
from Prosfera_App.models import *
from django.contrib.auth import login, update_session_auth_hash
from django.core.paginator import Paginator
from decimal import Decimal
from django.contrib import messages
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PayementOffrandeSerializer, PrevoirSerializer
import re
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A5
from django.http import HttpResponse
from num2words import num2words
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.http import HttpResponse, FileResponse
from .models import Depense  # Assure-toi que Depense est importé

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


@login_required
def homePage(request):
    if request.user.is_authenticated:
        
        soldes = Payement_Offrande.objects.aggregate(total=Sum('montant'))['total']
        soldes = Decimal(soldes) if soldes is not None else Decimal(0.0)
        
        
        depense = Depense.objects.aggregate(total=Sum('montant'))['total']
        depense = Decimal(depense) if depense is not None else Decimal(0.0)
        reste = soldes - depense
        montant_prevu = Prevoir.objects.aggregate(total=Sum('montant_prevus'))['total']
        montant_prevu = Decimal(montant_prevu) if montant_prevu is not None else Decimal(0.0)
        
        context = {
            'Soldes': reste,
            'encaissement': soldes,
            'Depense': depense,
            'Montant_prevu': montant_prevu,
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
        # Récupération des données du formulaire
        num_ordre = request.POST['num_ordre']
        
        
        try:
            # Récupération de l'instance Groupe_Previsions à modifier
            data_groupe = Groupe_Previsions.objects.get(id=id)
            # Vérification si les données sont différentes avant de les enregistrer
            if data_groupe.num_ordre != num_ordre :
                # Si les données sont différentes, on effectue la mise à jour
                data_groupe.num_ordre = num_ordre
                data_groupe.save()
            
            # Redirection vers la page des données de groupe de prévision
            return redirect('app:Groupe_Prevision_Data')

        except Groupe_Previsions.DoesNotExist:
            # Si l'instance avec l'id n'existe pas, on redirige ou on affiche un message d'erreur
            return redirect('app:Groupe_Prevision_Data')  # Ou une autre action selon ton besoin

    # Si la méthode n'est pas POST, on redirige vers la page des données de groupe de prévision
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
    
    nombre_id = 10  # Par exemple, ou un autre nombre selon votre logique
    range_list = list(range(1, nombre_id + 1))

    data = Prevoir.objects.all()
    #groupes_offrande_list = Sorte_Offrande.objects.filter(user=request.user)
    paginator = Paginator(data, 5)  # Afficher 10 éléments par page
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
        
        # Récupérer les valeurs envoyées par le formulaire
        nom_offrande_id = request.POST.get('nom_offrande')  # L'ID de la recette
        departement = request.POST.get('departement')
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
            return render(request, 'payement_offrande/formulaire_payement.html', context)
        
        # Vérification du montant (doit être un nombre décimal)
        try:
            montant = Decimal(montant)
        except (ValueError,):
            message_erreur = "Le montant n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'payement_offrande/formulaire_payement.html', context)
        
        # Vérification de l'année (doit être un entier)
        try:
            annee = int(annee)
        except ValueError:
            message_erreur = "L'année n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'payement_offrande/formulaire_payement.html', context)
        
        # Vérifier la date de paiement (assurez-vous qu'elle est dans un format valide)
        try:
            date_payement = datetime.strptime(date_payement, '%d-%m-%Y').date()
        except ValueError:
            message_erreur = "La date de paiement n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'payement_offrande/formulaire_payement.html', context)
        
        # Création de l'enregistrement
        payement_offrande = Payement_Offrande(
            nom_offrande=nom_offrande,  # Assigner l'objet Sorte_Offrande ici
            departement=departement,
            montant=montant,
            montant_lettre=montant_lettre,
            motif = motif,
            date_payement=date_payement,
            annee=annee
        )
        
        # Sauvegarde de l'enregistrement
        payement_offrande.save()
        message_succes = "Paiement réussi avec succès !"
        context = {'message_succes': message_succes}
        return render(request, 'payement_offrande/formulaire_payement.html', context)
    
    else:
        message_erreur = "Échec du paiement !"
        return render(request, 'payement_offrande/formulaire_payement.html', {'message_erreur': message_erreur})

@login_required
def  Payement_Offrande_Data(request): 

    # Récupération des objets Sorte_Offrande
    data = Payement_Offrande.objects.all()

    # Paginer les objets (5 éléments par page)
    paginator = Paginator(data, 5)
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
    return render(request, 'payement_offrande/data_payement_offrande.html', context)



############# DEPENSE ####################

def depensePage(request, id):
    
    sorte_offrande = get_object_or_404(Sorte_Offrande, num_compte=id)
    total_montant = Payement_Offrande.objects.filter(nom_offrande=sorte_offrande).aggregate(
        total_montant=Sum('montant')
    )['total_montant'] or 0
    
    current_date = datetime.now()
    formatted_date = current_date.strftime('%d-%m-%Y')
    formatted_anne = current_date.strftime('%Y')

     
    context = {
         
        'date_sortie' : formatted_date,
        'annee_sortie' : formatted_anne,
        'nom_offrande': sorte_offrande.nom_offrande,
        'num_compte': sorte_offrande.num_compte,
        'montant_total': total_montant,
        
        }
    page = 'depense/formulaire_depense.html'
    return render(request, page, context )

def depenser(request):
    
    context = {}

    if request.method == 'POST':
        compte = request.POST.get('compte')
        nom_compte = request.POST.get('nom_compte')
        nom_beneficiaire = request.POST.get('nom_beneficiaire')
        solde_str = request.POST.get('solde')
        montant_str = request.POST.get('montant')
        motif = request.POST.get('motif')
        date_sortie_str = request.POST.get('date_sortie')
        annee_str = request.POST.get('annee')

        # Vérification si les champs sont vides
        if not montant_str or not solde_str or not annee_str:
            context['message_erreur'] = "Veuillez remplir tous les champs obligatoires."
            context['num_compte'] = compte
            context['nom_offrande'] = nom_compte
            context['montant_total'] = solde_str
            context['annee_sortie'] = annee_str
            context['date_sortie'] = date_sortie_str
            return render(request, 'depense/formulaire_depense.html', context)

        try:
            # Conversion des valeurs en Decimal et en int, avec une vérification préalable
            montant = Decimal(montant_str.replace(',', '.'))  # Assurez-vous de remplacer les virgules par des points
            solde = Decimal(solde_str.replace(',', '.'))
            annee = int(annee_str)  # Conversion de l'année en entier

            current_date = datetime.now()
            formatted_date = current_date.strftime('%Y-%m-%d')
            date_sortie = formatted_date
        except (ValueError, TypeError, decimal.InvalidOperation):
            context['message_erreur'] = "Erreur de format dans les valeurs saisies."
            context['num_compte'] = compte
            context['nom_offrande'] = nom_compte
            context['montant_total'] = solde_str
            context['annee_sortie'] = annee_str
            context['date_sortie'] = date_sortie_str
            return render(request, 'depense/formulaire_depense.html', context)

        # Vérification du solde
        if solde < montant:
            context['message_erreur'] = "Compte insuffisant !"
            context['num_compte'] = compte
            context['nom_offrande'] = nom_compte
            context['montant_total'] = solde
            context['annee_sortie'] = annee
            context['date_sortie'] = date_sortie
            return render(request, 'depense/formulaire_depense.html', context)

        # Conversion du montant en lettres
        en_lettre = num2words(montant_str, lang='fr', to='currency', currency='USD')  
        montant_lettre = en_lettre

        # Création de la dépense
        depense = Depense(
            compte=compte,
            nom_compte=nom_compte,
            nom_beneficiaire=nom_beneficiaire,
            montant=montant,
            montant_lettre=montant_lettre,
            motif=motif,
            date_sortie=date_sortie,
            annee=annee
        )
        depense.save()

        # Message de succès après enregistrement de la dépense
        context['message_succes'] = "Sortie réussie avec succès !"
        context['num_compte'] = compte
        context['nom_offrande'] = nom_compte
        context['montant_total'] = solde
        context['annee_sortie'] = annee
        context['date_sortie'] = date_sortie

        return render(request, 'depense/formulaire_depense.html', context)

    return render(request, 'depense/formulaire_depense.html', context)


@login_required
def depense_data(request):
    # Récupération des données agrégées
    data = Depense.objects.values('nom_beneficiaire', 'date_sortie','motif').annotate(montant_total=Sum('montant')).order_by('nom_beneficiaire', 'date_sortie','motif')

    paginator = Paginator(data, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Ajouter un numéro d'ordre dynamique
    for index, item in enumerate(page_obj, start=1):
        item['numero_ordre'] = index

    # Préparer le contexte
    context = {
        'data': page_obj,
        # Tu peux ajouter d'autres informations au contexte ici si nécessaire
    }

    # Rendre la template
    return render(request, 'depense/data_depense.html', context)

@login_required
def Sortie_Data(request):
    
    # Récupération des montants des payements d'offrande
    data = Payement_Offrande.objects.values(
        'nom_offrande__id',
        'nom_offrande__nom_offrande',
        'nom_offrande__num_compte'
    ).annotate(
        total_montant=Sum('montant')
    )

    # Récupération des soldes de dépenses
    soldes = Depense.objects.values(
        'compte',
        'nom_compte'
    ).annotate(
        montant_total=Sum('montant')
    ).order_by('compte', 'nom_compte')

    # Créer un dictionnaire pour accéder facilement aux soldes par compte/nom_compte
    soldes_dict = {f"{solde['compte']}_{solde['nom_compte']}": solde['montant_total'] for solde in soldes}

    # Calculer la différence entre les offrandes et les soldes des dépenses
    result = []
    for off in data:
        # Créer une clé pour retrouver le solde associé
        key = f"{off['nom_offrande__num_compte']}_{off['nom_offrande__nom_offrande']}"
        
        # Chercher si ce compte existe dans les soldes
        #depense_montant = soldes_dict.get(key, 0.0)  # Utiliser 0.0 si pas de correspondance
        depense_montant = soldes_dict.get(key, Decimal('0.0'))
        # Calculer la différence (offrande - dépense)
        difference = off['total_montant'] - depense_montant
        
        # Ajouter cette différence dans le résultat
        result.append({
            'nom_offrande': off['nom_offrande__nom_offrande'],
            'num_compte': off['nom_offrande__num_compte'],
            'total_montant': off['total_montant'],
            'depense_montant': depense_montant,
            'difference': difference
        })

    # Paginer les objets (5 éléments par page)
    paginator = Paginator(result, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'data': page_obj
    }

    # Rendre la page avec les données paginées et numérotées
    return render(request, 'depense/sortie_data.html', context)


def bonSortiePage(request, nom):
    try:
        nom_beneficiaire_cible = nom  # Utilisez la variable 'nom' de votre requête initiale
        
        # Filtrer et grouper par nom_beneficiaire, puis calculer le montant total par bénéficiaire
        data_compte = Depense.objects.filter(nom_beneficiaire=nom_beneficiaire_cible).order_by('nom_beneficiaire', 'date_sortie','motif').values('nom_beneficiaire', 'nom_compte','compte').annotate(
            montant_total=Sum('montant'),).order_by('nom_beneficiaire', 'nom_compte','compte')
        
        data = Depense.objects.filter(nom_beneficiaire=nom_beneficiaire_cible).order_by('-date_sortie').values('nom_beneficiaire').annotate(
            montant_total=Sum('montant')
        ).order_by('nom_beneficiaire')
        
        context = {'data_compte': data_compte, 'data':data}
        page = 'rapport/bon_sortie.html'
        return render(request, page, context)
        
    except ObjectDoesNotExist: # type: ignore
        # Gérer le cas où aucun objet Depense n'est trouvé pour ce nom
        context = {'error_message': f"Aucune dépense trouvée pour le bénéficiaire '{nom}'."}
        page = 'rapport/bon_sortie.html'  # Vous pouvez créer une page d'erreur spécifique
        return render(request, page, context)


#################### AHADI #######################


@login_required
def souscrire_ahadi_Page(request):
    
    data = Sorte_Offrande.objects.filter(
    descript_recette__description_recette__icontains="Les encadrements des adhérents"
    )
   
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
    return render(request, 'ahadi/souscrire_ahadi.html', context)


@login_required
def payement_ahadi_Page(request):
    
    data = Ahadi.objects.all()
   
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
    return render(request, 'ahadi/liste_ahadi_doit_payer.html', context)



@login_required
def ahadiformulairePage(request, id):
    
    current_date = datetime.now()
    
    # Tu peux aussi formater la date selon ton besoin
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
  
    data = Ahadi.objects.get(id=id)
    
    context = {
        'data' : data,
        
        }
    page = 'ahadi/detail.html'
    return render(request, page, context )

@login_required
def Formulaire_Ahadi_Payement(request, id):
    
    current_date = datetime.now()
    
    # Tu peux aussi formater la date selon ton besoin
    formatted_date = current_date.strftime('%d-%m-%Y')
    formatted_anne = current_date.strftime('%Y')
    data = Sorte_Offrande.objects.get(id=id)
    
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
def  liste_souscription(request): 

    # Récupération des objets Sorte_Offrande
    data = Ahadi.objects.all()

    # Paginer les objets (5 éléments par page)
    paginator = Paginator(data, 5)
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
    return render(request, 'ahadi/liste_ahadi.html', context)


def recuPage(request, id):
    
    data = Payement_Offrande.objects.get(id=id)
    
    context = {'data' : data}
    page = 'rapport/recu.html'
    return render(request, page, context )

def recu_dataPage(request):
        # Récupération des objets Sorte_Offrande
    data = Payement_Offrande.objects.all()

    # Paginer les objets (5 éléments par page)
    paginator = Paginator(data, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculer un numéro d'ordre dynamique pour chaque objet sur la page
    for index, objet in enumerate(page_obj, start=1):  # `start=1` commence l'index à 1
        objet.numero_ordre = index  # Assigner le numéro d'ordre à chaque objet

    # Passer les objets à la template
    context = {
        'data': page_obj
    }

    page = 'rapport/recu_data.html'
    return render(request, page, context )


#################### RAPPORT PDF ##########################


def custom_404(request, exception):
    return render(request, 'et.html', {}, status=404)


############ DATA POUR LES GRAPHIQUES ##############


@api_view(['GET'])
def get_presfora_data(request):
    
    # Obtenez les paiements par année
    payements = Payement_Offrande.objects.values('annee').annotate(total_payement=Sum('montant')).order_by('annee')
    previsions = Prevoir.objects.values('annee_prevus').annotate(total_prevision=Sum('montant_prevus')).order_by('annee_prevus')
    depenses = Depense.objects.values('annee').annotate(total_depense=Sum('montant')).order_by('annee')
    # Sérialiser les données de Payement_Offrande
    payements_data = [{"annee": p['annee'], "total_payement": p['total_payement']} for p in payements]
    
    annees = Payement_Offrande.objects.values('annee').order_by('annee')
    
    depenses_data = [{"annee": p['annee'], "total_depense": p['total_depense']} for p in depenses]
    # Sérialiser les données de Prevoir
    previsions_data = [{"annee_prevus": p['annee_prevus'], "total_prevision": p['total_prevision']} for p in previsions]
    
    # Préparer les données à envoyer au frontend
    labels = list(set([p['annee'] for p in payements] + [p['annee'] for p in annees] + [p['annee'] for p in depenses] + [p['annee_prevus'] for p in previsions]))
    labels.sort()

# Requête qui calcule la somme des montants groupés par nom_offrande  
    
    data = {
        #'labels': ["2014", "2015", "2016", ],
        'labels' : [next((item['annee'] for item in annees if item['annee'] == label), 0) for label in labels],
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
                #'data': [0, 10000, 5000, 15000, 10000, 20000, 15000, 25000, 20000, 30000, 25000, 40000],
                'data': [next((item['total_payement'] for item in payements_data if item['annee'] == label), 0) for label in labels],
            },
            {
                'label': "Depense total",
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
                #'data': [0, 1000, 500, 1000, 1000, 2000, 0, 5000, 20000, 30000, 25000, 40000],
                'data': [next((item['total_depense'] for item in depenses_data if item['annee'] == label), 0) for label in labels],    
            }, 
            {
                'label': "Prevision total",
                'lineTension': 0.3,
                'backgroundColor': "rgba(78, 115, 223, 0.05)",
                'borderColor' : "#858796",
                'pointRadius': 3,
                'pointBackgroundColor': "#858796",
                'pointBorderColor': "#858796",
                'pointHoverRadius': 3,
                'pointHoverBackgroundColor': "#858796",
                'pointHoverBorderColor': "#858796",
                'pointHitRadius': 10,
                'pointBorderWidth': 2,
                #'data': [0, 1000, 500, 1000, 1000, 20000, 15000, 25000, 20000, 30000, 25000, 0]
                'data': [next((item['total_prevision'] for item in previsions_data if item['annee_prevus'] == label), 0) for label in labels],
            },
        ]
    }

    return Response(data)


################## PDF #########################

def recu_pdf(request,pdf_id):
    
    try:
        data = Payement_Offrande.objects.get(id=pdf_id)
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
    receipt_number = f"0001/{datetime.now().year}"  # Exemple de numéro de reçu
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

from collections import defaultdict
@login_required
def  bilan(request): 

    # # Récupération des objets Sorte_Offrande
    # #data_2 = Prevoir.objects.all()
    # #data = Prevoir.objects.values('descript_prevision__description_prevision','descript_prevision__num_ordre','annee_prevus').annotate(total_prevus=Sum('montant_prevus'))

    #     # Récupérer les données agrégées (somme des montants par descript_prevision et annee_prevus)
    # data = Prevoir.objects.values(
    #         'descript_prevision__description_prevision',
    #         'descript_prevision__num_ordre',
    #         'annee_prevus'
    #     ).annotate(total_prevus=Sum('montant_prevus'))

    #     # Récupérer toutes les données complètes (objets Prevoir)
    # data_2 = Prevoir.objects.all()

    #     # Combiner les deux ensembles de données
    #     # Créer une liste de dictionnaires avec les données agrégées et les données complètes
    # combined_data = []
    # for item in data:
    #         # Trouver tous les objets Prevoir qui correspondent à l'agrégation (en fonction de descript_prevision et annee_prevus)
    #     related_data = data_2.filter(
    #             descript_prevision__description_prevision=item['descript_prevision__description_prevision'],
    #             annee_prevus=item['annee_prevus']
    #         )
    #         # Ajouter les données complètes à chaque agrégation
    #     combined_data.append({
    #             'description_prevision': item['descript_prevision__description_prevision'],
    #             'num_ordre': item['descript_prevision__num_ordre'],
    #             'annee_prevus': item['annee_prevus'],
    #             'total_prevus': item['total_prevus'],
    #             'related_data': related_data  # Données complètes associées
    #         })


    # # Passer les objets à la template
    # context = {
    #     'data': combined_data
    # }
    annee_cible = 2025
    previsions = Prevoir.objects.filter(annee_prevus=annee_cible).order_by('descript_prevision')
    context = {'previsions': previsions}

    # Rendre la page avec les données paginées et numérotées
    return render(request, 'rapport/bilan.html', context)



def bon_sorti_pdf(request, id, pdf_id):
    try:
        data = Depense.objects.get(id=id)
    except Depense.DoesNotExist:
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
    p.drawString(width - 160, height - 50, f"Date : {data.date_sortie}")
    
    # Titre du reçu
    p.setFont("Helvetica-Bold", 16)
    p.drawString(width / 2 - 150, height - 120, "BON DE SORTIE DE CAISSE N° 0001/2025")
    en_lettre = num2words(data.montant, lang='fr', to='currency', currency='USD')  
    montant_lettre = en_lettre
    # Détails du reçu
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 150, f"Nom du bénéficiaire : {data.nom_beneficiaire}")
    p.drawString(50, height - 170, f"Montant (en lettres) : {montant_lettre}")
    p.drawString(50, height - 190, f"Motif du paiement : {data.motif}")
    
    # Tableau avec Table et TableStyle
    table_data = [
        ['Numéro du compte', 'Description', 'Montant'],  # En-têtes
        [data.compte.nom_offrande.num_compte, data.compte.nom_offrande, data.montant]  # Valeurs
    ]
    
    # Créer l'objet Table
    table = Table(table_data, colWidths=[150, 150, 150], rowHeights=20)
    
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
    return FileResponse(buffer, as_attachment=True, filename=f"Bon_de_sortie_{data.nom_beneficiaire}.pdf")



def num_lettre():
    num = 12.4
    en_lettre = num2words(num, lang='fr', to='currency', currency='USD')
    print(en_lettre)
    
    return HttpResponse()