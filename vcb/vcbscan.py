#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import urllib
import pywikibot
site = pywikibot.Site('fr', u'wikiversity')

### SHORTLIST
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
      page = page[iMoPlace : ]    #tronque le prefix
      if '/' in page:   # Si il reste une barre oblique : sous dossier, on ne traitera pas
        pass            # on ne traite pas les sous dossiers
      else:
        shortList.append(argument + '/' + page)   # On place la page dans PAGESHORTLIST
  return shortList 

### PATHNAME sépare l'argument initial en élements du path
def pathname(path, srv):
  rqParseWkt = '?action=parse&format=xml&page=%s&prop=wikitext&contentdataZone=wikitext' % path   # rećupère le Wikitext de la page cible
  objf = urllib.urlopen(srv + rqParseWkt)   # Ouvre l'url dans l'objet
  varf = objf.read()              # Lit le contenu dans la variable.
  objf.close()                    # ferme l'objet url
  strfile = str(varf)             # convertit la varible en chaine
  ufile = unicode(varf, 'utf-8')
  reLesson = re.compile('{{[L|l]eçon')   # ATTENTION probleme encodage unicode sur le ç de leçon
  reChapitre = re.compile('{{[C|c]hapitre')  # RegEx pour trouver le modèle "Chapitre"
  list_names = path.split('/')   # split le path dans la liste
  nbName = len(list_names)       # -2 (
  rootName = list_names[0]       # Premier element
  lastName = list_names[nbName -1]   # Dernier element
  list_sections = []  # Liste des sections à l'exclusion de rootName et lastName ex: rootname/nSec1/nSec2/lastname
  for element in list_names[1:list_names.index(lastName)]:  # Exclut rootName et lastName
    list_sections.append(element)
  lPath = [path, rootName, lastName, nbName, list_sections]
  moLesson = reLesson.search(strfile)   # ATTENTION ici on cherche sur strfile
  moChapitre = reChapitre.search(ufile) # ATTENTION ici on cherche sur ufile - faire un choix!
  sommaire = unicode(rootName + '/Index vocabulaire', 'utf-8') # titre de la page contenant le sommaire des fiches de vocabulaire
  if nbName == 1: # Si un seul element dans le path
    ### Attention à la condition
    print "La cible est un département, l\'exécution du programme peut prendre prendre plusieurs secondes en fonctions du nombre de leçons à traiter"   # On previent l'utilisateur
    className = 'Département'              ### 
    new_page = rootName + '/Index vocabulaire/Index global'  # Titre de la page 
    #linkTo = rootName + '/Index vocabulaire/' 
  elif moLesson:   # Si la page donnée en argument contient le modèle Leçon
    className = 'Leçon'  
    print 'La cible est une ' + className
    new_page = rootName + '/Index vocabulaire/vcb ' + lastName
    #linkTo = rootName + '/Index vocabulaire/'
  elif moChapitre:   # Si la page donnée en argument contient le modèle "Chapitre"
    className = 'Chapitre'    
    print 'La cible est un ' + className
    new_page = rootName + '/Index vocabulaire/vcb '+ lastName
    #linkTo = rootName + '/Index vocabulaire/'
  else:   # Si aucun des modèles suivants: Departement, leçon ou Chapitre
    className = 'none'
    print 'Le type de cible est indéfini, ' + className    
    new_page = rootName + '/Index vocabulaire/vcb ' + lastName
    #linkTo = rootName + '/Index vocabulaire/'
  linker = [className, new_page, sommaire] # Sortie de boucle on sauve les varibles dans linker
  # linkTo
  lPath.append(linker) # ajoute linker à la liste lPath (list_path_elements)
  return lPath   # retourne la liste des elements du path
### PATHNAME FIN

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

def write_position(list_sections, sommaire): #Verfifie si le titr-section existe
  section_index = 0
  
  title = sommaire   
  page = pywikibot.Page(site, title) # PWB variable
  wikitext = page.get()
  for section in list_sections:
    section_uni = unicode(section, 'utf-8') # UNICODE
    reSection = re.compile('=+ ' + section + ' =+') # ATTENTION il faudrait determiner le nombre precis de symbole = à chercherla section encadré de plusieurs = ou ===
    moSection = reSection.search(wikitext)   # cherche les titres du sommaire 
    if moSection:  
      sommaire = title + '#' + section_uni  # defini la titre-section où écrire le lien
      section_index = list_sections.index(section) +1 # position dans liste pour fx insert
  return sommaire, section_index

def insert(section_index, list_sections):  # ecrit les sections `a inserer
  filtred_sections = list_sections[ section_index : ]  # Ne pas ecrire les sections déjà présentes
  insert_txt = u''
  for section in filtred_sections:
    section_uni = unicode(section, 'utf-8') # UNICODE
    title_level = section_index + 2
    fix = ''
    count =1
    while count <= title_level: # ajoute le nombre de symbole egal necessaire
      fix = fix + '='
      count = count + 1
    insert_txt = insert_txt + '\n' + fix + ' ' + section_uni + ' ' + fix # Compile les sections
  return insert_txt
  

### FXPRON Scan les modèles Prononciation
## Améliorer en testant la présence de la colonne 4