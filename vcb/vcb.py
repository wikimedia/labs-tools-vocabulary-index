#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import re
import sys
import pywikibot # PWB now
import codecs
import argparse
import time
from vcbscan import *
from vcbformat import *
from international import *

srv="https://fr.wikiversity.org/w/api.php"      # Adresse du serveur API
site = pywikibot.Site('fr', u'wikiversity')     # Variables PWB,  utile pour determiner pageLang

### ARGPARSE
parser = argparse.ArgumentParser()
parser.add_argument("cible", type=str,
                    help="Indiquez le titre de la leçon du département de langues étrangère dont vous souhaitez collecter le vocabulaire. Par défaut la liste obtenue sera sauvegardée dans le département à l'adresse suivante Département/Index vocabulaire/vcb NomLeçon")
parser.add_argument("-t", "--test", help="Enregistre la liste dans l'espace de test du laboratoire. Projet:Laboratoire/Propositions/Index_vocabulaire",
                    action="store_true")
args = parser.parse_args()
cible_unicode = unicode(args.cible, 'utf-8') # Encodage UNICODE pour PWB 
### EXEC PATHNAME
lPath = pathname(args.cible, srv)       # pathname avec l'argument et le serveur forme la variable lPath
[path, list_path_elemt, rootName, lastName, nbName, list_sections, linker] = lPath # dont ceci est la composition
[className, new_page, sommaire] = linker # avec la composition de linker

###PYWIKIBOT
title = cible_unicode   # Titre reçoit l'argument au format UNICODE
page = pywikibot.Page(site, title) # PWB variable

rqRootLang = '?action=languagesearch&format=xml&search=%s' % rootName
fromPage = args.cible
toPage = args.cible + 'a'
rqAllPages = '?action=query&list=allpages&format=xml&apfrom='+fromPage+'&apto='+toPage+'&aplimit=275' # ATTENTION max 275 pages
rqParseWkt = '?action=parse&format=xml&page=%s&prop=wikitext&contentdataZone=wikitext' % args.cible   # REQUETE PARSE Format XML content WIKITEXT

### RECHERCHE PAGELANG
sts =  str(site) # convertit site en string
i=sts.find(':')  # tronque la première partie
sts = sts[i+1:]  # defin it langue d'origine
pageLang = sts   # pageLang (langue native)
print 'Le script s\'execute dans l\'espace francophone.\nLangue source: fr'
### RECHERCHE ROOTLANG
askRootLang = srv + rqRootLang
objr = urllib.urlopen(askRootLang)
varf = objr.read()
xml_lang = str(varf)
reRootLang = re.compile('languagesearch \w*=') # The API changed
moRootLang = reRootLang.search(xml_lang)
if moRootLang:
  rootLang = moRootLang.group()
  rootLang = rootLang[ 15 : len(rootLang)-1 ]
  print rootLang  + '-' + pageLang 
else:
  print 'Impossible de déterminer la langue étudiée pour: ' + rootName
  exit()
###
log = ''     # Variable pour le journal
lAudio = []     # Liste pour la 3ème colonne du modèle Prononciation
globalDict = {} # Dictionnaire global 
###

### TRAITEMENT DE LA LISTE DEs PAGES
fileList = urllib.urlopen(srv + rqAllPages)   # requete fromPage toPage via urllib et APIsrv max limit
vfileList = fileList.read()
ufileList = unicode(vfileList, 'utf-8')       # UNICODE XML liste des pages ciblées
re_title_page=re.compile('title=".*"')        # recherche du titre de la page
rePron = re.compile('[P|p]rononciation\w*')   # recherche les modèles "Prononciaition(s)"
reTrad = re.compile('[T|t]raduction\w*')      # recherche les modèles "Traduction(s)"
reEq = re.compile('=')                        # recherche des parametres
l1 = re.compile('langue1')                    # re pour chercher le paramètre dans les modèles
l2 = re.compile('langue2')                    # re pour chercher le paramètre dans les modèles

### Liste de pages, via ufileList - stage1
list_tmp_pg = ufileList.split('>')   # divise pour filtrer le titre des page
list_page = []                       # Liste pour titre des pages
for l in list_tmp_pg:     # pour chaque chaine dans xml list_tmp_pg
  mo_title_page = re_title_page.search(l) # Cherche le titre
  if mo_title_page:               # Si MATCH OBJECT
    p=mo_title_page.group()       # 
    title_page = p[7:len(p)-1]    # tronque la chaine nom de page
    list_page.append(title_page)  # enregistre liste des pages
allFiles = len(list_page)         # Voir nbPages ; La fx writepack utilise allfiles pour ecrire le résumé

### Liste des pages pour Leçon et defaut - stage2
if className == 'Leçon':  # ATTENTION Si type page 'none' traite uniquement la page = chapitre
  list_page = shortlist(list_page, cible_unicode)   # Filtre les fichiers de la leçon
# Analyse modèles de chaque page, creation de listes distinctes pour chaque modèle, 
lPron = []   # Liste des modèles Prononcition
lTrad = []   # Liste des modèles Traduction
for title in list_page: # chaque pages
  #title = p
  page = pywikibot.Page(site, title)
  gen = page.templatesWithParams() # liste les modèles et contenu
  #linkIn = 'none'
  if gen:                            # si l'objet generator existe
    for template in gen:             # pour chaque item du generator
      template_name = template[0]    # Le nom de la pge du modele
      template_params = template[1] # liste des parametres
      template_name = str(template_name)
      moTrad = reTrad.search(template_name) # cherche trad dans liste des modeles
      if moTrad:
	lTrad.append(template)      # si trad enregistre dans LISTE TRAD
      moPron = rePron.search(template_name) # cherche prononciation dans liste des modèles
      if moPron:
	lPron.append(template)      # si pron enregistre dans LISTE PRON
nbPages = len(list_page)   # Nombre de pages à comparer avec allFiles
nbPron = len(lPron)        # Nombre de modèles prononciation
nbTrad = len(lTrad)        # Nombre de modèles traduction
part1_log =str(allFiles) + ' pages au total\n' + str(nbPages) + '  pages dans la liste\n' + str(nbPron) + '  modèle PRON, ' + str(nbTrad) + '  modèle TRAD\n'
log = log + part1_log
print '### Les Listes sont prêtes ###' # On obtient une liste pour chaque modele
### LISTES FIN

### TRAITEMENT LISTE PRONONCIATION
# crèer fxpron ; déclarer ou passer les var: reEq, lAudio à linterieur
# retourner une liste qui sera revèrsée dans lTrad
if nbPron > 0: 
  for template_object in lPron: # LPRON
    template_name = template_object[0]   # Nom du modele
    template_params = template_object[1] # Liste des parametres
    lrm = []  # liste des elements à supprimer
    count = 1 # initialise le compteur
    for param in template_params:  # pour chaque parametre
      # i = template_params.index(param)  # calcul l'index du parametre
      moEq = reEq.search(param)         # cherche symbol egual, param nommé
      if moEq: # Si le param est nommé
	pass    
      else:    # c'est une cellule
	if count % 3 == 0:   # si elle est multiple de trois
	  lAudio.append(param)   # copie dans la liste lAudio
	  lrm.append(param)      # copie dans liste à supprmer
      count = count + 1      # prochain param
    for rm in lrm:    #  chaque element
      template_params.remove(rm)   # est supprimé
    lTrad.append(template_object)  # copie les objets restants dans lTrad
# Ce modèle propose une quatrième colonne transcritpion
# quand cette 4èmme colonne existe, les données ne sont pas collectée cf log
###LPRON FIN Il faudrait detecter la quatrième colonne si existe

nbMod = len(lTrad) # Les modèles pron. versés dans lTrad, nbMod donne le nombre total de modele.
log = log + str(nbMod) + ' modèles à traiter\n'   #LogInfo

### TRAITEMENT LISTE TRADUCTION
if nbMod > 0:
  for template_object in lTrad: # LTRAD
    template_name = template_object[0]      # Nom du modèle
    template_params = template_object[1]    # Liste des paramètres
    named_params = [] # Liste pour les parametres nommés
    raw1 = rootLang   # initialise les langues
    raw2 = pageLang   # avec paramètres par défaut
    for param in template_params:  # PARAMETRES
    # ATTENTION API retourne lzh pour chinois mais wikversité utilise zh
      moEq = reEq.search(param)    # cherche symbole egal param nommés
      if moEq:     # Si symbol
        named_params.append(template_params.index(param)) # enregistre son index dans liste named_params
        mol2 = l2.search(param)    # Cherche langue2
        if mol2:   # SI langue2
	  spl2 = param.split('=')  # split sur symbol=
	  raw2 = spl2[1]           # enregistre dans raw2
	  raw2 = raw2.strip()      # retire éspaces inutiles
        mol1 = l1.search(param)    # Cherche langue1
        if mol1:   # SI langue1
          spl1 = param.split('=') # split egual
	  raw1 = spl1[1]      # stock valeur
	  raw1 = raw1.strip() # enleve espaces
    cdl = raw1+'-'+raw2     # variable cdl = langue1-langue2
    iMaxData = min(named_params)  # Calcul dernière donnée = premier paramètre nommé ???
    data = template_params[0:iMaxData]   # Calcul la zone de données
    nbCel = len(data)       # Pour vérifier parité du nombre de cellule
    tplParam = [cdl, iMaxData, nbCel]    # langue1-langue2, dernier index de donnée, nombre de cellules
    template_params.append(tplParam)     # Stoque les paramètres dans template_params
    if nbCel %2 <> 0:   # Si le nombre de cellule n'est pas paire verifier si dernière cellule vide
      error_nbCel_log = 'Template error:\nVérifier le nombre de cellules: '
      log = log + error_nbCel_log + str(nbCel)
      lastCel = template_params[iMaxData-1]
      print '######'
      print lastCel
      print '#######'
      reSpaces = re.compile('\s\n') # resoud le cas Anglais/Grammaire/Conjugaison/Impératif
      # Attention le problème reste relatif à la 4ème colonne de prononciation
      moSpaces = reSpaces.match(lastCel)
      if lastCel == '':
        print 'DERNIERE CELLULE VIDE A DETRUIRE'
        # resoud le cas de la dernière cellule vide sans espaces ni saut de ligne
        # il reste à supprimer l'element de la liste lb
      if moSpaces:
        print 'Celule vide à détruire'
        print moSpaces.group()
        #template_params.remove[lastCel]        
    if cdl == rootLang + '-' + pageLang and nbCel % 2 == 0:   # Si langues par defaut et nombre cellule paire
      for cellule in data:                # Pour chaque donnée dans dataZone
        if data.index(cellule) % 2 == 0:     # Si son index est paire
	  index_next = data.index(cellule)+1   # Calcul index prochaine valeur
	  next_cell = data[index_next]         # next_cell = prochaine valeur
	  globalDict[cellule] = next_cell      # Dictionnaire Global reçoit mot_PT : mot_FR
        else:          # Ce n'est pas une clé mais une valeur (deja traité)
	  pass
    elif cdl == pageLang + '-' + rootLang and nbCel % 2 == 0: # Si langues INVERSE fr-pt celulles paire
      for cellule in data:                # Pour chaque donnée dans dataZone
        if data.index(cellule) % 2 == 0:     # Si son index est paire
	  index_next = data.index(cellule) + 1   # Calcul index prochaine valeur
	  next_cell = data[index_next]           # next_cell = prochaine valeur
	  globalDict[next_cell] = cellule        # On inverse cellule et next_cell dans le dictionnaire
        else: # IMPAIR PASS
          pass
    else:
      error_codes_langues = 'Titres de colonnes: \n' + cdl
      log = log + error_codes_langues
      print cdl
      print template_name
      print data
      # chinois code langue sur 3 caractères tronque le l, lzh devient zh
total_line = len(globalDict)
log = log + str(total_line) + ' lignes au total dans dictionnaire global\n'
### LTRAD FIN

### Traitement des APOSTROPHES et des espaces inutiles
finalDict = {}
for key in globalDict:
  value = globalDict[key]
  key = aposoff(key)
  value = aposoff(value)
  key = key.strip()
  value = value.strip()
  finalDict[key] = value
###

#### Suppression des données contenant des modèles
tplInsideLog = ''
removeDict = tplinside(finalDict)
if len(removeDict) > 0:
  tplInsideLog = str(len(removeDict)) + ' lignes contenant des modèles ne seront pas prises en compte\n'
  for rmk in removeDict:  # pour chaque clé dans la liste à supprimer
    print rmk
    # rmv = removeDict[rmk] #?¿
    del finalDict[rmk]    # supprime la clé de finalDict
  #tplInsideLog = tplInsideLog  + str(rmv)#unicode(rmk, 'utf-8')# +  str(rmv) + '\n'
  # Japonais/Vocabulaire ne reussit pas à convertir rmk et rmv en string ni en unicode
  # Portugais indexGlobal plante aussi sur cette ligne
  log = log + tplInsideLog

nbLine = len(finalDict)   # Le nombre de ligne dans le dictionnaire apres nettoyage
wlp = divdict(finalDict)  # Division en 3 listes Word, Locution, Phrase
[tupWord, tupLocution, tupPhrase] = wlp # Le tuple contient les 3 listes
chkword(tupLocution, tupWord)   # Sépare les locutions dont le formatage permet le deplacement dans la liste des mots simples
### TRAITEMENT DES ARTICLES RECONNUS SELON LANGPACK
for lang in langPack:  
  pack = langPack[lang]
  if lang == rootLang:
    chkarticle(tupLocution, tupWord, pack)
  else:
    print ' Pas de langPack'
### JOURNALISE TAILLE DES LISTES
nb_words = len(tupWord)
nb_locutions = len(tupLocution)
nb_phrases = len(tupPhrase)
resume_log = str(nb_words) + ' mots, ' + str(nb_locutions) + ' locutions, ' + str(nb_phrases) + ' phrases.\n'
log = log + resume_log

secW = linkedlines(tupWord, rootLang)
secL = linesans(tupLocution)
secP = linesans(tupPhrase)

script_name = sys.argv[0]
writePack = [script_name, allFiles, nbMod, nbLine, cible_unicode, secW, secL, secP]
print '### Log: ###'
print log
if nbLine < 5:
  print 'Pas suffisament de données pour créer une page. Minimum 5 lignes.'
  print nbLine
else:
  txtin = writelist(writePack)
  comment = 'Indexation automatique du vocabulaire pour les langues étrangères. Youni Verciti Bot'
  if args.test: # MODE TEST SAVE IN LABORATOIRE
    new_page = 'Projet:Laboratoire/Propositions/Index_vocabulaire/vcb '+ lastName
    sommaire = u'Projet:Laboratoire/Propositions/Index_vocabulaire#Exemples'
    print new_page + 'La nouvelle page se trouve dans l\'espace de test du laboratoire.\nLe lien en bas de la page.'
  print 'Page à publier:       ' + new_page
  new_page = unicode(new_page, 'utf-8')  # UNICODE
  page = pywikibot.Page(site, new_page)
  page.text = txtin
  try:
    page.save(comment)
  except:
    print 'Pas sauvegardé, exception'
  else:
    print 'Feĺicitation vous avez enregistré une nouvelle page de vocabulaire'
    title = sommaire     # vérifier existance de dpt/Index vocabulaire
    page = pywikibot.Page(site, title)
    exist = page.exists()
    if exist:   # Test exist page du sommaire
      print 'Le sommaire existe:' + sommaire    # Hote du lien à créer: sommaire
      lastName_uni = unicode(lastName, 'utf-8') # UNICODE!
      link_generator = page.linkedPages(namespaces=0)   # L'objet PWB
      if link_generator:  # Si le sommaire contient des liens dans l'espace principal
	for linked in link_generator:    ### l'objet pagegenerator PWB contient des objets page.Page
	  #print linked.title()          ### la syntaxe PWB pour extaire le titre UNICODE
	  if linked.title() == new_page: # Le lien pour notre nouvelle page existe
	    print 'Le lien est déja en place dans le sommaire.\nLe programme se termine avec succès, actualiser la page <vcb>.'
	    exit()
      ## Sortie de boucle le lien n'y est pas le prog se POURSUIT
      print 'Création du lien vers la nouvelle page'      
      link_write  = '\n' + '* [[' + new_page + ' | Vocabulaire ' + lastName_uni + ']]\n' 
      title = sommaire
      page = pywikibot.Page(site, title) # PWB variable
      witext = page.get()
      page.text = witext + link_write # AJOUTE le lien
      comment = u'Ajout du lien au sommaire des fiches de vocabulaire'
      page.save(comment)      
      print sommaire
      print link_write
    else:   # PAS DE SOMMAIRE Creation du sommaire des sections et du lien
      print 'Création du sommaire des fiches vocabulaire!'
      link_write =  '\n[[' + new_page + ' | Vocabulaire ' + lastName_uni + ']]\n'
      title = sommaire
      page = pywikibot.Page(site, title)
      comment = u'Création du sommaire, avec le lien vers la nouvelle page de vocabulaire.'
      page.text = insert # EDITE LE TEXTE DE LA PAGE
      page.save(comment)
      
#time.sleep(15)
#wait = input('PRESS ENTER TO CONTINUE')


