#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import urllib
import pywikibot
import datetime #???

langPack = {}


### PORTUGAIS: Liste des articles
genre = re.compile('[o|a]\\s') # ATTENTION PARAMETRES REGIONAUX
pluriel_masculin = re.compile('os\\s')    # ATTENTION REMPLACER PAR LES ARTICLES DE LA LANGUE ÉTUDIÉE
pluriel_feminin = re.compile('as\\s')    # ATTENTION
um = re.compile('um\\s')       # ATTENTION
uma = re.compile('uma\\s')     # ATTENTION
ptPack= [genre, pluriel_masculin, pluriel_feminin, um, uma]   # Les articles de la langue portugaise
langPack['pt']= ptPack

## Check langPack
def chkarticle(locution, word, pack):
  kToDelete = []
  for k in locution:           # Chaque clé de tupLocution
    liste_mots = k.split()     # Listes les mots
    nombre_mots = len(liste_mots)    # Calcul le nbre de mots
    if nombre_mots ==2:              # Si DEUX mots
      for article in pack:    # Pour chaque regex article dans...
        moArticle = article.match(k)     # Cherche l'article en debut de chaine
        if moArticle:              # Si la clé commence par un article
          newKey = liste_mots[1] + ' (' +liste_mots[0] + ')'   # newKey déplace l'article après le nom
          word[newKey] = locution[k]             # tupWord reçoit newKey
          kToDelete.append(k)                          # On enregistre la clé à supprimer
        else: # pas d'article à gérer
          pass
    # Le Wiktionnaire (fr) reconnait l'article et le lien fonctionne ce sera necessaire de déplacer
    # les articles français uniquement si on fait une liste triée sur le nom français...
    
  for k in kToDelete:    # Pour chaque clé à supprimer
    del locution[k]      # Enlève les couples article/mots du tupLocution
