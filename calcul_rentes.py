#%%

## REMARQUE : lx_dict a rapidement été supprimé des inputs mais quand on aura plusieurs variables il faudra le remettre et adapter

import pandas as pd
import math
import datetime

# import de la table de mortalité 
df_morta = pd.read_csv("table_pr_python.csv")

# On transforme en entier et on créé un dictionnaire 
df_morta["lx"] = df_morta["lx"].str.replace(",", "", regex=False)
df_morta["lx"] = df_morta["lx"].astype(int)
lx_dict = dict(zip(df_morta["âge"], df_morta["lx"])) # lx est le nombre de survivant à l'âge x

# On va considérer (même si cela est un petit peu erroné que l'on a pas de chances de survie après 104 ans cf. table) 
# Il faudra adapter ceci ensuite quand on aura des vrais tables 
for age in range(105, 201):
    lx_dict[age] = 0


def proba(x, t, lx_dict):
    "calcule la probabilité conditionelle tpx en fonction du dictionnaire i.e de la table sélectionnée"
    return lx_dict[x + t] / lx_dict[x]


########################################################################################################
################################## Calcul des coefficients de rentes ###################################
########################################################################################################

########################## 1. Âge entier et paiement annuel ##########################

# Paramètre TE : pour préciser si le terme est "Échu" (payable en fin de période) ou "À échoir" (en début de période)

def coeff_rente_classique(x, taux, lx_dict, TE):
    "Calcul du coefficient de rente dans le cas d'une rente classique"
    "x : âge, taux : taux d'actualisation / taux d'intérêt technique, lx_dict : dictionnaire de la table de mortalité"
    "TE : pour le terme, vaut 'Échu' si paiement des rentes en fin de période et 'À échoir' si paiement en début de période"
    a = 0
    if TE == "À échoir":
        for t in range(0, 120):
            a += proba(x, t, lx_dict) / (1 + taux)**t
    elif TE == "Échu":
        for t in range(1, 121):
            a += proba(x, t, lx_dict) / (1 + taux)**t
    else :
        raise ValueError("TE doit être égal à 'Échu' ou 'À échoir'")
    return a 



def coeff_rente_avec_reversion(x, y, taux, lx_dict, TE): # normalement il y a sûrement deux tables de mortalité différentes pour les deux conjoints
    "y : âge du conjoint"
    a=0
    if TE == "À échoir":
        for t in range(0, 120):
            a += (proba(x, t, lx_dict) + proba(y, t, lx_dict) - proba(x, t, lx_dict)*proba(y, t, lx_dict)) / (1 + taux)**t
    elif TE == "Échu":
        for t in range(1, 121):
            a += (proba(x, t, lx_dict) + proba(y, t, lx_dict) - proba(x, t, lx_dict)*proba(y, t, lx_dict)) / (1 + taux)**t
    else :
        raise ValueError("TE doit être égal à 'Échu' ou 'À échoir'")
    return a


def coeff_rente_annuites(x, taux, lx_dict, TE, n, alpha):
    "n = nombre d'annuités garanties chosies"
    "alpha : pourcentage de rente versées au bénéficiaire le cas échéant"
    if x > 67:
        raise ValueError("x ne peut pas être supérieur à 67")
    a = 0
    if TE == "À échoir":
        for t in range(0, 120):
            a += proba(x, t, lx_dict) / (1 + taux)**t
    elif TE == "Échu":
        for t in range(1, 121):
            a += proba(x, t, lx_dict) / (1 + taux)**t
    else :
        raise ValueError("TE doit être égal à 'Échu' ou 'À échoir'")
    for t in range(0, n):
        a += alpha * (1 - proba(x, t, lx_dict)) / (1 + taux)**t
    return a

def coeff_rente_reversion_annuites(x, y, taux, lx_dict, TE, beta, n, alpha):
    "Cas d'une rente avec réversion + annuités garanties"
    "beta : pourcentage de réversion, i.e pourcentage de la rente versée au conjoint s'il en reçoit une"
    "alpha : pourcentage de la rente versée au bénéficiaire s'il en reçoit une"
    if x > 67:
        raise ValueError("x ne peut pas être supérieur à 67")
    a = 0
    if TE == "À échoir":
        for t in range(0, 120):
            a += (proba(x, t, lx_dict) + beta*(1 - proba(x, t, lx_dict))*proba(y, t, lx_dict)) / (1 + taux)**t
    elif TE == "Échu":
        for t in range(1, 121):
            a += (proba(x, t, lx_dict) + beta*(1 - proba(x, t, lx_dict))*proba(y, t, lx_dict)) / (1 + taux)**t
    else :
        raise ValueError("TE doit être égal à 'Échu' ou 'À échoir'")
    for t in range(0, n):
        a += alpha * (1 - proba(x, t, lx_dict))*(1 - proba(y, t, lx_dict)) / (1 + taux)**t
    return a

def coeff_rente_palier(x, taux, lx_dict, TE): 
    "augmentation de 20% à 70 ans et à nouveau de 20% à 75 ans"
    if x > 67:
        raise ValueError("x ne peut pas être supérieur à 67")
    t1 = 70 - x
    t2 = 75-x
    a = 0
    if TE == "À échoir":
        for t in range(0, t1):
            a += proba(x, t, lx_dict) / (1 + taux)**t
        for t in range(t1, t2):
            a += 1.2 * proba(x, t, lx_dict) / (1 + taux)**t
        for t in range(t2, 120):
            a += 1.44 * proba(x, t, lx_dict) / (1 + taux)**t
    elif TE == "Échu":
        for t in range(1, t1 + 1):
            a += proba(x, t, lx_dict) / (1 + taux)**t
        for t in range(t1 + 1, t2 + 1):
            a += 1.2 * proba(x, t, lx_dict) / (1 + taux)**t
        for t in range(t2 + 1, 121):
            a += 1.44 * proba(x, t, lx_dict) / (1 + taux)**t
    else :
        raise ValueError("TE doit être égal à 'Échu' ou 'À échoir'")
    return a




################ 2. Ajustement pour prendre en compte les âges non entiers et les paiements non annuels #################

## WARNING : On a supprimé lx_dict (qui est toujours le même) des variables d'entrée, à l'avenir si on a plusieurs tables de 
# mortalité il faudra rajouter cette variable à partir d'ici jusqu'au fonctions finales 


def calcul_age(date_naissance, date_actuelle):
    "renvoie deux valeurs : le nombre d'années + le nombre de mois de l'âge"
    age_years = date_actuelle.year - date_naissance.year
    if (date_actuelle.month, date_actuelle.day) < (date_naissance.month, date_naissance.day): # si l'anniversaire n'est pas passé
        age_years -= 1 # on retire une année
        age_months = 12 - (date_naissance.month - date_actuelle.month) 
    else:
        age_months = date_actuelle.month - date_naissance.month
    return (age_years, age_months)

# print(calcul_age(datetime.date(2000, 3, 4), datetime.date(2025, 3, 2)))


def calcul_rente_simple(capital, date_naissance, date_actuelle, taux, TE, m):
    "On calcule le coefficient de rente en prenant en compte le nombre de mois dans l'âge et la fréquence de paiement"
    "m : fréquence de paiement : 1 pour annuelle, 2 pour semestrielle, 4 pour trimestrielle etc."
    # m est la fréquence de paiement : 1 pour annuel, 12 pour mensuel, etc.
    x, mois = calcul_age(date_naissance, date_actuelle) # on récupère le nombre d'années de l'âge
    a_0 = coeff_rente_classique(x, taux, lx_dict, TE)
    a_1 = coeff_rente_classique(x + 1, taux, lx_dict, TE)
    if TE == "À échoir":
        a = (1 - mois/12)*a_0 + (mois/12)*a_1 - (m-1)/(2*m)
    elif TE == "Échu":
        a = (1 - mois/12)*a_0 + (mois/12)*a_1 + (m-1)/(2*m)
    return capital / a



def calcul_rente_reversion(capital, date_naissance, date_actuelle, taux, TE, m, date_naissance_conjoint):
    "On demande également la date de naissance du conjoint dans le cas de la réversion"
    x, mois_x = calcul_age(date_naissance, date_actuelle) # on récupère le nombre d'années et de mois de l'âge
    y, mois_y = calcul_age(date_naissance_conjoint, date_actuelle)
    a_0_0 = coeff_rente_avec_reversion(x, y, taux, lx_dict, TE)
    a_1_0 = coeff_rente_avec_reversion(x + 1, y, taux, lx_dict, TE)
    a_0_1 = coeff_rente_avec_reversion(x, y + 1, taux, lx_dict, TE)
    a_1_1 = coeff_rente_avec_reversion(x + 1, y + 1, taux, lx_dict, TE)
    if TE == "À échoir":
        a = (1 - mois_x/12)*(1 - mois_y/12)*a_0_0 + (mois_x/12)*(1 - mois_y/12)*a_1_0 + (1 - mois_x/12)*(mois_y/12)*a_0_1 + (mois_x/12)*(mois_y/12)*a_1_1 - (m-1)/(2*m)
    elif TE == "Échu":
        a = (1 - mois_x/12)*(1 - mois_y/12)*a_0_0 + (mois_x/12)*(1 - mois_y/12)*a_1_0 + (1 - mois_x/12)*(mois_y/12)*a_0_1 + (mois_x/12)*(mois_y/12)*a_1_1 + (m-1)/(2*m)
    return capital / a

def calcul_rente_annuites(capital, date_naissance, date_actuelle, taux, TE, m, n, alpha):
    x = calcul_age(date_naissance, date_actuelle)[0] # on récupère le nombre d'années de l'âge
    mois = calcul_age(date_naissance, date_actuelle)[1]
    a_0 = coeff_rente_annuites(x, taux, lx_dict, TE, n, alpha)
    a_1 = coeff_rente_annuites(x + 1, taux, lx_dict, TE, n, alpha)
    if TE == "À échoir":
        a = (1 - mois/12)*a_0 + (mois/12)*a_1 - (m-1)/(2*m)
    elif TE == "Échu":
        a = (1 - mois/12)*a_0 + (mois/12)*a_1 + (m-1)/(2*m)
    return capital / a

def calcul_rente_reversion_annuites(capital, date_naissance, date_actuelle, taux, TE, m, date_naissance_conjoint, beta, n, alpha):
    x = calcul_age(date_naissance, date_actuelle)[0] # on récupère le nombre d'années de l'âge
    y = calcul_age(date_naissance_conjoint, date_actuelle)[0]
    mois_x = calcul_age(date_naissance, date_actuelle)[1]
    mois_y = calcul_age(date_naissance_conjoint, date_actuelle)[1]
    a_0_0 = coeff_rente_reversion_annuites(x, y, taux, lx_dict, TE, beta, n, alpha)
    a_1_0 = coeff_rente_reversion_annuites(x+1, y, taux, lx_dict, TE, beta, n, alpha)
    a_0_1 = coeff_rente_reversion_annuites(x, y+1, taux, lx_dict, TE, beta, n, alpha)
    a_1_1 = coeff_rente_reversion_annuites(x+1, y+1, taux, lx_dict, TE, beta, n, alpha)
    if TE == "À échoir":
        a = (1 - mois_x/12)*(1 - mois_y/12)*a_0_0 + (mois_x/12)*(1 - mois_y/12)*a_1_0 + (1 - mois_x/12)*(mois_y/12)*a_0_1 + (mois_x/12)*(mois_y/12)*a_1_1 - (m-1)/(2*m)
    elif TE == "Échu":
        a = (1 - mois_x/12)*(1 - mois_y/12)*a_0_0 + (mois_x/12)*(1 - mois_y/12)*a_1_0 + (1 - mois_x/12)*(mois_y/12)*a_0_1 + (mois_x/12)*(mois_y/12)*a_1_1 + (m-1)/(2*m)
    return capital / a

def calcul_rente_palier(capital, date_naissance, date_actuelle, taux, TE, m):
    x = calcul_age(date_naissance, date_actuelle)[0] # on récupère le nombre d'années de l'âge
    mois = calcul_age(date_naissance, date_actuelle)[1]
    a_0 = coeff_rente_palier(x, taux, lx_dict, TE)
    a_1 = coeff_rente_palier(x + 1, taux, lx_dict, TE)
    if TE == "À échoir":
        a = (1 - mois/12)*a_0 + (mois/12)*a_1 - (m-1)/(2*m)
    elif TE == "Échu":
        a = (1 - mois/12)*a_0 + (mois/12)*a_1 + (m-1)/(2*m)
    return capital / a




########################################################################################################
######################################### Simulateur de rentes #########################################
########################################################################################################


################################ 1. Gestion du rendement et fonctions intermédiaires ################################ 

# On ne prendra que les gestions pilotées en compte pour l'instant comme on ne peut pas récupérer l'allocation entre les fonds
# dans le cas de a gestion manuelle 

# import des grilles d'allocation entre les fonds en fonction du profil de l'épargnant
df_grille_prudent = pd.read_csv("grille_fond_prudent.csv")
df_grille_equilibre = pd.read_csv("grille_fond_equilibre.csv")
df_grille_dynamique = pd.read_csv("grille_fond_dynamique.csv")


def transfo_grilles(df):
    "Permet de transformer les grilles d'allocation en dictionnaire de la forme {âge : [répartition entre les fonds]}"
    colonnes_fonds = [f"fond{i}" for i in range(1, 7)]

    df[colonnes_fonds] = (
        df[colonnes_fonds].replace('%', '', regex=True) # Conversion "3%" -> 0.03
        .astype(float)
        / 100)
    
    dico_grille = {
    int(row["annee avant retraite"]): row[colonnes_fonds].to_numpy()
    for _, row in df.iterrows()
    }
    return dico_grille

# On se sert de la fonction pour transformer les 3 grilles 
dico_grille_dynamique = transfo_grilles(df_grille_dynamique)
dico_grille_equilibre = transfo_grilles(df_grille_equilibre)
dico_grille_prudent = transfo_grilles(df_grille_prudent)


def rendement_annuel(dico_grille, annee_avant_retr):
    "Renvoie le rendement annuel en fonction de la grille et du nombre d'année avant retraite"
    "On détermine les rendements individuels des fonds en fonction de son risque (sur 7) uniquement"
    # rendements_nets = [1.073, 1.0619, 1.0604, 0.9972, 0.9967, 0.98]
    rendement_nets = [1.05, 1.03, 1.02, 1.02, 1.01, 1.0] # rendements en fonction du niveau de risque sur 7 des fonds
    if annee_avant_retr > 25:
        annee_avant_retr=25
    allocation = dico_grille[annee_avant_retr]
    return (allocation*(rendement_nets)).sum() - 1


def annees_pleine_avant_sortie(t, T):
    "Renvoie le nombre d'années pleines avant la sortie de l'argent en rente en fonction du temps t"
    return math.floor((T-1-t)/12)

def annee_civile(t, date_simul):
    "Renvoie l'année civile à laquelle correspond le temps t (en mois) : 0 pour l'année de simulation, puis 1 l'année suivante etc."
    mois_simul = date_simul.month 
    return math.floor((mois_simul + t - 1)/12)

def rendement_mensuel(t, dico_grille, date_simul, date_sortie):
    "Renvoie le rendement mensuel en fonction du temps : dépend la grille"
    T = (date_sortie.year - date_simul.year)*12 + (date_sortie.month - date_simul.month) # nombre de mois entre la simulation et la sortie d'argent
    k = annees_pleine_avant_sortie(t, T) # nombre d'années pleines avant sortie
    rend_annuel = rendement_annuel(dico_grille, k)
    return (1 + rend_annuel)**(1/12) - 1
 

################################ 2. Premier compartiment ################################ 

def K1_fin(K1, date_simul, date_sortie, dico_grille, VV_mens, taux_versement):
    """
    Calcule la valeur finale d'un capital selon la formule :
    K1_fin = Σ(t=1 à T-1) [ VV_mens * (1 - taux_versement) * Π(j=t+1 à T-1)(1 + r(j)) ]
             + K1 * Π(t=1 à T-1)(1 + r(t))
    """

    T = (date_sortie.year - date_simul.year)*12 + (date_sortie.month - date_simul.month)
    versement_net = VV_mens * (1 - taux_versement)

    # Partie 1 : somme des versements capitalisés
    somme_versements = 0
    for t in range(1, T):  
        # Produit Π(j=t+1 à T-1)(1 + r(j))
        capitalisation = 1.0
        for j in range(t + 1, T): 
            capitalisation *= (1 + rendement_mensuel(j, dico_grille, date_simul, date_sortie))
        somme_versements += versement_net * capitalisation

    # Partie 2 : capital initial capitalisé
    # Produit Π(t=1 à T-1)(1 + r(t))
    capitalisation_K1 = 1.0
    for t in range(1, T): 
        capitalisation_K1 *= (1 + rendement_mensuel(t, dico_grille, date_simul, date_sortie))

    K1_fin = somme_versements + K1 * capitalisation_K1

    return K1_fin



################################ 3. Second compartiment ################################

def abondement_brut(t, VV, tau, P, A0_deja_verse, date_simul):
    "t = mois courant (t=0 correspond au mois de simulation)"
    "VV : versement volontaire mensuel"
    "tau : taux d'abondement" 
    "P : plafond d'abondement"
    "A0_deja_verse : abondement déjà versé sur l'année civile en cours "
    "mois_simul : mois de simulation (1 à 12)"
    
    # On initialise les variables cumul et annee_courante :

    cumul = A0_deja_verse # abondements déjà versés sur l'année civile en cours

    annee_courante = annee_civile(0, date_simul)  # année civile en cours

    # on calcule tous les abondements précédents qui sont nécesaires pour le calcul du plafond restant
    for s in range(1, t + 1): # on ne compte pas le mois en cours car on considère qu'il n'y aura de VV le mois de simulation

        # Si changement d'année civile → reset du cumul
        if annee_civile(s, date_simul) != annee_courante:
            annee_courante = annee_civile(s, date_simul) # màj de l'année courante
            cumul = 0.0 # reset du cumul

        plafond_restant = P - cumul # Détermination du plafond restant

        A_s = max(0.0, min(tau * VV, plafond_restant))
    
        # Si on est au mois voulu, on return 
        if s == t:
            return A_s
        
        # Sinon on met à jour le cumul
        cumul += A_s
    


def abondement_net(t, VV, tau, P, A0_deja_verse, date_simul, statut):
    "Passage de l'abondement brut à celui prêt à être soumis aux frais d'entrée, avant d'arriver dans le C2"
    "Statut : 'TS' ou 'TNS'"
    "On prend le cas général pour ne pas s'embêter avec les différents taux"

    A_brut = abondement_brut(t, VV, tau, P, A0_deja_verse, date_simul)

    if statut == 'TS':
        abondement_net = A_brut * (1 - 0.097) # CSG 9,2% + CRDS 0,5%
    else :
        abondement_net = A_brut

    return abondement_net



def K2_fin(K2, date_simul, date_sortie, dico_grille, VV_mens, taux_versement, tau, P, A0_deja_verse, statut):
    T = (date_sortie.year - date_simul.year)*12 + (date_sortie.month - date_simul.month)

    total = 0.0

    # Somme liée aux versements à venir et leur rendement
    for t in range(1, T):
        produit = 1.0
        for j in range(t + 1, T):
            produit *= (1 + rendement_mensuel(j, dico_grille, date_simul, date_sortie))

        total += abondement_net(t, VV_mens, tau, P, A0_deja_verse, date_simul, statut) * (1 - taux_versement) * produit

    # Prise en valeur du capital déjà présent sur le compte
    produit_K2 = 1.0
    for t in range(1, T):
        produit_K2 *= (1 + rendement_mensuel(t, dico_grille, date_simul, date_sortie))

    total += K2 * produit_K2

    return total



################################ 4. Troisième compartiment ################################


def cotis_oblig_annuels(t, date_simul, cotis_obligatoire_an_dernier, statut):
    "Cotisations annuels pour l'année civile du mois t, net de CSG - CRDS (mais avant paiement des frais de versement)"
    "Demande de récupérer les cotisations obligatoires versées l'année civile précédente"
    c = annee_civile(t, date_simul)
    cotis_brute = cotis_obligatoire_an_dernier*(1.01)**(c + 1)
    if statut == 'TS' :
        cotis_nette = cotis_brute*(1-0.097) # CSG + CRDS = 9,7%
    else : 
        cotis_nette = cotis_brute
    return cotis_nette


def K3_fin(K3, date_simul, date_sortie, dico_grille, cotis_obligatoire_an_dernier, taux_versement, statut):
    "Dans le cas où les cotisations obligatoires sont versées mensuellement (en fin de mois) "
    T = (date_sortie.year - date_simul.year) * 12 + (date_sortie.month - date_simul.month)
    total = 0.0

    # Somme liée aux versements à venir et leur rendement
    for t in range(1, T):
        produit = 1.0
        for j in range(t + 1, T):
            produit *= (1 + rendement_mensuel(j, dico_grille, date_simul, date_sortie))

        total += cotis_oblig_annuels(t, date_simul, cotis_obligatoire_an_dernier, statut)* (1/12) * (1 - taux_versement) * produit

    # Prise en valeur du capital déjà présent sur le compte
    produit_K3 = 1.0
    for t in range(1, T):
        produit_K3 *= (1 + rendement_mensuel(t, dico_grille, date_simul, date_sortie))

    total += K3 * produit_K3

    return total



################################ 5. rassemblement des fonctions ################################

def capitaux_fin(K1, K2, K3, date_simul, date_sortie, grille, VV_mens, tau, P, A0_deja_verse, statut, taux_vers, cotis_moins1):
    K1_sortie = K1_fin(K1,  date_simul, date_sortie, grille, VV_mens, taux_vers)
    K2_sortie = K2_fin(K2, date_simul, date_sortie, grille, VV_mens, taux_vers, tau, P, A0_deja_verse, statut)
    K3_sortie = K3_fin(K3, date_simul, date_sortie, grille, cotis_moins1, taux_vers, statut)
    return (K1_sortie, K2_sortie, K3_sortie)

# print(capitaux_fin(10000, 10000, 10000, datetime.date(2026, 3, 8), datetime.date(2046, 6, 15), dico_grille_dynamique, 200, 0.75, 700, 400, 'TS', 0.02, 500))



################################ 6. Fiscalité en sortie - par compartiment ################################

def taux_abbatement_C1(x):
    if x < 50 : 
        return 0.3
    elif x >= 50 and x<60 :
        return 0.5
    elif x >= 60 and x<70 :
        return 0.6
    else :
        return 0.7

def net_C1(rente, date_naissance, date_actuelle, taux_arrerage, taux_PAS):
    x = calcul_age(date_naissance, date_actuelle)[0] # on récupère le nombre d'années de l'âge
    rente_brute = rente*(1-taux_arrerage)
    PS = rente_brute*(1 - taux_abbatement_C1(x))*0.186 # on taxe à 18,6% (après avoir enlevé la part abbatu)
    PAS = rente_brute*(1-0.068)*taux_PAS # 6,8% déductible
    return rente_brute - PS - PAS

def net_C2(rente, taux_arrerage):
    return rente*(1-taux_arrerage)

def net_C3(rente, taux_arrerage, taux_PAS):
    "Version simple à 10,1% --> on ne traite pas tous les cas particuliers"
    rente_brute = rente*(1-taux_arrerage)
    PS = rente_brute*0.0101 # dans le cas général : on négligera les cas plus rares dans ce simulateur 
    PAS = rente_brute*(1-0.059)*taux_PAS # dans le cas général : 5,9% déductible
    return rente_brute - PS - PAS




########################################################################################################
############################# Les fonctions finales - sortie et simulateur ##############################
########################################################################################################


# Dictionnaire de correspondance type_rente -> fonction
FONCTIONS_RENTE = {
    "classique": calcul_rente_simple,
    "reversion": calcul_rente_reversion,
    "annuites": calcul_rente_annuites,
    "reversion_annuites": calcul_rente_reversion_annuites,
    "palier": calcul_rente_palier,
}

def calcul_sortie_rente(type_rente, K1, K2, K3, date_naissance, date_simul, taux_arrerage, taux_PAS, **kwargs):
    try:
        fonction_coeff = FONCTIONS_RENTE[type_rente]
    except KeyError:
        raise ValueError(f"Type de rente '{type_rente}' non reconnu. Les types de rente valides sont : {', '.join(FONCTIONS_RENTE.keys())}.")

    r1_brute = fonction_coeff(K1, date_naissance, date_simul, **kwargs)
    r2_brute = fonction_coeff(K2, date_naissance, date_simul, **kwargs)
    r3_brute = fonction_coeff(K3, date_naissance, date_simul, **kwargs)

    # Prise en compte de la fiscalité
    r1_nette = net_C1(r1_brute, date_naissance, date_simul, taux_arrerage, taux_PAS)
    r2_nette = net_C2(r2_brute, taux_arrerage)
    r3_nette = net_C3(r3_brute, taux_arrerage, taux_PAS)

    return (r1_brute + r2_brute + r3_brute, r1_nette + r2_nette + r3_nette)



def simulateur_rente(K1, K2, K3, date_simul, date_sortie, grille, VV_mens, tau, P, A0_deja_verse, statut, taux_vers, 
                     cotis_moins1, date_naissance, type_rente, taux_arrerage, taux_PAS, **kwargs):
    K1_fin, K2_fin, K3_fin = capitaux_fin(K1, K2, K3, date_simul, date_sortie, grille, VV_mens, tau, P, A0_deja_verse, statut, taux_vers, cotis_moins1)
    
    # on utilise ces capitaux finaux pour faire tourner la fonction de sortie en rente
    rente_brute, rente_nette = calcul_sortie_rente(type_rente, K1_fin, K2_fin, K3_fin, date_naissance, date_simul, taux_arrerage,
                                                    taux_PAS, **kwargs)

    return (rente_brute, rente_nette)


# print(simulateur_rente(
#     25000, 10000, 15000,
#     datetime.date(2026, 3, 8),
#     datetime.date(2047, 6, 15),
#     dico_grille_dynamique,
#     739.84, 
#     1, 1200, 0,
#     'TS', 0.02, 1200,
#     datetime.date(1982, 1, 14),
#     "classique",
#     0.01, 0.14,
#     taux=0.01,
#     TE="Échu",
#     m=4
# ))



# Listing des informations à demander : 
# - les trucs de base : K1, K2, K3, date_simul, date_sortie, grille, VV_mens, tau, P, A0_deja_verse, statut, taux_vers, cotis_moins1, 
# - date_naissance, type_rente
# - ce qui est toujours dans le kwargs : taux (taux technique), TE, m
# - ce qui est des fois dans le kwargs : date_naissance_conjoint, n, alpha, beta



########################################################################################################
##################################### Réciproque : calcul des VV #######################################
########################################################################################################


# Méthode de dichotomie pour la fonction réciproque : détermination de VV_mens à partir de la rente nette visée 

def versement_pour_rente_cible(rente_nette_cible, K1, K2, K3, date_simul, date_sortie, grille, tau, P, A0_deja_verse, 
                                statut, taux_vers, cotis_moins1, date_naissance, type_rente, taux_arrerage, taux_PAS, **kwargs):
    
    def rente_nette_pour_VV(VV):
        _, rente_nette = simulateur_rente(K1, K2, K3, date_simul, date_sortie, grille, VV, tau, P, A0_deja_verse,
                                          statut, taux_vers, cotis_moins1, date_naissance, type_rente, taux_arrerage, taux_PAS, **kwargs)
        return rente_nette

    # Borne basse : VV = 0
    VV_bas = 0.0
    # Vérification que la rente cible est atteignable depuis VV=0
    rente_bas = rente_nette_pour_VV(VV_bas)
    if rente_bas >= rente_nette_cible:
        return 0.0

    # Recherche de la borne haute : on double VV jusqu'à dépasser la rente cible
    VV_haut = 100.0
    while rente_nette_pour_VV(VV_haut) < rente_nette_cible:
        VV_bas = VV_haut
        VV_haut *= 2

    # Dichotomie
    while (VV_haut - VV_bas) > 0.05:  # précision à 5 centimes sur VV --> pour éviter les boucles infinies 
        VV_mid = (VV_bas + VV_haut) / 2
        rente_mid = rente_nette_pour_VV(VV_mid)

        if abs(rente_mid - rente_nette_cible) < 1.0:  # moins d'1€ d'écart --> on considère que c'est bon
            return round(VV_mid, 2)
        elif rente_mid < rente_nette_cible:
            VV_bas = VV_mid
        else:
            VV_haut = VV_mid

    return round((VV_bas + VV_haut) / 2, 2)


# print(versement_pour_rente_cible( 
#     10000,
#     25000, 10000, 15000,
#     datetime.date(2026, 3, 8),
#     datetime.date(2047, 6, 15),
#     dico_grille_dynamique,
#     1, 1200, 0,
#     'TS', 0.02, 1200,
#     datetime.date(1982, 1, 14),
#     "classique",
#     0.01, 0.14,
#     taux=0.01,
#     TE="Échu",
#     m=4
# ))


# %%
