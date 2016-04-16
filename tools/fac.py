#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
### Création d'une liste de faculté 
### basée sur l'analyse de l'espace de nom "Faculté:" num_id "106" via Pywikibot
### le script produit 3 pages, liste des facultés, liste des départements par faculté
### et  liste des départements
########################################################################

# Variables PWB
import pywikibot
lang = 'fr'                    # prefixe langue
family = 'wikiversity'
site = pywikibot.Site(lang, family) # On obtient très facilement la liste des pages dans l'espace de nom 106 Faculté via Pywikibot
### Variables etape-1
liste_facultes = []   # pages
liste_sous_pages = [] # sous-pages
listes = [liste_facultes, liste_sous_pages]
### Variables etape-2
data_fac = {}         # key = faculté ; value = fac_params
### Variables etape-3
dpt_fac = {}          # Tuple invere
### Variables edition de pages
title_list_fac = u"Projet:Laboratoire/Propositions/Espace de nom Faculté/Liste des facultés"
title_list_dpt = u"Projet:Laboratoire/Propositions/Espace de nom Faculté/Liste des départements par faculté"
title_list_dpt2 = u"Projet:Laboratoire/Propositions/Espace de nom Faculté/Liste des départements"

### Fonction etape-1 : scanfac retourne reourne 2 listes (pages et sous-page)
def scanfac():
  gen_fac = site.allpages(namespace=106) #, prefix='j')
  for page in gen_fac:
    str_page = str(page)           # Une chaine pour rechercher '/'
    if '/' in str_page: # SOUS-PAGE
      liste_sous_pages.append(page)  # La liste des sous-pages
    else:               # PAGE
      liste_facultes.append(page)    # La liste des facultés
  return listes
### Fonction etape 2: tuplefac retourne un tuple, data_fac qui associe les facultés et leurs paramètres
### data_fac[faculte] = fac_params (sous_page_fac, gen_dpt, nombre_departement)
### et la fonction imprime un fichier csv ; tableau simple sur 3 colonnes
def tuplefac():
  count_fac = 0
  liens_departements = 0   # valeur de controle
  for faculte in liste_facultes:   # pour chaque faculté
    count_fac = count_fac + 1
    fac_params = []     # liste contenanat celle des departements (gen_dpt) puis nombre_departement
    sous_page_fac = []  # Liste les sous_pages de chaque faculté dans ns
    str_faculte = str(faculte)
    str_faculte = str_faculte[0:-2] + '/'  # tronque les crochets fermants et Ajoute le separateur
    for sous_page in liste_sous_pages:     # Attribue les sous-pages sur la base du prefix
      str_sous_page = str(sous_page)       # 
      if str_faculte in str_sous_page:     # en comparant les deux chaines
	sous_page_fac.append(sous_page)    # Pas d'autre verification...    
    fac_params.append(sous_page_fac)       # Affecte la liste sp_fac comme premier elemnt de liste fac_params
    fac_params.append(len(sous_page_fac))
    gen_dpt = faculte.linkedPages(namespaces=108)
    fac_params.append(gen_dpt)
    nombre_departement = 0   # Initialise le compteur de département
    for departement in gen_dpt:   # Pour chaque lien dans le generateur PWB
      nombre_departement = nombre_departement + 1   # Compte les départements
    fac_params.append(nombre_departement)   # Le nombre de dṕartement par faculté
    ### isRedirectPage(self) # ATTENTION verifier si la page du DEPARTEMENT est une redirection
    redir = faculte.isRedirectPage()
    target_faculte = ''
    #fac_params.append(redir)
    if redir == True:
      target_faculte = faculte.getRedirectTarget()
     # Stocker redir et target_page dans le tuple cf fonction 3 tupleinvert  
    fac_params.append(redir)            # ATTENTION
    fac_params.append(target_faculte)   # Ajouter les nouveaux param. à la fin (index code module Lua)
    data_fac[faculte] = fac_params
    liens_departements = liens_departements + nombre_departement
    print str(count_fac) + " sur: " + str(nombre_faculte)
  print liens_departements
  return data_fac

### Fonction 3 tupleinvert() - La fonction inverse le tuple data_fac
### Liste des facultés par département
### departement |liste facultés | nombre de faculte
def tupleinvert():
  for page in data_fac:   #  Pour Chaque faculté
    fac_params = data_fac[page]     # une liste de parametres
    [sous_page_fac, nb_sous_page_fac, gen_dpt, nombre_departement, redir, target_faculte] = fac_params # Liste des parametre deja dans le tuple
    for departement in gen_dpt:     # pour chaque departement dans cette faculté
      redir = False
      redir = departement.isRedirectPage()
      target_departement = ''
      if redir == True:
	target_departement = departement.getRedirectTarget()
      if not departement in dpt_fac:  # Si le departement n'est pas dans le tuple inverse
        l_fac = []                     # Initialise Liste des faculté pour ce departement
        l_fac.append(page)             # Ajoute la faculté dans la liste
        dpt_params = [redir, target_departement, l_fac]
        dpt_fac[departement] = dpt_params   # enregistre clé valeur dans le tuple inverse
      else:                           # Le departement est deja dans le tuple inverse
        dpt_params = dpt_fac[departement]   # Recupere la liste 
        [redir, target_departement, l_fac] = dpt_params
        l_fac.append(page)             # Ajoute la faculté dans la liste
  return dpt_fac

### Fonctions Etape-4: Edition des pages
def writelistfac():
  page_txt = u"{{Titre|Liste des facultés (automatique)}}\n"
  page_txt = page_txt + u'{|class="wikitable sortable"\n!Faculté\n!Nombre de département\n!Nombre de sous pages\n|-\n'
  tableau_txt = u'' # initialise le tableau
  for faculte in data_fac:
    fac_params = data_fac[faculte]
    [sous_page_fac, nb_sous_page_fac, gen_dpt, nombre_departement, redir, target_faculte] = fac_params
    line_fac = '|' + str(faculte) + '\n|' + str(nombre_departement) + '\n|' + str(nb_sous_page_fac) + '\n|-\n'
    line_fac = unicode(line_fac, 'utf-8')
    tableau_txt = tableau_txt + line_fac # ajoute la ligne
  page_txt = page_txt + tableau_txt + '|}\n'
  page_txt = page_txt + u'[[Catégorie:Laboratoire]]'
  comment = u'Analyse de l\'espace de noms Faculté - fr:wv'
  title = title_list_fac
  page = pywikibot.Page(site, title) # PWB variable
  page.text = page_txt
  page.save(comment) 

def writelistdpt():
  title = title_list_dpt
  page_txt = u"{{Titre|Liste des départements par facultés (automatique)}}\n<small>fac.py</small>\n"
  section_txt = u''
  for faculte in data_fac:
    fac_params = data_fac[faculte]
    [sous_page_fac, nb_sous_page_fac, gen_dpt, nombre_departement, redir, target_faculte] = fac_params
    ### modifier la variable str_faculte pour ajouter le label
    line_txt = "== " + str(faculte) + " ==\n"
    line_txt = unicode(line_txt, 'utf-8')
    section_txt = section_txt + line_txt
    dpt_txt = u''
    for departement in gen_dpt:
      line_txt = "* " + str(departement) + "\n"
      line_txt = unicode(line_txt, 'utf-8')
      dpt_txt = dpt_txt + line_txt
    section_txt = section_txt + dpt_txt
  page_txt = page_txt + section_txt + u"[[Catégorie: Laboratoire]]"
  page = pywikibot.Page(site, title) # PWB variable
  page.text = page_txt
  comment = u'Liste des départements par facultés'
  page.save(comment) 

def writelistdpt2(): 
  title = title_list_dpt2
  page_txt = u"{{Titre|Liste des départements (automatique)}}\n<small>fac.py</small>\n"
  page_txt = page_txt + u'{|class="wikitable sortable"\n!Département\n!Nombre de facultés\n!Facultés\n!Redirection\n!Redirige vers\n|-\n'
  tableau = u''
  for departement in dpt_fac:
    dpt_params = dpt_fac[departement]
    [redir, target_departement, l_fac] = dpt_params
    nb_fac_dep = len(l_fac)
    fac_txt = ''
    for fac in l_fac:      
      fac_txt = fac_txt + str(fac) + ' '
    line_txt = "|" + str(departement) + "\n|" + str(nb_fac_dep) + "\n|" + fac_txt + "\n|" + str(redir) + "\n|" + str(target_departement) + "\n|-\n"
    
    #fac_txt = unicode(fac_txt, 'utf-8')
    line_txt = unicode(line_txt, 'utf-8') #+ fac_txt + "\n|-\n"
    tableau = tableau + line_txt
  page_txt = page_txt + tableau + u"|}\n[[Catégorie:Laboratoire]]"
  page = pywikibot.Page(site, title) # PWB variable
  page.text = page_txt
  comment = u'Liste des facultés par départements'
  page.save(comment) 

### Fonction 5 - write_module() - Ecriture du module "Table faculté"
# ATTENTION ajouter redir et cible dans la table "ns_faculte"
# Ajouter la table "dpt_fac" issue de la fonction tupleinvert().
def write_module(): # RENOMMER write_module
  result = 'local p = {}\n'
  # DEBUT fx write_table_fac()
  result = result + 'p.ns_faculte = {' # la table de l'ESPACE DE NOM
  for fac in data_fac:
    [sous_page_fac, nb_sous_page_fac, gen_dpt, nombre_departement, redir, target_faculte] = data_fac[fac]
    result = result + '{' + str(fac) + ', ' + str(nb_sous_page_fac ) + ', '
    var_liste_sous_page = '{'
    if len(sous_page_fac) == 0:
      var_liste_sous_page = var_liste_sous_page + '}'
    else:
      for sous_page in sous_page_fac :
        var_liste_sous_page = var_liste_sous_page + str(sous_page) + ', '
      var_liste_sous_page = var_liste_sous_page[:-2] + '}' # supprime la dernière virgule espace puis ferme l'accolades
    result = result + var_liste_sous_page + ', ' + str(nombre_departement) + ', '
    var_liste_departement = '{' # Ouvre la table Lua
    c=0   ### Compte les departements
    for departement in gen_dpt:      ### PWB Generator !#@#
      c = c + 1   # Incremente le nombre de departement
      var_liste_departement = var_liste_departement + str(departement) + ', ' # ajoute le departement au code Lua
    if c == 0:    # Si aucun departement
      var_liste_departement = var_liste_departement + '}' # penser à fermer la table lua
    else:         
      var_liste_departement = var_liste_departement[:-2] + '}'    
    result = result + var_liste_departement + '}, '
  result = result[:-2] + '}\n'  
  # STOP ici ajouter la table DEPARTEMENT dpt_fac AVANT RETURN P
  lua_table_departement = write_table_dpt() # La fonction ajoute la table des départements
  result = result + lua_table_departement
  result = result + 'return p\n' ### page /documentatio \n[[Catégorie:Modules tests]]
  result = unicode(result, 'utf-8')
  return result

### Fonction 5.1 - write_table_dpt() - Ecrit le code lua de la table dpt_fac
def write_table_dpt():
  lua_code = 'p.t_departements = {'   # la tables des DEPARTEMENTS à l'exception de toutes les autres pages 
  for departement in dpt_fac:
    lua_code = lua_code + '{'
    [redir, target_departement, l_fac] = dpt_fac[departement]
    lua_code = lua_code + str(departement) + ', '
    if len(l_fac) == 0:
      lua_code = lua_code + '{}, '
    else:
      lua_code = lua_code + '{'
      for faculte in l_fac:
	lua_code = lua_code + str(faculte) + ', '
      lua_code = lua_code[:-2] + '}, ' 
    lua_code = lua_code + str(redir) + ', ' + str(target_departement) + '}, '
  lua_code = lua_code[:-2] + '}\n'
  return lua_code
###

### Etape-1
listes = scanfac()  # Calcul liste_facultes ; liste_sous_pages
nombre_faculte = len(liste_facultes)
print str(nombre_faculte) + ' Facultés\nListe des départements pour chaque faculté'
### Etape-2
data_fac = tuplefac() # Calcul les propriete des facultés
### Etape-3
dpt_fac = tupleinvert() # Inverse le tuple, calcul le nb de dpt
### Etape-4 Edition des pages
#writelistfac()
#writelistdpt()
#writelistdpt2()



### Etape 5 - Ecriture du module Lua-scribunto "Module:Table faculté"
code_module = write_module()

print code_module
title = u'Module:Table faculté' #u'Module:Catest' #
comment = u'Le module reçoit les données depuis le srcipt Python "fac.py" (cf vocabulary-index on Wikimedia Tool Labs).'
page = pywikibot.Page(site, title)
page.text = code_module
page.save(comment)

### Ecriture fichier csv abandonnée
#fFac = open('Fac.csv', 'w')
#fFac.write('Faculté, Nombre département(s)\n') # en_tête liste Facultés | départements
#print str(totalDpt) + ' dept répartis dans les facultés' #  Ce total ne tient pas compte des doublons ( 1 dept=> +2 Fac)
#fFac.close()

### ecriture des valeurs comme argument ABANDONNEE.
### Ecriture via module(args) test1
# Nous parvenons a formater les argument dans une table mais 
# impossible d'utliser cette tabe sans lui passer tous les arguments de nouveaux
# {{#Invoke:Catest|facdata|
#result = '{{#Invoke:Catest|facdata|'
#for fac in data_fac:
  #[sous_page_fac, nb_sous_page_fac, gen_dpt, nombre_departement, redir, target_faculte] = data_fac[fac]
  #uuu = '|' + str(nb_sous_page_fac) + '|' + str(nombre_departement) + '|' + str(sous_page_fac) + '|\n'
  #result = result + str(fac) + uuu
  #for departement in gen_dpt:
    #result = result + '\n' + '* ' + str(departement) + '\n'
  #result = result + '|'
#result = result + '}}'
#title = u'Projet:Laboratoire/Propositions/Espace de nom Faculté/Test'
#page = pywikibot.Page(site, title)
#page.text = unicode(result, 'utf-8')
#comment = 'Tentative pour passer les données Python vers un module Lua Scribunto'
#page.save(comment)