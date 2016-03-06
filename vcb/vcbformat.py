#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import urllib
import pywikibot
import datetime

### USTR transforme en string puis unicode 
def ustr(myvar):   ### Verifier si necessaire?¿
  mystr = str(myvar)
  myu = unicode(mystr, 'utf-8')
  return myu

### DEF APOSOFF
def aposoff(instr):   # Apostrophe_Off(Inside_String) enleve les '' et ''' de la chaine
  reAps = re.compile('\'{2,3}')           # RegEx pour les groupes de 2 ou 3 apostrophes
  nbApo = len(re.findall(reAps, instr))   # nombre d'item
  if nbApo > 0:   # SI apostrophes dans mystr
    filAps = re.finditer(reAps, instr)    # Find Iter List les occurences  regex '' et '''
    iDeb = 0      # debut de la recherche
    cleaned = ''  # initialise la chaîne pour recevoir la clé sans apostrophe de formatage
    n=1           # initialise le compteur de boucle
    for l in filAps:   # POUR CHAQUE mo in fil (VOIR SI ON FAIT MIEUX AVEC WHILE)
      if n < nbApo:       # TANT QUE ce n'est pas le dernier
	clean = instr[iDeb:l.start()]   # Calcul le debut sans aps
        cleaned = cleaned + clean       # Ajoute la section debut sans aps à la mystr cleaned
        iDeb = l.end()                  # Position de départ pour le prochain tour de boucle = après le dernier aps
        n=n+1                           # Compteur de tours
      else:               # On arrive au dernier aps
        clean = instr[iDeb:l.start()]   # calcul le debut sans aps
        fin = instr[l.end():]           # calcul la fin sans aps
        cleaned = cleaned + clean + fin # ajoute le début et la fin à la mystr cleaned
        cleaned = cleaned.strip()       # Enleve espace inutile
    instr = cleaned
  else:          # SANS aposoff
    cleaned = instr.strip()   # cleaned est identique à instr
  return cleaned   # Renvoi la version sans apostrophe de instr
### APOSOFF FIN

### DIVDICT Divise le dictionnaire global en 3 
def divdict(myDict):
  tupWord = {} # stockage des mots simples
  tupLocution = {} # stockage des clés de plus de 2 mots
  tupPhrase = {}   # traitement des clés de plus de 5 mot
  wlp = [tupWord, tupLocution, tupPhrase]
  # En premier detecter phrases selon premìere majuscule et dernier point
  # Enlever le couple de tupLesson pour le copier dans tupPhrase
  reMaj = re.compile('[A-Z]')   # Une majuscule alnum
  rePoint = re.compile('\.\Z')    # Un point à la fin de la chaîne
  kToDelete = []           # Liste pour stocker les clé à supprimer de tupLocution
  if len(myDict) > 0:
    for k in myDict:   # Pour chauqe cle dans tupLocution
      moMaj = re.match(reMaj, k)   # Commence par une majuscule alphanumerique
      moPoint = re.search(rePoint, k)  # Termine par un point (ajouter exclamation et interrogation)
    if moMaj and moPoint:   # Si Majuscule début et point final
      tupPhrase[k] = myDict[k]    # copie le couple dans tupPhrase
      kToDelete.append(k)   # Stock k dans liste à supprimer
    for k in kToDelete:
      del myDict[k]    # enlève les phrases courtes du tupLocution
    for k in myDict: # Pour chaque clé
      v = myDict[k]  # definition de sa valeur
      kSplit = k.split()   # découpe la clé en nombre de mots
      kSize = len(kSplit)  # calcul le nombre de mot dans la clé
      if kSize > 5:   # Si plus de 5 mots dans la clé
        tupPhrase[k] = v   # Copie dans tupPhrase
      else:   #SINON
        if kSize > 1: # SI plus que 1 mot dans la clé
          tupLocution[k] = v   # On copie dans tupLocution
        else: # SINON
          tupWord[k] = v   # On copie dans tupWord
    wlp = [tupWord, tupLocution, tupPhrase]
  return wlp
### DIVDICT FIN

### CHECK WORDS
# Certaines occurrences de tupLocution seront re-affectées à tupWord
# Tester si ksize = 2 et virgule ou articles. Si oui affecter à tupWrd
def chkword(locution, word):
  kToDelete = []   # Liste de clés à detruire après déplacement
  for k in locution:    # Chaque clé de tupLocution
    kSplit = k.split()     # Listes les mots
    kSize = len(kSplit)    # Calcul le nbre de mots
    if kSize ==2:      # Si DEUX mots
      if ',' in k:       # Et une virgule
        word[k] = locution[k] # Déplace dans tWord
        kToDelete.append(k)         # Enregistre la clé à detruire
      
  for k in kToDelete:    # Pour chaque clé à supprimer
    del locution[k]      # Enlève les couples article/mots du tupLocution
### Gérer les couples qui commencent par un mot entre parentèses (os)
### Gérer les occurences dont chaque mot est séparé par virgules
### Observer les listes des autres dept
### Tester si article+1mot+virgule


### linesans formate les lignes sans liens (locutions & phrases)
def linesans(locuPhrase):
  sectionSans = ''
  if len(locuPhrase ) > 0:
    for k in sorted(locuPhrase):
      v = locuPhrase[k]
      lineSans = '* ' + k + ' : '+ v + '<br>\n'
      sectionSans = sectionSans + lineSans
  return sectionSans
### Lignes sans Fin

### LINKEDLINES formate les lignes avec liens (mots simples)
def linkedlines(simplewords, rootLang):
  sectionWords = ''
  if len(simplewords) > 0:
    for k in sorted(simplewords):
      v = simplewords[k]
      kSplit = k.split()
      kSize = len(kSplit)
      if kSize ==2: # Deux mots dans la clé, l'article est en seconde position
	if ',' in k:
	  kCut = k.split(',')   # on split sur la virgule et on créé les liens avec premier element du split
	  line = '* [[wikt:' + rootLang +':'+ kCut[0] + '|' + k + ']] : [[wikt:' + kCut[0] + '#'+ rootLang + '|' + v + ']]<br>\n'
	  sectionWords = sectionWords +line
	else: # Deux mots sans virgule
	  line = u'* [[wikt:' + rootLang +u':'+ kSplit[0] + u'|' + k + u']] : [[wikt:' + kSplit[0] + u'#' + rootLang + u'|' + v + u']]<br>\n'
	  sectionWords = sectionWords +line
      else: # Un seul mot dans la clé création des liens wikt
	line = u'* [[wikt:'+ rootLang + u':' + k + u'|' + k + u']] : [[wikt:' + k + u'#' + rootLang + u'|' + v + u']]<br>\n'
	sectionWords = sectionWords +line
  return sectionWords
###LINKEDLINES FIN

### ECRITURE DE LA LISTE A PUBLIER
def writelist(dataPack):
  [scriptName, allFiles, nbMod, nbLine, cible_unicode, secW, secL, secP] = dataPack
  now = datetime.date.today()   # PASSER AU FORMAT FRANÇAIS
  tnow = str(now)               # pour écrire la date 
  head1 = u'{{Entête de fiche}}<small> Liste auto. script: ' + scriptName + ' - Date: ' + tnow + ' - ' + ustr(allFiles) + ' pages - '
  head2 = str(nbMod) + ' modèles - ' + str(nbLine) + ' lignes.</small><br>'
  head2 = unicode(head2, 'utf-8')
  #head2 = unicode(str(nbMod), 'utf-8') + ' modèles - ' + ustr(nbLine) + ' lignes.</small><br>'
  backLink = 'Retour: [[' + cible_unicode + ']]\n' # Lien pour retourner à la leçon
  txtin = head1 + head2 + backLink
  if secW <> '':
    section1 = '== Mots ==\n<div style="-moz-column-count:2; column-count:2;">\n'
    txtin = txtin + section1 + secW
  if secL <> '':
    section2 = '</div>\n== Locutions ==\n'
    txtin = txtin + section2 + secL
  if secP <> '':
    section3 = '== Phrases ==\n'
    txtin = txtin + section3 + secP
  txtin = txtin + unicode('[[Catégorie:Page auto]]', 'utf-8')
  #txtin = headDraft+suite+backLnk + section1 + secW + section2 + secL + section3 + secP
  return txtin 