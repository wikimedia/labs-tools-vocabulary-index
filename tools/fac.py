#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
### Création d'une liste de faculté 
### basée sur l'analyse de l'espace de nom "Faculté:" via Pywikibot sur num_id "106"
### modifier les var num_id language et api pour obtenir les listes en,de,es,pt
### le script produit un fichier csv, liste des facultés & départements associés
### ATTENTION la page accueil (à déplacere t renommer) et la page Sociologie (Redirection)
# voir nb dept Médecine 73 ou 75?
########################################################################

import pywikibot
lang = 'fr'                    # prefixe langue
family = 'wikiversity'
site = pywikibot.Site(lang, family) # On obtient très facilement la liste des pages dans l'espace de nom 106 Faculté via Pywikibot
gen_fac = site.allpages(namespace=106) #, prefix='a')
count = 0
liste_facultes = []  # pages
liste_sous_pages = [] # sous-pages

for page in gen_fac:
  str_page = str(page) # il faut une chaine pour re
  if '/' in str_page: #mosp:
    liste_sous_pages.append(page)  # La liste des sous-pages
  else:
    liste_facultes.append(page)   # La liste des facultés
print str(len(liste_facultes)) + ' Facultés\nListe des départements pour chaque faculté'

fFac = open('Fac.csv', 'w')
fFac.write('Faculté, Nombre département(s)\n') # Liste des départements
totalDpt = 0 # Ce total ne tient pas compte des doublons ( 1 dept=> +2 Fac)

data_fac = {}   # key = faculté ; value = fac_params
for faculte in liste_facultes:   # pour chaque faculté
  fac_params = []     # liste contenanat celle des departements (gen_dpt) puis nombre_departement
  sous_page_fac = []  # Liste les sous_pages de chaque faculté dans ns
  str_faculte = str(faculte)
  str_faculte = str_faculte[0:-2] + '/'  # tronque les crochets fermants et Ajoute le separateur 
  for sous_page in liste_sous_pages:     # Attribue les sous-pages sur la base du prefix
    str_sous_page = str(sous_page)       # 
    if str_faculte in str_sous_page:     # en comparant les deux chaines
      sous_page_fac.append(sous_page)    # Pas d'autre verification...
  fac_params.append(sous_page_fac)       # Affecte la liste sp_fac comme premier elemnt de liste fac_params
  gen_dpt = faculte.linkedPages(namespaces=108)
  fac_params.append(gen_dpt)
  nombre_departement = 0   # Initialise le compteut de département
  texte = ''
  for departement in gen_dpt:   # Pour chaque lien dans le generateur PWB
    nombre_departement = nombre_departement + 1   # Compte les départements
    #texte = (texte + str(departement) + ' ; ')    # ATTENTION impression liste des departements désactivé
    ### Pour enregistrer localement coder les chaines en string!     
  fac_params.append(nombre_departement)   # Le nombre de dṕartement par faculté
  data_fac[faculte] = fac_params
  nb_sous_page = len(sous_page_fac)
  s_nb_sp = str(nb_sous_page)
  texte = str(nombre_departement) + ', ' + s_nb_sp     
  fFac.write(str(faculte) + ', ' + texte + '\n')   # Imprime une faculté, nb_departement, nb sous-page 
  ### Imprimer une liste supplémentaire
  ### titre de la page = ../Liste des départements par faculté
  ### == Faculté ==
  ### * Departement 1
  ### * Departement 2...
  totalDpt = totalDpt + nombre_departement
  print nombre_departement
fFac.close()
print str(totalDpt) + ' dept répartis dans les facultés'
#   data_fac[faculte] = fac_params (sous_page_fac, gen_dpt, nombre_departement)

### Pour obtenir le nombre departements, les facultés associées et leur nombre
### Nous inversons le dictionnaire (Liste des facultés par département)
dpt_fac = {}            # Tuple invere
for page in data_fac:   #  Pour Chaque faculté
  fac_params = data_fac[page]  # une liste de parametres
  [sous_page_fac, gen_dpt, nombre_departement] = fac_params # Liste des parametre deja dans le tuple
  for departement in gen_dpt:  # pour chaque departement dans cette faculté
    if not departement in dpt_fac:   # Si le departement n'est pas dans le tuple inverse
      l_fac = []         # Initialise Liste des faculté pour ce departement
      l_fac.append(page) # Ajoute la faculté dans la liste
      dpt_fac[departement] = l_fac   # enregistre clé valeur dans le tuple invers
    else:   # Le departement est deja dans le tuple inverse
      l_fac = dpt_fac[departement]  # Recupere la liste 
      l_fac.append(page)            # Ajoute la faculté dans la liste

f_dpt_fac = open('dpt_fac.csv', 'w')
f_dpt_fac.write('Departement, Nombre Faculté(s), Liste des Facultés\n')
for dpt in dpt_fac:  
  l_fac = dpt_fac[dpt]
  nb_fac_dep = len(l_fac)
  dpt_params = [nb_fac_dep, l_fac]
  dpt_fac[dpt] = dpt_params
  texte = '"' + str(dpt) + '", '   # + str(len(l_fac)) + ', '
  print_fac = ''
  for fac in l_fac:
    print_fac = print_fac + str(fac) + ' - '
  f_dpt_fac.write(texte +  str(nb_fac_dep) + ', ' + print_fac + '\n')
f_dpt_fac.close()
print len(dpt_fac)
### Imprimer le tableau  directement dans une page distincte
### titre page = ../Liste des facultés par département