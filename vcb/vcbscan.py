#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import urllib
import pywikibot

### SHORTLIST
def shortlist(mylist, arg1) :
  shortList = []    # Liste pour les pages à traiter
  subFolder = ['Annexe', 'Exercices', 'Fiche', 'Quiz', 'Travail_pratique'] # LES DOSSIERS DES LEÇONS
  prefix = arg1 + '/'       # declare prefix pour tronquer la première partie
  for page in mylist:   
    for sub in subFolder:
      argSub = arg1 + '/' + sub
      if re.match(argSub, page):   # si la ligne commence par argv1/sub
        shortList.append(page)       # place la page dans la liste
  for page in mylist:
    if re.match(prefix, page):   # on gardera la page racine
      moPlace = re.match(prefix, page)   
      iMoPlace =  moPlace.end()  #index de la fin du prefix
      page = page[iMoPlace : ]    #tronque le prefix
      if '/' in page:   # Si il reste une barre oblique : sous dossier, on ne traitera pas
        pass             # on ne traite pas les sous dossiers
      else:
        shortList.append(arg1 + '/' + page)   # On place la page dans PAGESHORTLIST
  return shortList 

### PATHNAME sépare l'argument initial en élements du path
def pathname(name, srv):
  rqParseWkt = '?action=parse&format=xml&page=%s&prop=wikitext&contentdataZone=wikitext' % name   # REQUETE PARSE Format XML content WIKITEXT
  objf = urllib.urlopen(srv + rqParseWkt)   # Ouvre l'url dans l'objet
  varf = objf.read()              # Lit le contenu dans la variable.
  objf.close()                    # ferme l'objet url
  strfile = str(varf)
  ufile = unicode(varf, 'utf-8')
  reLesson = re.compile('{{[L|l]eçon')   # ATTENTION probleme ecodage unicode sur le ç de leçon
  reChapitre = re.compile('{{[C|c]hapitre')
  splName = name.split('/')
  nbName = len(splName)   ### -2 (rootname et lastname ex: rootname/nSec1/nSec2/lastname)
  rootName = splName[0]
  lastName = splName[nbName -1]
  lSec = []
  for sname in splName[1:splName.index(lastName)]:
    lSec.append(sname)
  lPath = [name, rootName, lastName, nbName, lSec]
  uSec=''
  for sec in lSec:
    uSec = uSec + u'/' + sec
  moLesson = reLesson.search(strfile)
  moChapitre = reChapitre.search(ufile)
  if nbName == 1:
    print ' La cible est un département'
    className = 'Département'
    titleS = rootName + '/Index vocabulaire/vcb Global'
    linkTo = rootName + '/Leçons par thèmes'
    link = '[['+ titleS + '| Index du vocabulaire]]'
    retplk = ''
    reLink = re.compile(titleS)
    defaultKey = ''
  elif moLesson:
    className = 'Leçon'    
    titleS = rootName + '/Index vocabulaire/vcb ' + lastName
    linkTo = rootName + '/Index vocabulaire/Inventaire des fiches'
    link = '{{F|vcb'+lastName   # chercher la ligne commençant par {{F|¿?
    retplk = re.compile('[F|f]iche\s*=')
    reLink = re.compile(link)
    defaultKey = 'fiche = '  
    moLink = reLink.search(strfile)
    if moLink:
      print 'Le lien existe: '
      print moLink.group()
    else : 
      motplk = retplk.search(strfile)
      if motplk:
	print 'Attention la leçon contient une fiche: \n'
	print motplk.group()
	print 'Placer le lien dans la leçon manuellement'
      else:
	print 'On peut envisager de créer le lien dans le modèle leçon'
	
  elif moChapitre:
    print moChapitre.group()
    print 'La cible est un chapitre'
    className = 'Chapitre'    
    titleS = rootName + '/Index vocabulaire/vcb '+ lastName
    linkTo = rootName + '/Index vocabulaire/Inventaire des fiches'
    link = '[[' + rootName + '/Index vocabulaire/vcb '+ lastName
    retplk = re.compile('page_liée\s*=')
    reLink = re.compile(titleS)
    defaultKey = 'page_liée = '
    moLink = reLink.search(strfile)
    motplk = retplk.search(strfile)
    if moLink:
      print 'Le lien est en place'
      print moLink.group()
    else:
      if motplk:
	print 'Attention une page liée: '
	print motplk.group()
	print 'Etablir le lien manuellement'
      else:
	print 'On peut écrire le lien: '
	print defaultKey + link 
	print 'Le modèle Chapitre est infernal et le paramètre page_liée un cauchemard.'
	print 'cibler la page rootName/Index vocabulaire/Inventaire des fiches'
  else:
    print 'Le type de cible est indéfini, none'
    className = 'none'
    titleS = rootName + '/Index vocabulaire/vcb ' + lastName
    linkTo = rootName + '/Index vocabulaire/Fiches vocabulaire'
    print lSec
    for sec in lSec:
      print sec
    link = titleS
    reLink = re.compile(link)
    retplk=''
    defaultKey=''
  linker = [className, titleS, linkTo, link, reLink, retplk, defaultKey]
  lPath.append(linker)
  #print cible
  return lPath
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

### FXPRON Scan les modèles Prononciation
## Améliorer en testant la présence de la colonne 4

  