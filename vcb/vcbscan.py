#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import urllib
import pywikibot
site = pywikibot.Site('fr', u'wikiversity')

### PATHNAME sépare l'argument initial en élements du path
def pathname(path, srv):
  rqParseWkt = '?action=parse&format=xml&page=%s&prop=wikitext&contentdataZone=wikitext' % path   # rećupère le Wikitext de la page cible
  objf = urllib.urlopen(srv + rqParseWkt)   # Ouvre l'url dans l'objet
  varf = objf.read()              # Lit le contenu dans la variable.
  objf.close()                    # ferme l'objet url
  strfile = str(varf)             # convertit la varible en chaine
  ufile = unicode(varf, 'utf-8')
  reLesson = re.compile('{{[L|l]eçon')       # RegEx pour trouver le modèle "Leçon"
  reChapitre = re.compile('{{[C|c]hapitre')  # RegEx pour trouver le modèle "Chapitre"
  list_path_elemt = path.split('/')     # split le path dans la liste
  nb_path_elemt = len(list_path_elemt)         # list_path_elemt contient tous les elements du path
  root_name = list_path_elemt[0]         # Premier element
  last_name = list_path_elemt[nb_path_elemt -1] # Dernier element
  list_sections = []  # Liste des sections à l'exclusion de root_name et last_name ex: rootname/nSec1/nSec2/lastname
  for element in list_path_elemt[1:list_path_elemt.index(last_name)]:  # Exclut root_name et last_name
    list_sections.append(element)
  lPath = [path, list_path_elemt, root_name, last_name, nb_path_elemt, list_sections]
  moLesson = reLesson.search(strfile)   # ATTENTION ici on cherche sur strfile
  moChapitre = reChapitre.search(ufile) # ATTENTION ici on cherche sur ufile - faire un choix!
  sommaire = unicode(root_name + '/Index vocabulaire', 'utf-8') # titre de la page contenant le sommaire des fiches de vocabulaire
  if nb_path_elemt == 1: # Si un seul element dans le path # Attention la condition
    print "La cible est un département, l\'exécution du programme peut prendre prendre plusieurs secondes en fonctions du nombre de leçons à traiter"   # On previent l'utilisateur
    class_doc = 'Département'      # On attribue class_doc en fonction de l'argument (pas de modèle en cause)
    new_page = root_name + '/Index vocabulaire/Index global'  # ATTENTION scinder la liste Indexglobal en 3
    # word (Index_global_des_mots), locution (Index_global_des_locutions), phrase (Index_global_des_phrases)
  elif moLesson:   # Si la page donnée en argument contient "le modèle Leçon"
    class_doc = 'Leçon'  # class_doc est attribué par "le modèle Leçon"
    print 'La cible est une ' + class_doc
    new_page = root_name + '/Index vocabulaire/vcb ' + last_name
  elif moChapitre:   # Si la page donnée en argument contient le modèle "Chapitre"
    class_doc = 'Chapitre'    
    print 'La cible est un ' + class_doc
    new_page = root_name + '/Index vocabulaire/vcb '+ last_name
  else:   # Si aucun des modèles suivants: Departement, leçon ou Chapitre
    class_doc = 'none'
    print 'Le type de cible est indéfini, ' + class_doc    
    new_page = root_name + '/Index vocabulaire/vcb ' + last_name
  ### QUELLE DIFFERENCE ENTRE CHAPITRE ET NONE?
  linker = [class_doc, new_page, sommaire] # Sortie de boucle on sauve les varibles dans linker
  lPath.append(linker) # ajoute linker à la liste lPath (list_path_elements)
  return lPath         # retourne la liste des elements du path
### PATHNAME FIN

### SHORTLIST (add_special_dir) Ajoute les pages des dossiers spéciaux pour leçons françaises
def shortlist(mylist, argument) :
  shortList = []    # Liste pour les pages à traiter
  subFolder = ['Annexe', 'Exercices', 'Fiche', 'Quiz', 'Travail_pratique'] # LES DOSSIERS DES LEÇONS
  prefix = argument + '/'       # declare prefix pour tronquer la première partie
  for page in mylist:   
    for sub in subFolder:
      argSub = argument + '/' + sub  # ajoute separateur (utiliser la variable prefix!)
      if re.match(argSub, page):     # si la ligne commence par argument/sub
        shortList.append(page)       # place la page dans la liste
  for page in mylist:
    if re.match(prefix, page):   # on gardera la page racine
      moPlace = re.match(prefix, page)   
      iMoPlace =  moPlace.end()  #index de la fin du prefix
      page = page[iMoPlace : ]   #tronque le prefix
      if '/' in page:   # Si il reste une barre oblique : sous dossier, on ne traitera pas
        pass            # on ne traite pas les sous dossiers
      else:
        shortList.append(argument + '/' + page)   # On place la page dans PAGESHORTLIST
  return shortList 

### TPLINSIDE Vérifie la présence de modèle à l'interieur des cellules
def tplinside (myDict):   # Attend un dictionnaire en entrée
  tplInsideDict = {}      # Dictionnaire des items à supprimer
  reTplInside = re.compile('{{')   # Expression régulière à chercher
  for k in myDict:   # Pour chaque clé
    v = myDict[k]    # La valeur correspondante
    moTplk = reTplInside.search(k)   # Cherche modèle et répond 
    moTplv = reTplInside.search(v)   # Cherche modèle et répond 
    if moTplk:   # Si model dans la clé
      tplInsideDict[k] =  myDict[k]   # Copie dans liste à supprimer
    elif moTplv: # Si model dans la valeur
      tplInsideDict[k] =  myDict[k]   # Copie dans liste à supprimer
  return tplInsideDict   # Retourne le dictionnaire des items à supprimer
### TPLINSIDE FIN



### Abandon momentané des fonctions write position et insert
### Même en programmant l'ecriture du sommaire, les liens ne seraient pas triés correctement
### c-à-d selon leur position dans les index des leçons. Si reprise du travail, considérer la liste 
### path_elemt
#def write_position(list_sections, sommaire): #Verfifie si le titr-section existe
  #section_index = 0
  
  #title = sommaire   
  #page = pywikibot.Page(site, title) # PWB variable
  #wikitext = page.get()
  #for section in list_sections:
    #section_uni = unicode(section, 'utf-8') # UNICODE
    #reSection = re.compile('=+ ' + section + ' =+') # ATTENTION il faudrait determiner le nombre precis de symbole = à chercherla section encadré de plusieurs = ou ===
    #moSection = reSection.search(wikitext)   # cherche les titres du sommaire 
    #if moSection:  
      #sommaire = title + '#' + section_uni  # defini la titre-section où écrire le lien
      #section_index = list_sections.index(section) +1 # position dans liste pour fx insert
  #return sommaire, section_index

#def insert(section_index, list_sections):  # ecrit les sections `a inserer
  #filtred_sections = list_sections[ section_index : ]  # Ne pas ecrire les sections déjà présentes
  #insert_txt = u''
  #for section in filtred_sections:
    #section_uni = unicode(section, 'utf-8') # UNICODE
    #title_level = section_index + 2
    #fix = ''
    #count =1
    #while count <= title_level: # ajoute le nombre de symbole egal necessaire
      #fix = fix + '='
      #count = count + 1
    #insert_txt = insert_txt + '\n' + fix + ' ' + section_uni + ' ' + fix # Compile les sections
  #return insert_txt
  

### FXPRON Scan les modèles Prononciation
## Améliorer en testant la présence de la colonne 4