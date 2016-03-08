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
site = pywikibot.Site('fr', u'wikiversity')     ### Variables PWB The site we want to run our bot on

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
[path, rootName, lastName, nbName, list_sections, linker] = lPath # dont ceci est la composition
[className, new_page, sommaire] = linker # avec la composition de linker
print className # Affiche  le type de page
###PYWIKIBOT
title = cible_unicode   # Titre reçoit l'argument au format UNICODE
page = pywikibot.Page(site, title) # PWB variable

rqRootLang = '?action=languagesearch&format=xml&search=%s' % rootName
fromPage = args.cible
toPage = args.cible + 'a'
rqAllPages = '?action=query&list=allpages&format=xml&apfrom='+fromPage+'&apto='+toPage+'&aplimit=275' # ATTENTION max 275 pages
rqParseWkt = '?action=parse&format=xml&page=%s&prop=wikitext&contentdataZone=wikitext' % args.cible   # REQUETE PARSE Format XML content WIKITEXT

### RECHERCHE PAGELANG
sts =  str(site)
i=sts.find(':')
sts = sts[i+1:]
pageLang = sts
### RECHERCHE ROOTLANG
askRootLang = srv + rqRootLang
objr = urllib.urlopen(askRootLang)
varf = objr.read()
xml_lang = str(varf)
reRootLang = re.compile('languagesearch \w*=') # The API changed
moRootLang = reRootLang.search(xml_lang)
rootLang = moRootLang.group()
rootLang = rootLang[ 15 : len(rootLang)-1 ]
print rootLang  + '-' + pageLang 
###
strLog = ''     # Variable pour le journal
lAudio = []     # Liste pour la 3ème colonne de modèle Prononciation
globalDict = {} # Dictionnaire global 
###

### TRAITEMENT DE LA LISTE DEs PAGES
# requete fromPage toPage via urllib et APIsrv
fileList = urllib.urlopen(srv + rqAllPages) ### ATTENTION Si Dept, Leçon, Chap: liste des fichiers à traiter
vfileList = fileList.read()
ufileList = unicode(vfileList, 'utf-8')       # UNICODE XML liste des pages ciblées
rePg=re.compile('title=".*"')                 # recherche du nom de page
rePron = re.compile('[P|p]rononciation\w*')   # recherche le modèle
reTrad = re.compile('[T|t]raduction\w*')      # ''
reEq = re.compile('=')                        # recherche des parametres
l1 = re.compile('langue1')                    # First raw (filtre param Langue1)
l2 = re.compile('langue2')                    # Second raw ('' langue2)

### Liste de pages, via ufileList - stage1
list_tmp_pg = ufileList.split('>')   # divise pour filtre nom page
list_page = []                       # liste pour pages
for l in list_tmp_pg:     # pour chaque chaine dans xml list_tmp_pg
  moPg = rePg.search(l)   # Cherche le titre
  if moPg:                # 
    p=moPg.group()        # 
    cp = p[7:len(p)-1]    # tronque la chaine nom de page
    list_page.append(cp)      # enregistre liste des pages
allFiles = len(list_page)     # Voir nbPages ATTENTION cf fx writepack li273

### Liste des pages pour Leçon et defaut via fx(patname) - stage2
if className == 'Leçon':  # ATTENTION Si type page 'none' traite uniquement la page = chapitre
  list_page = shortlist(list_page, cible_unicode)   # Filtre les fichiers de la leçon ATTENTION cible_unicode et l'enfer unicode
# Analyse modèles de chaque page, creation de listes distinctes pour chaque modèle, 
lPron = []   # Liste des modèles Prononcition
lTrad = []   # Liste des modèles Traduction
for p in list_page: # chaque pages
  title = p
  page = pywikibot.Page(site, p)
  gen = page.templatesWithParams() # liste les modèles et contenu
  linkIn = 'none'
  if gen:# si  modeles
    for g in gen: #pour chaque item du generator
      a = g[0] # a le nom de la pge du modele
      b = g[1] # b a liste des params
      stra = str(a)
      moTrad = reTrad.search(stra) # cherche trad dans liste des modele
      if moTrad:
	lTrad.append(g) # si trad enregistre dans LISTE TRAD
      moPron = rePron.search(stra)
      if moPron:
	lPron.append(g) # si pron enregistre dans LISTE PRON
nbPages = len(list_page)
nbPron = len(lPron)
nbTrad = len(lTrad)
part1Log = str(nbPages) + '  pages\n' + str(nbPron) + '  modèle PRON, ' + str(nbTrad) + '  modèle TRAD\n'
strLog = strLog + part1Log
print strLog
print '### Les Listes sont prêtes ###' # On a une liste pour chaque modele
### LISTES FIN

### TRAITEMENT LISTE PRONONCIATION
if nbPron > 0: 
  # crèer fxpron ; déclarer ou passer les var: reEq, lAudio à linterieur
  # retourner une liste qui sera revèrsée dans lTrad
  for l in lPron: # LPRON
    # Ce modèle propose une qutrimr colonne transcritpion
    # quand cette 4èmme colonne existe
    # les données ne sont pas collectée cf strLog
    a = l[0] # Nom du modele
    lb = l[1] # Liste des parametres
    lrm = []  # liste des elements à supprimer
    count = 1 # initialise le compteur
    for b in lb:  # pour chaque parametre
      i = lb.index(b)  # calcul l'index du parametre
      moEq = reEq.search(b)   # cherche symbol egual, param nommé
      if moEq: # Si le param est nommé
	pass    
      else:  # c'est une cellule
	if count % 3 == 0:   # si elle est multiple de trois
	  lAudio.append(b)   # copie dans la liste lAudio
	  lrm.append(b)      # copie dans liste à supprmer
      count =count + 1     # prochain param
    for rm in lrm:    #  chaque element
      lb.remove(rm)   # est supprimé
    lTrad.append(l)   # copie les param restants dans lTrad
###LPRON FIN Il faudrait detecter la quatrième colonne si existe

nbMod = len(lTrad) # Les modèles pron. versés dans lTrad, lTrad donne le nombre de modele.
strLog = strLog + str(nbMod) + ' modèles à traiter\n'   #LogInfo

if nbMod > 0:   ### TRAITEMENT LISTE TRADUCTION
  for l in lTrad: # LTRAD
    a = l[0]      # le nom du modèle
    lb = l[1]     # la liste des paramètres
    lParam = []   # Nouvelle liste pour les parametres nommés
    raw1 = rootLang   # initialise les langues
    raw2 = pageLang   # avec paramètres par défaut
    for b in lb:    # PARAMETRES
    # print b ATTENTION API retourne lzh pour chinois mais wikversité utilise zh
      moEq = reEq.search(b)   # cherche symbole egal param nommés
      if moEq:     # Si symbol
        lParam.append(lb.index(b)) # enregistre son index dans liste lParam
        mol2 = l2.search(b)        # Cherche langue2
        if mol2:   # SI langue2
	  spl2 = b.split('=')  # split sur symbol=
	  raw2 = spl2[1]       # enregistre dans raw2
	  raw2 = raw2.strip()  # retire éspaces inutiles
        mol1 = l1.search(b) # Cherche langue1
        if mol1:   # SI langue1
          spl1 = b.split('=') # split egual
	  raw1 = spl1[1]      # stock valeur
	  raw1 = raw1.strip() # enleve espaces
    cdl = raw1+'-'+raw2     # variable cdl = langue1-langue2
    iMaxData = min(lParam)  # Calcul dernière donnée = premier paramètre nommé ???
    data = lb[0:iMaxData]   # Calcul la zone de données
    nbCel = len(data)       # Pour vérifier parité du nombre de cellule
    tplParam = [cdl, iMaxData, nbCel]   # langue1-langue2, dernier index de donnée, nombre de cellules
    lb.append(tplParam)     # Stoque les paramètres dans lb
    if nbCel %2 <> 0:   # Si le nombre de cellule n'est pas paire
      lastCel = lb[iMaxData-1]
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
        #lb.remove[lastCel]        
    if cdl == rootLang + '-' + pageLang and nbCel % 2 == 0:   # Si langues par defaut et nombre cellule paire
      for d in data:   # Pour chaque donnée dans dataZone
        if data.index(d) % 2 == 0: # Si son index est paire
	  iTmp = data.index(d)+1   # Calcul index prochaine valeur
	  tmp = data[iTmp]         # tmp = prochaine valeur
	  globalDict[d] = tmp      # Dictionnaire Global reçoit mot_PT : mot_FR
        else:          # Ce n'est pas une clé mais une valeur (deja traité)
	  pass
    elif cdl == pageLang + '-' + rootLang and nbCel % 2 == 0: # Si langues INVERSE fr-pt celulles paire
      for d in data:   # Pour chaque donnée dans dataZone
        if data.index(d) % 2 == 0:   # Si son index est paire
	  iTmp = data.index(d) + 1   # Calcul index prochaine valeur
	  tmp = data[iTmp]           # tmp = prochaine valeur
	  globalDict[tmp] = d        # On inverse d et tmp dans le dictionnaire
        else: # IMPAIR PASS
          pass
    else:
      errorLog = 'Template error:\nVérifier le nombre de cellules: '
      print errorLog
      print nbCel
      # si nbCel impair alors verifier si dernière cellule vide
      error2 = 'Titres de colonnes: \n'
      print cdl
      print page #Affiche page erronée
      print a
      print data
      # chinois code langue sur 3 caractères tronque le l, lzh devient zh
      #tplErrorLog = unicode(str(page), 'utf-8') +'\n'+ unicode(str(lb), 'utf-8') +'\n'
      #print  tplErrorLog
      #strLog = strLog + errorLog + tplErrorLog
ligd = len(globalDict)
strLog = strLog + str(ligd) + ' lignes dans dictionnaire global\n'
### LTRAD FIN

### Traitement des APOSTROPHES et des espaces inutiles
finalDict = {}
for t in globalDict:
  v = globalDict[t]
  t = aposoff(t)
  v = aposoff(v)
  t = t.strip()
  v = v.strip()
  finalDict[t] = v
###

#### Suppression des données contenant des modèles
tplInsideLog = ''
removeDict = tplinside(finalDict)
if len(removeDict) > 0:
  tplInsideLog = 'Les entrées contenant des modèles ne seront pas prise en compte\n'
  for rmk in removeDict:  # pour chaque clé dans la liste à supprimer
    rmv = removeDict[rmk] #?¿
    del finalDict[rmk]    # supprime la clé de finalDict
  #tplInsideLog = tplInsideLog  + str(rmv)#unicode(rmk, 'utf-8')# +  str(rmv) + '\n'
  # Japonais/Vocabulaire ne reussit pas à convertir rmk et rmv en string ni en unicode
  # Portugais indexGlobal plante aussi sur cette ligne
  strLog = strLog + tplInsideLog

nbLine = len(finalDict)   # Le nombre de ligne dans le dictionnaire
wlp = divdict(finalDict)  # Division en 3 listes
[tupWord, tupLocution, tupPhrase] = wlp
chkword(tupLocution, tupWord)   # Sépare les locutions dont le formatage suppose apartenir à la liste des mots simples
### TRAITEMENT DES ARTICLES RECONNUS SELON LANGPACK
for lang in langPack:  
  pack = langPack[lang]
  if lang == rootLang:
    chkarticle(tupLocution, tupWord, pack)
  else:
    print ' Pas de langPack'
### JOURNALISE TAILLE DES LISTES
words = len(tupWord)
locutions = len(tupLocution)
phrases = len(tupPhrase)
format1Log = str(words) + ' mots, ' + str(locutions) + ' locutions, ' + str(phrases) + ' phrases.\n'
strLog = strLog + format1Log

secW = linkedlines(tupWord, rootLang)
secL = linesans(tupLocution)
secP = linesans(tupPhrase)

scriptName = sys.argv[0]
writePack = [scriptName, allFiles, nbMod, nbLine, cible_unicode, secW, secL, secP]
print '### Log: ###'
print strLog
if nbLine < 5:
  print 'Pas suffisament de données pour créer une page. Minimum 5 lignes.'
  print nbLine
else:
  txtin = writelist(writePack)
  comment = 'Indexation automatique du vocabulaire pour les langues étrangères. Youni Verciti Bot'
  if args.test: # ATTENTION
    new_page = 'Projet:Laboratoire/Propositions/Index_vocabulaire/vcb '+ lastName
    sommaire = u'Projet:Laboratoire/Propositions/Index_vocabulaire'
    
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
    if exist:   # Test existance de la page du sommaire
      print ' Le sommaire existe:' + sommaire  # Hote du lien à créer: sommaire
      ### BUG si la page existe mais ne contient aucun lien le programme se termine
      ### en théorie la situation ne peut se produire que  par modif manuelle
      ### AJOUTER UNE CONDITION si genLN vide
       
      genLN = page.linkedPages(namespaces=0)
      for linked in genLN:   ### l'objet pagegenerator PWB
	# print type(linked)  ### contient des objets page.Page
	print linked.title()   ### la syntaxe PWB pour extaire le titre UNICODE
	if linked.title() == new_page:  # le lien existe
	  #create_link = False   # le boléen devient faut
	  print 'le lien est déja en place dans le sommaire\n Le programme se termine avec succès, actualiser la page <vcb>'
	  exit   # Le programme se TERMINE
      ## Sortie de boucle
      print 'Création du lien vers la nouvelle page'
      response = insert(list_sections, new_page, sommaire)  # ATTENTION, lastName
      # Modifier la fonction insert pour prendre en compte lastNAme comme titre
      # si list_section vide utiliser lastName attention si lastname vide ecrire au debut
      [title, insert] = response
      page = pywikibot.Page(site, title) # PWB variable
      witext = page.get()
      page.text = witext + insert # AJOUTE LA CHAINE DANS LA SECTION cf URL
      comment = u'Ajout du lien au sommaire des fiches de vocabulaire'
      page.save(comment)      
    else:   # PAS DE SOMMAIRE Creation du sommaire des sections et du lien
      print 'Création du sommaire des fiches vocabulaire!'
      ### Copie de la deuxime partie de la fonction insert (scinder fx insert)
      for section in list_sections:
	nbre_eq = list_sections.index(section) + 2
	fix = ''   # il reste à écrire les sections suivantes
	count = 1
	while count <= nbre_eq:  ### ajouter automatiquement 1 caractère égal en fonction de liste.index
	  fix = fix + '='
	  count = count + 1
	insert = insert + '\n' + fix + ' ' + section + ' ' + fix # Debut concaténation des sections
      # en sortant de la boucle on ajoute le lien
      insert = insert + '\n' + page_to_link
      title = sommaire
      page = pywikibot.Page(site, title)
      comment = u'Création du sommaire, avec le lien vers la nouvelle page de vocabulaire.'
      page.text = insert # EDITE LE TEXTE DE LA PAGE
      page.save(comment)
      
#time.sleep(15)
#wait = input('PRESS ENTER TO CONTINUE')