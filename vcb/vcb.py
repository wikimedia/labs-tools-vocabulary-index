#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import re
import sys
import pywikibot # PWB now
import argparse
from vcbscan import *
from vcbformat import *
from international import *

#import codecs
#import time

srv="https://fr.wikiversity.org/w/api.php"  # Adresse du serveur API
language = u"fr"                            # utilisé aussi pour determiner site_lang
family = u"wikiversity"
site = pywikibot.Site(language, family)     # Variable PWB

### ARGPARSE
parser = argparse.ArgumentParser()
parser.add_argument("cible", type=str, # ATTENTION UNICODE impossible de traduire les accents entrés
                    help="Indiquez le titre de la leçon du département de langues étrangère dont vous souhaitez collecter le vocabulaire. Par défaut la liste obtenue sera sauvegardée dans le département à l'adresse suivante Département/Index vocabulaire/vcb NomLeçon")
parser.add_argument("-t", "--test", help="Enregistre la liste dans l'espace de test du laboratoire. Projet:Laboratoire/Propositions/Index_vocabulaire",
                    action="store_true")
args = parser.parse_args()

### VARIABLES ###
cible_unicode = unicode(args.cible, 'utf-8') # Encodage UNICODE pour PWB 
log = ''        # Variable pour le journal
### PYWIKIBOT 
title = cible_unicode   # Titre reçoit l'argument au format UNICODE
page = pywikibot.Page(site, title) # PWB variable

### EXEC PATHNAME (full PWB)
lPath = pathname(cible_unicode) #, srv)       # pathname avec l'argument et le serveur forme la variable lPath
[path, list_path_elemt, root_name, last_name, nb_path_elemt, list_sections, linker] = lPath # dont ceci est la composition
[class_doc, new_page, sommaire] = linker # avec la composition de linker

#### LANGUAGE SOURCE via PWB
site_lang = language
print 'Le script s\'execute dans l\'espace: ' + str(language) + '\nLangue source: ' + str(site_lang)

### RECHERCHE ROOTLANG via urrlib
rqRootLang = '?action=languagesearch&format=xml&search=%s' % root_name
rqParseWkt = '?action=parse&format=xml&page=%s&prop=wikitext&contentdataZone=wikitext' % args.cible   # REQUETE PARSE Format XML content WIKITEXT
askRootLang = srv + rqRootLang
objr = urllib.urlopen(askRootLang)
varf = objr.read()
xml_lang = str(varf)
reRootLang = re.compile('languagesearch \w*=') # The API changed
moRootLang = reRootLang.search(xml_lang)
if moRootLang:
  lang_dest = moRootLang.group()
  lang_dest = lang_dest[ 15 : len(lang_dest)-1 ]
  print 'Département: ' + str(root_name) + ' codes: ' + str(lang_dest)  + '-' + str(site_lang)
else:
  print 'Impossible de déterminer la langue étudiée pour: ' + str(root_name)
  exit()

### CREATION DE LA LISTE DES PAGES A SCANNER
liste_cible = cibles(cible_unicode, class_doc)   # La fonction retourne la liste de pages à scanner
nb_page_cible = len(liste_cible)  # Voir nbPages ; La fx writepack utilise allfiles

# ANALYSE CHAQUE PAGE, CHERCHE MODÈLES CREATION DE LISTES DISTINCTES POUR CHAQUE MODÈLE
templates = scantemplate(liste_cible)
[lPron, lTrad] = templates
nb_tpl_pron = len(lPron)        # Nombre de modèles prononciation
nb_tpl_trad = len(lTrad)        # Nombre de modèles traduction

part1_log =str(nb_page_cible) + ' pages au total\n' + str(nb_page_cible) + '  pages dans la liste\n' + str(nb_tpl_pron) + '  modèle PRON, ' + str(nb_tpl_trad) + '  modèle TRAD\n'
log = log + part1_log
print '### Les Listes sont prêtes ###' # On obtient une liste pour chaque modele

if nb_tpl_pron > 0:
  [lTrad, lAudio] = scanpron(lPron, lTrad) # TRAITEMENT LISTE DES MODÈLES PRONONCIATION

nb_templates = len(lTrad) # Les modèles pron. versés dans lTrad, nb_templates donne le nombre total de modele.
log = log + str(nb_templates) + ' modèles à traiter\n'   #LogInfo

globalDict = {} # necessaire (phonétique)
if nb_templates > 0:
  globalDict = scantrad(lTrad, lang_dest, site_lang)   # TRAITEMENT LISTE DE MODÈLES TRADUCTION
total_line = len(globalDict)

log = log + str(total_line) + ' lignes au total dans dictionnaire global\n'

### Traitement des APOSTROPHES et des espaces inutiles
finalDict = {}
for key in globalDict:
  value = globalDict[key]
  key = aposoff(key)
  value = aposoff(value)
  key = key.strip()
  value = value.strip()
  finalDict[key] = value

#### Suppression des données contenant des modèles
tplInsideLog = ''
removeDict = tplinside(finalDict)
if len(removeDict) > 0:
  tplInsideLog = str(len(removeDict)) + ' lignes contenant des modèles ne seront pas prises en compte\n'
  for rmk in removeDict:  # pour chaque clé dans la liste à supprimer
    print rmk
    # rmv = removeDict[rmk] #?¿
    del finalDict[rmk]    # supprime la clé de finalDict
  # tplInsideLog = tplInsideLog  + str(rmv)#unicode(rmk, 'utf-8')# +  str(rmv) + '\n'
  # Japonais/Vocabulaire ne reussit pas à convertir rmk et rmv en string ni en unicode
  # Portugais indexGlobal plante aussi sur cette ligne
  log = log + tplInsideLog

nb_lines = len(finalDict)   # Le nombre de ligne dans le dictionnaire apres nettoyage

wlp = divdict(finalDict)    # Division en 3 listes Word, Locution, Phrase
[tupWord, tupLocution, tupPhrase] = wlp # Le tuple contient les 3 listes

# Sépare les locutions dont le formatage permet le deplacement dans la liste des mots simples
chkword(tupLocution, tupWord)

### TRAITEMENT DES ARTICLES RECONNUS SELON LANGPACK
for lang in lang_pack:  
  pack = lang_pack[lang]
  if lang == lang_dest:
    chkarticle(tupLocution, tupWord, pack)
  else:
    print ' Pas de lang_pack'

### JOURNALISE TAILLE DES LISTES
nb_words = len(tupWord)
nb_locutions = len(tupLocution)
nb_phrases = len(tupPhrase)
resume_log = str(nb_words) + ' mots, ' + str(nb_locutions) + ' locutions, ' + str(nb_phrases) + ' phrases.\n'
log = log + resume_log
print '### Log: ###'
print log

words_formated = linkedlines(tupWord, lang_dest) # Formate la liste des mots simples
locutions_formated = linesans(tupLocution)       # Formate la liste des locutions
phrases_formated = linesans(tupPhrase)           # Formate la liste des phrases

script_name = sys.argv[0]
write_pack = [script_name, nb_page_cible, nb_templates, nb_lines, cible_unicode, words_formated, locutions_formated, phrases_formated, root_name, last_name]

if nb_lines < 5:
  print 'Pas suffisament de données pour créer une page. Minimum 5 lignes.'
  print nb_lines
else:
  txtin = writelist(write_pack)
  comment = 'Indexation automatique du vocabulaire pour les langues étrangères. Youni Verciti Bot'
  if args.test: # MODE TEST SAVE IN LABORATOIRE
    new_page = 'Projet:Laboratoire/Propositions/Index_vocabulaire/vcb '+ root_name + ' ' + last_name
    sommaire = u'Projet:Laboratoire/Propositions/Index_vocabulaire#Exemples'
    print new_page + 'La nouvelle page se trouve dans l\'espace de test du laboratoire.\nLe lien en bas de la page.'
  #print 'Page à publier:       ' + str(new_page) #ATTENTION
  #new_page = unicode(new_page, 'utf-8')  # UNICODE (nettoyer)
  page = pywikibot.Page(site, new_page)
  page.text = txtin
  try:
    page.save(comment)
  except:
    print 'Pas sauvegardé, exception'
  else:
    print 'Feĺicitation vous avez enregistré une nouvelle page de vocabulaire'
    title = sommaire                            
    page = pywikibot.Page(site, title)
    exist = page.exists()                       # vérifie existance du sommaire dpt/Index vocabulaire
    if exist:                                   # La page du sommaire
      print 'Le sommaire existe:' + sommaire    # Hote du lien à créer: sommaire
      link_generator = page.linkedPages(namespaces=0)   # L'objet PWB
      if link_generator:  # Si le sommaire contient des liens dans l'espace principal
	for linked in link_generator:    # l'objet pagegenerator PWB contient des objets page.Page
	  print linked.title()           # la syntaxe PWB pour extaire le titre UNICODE
	  if linked.title() == new_page: # Le lien pour notre nouvelle page existe
	    # ATTENTION vcb.py "Portugais/Grammaire/Article/Articles définis"
	    # Il faut encadrer l'argument avec des " guillemets, sinon
	    # le programme ne voit pas que le lien du chapitre est deja en place!
            # Le dernier espace est interpré comme une option l'ajout de _ provoque une différence...
	    print 'Le lien est déja en place dans le sommaire.\nLe programme se termine avec succès, actualiser la page <vcb>.'
	    exit()
      ## Sortie de boucle le lien n'y est pas le prog se POURSUIT
      print 'Création du lien vers la nouvelle page'      
      link_write  = '\n' + '* [[' + new_page + ' | Vocabulaire ' + last_name + ']]\n' 
      title = sommaire
      page = pywikibot.Page(site, title) # PWB variable
      witext = page.get()
      page.text = witext + link_write    # AJOUTE le lien
      comment = u'Ajout du lien au sommaire des fiches de vocabulaire'
      page.save(comment)      
      print sommaire
      print link_write
    else:   # PAS DE SOMMAIRE Creation du sommaire des sections et du lien
      print 'Création du sommaire des fiches vocabulaire!'
      head = u'{{Titre | Index vocabulaire du département ' + root_name +'}}'
      link_write =  u'\n[[' + new_page + ' | Vocabulaire ' + last_name + ']]\n'
      category = u'\n[[Catégorie:' + root_name + '/Vocabulaire/Index]]'
      page = pywikibot.Page(site, title)
      comment = u'Création du sommaire des fiches vocabulaire, avec un premier lien.'
      page.text = head + link_write + category   # EDITE LE TEXTE DE LA PAGE
      page.save(comment)
      
#time.sleep(15)
#wait = input('PRESS ENTER TO CONTINUE')