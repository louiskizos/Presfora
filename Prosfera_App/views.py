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
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A5
from django.http import HttpResponse

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
        
        soldes = Payement_Offrande.objects.aggregate(total = Sum('montant'))['total']
        soldes = soldes if soldes is not None else 0.0
        
        depense = Depense.objects.aggregate(total = Sum('montant'))['total']
        depense = depense if depense is not None else 0.0
        reste = (soldes - depense)
        montant_prevu = Prevoir.objects.aggregate(total = Sum('montant_prevus'))['total']
        montant_prevu = soldes if montant_prevu is not None else 0.0
        groupes_offrande_list = Groupe_Offrandes.objects.filter(user=request.user)
    
    # Récupérer le terme de recherche depuis la requête GET
    
        context = {
                'Soldes' : reste,
                'Depense' : depense,
                'Montant_prevu' : montant_prevu,
                #'search_query': search_query
                #'countTrans' : total_trans,
                # 'pourcentage' : total_pourc
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
        
        # Récupérer les valeurs envoyées par le formulaire
        #user_id = request.POST.get('user')  # L'ID de la recette
        num_ordre = request.POST.get('num_ordre')
        description_prevision = request.POST.get('description_prevision')
        
        
       
        # Vérification si le numéro de compte existe déjà
        if Groupe_Previsions.objects.filter(description_prevision=description_prevision).exists():
            message_erreur = "Le nom du groupe du prevision existe déjà !"
            return render(request, 'prevision/groupe_prevision.html', {'message_erreur': message_erreur })

        if Groupe_Previsions.objects.filter(num_ordre=num_ordre).exists():
            message_erreur = "Le numero du groupe du prevision existe déjà !"
            return render(request, 'prevision/groupe_prevision.html', {'message_erreur': message_erreur })

        
        # Création de l'enregistrement
        prevision = Groupe_Previsions(
            description_prevision=description_prevision,  # Assigner l'objet Recette_Budget ici
            num_ordre = num_ordre,
            #user=id_user,
           
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
    if Sorte_Prevision.objects.filter(descript_prevision=groupe_prevision).exists():
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
        description_prevision = request.POST['description_prevision']
        
        try:
            # Récupération de l'instance Groupe_Previsions à modifier
            data_groupe = Groupe_Previsions.objects.get(id=id)
            # Vérification si les données sont différentes avant de les enregistrer
            if data_groupe.num_ordre != num_ordre or data_groupe.description_prevision != description_prevision:
                # Si les données sont différentes, on effectue la mise à jour
                data_groupe.num_ordre = num_ordre
                data_groupe.description_prevision = description_prevision
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
def sorte_previsonPage(request):
    data = Groupe_Previsions.objects.all()
    context = {
        'data' : data
    }
    page = 'sorte_previsions/sorte_previsions.html'
    return render(request, page, context)



@login_required
def CreateSortePrevision(request):
    
    
    if request.method == 'POST':
        # Récupérer les valeurs envoyées par le formulaire
        descript_prevision = request.POST.get('descript_prevision')  # L'ID de la recette
        num_compte = request.POST.get('num_compte')
        nom_prevision = request.POST.get('nom_prevision')
        
        groupe_previsions =  Groupe_Previsions.objects.all()[:4]
        
        if descript_prevision == "#":
            
            message_erreur = "Le groupe des offrandes est vide !"
            context = {
                'message_erreur': message_erreur,
                'data' : groupe_previsions
                }
            return render(request, 'sorte_previsions/sorte_previsions.html', context)
        
        
        try:
            # Vérifier si l'ID de la recette existe dans la base de données
            descript_prevision = Groupe_Previsions.objects.get(id=descript_prevision)
            
        except Groupe_Previsions.DoesNotExist:
            message_erreur = "La description spécifiée n'existe pas."
            context = {
                'message_erreur': message_erreur,
                'data' : groupe_previsions
                }
            return render(request, 'sorte_previsions/sorte_previsions.html', context)

        if Sorte_Prevision.objects.filter(num_compte=num_compte).exists():
            message_erreur = "Le numéro du compte existe déjà !"
            context = {
                'message_erreur': message_erreur,
                'data' : groupe_previsions
                }
            return render(request, 'sorte_previsions/sorte_previsions.html', context)
        
        # Vérification si le numéro de compte existe déjà
        
        
        if Sorte_Prevision.objects.filter(nom_prevision=nom_prevision).exists():
            message_erreur = "Le nom de la prevision existe déjà !"
            context = {
                'message_erreur': message_erreur,
                'data' : groupe_previsions
                }
            return render(request, 'sorte_previsions/sorte_previsions.html', context)

        
        # Création de l'enregistrement
        sorte_prevision = Sorte_Prevision(
            descript_prevision=descript_prevision,  # Assigner l'objet Recette_Budget ici
            num_compte=num_compte,
            nom_prevision=nom_prevision
        )
        
        # Sauvegarde de l'enregistrement
        sorte_prevision.save()
        message_succes = "Enregistrement réussi avec succès !"
        context = {
                'message_succes': message_succes,
                'data' : groupe_previsions
                }
        return render(request, 'sorte_previsions/sorte_previsions.html', context)
    
    else:
        message_erreur = "Échec d'enregistrement !"
        return render(request, 'sorte_previsions/sorte_previsions.html', {'message_erreur': message_erreur, 'data' : groupe_previsions})



@login_required
def  Sorte_Prevision_Data(request): 
    
    nombre_id = 10  # Par exemple, ou un autre nombre selon votre logique
    range_list = list(range(1, nombre_id + 1))

    data = Sorte_Prevision.objects.all()
    #groupes_offrande_list = Sorte_Offrande.objects.filter(user=request.user)
    paginator = Paginator(data, 5)  # Afficher 10 éléments par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'data' : page_obj,
        'range_list' : range_list
    }
    page = 'sorte_previsions/prevision_data.html'
    
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
    
    # Tu peux aussi formater la date selon ton besoin
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
        montant_lettre = request.POST.get('montant_lettre')
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

def depensePage(request):
    
    current_date = datetime.now()
    formatted_date = current_date.strftime('%d-%m-%Y')
    formatted_anne = current_date.strftime('%Y')
    data = Payement_Offrande.objects.all()[:2]
    #data = Payement_Offrande.objects.aggregate(total = Sum('montant'))['total']
    
    context = {
        'data' : data,
        'date_sortie' : formatted_date,
        'annee_sortie' : formatted_anne,
        }
    page = 'depense/formulaire_depense.html'
    return render(request, page, context )

@login_required
def depenser(request):
    
    
    if request.method == 'POST':
        
       
        compte_id = request.POST.get('compte') 
        nom_beneficiaire = request.POST.get('nom_beneficiaire')
        montant = request.POST.get('montant')
        montant_lettre = request.POST.get('montant_lettre')
        motif = request.POST.get('motif')
        date_sortie = request.POST.get('date_sortie')
        annee = request.POST.get('annee')
        
        soldes = Payement_Offrande.objects.aggregate(total = Sum('montant'))['total']

        # Validation des données
        try:
            # Vérifier si l'ID de la recette existe dans la base de données
            compte = Payement_Offrande.objects.get(id=compte_id)
            
        except Payement_Offrande.DoesNotExist:
            message_erreur = "Le compte spécifié n'existe pas."
            context = {'message_erreur': message_erreur}
            return render(request, 'depense/formulaire_depense.html', context)
        
        # Vérification du montant (doit être un nombre décimal)
        try:
            montant = Decimal(montant)
        except (ValueError,):
            message_erreur = "Le montant n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'depense/formulaire_depense.html', context)
        
        # Vérification de l'année (doit être un entier)
        try:
            annee = int(annee)
        except ValueError:
            message_erreur = "L'année n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'depense/formulaire_depense.html', context)
        
        # Vérifier la date de sortie (assurez-vous qu'elle est dans un format valide)
        try:
            date_sortie = datetime.strptime(date_sortie, '%d-%m-%Y').date()
        except ValueError:
            message_erreur = "La date de sortie n'est pas valide."
            context = {'message_erreur': message_erreur}
            return render(request, 'depense/formulaire_depense.html', context)
        
        if soldes < montant:
            message_erreur = "Compte insuffisant !"
            context = {'message_erreur': message_erreur}
            return render(request, 'depense/formulaire_depense.html', context)
            
        # Création de l'enregistrement
        depenser = Depense(
            compte=compte,  # Assigner l'objet Sorte_Offrande ici
            nom_beneficiaire=nom_beneficiaire,
            montant=montant,
            montant_lettre=montant_lettre,
            motif = motif,
            date_sortie=date_sortie,
            annee=annee
        )
        
        # Sauvegarde de l'enregistrement
        depenser.save()
        message_succes = "Sortie réussie avec succès !"
        context = {'message_succes': message_succes}
        return render(request, 'depense/formulaire_depense.html', context)
    
    else:
        message_erreur = "Échec de la sortie !"
        return render(request, 'depense/formulaire_depense.html', {'message_erreur': message_erreur})

@login_required
def  Depense_Data(request): 

    # Récupération des objets Sorte_Offrande
    data = Depense.objects.all()

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
    return render(request, 'depense/data_depense.html', context)




def bonSortiePage(request, id):
    
    data = Depense.objects.get(id=id)
    
    context = {'data' : data}
    page = 'rapport/bon_sortie.html'
    return render(request, page, context )


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
    # Format des données pour le graphique
    
    
    
    
    
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

def recu_pdf(request, id):
    
    try:
        data = Payement_Offrande.objects.get(id=id)
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
    p.drawString(130, height - 30, "ECC/36ème C.B.C.A")
    p.drawString(130, height - 50, "Département : FINANCE")  # Assurez-vous que c'est correct
    p.drawString(130, height - 70, "Institution : BP 495 GOMA")

    # Montant en haut à droite
    p.setFont("Helvetica-Bold", 12)
    p.drawString(width - 150, height - 50, f"{data.montant}$")

    # Titre du reçu (générer un numéro de reçu unique)
    receipt_number = f"0001/{datetime.now().year}"  # Exemple de numéro de reçu
    p.setFont("Helvetica-Bold", 16)
    p.drawString(220, height - 130, f"REÇU N° {receipt_number}")

    # Détails du reçu
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 170, f"Reçu de : Louis")  # Assurez-vous que c'est correct
    p.drawString(50, height - 190, f"Montant (en lettres) : {convert_amount_to_words(data.montant)} $") #fonction à créer pour convertir le montant en lettres.
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

def convert_amount_to_words(amount):
    # Fonction à implémenter pour convertir le montant en lettres
    # Exemple simple (à adapter pour une gestion complète)
    return "Dix" if amount == 10 else "Montant non géré"


def bon_sorti_pdf(request, id):
    
    try:
        data = Depense.objects.get(id=id)
    except Depense.DoesNotExist:
        return HttpResponse("Pas de donnee sur les penses", status=404)  # Gestion de l'erreur si l'objet n'existe pas

    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A5))
    width, height = landscape(A5)
    
    # Ajout du logo avec fond opaque
    logo_path = "static/img/logo.png"  # Remplacez par le chemin de votre logo
    p.drawImage(logo_path, 50, height - 80, width=60, height=60, mask='auto')
    
    # Informations générales (montées légèrement)
    p.setFont("Helvetica", 12)
    p.drawString(120, height - 30, "ECC/36ème C.B.C.A")
    p.drawString(120, height - 50, "Département : FINANCE")
    p.drawString(120, height - 70, "Institution : EGLISE CBCA/KATOYI")
    p.drawString(120, height - 90, "BP : 495 GOMA")
    # Montant en haut à droite
    p.setFont("Helvetica-Bold", 12)
    p.drawString(width - 160, height - 50, f"Date : {data.date_sortie}")
    
    # Titre du reçu
    p.setFont("Helvetica-Bold", 16)
    p.drawString(width / 2 - 150, height - 120, "BON DE SORTIE DE CAISSE N° 0001/2025")
    
    # Détails du reçu
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 150, f"Nom de beneficiaire : {data.nom_beneficiaire}")
    p.drawString(50, height - 170, f"Montant (en lettres) : {data.montant_lettre}")
    p.drawString(50, height - 190, f"Motif du paiement : {data.motif}")
    
    # Tableau 3x3
    # 3x3 Tableau (on dessine d'abord les lignes, puis on les remplit avec des textes)
    x_start = 50
    y_start = height - 220
    cell_width = 150
    cell_height = 20

# Dessiner les lignes du tableau
    for i in range(4):  # 4 lignes (inclut la ligne du bas)
        p.line(x_start, y_start - i * cell_height, x_start + 3 * cell_width, y_start - i * cell_height)

    for j in range(4):  # 4 colonnes (inclut la colonne de droite)
        p.line(x_start + j * cell_width, y_start, x_start + j * cell_width, y_start - 3 * cell_height)

# Remplir le tableau avec des données (par exemple des informations sur les transactions)
    p.setFont("Helvetica", 10)

# Ligne 1 (Titres des colonnes)
    p.drawString(x_start + 10, y_start - 10, "Numero du compte")
    p.drawString(x_start + cell_width + 10, y_start - 10, "Description")
    p.drawString(x_start + 2 * cell_width + 10, y_start - 10, "Montant")

# Ligne 2
    p.drawString(x_start + 10, y_start - 30, f"{data.compte.nom_offrande.num_compte}")
    p.drawString(x_start + cell_width + 10, y_start - 30, f"{data.compte.nom_offrande}")
    p.drawString(x_start + 2 * cell_width + 10, y_start - 30, f"{data.montant}")

    
    # Section Caisse
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 310, "Tresorier/ RPS/EVARES/ Comptable.Sce")
    
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
    return FileResponse(buffer, as_attachment=True, filename=f"Bon de sorti de {data.nom_beneficiaire}.pdf")
