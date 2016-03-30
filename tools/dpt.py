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
site = pywikibot.Site(lang, family)  # 

#log = ''
sous_pages = []
redir = False
all_sous_pages = [] # DEBUG liste brute des sous_pages
no_match = [] 
data_dpt = {}    # [departement] = sous_pages
### 
#list_link_theme = []
#list_link_niveau = []
###
#list_link_add = []
#list_link_total = []
#list_link_exist = []
#balance = 0
title_tableau = u"Projet:Laboratoire/Propositions/Espace_de_nom_Département/Départements_et_paramètres"

### Fonction tuplepages, sépare les pages de départements et les sous-pages
### Teste si les départements sont redirigé stock boléen dans redir
### Associe Département avec sous-page et redir
### liste all_sous_pages et no_match pour contrôle
# data_dpt[departement] = [sous_pages, redir]

### Fonction tupledpt[Departement]=[sous-page, redir]
def tupledpt():
  gen_dpt = site.allpages(namespace=108) #, prefix='j')
  count_all = 0 # Compteur de pages
  curent = u''
  for page in gen_dpt:
    count_all = count_all + 1
    str_page = str(page) # il faut une chaine 
    if '/' in str_page:    #  SI Le titre de la page contient un separateur
      all_sous_pages.append(page)   # Ajoute dans liste de contrôle
      prefix = curent[ 0 : -2]      # supprime crochets fermants de la page courante
      if prefix in str_page:     # Si le prefixe de la page courante se trouve dans le nom de la sous-page
        sous_pages.append(page)  # Incrémente la liste des sous-pages
      else:   # ATTENTION Le prefix courant ne correspond pas
        pass
        #no_match.append(page)    # Controle ; stock les sous-pages dont le prefix ne correspond pas
        #log = log + 'Mauvais prefix, \n'+ str_page + 'n\'est pas une sous-page de\n' + str(curent) + '.\n'
    else:   # Pas de separateur donc département
      departement = page
      curent = str_page
      print departement
      redir = departement.isRedirectPage()
      sous_pages = []
      data_dpt[departement] = [sous_pages, redir]
  #print count_all
  return data_dpt, count_all # Retourne le tupe et la sommes des pages dans l'espace de noms

### La fonction cherche les liens dans les pages speciales
### et ajoute la liste des leçons par themes et par niveaux dans le tuple
def findlinks():
  count_dpt = 0
  for departement in sorted(data_dpt):
    #log = 0 # (1 si pas de page thème, 2 si pas de page leçon)
    count_dpt = count_dpt + 1
    print count_dpt
    dpt_params = data_dpt[departement]
    [sous_pages, redir] = dpt_params
    list_link_theme = []  # Liste Leçons par Thèmes
    list_link_niveau = [] # Liste Leçons par Niveaux
    str_departement = str(departement)
    theme = str_departement[2:-2] + '/Leçons par thèmes'
    title = unicode(theme, 'utf-8')     # Leçons par thèmes
    page = pywikibot.Page(site, title)  # La page 
    exist = page.exists()               # Teste
    if exist:     # Leçons par thèmes EXIST
      gen_lesson_theme = page.linkedPages(namespaces=0) # place les pages liéés dans un generateur
      for link_theme in gen_lesson_theme:  # chaque element du generateur
        list_link_theme.append(link_theme) # est stocké dans la liste des leçons par thèmes
      dpt_params.append(list_link_theme)
      data_dpt[departement] = dpt_params   # la liste est ajoutée au tuple    
    else:
      #log = log + 1
      dpt_params.append(list_link_theme)
      data_dpt[departement] = dpt_params
    niveau = str_departement[2:-2] + '/Leçons par niveaux' # Compile le nom de  la page
    title = unicode(niveau, 'utf-8')   # Unicode pour PWB
    page = pywikibot.Page(site, title) # Leçon par niveaux
    exist = page.exists()              #Test
    if exist:   # Leçon par niveaux EXIST
      gen_lesson_niveau = page.linkedPages(namespaces=0) # place les pages liéés dans un generateur
      for link_niveau in gen_lesson_niveau:  # chaque element du generateur
        list_link_niveau.append(link_niveau) # est stocké dans la liste des leçons par 
      dpt_params.append(list_link_niveau)
      data_dpt[departement] = dpt_params   
    else: 
      #log = log + 2 # niveau + 'La page Leçon par niveau n\'existe pas!\n'
      dpt_params.append(list_link_niveau)
      data_dpt[departement] = dpt_params 
  return data_dpt

### Fonction linkexist compare les liens par thèmes te par niveau
### et verifie si la page du lien existe
def linkexist():
  for departement in data_dpt: # chaque departement
    dpt_params = data_dpt[departement]
    [sous_pages, redir, list_link_theme, list_link_niveau] = dpt_params
    list_link_add = []    # vider à chaque passage
    list_link_total = []  # vider à chaque passage
    list_link_exist = []  # vider à chaque passage
    for link_niveau in list_link_niveau:  # chaque leçon par niveau (tester avec if not)
      if link_niveau in list_link_theme:  # si contenue dans la liste par theme
        pass
      else:
        list_link_add.append(link_niveau) # Sinon ajoute dans la Liste Lien Additionnel
    dpt_params.append(list_link_add)
    list_link_total = list_link_theme + list_link_add   # Liste des Lien Joints = leçons par thèmes + par niveaux flitrées
    dpt_params.append(list_link_total)
    for link in list_link_total: 
      page = link            #
      exist = page.exists()  # Si la page existe
      if exist:
        list_link_exist.append(link)   # Liste des Liens existants (Touched)
      else:
        pass
    dpt_params.append(list_link_exist)
    balance = len(list_link_exist) - (len(sous_pages) + 1)
    dpt_params.append(balance)
    data_dpt[departement] = dpt_params #sous_pages, redir, list_link_theme, list_link_niveau, list_link_add, list_link_total, list_link_exist, balance
    csv = '"'+ str(departement) + '", ' + str(len(sous_pages)) +', ' + str(redir) + ', ' + str(len(list_link_theme)) + ', ' + str(len(list_link_niveau) ) + ', ' + str(len(list_link_add) ) + ', ' + str(len(list_link_total)) + ', ' + str(len(list_link_exist))  +  ', ' + str(balance) + '\n'
    file_departements_params.write(csv) # 
  file_departements_params.close()
  return data_dpt
###
# START
###
data_dpt, nb_pages = tupledpt()

data_dpt = findlinks()

file_departements_params = open('Départements.csv', 'w') # ouvre le fichier local en écriture
line_1 = 'Départements, Sous-pages, redir, Leçons par thèmes, Leçons par niveaux, Ajouter, Total liens, Page existe, Balance \n'
file_departements_params.write(line_1)

data_dpt = linkexist()

# Ajouter en en-tête le nombre de pages, sous-pages et total
page_txt = u"{{Titre|Liste des pages de l'espace de noms Départements}}\n"
page_txt = page_txt + u'{|class="wikitable sortable"\n!Départements\n!Sous-pages\n!Redir\n!Leçons thèmes\n!Leçons niveaux\n!Ajouter\n!Total liens\n!Page existe\n!Balance\n|-\n'
for departement in data_dpt:
  dpt_params = data_dpt[departement]
  [sous_pages, redir, list_link_theme, list_link_niveau, list_link_add, list_link_total, list_link_exist, balance] = dpt_params

  line = '\n|' + str(departement) + '\n|' + str(len(sous_pages)) + '\n|' + str(redir) + '\n|' + str(len(list_link_theme)) + '\n|' + str(len(list_link_niveau) ) + '\n|' + str(len(list_link_add) ) + '\n|' + str(len(list_link_total)) + '\n|' + str(len(list_link_exist))  +  '\n|' + '('+str(balance) + ')\n|-\n'
  page_txt = page_txt + unicode(line, 'utf-8')
page_txt = page_txt + u'|}\n[[Catégorie:Laboratoire]]'
title = title_tableau
page = pywikibot.Page(site, title)
comment = "Liste des pages de l'espace de noms Département"
page.text = page_txt
page.save(comment)

#print log

print '########\n'
print 'Toutes les pages dans l\'espace de noms'
print nb_pages
print 'Tous les départements dans le tuple data_dpt'
print len(data_dpt)
print 'Toutes les sous-pages'
print len(all_sous_pages)
print 'no_match'
print len(no_match)
