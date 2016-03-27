#!/usr/bin/env python
# -*- coding: utf-8 -*-

### Liste les pages de l'espace de nom "Département" nº 108 
### Liste les Départements dans le fichier local "Départements.csv"
### Liste les sous-pages. les liens dans leçons par thèmes et leçons par niveaux
### Compare les deux liste de liens et les fusionne
### Verifie si les pages derrière les liens existent
### Compare le nombre de page d'interface et le nombre de leçons du département

import pywikibot
lang = 'fr'                    # prefixe langue
family = 'wikiversity'
site = pywikibot.Site(lang, family)  # The site we want to run our bot on
gen_dpt = site.allpages(namespace=108, prefix='p')
log = ''
sous_pages = []
all_sous_pages = [] # DEBUG liste brute des sous_pages
no_match = [] 
data_dpt = {}    # [departement] = sous_pages
curent = u''
count_all = 0
for page in gen_dpt:
  count_all = count_all + 1
  str_page = str(page) # il faut une chaine
  if '/' in str_page:
    all_sous_pages.append(page)
    prefix = curent[ 0 : -2]
    if prefix in str_page:
      sous_pages.append(page)  # Incrémente la liste des sous-pages
    else:   # ATTENTION
      no_match.append(page)    # Stock les sous-pages dont le prefix ne correspond pas
      log = log + 'Mauvais prefix, '+ str_page + 'n\'est pas une sous-page de ' + str(curent) + '.\n'
  else:   # Pas de separateur donc département
    departement = page
    curent = str_page
    print departement
    sous_pages = []
    data_dpt[departement] = sous_pages
# data_dpt[departement] = sous_pages
count = 0
for departement in sorted(data_dpt):
  count = count + 1
  print count
  sous_pages = data_dpt[departement]
  dpt_params = [sous_pages]
  list_link_theme = [] # Liste Leçons par Thèmes
  list_link_niveau = [] # Liste Leçons par Niveaux
  str_departement = str(departement)
  theme = str_departement[2:-2] + '/Leçons par thèmes'
  title = unicode(theme, 'utf-8')
  page = pywikibot.Page(site, title)
  exist = page.exists()   # Si la page existe
  if exist:
    #print 'YES EXIST'
    gen_lesson_theme = page.linkedPages(namespaces=0) # place les pages liéés dans un generateur
    for link_theme in gen_lesson_theme: # chaque element du generateur
      list_link_theme.append(link_theme) # est stocké dans la liste des leçons par thèmes
    dpt_params = [sous_pages, list_link_theme]
    data_dpt[departement] = dpt_params # la liste est ajoutée au tuple    
  else: 
    log = log + theme + ' NO exist\n'
    dpt_params = [sous_pages, list_link_theme]
    data_dpt[departement] = dpt_params
  niveau = str_departement[2:-2] + '/Leçons par niveaux'
  title = unicode(niveau, 'utf-8')
  page = pywikibot.Page(site, title)
  exist = page.exists() 
  if exist:
    gen_lesson_niveau = page.linkedPages(namespaces=0) # place les pages liéés dans un generateur
    for link_niveau in gen_lesson_niveau: # chaque element du generateur
      list_link_niveau.append(link_niveau) # est stocké dans la liste des leçons par 
    dpt_params = [sous_pages, list_link_theme, list_link_niveau]
    data_dpt[departement] = dpt_params   
  else: 
    log = log + niveau + 'NO exist\n'
    dpt_params = [sous_pages, list_link_theme, list_link_niveau]
    data_dpt[departement] = dpt_params 
# LE tuple contient, liste des départements, listes des sous-pages, des leçons par themes et par niveaux

file_departements_params = open('Départements.csv', 'w') # ouvre le fichier local en écriture
line_1 = 'Départements, Sous-pages, Leçons par thèmes, Leçons par niveaux, Ajouter, Total liens, Page existe, Balance \n'
file_departements_params.write(line_1)
#count_sous_pages = 0
for departement in data_dpt: # chaque departement
  #count_sous_pages = count_sous_pages + len(sous_pages)  # BUG différent du nombre total de sous-pages
  dpt_params = data_dpt[departement]
  [sous_pages, list_link_theme, list_link_niveau] = dpt_params
  list_link_add = []    # vider à chaque passage
  list_link_total = []   # vider à chaque passage
  list_link_exist = []  # vider à chaque passage
  for link_niveau in list_link_niveau: # chaque leçon par niveau (tester avec if not)
    if link_niveau in list_link_theme:   # si contenue dans la liste par theme
      pass
    else:
      list_link_add.append(link_niveau) # Sinon ajoute dans la Liste Lien Additionnel
  dpt_params = [sous_pages, list_link_theme, list_link_niveau, list_link_add]
  list_link_total = list_link_theme + list_link_add   # Liste des Lien Joints = leçons par thèmes + par niveaux flitrées
  dpt_params = [sous_pages, list_link_theme, list_link_niveau, list_link_add, list_link_total]
  #data_dpt[departement] = sous_pages, list_link_theme, list_link_niveau, list_link_add, list_link_total
  for link in list_link_total: 
    page = link #title #pywikibot.Page(site, title)
    exist = page.exists()   # Si la page existe
    if exist:
      list_link_exist.append(link)   # Liste des Liens existants (Touched)
    else:
      pass
  dpt_params = [sous_pages, list_link_theme, list_link_niveau, list_link_add, list_link_total, list_link_exist]
  balance = len(list_link_exist) - (len(sous_pages) + 1)
  dpt_params.append(balance)
  data_dpt[departement] = dpt_params #sous_pages, list_link_theme, list_link_niveau, list_link_add, list_link_total, list_link_exist, balance
  csv = '"'+ str(departement) + '", ' + str(len(sous_pages))  + ', ' + str(len(list_link_theme)) + ', ' + str(len(list_link_niveau) ) + ', ' + str(len(list_link_add) ) + ', ' + str(len(list_link_total)) + ', ' + str(len(list_link_exist))  +  ', ' + str(balance) + '\n'
  # Ajouter en en-tête le nombre de pages, sous-pages et total
  file_departements_params.write(csv) # 
file_departements_params.close()
print log
print count_all
print len(data_dpt)
print len(all_sous_pages)
print len(no_match)
