#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pywikibot
#import urllib

language = u'fr'
family = u'wikiversity'
site = pywikibot.Site(language,family)

### PATHNAME sépare l'argument initial en élements du path
def pathname(path):
  title =  path
  page = pywikibot.Page(site, title)
  page_cible_txt = page.get()
  reLesson = re.compile(u'{{[L|l]eçon')       # RegEx pour trouver le modèle "Leçon"
  reChapitre = re.compile(u'{{[C|c]hapitre')  # RegEx pour trouver le modèle "Chapitre"
  list_path_elemt = path.split('/')           # split le path dans la liste
  nb_path_elemt = len(list_path_elemt)        # list_path_elemt contient tous les elements du path
  root_name = list_path_elemt[0]              # Premier element
  last_name = list_path_elemt[nb_path_elemt -1] # Dernier element
  list_sections = []  # Liste des sections à l'exclusion de root_name et last_name ex: rootname/nSec1/nSec2/lastname
  for element in list_path_elemt[1:list_path_elemt.index(last_name)]:  # Exclut root_name et last_name
    list_sections.append(element)
  lPath = [path, list_path_elemt, root_name, last_name, nb_path_elemt, list_sections]
  moLesson = reLesson.search(page_cible_txt)   
  moChapitre = reChapitre.search(page_cible_txt) #  on cherche sur page_cible_txt 
  sommaire = root_name + '/Index vocabulaire' # unicode
  # titre de la page contenant le sommaire des fiches de vocabulaire
  if nb_path_elemt == 1: # Si un seul element dans le path # Attention la condition
    print "La cible est un département, l\'exécution du programme peut prendre prendre plusieurs secondes en fonctions du nombre de leçons à traiter"   # On previent l'utilisateur
    class_doc = 'Département'      # On attribue class_doc en fonction de l'argument (pas de modèle en cause)
    new_page = root_name + '/Index vocabulaire/Index global'  # ATTENTION scinder la liste Indexglobal en 3
    # word (Index_global_des_mots), locution (Index_global_des_locutions), phrase (Index_global_des_phrases)
  elif moLesson:   # Si la page donnée en argument contient "le modèle Leçon"
    class_doc = 'Leçon'  # class_doc est attribué par "le modèle Leçon"
    print 'La cible est une ' + class_doc
    new_page = root_name + '/Index vocabulaire/vcb ' + last_name
  elif moChapitre:   # Si la page donnée en argument contient le modèle "Chapitre"
    class_doc = 'Chapitre'    
    print 'La cible est un ' + class_doc
    new_page = root_name + '/Index vocabulaire/vcb '+ last_name
  else:   # Si aucun des modèles suivants: Departement, leçon ou Chapitre
    class_doc = 'none'
    print 'Le type de cible est indéfini, ' + class_doc    
    new_page = root_name + '/Index vocabulaire/vcb ' + last_name
  ### QUELLE DIFFERENCE ENTRE CHAPITRE ET NONE?
  linker = [class_doc, new_page, sommaire] # Sortie de boucle on sauve les varibles dans linker
  lPath.append(linker) # ajoute linker à la liste lPath (list_path_elements)
  return lPath         # retourne la liste des elements du path
### PATHNAME FIN

### TRAITEMENT DE LA LISTE DEs PAGES  (via PWB) 
# (add_special_dir) Ajoute les pages des dossiers spéciaux pour leçons françaises
# Fonction liste_cible renvoi la liste des pages à scanner
# sur la base de args.cible et class_doc
def cibles(cible_unicode, class_doc):
  liste_cible = []                       # Liste pour titre des pages
  gen_pages = site.allpages(prefix=cible_unicode) # suffisant si la cible est un departement
  if class_doc == "Département":
    liste_cible = gen_pages
  else :
    for page in gen_pages:
      #print page
      s_page = str(page)
      liste_dossiers = ['Annexe', 'Exercices', 'Fiche', 'Quiz', 'Travail_pratique']
      prefix = cible_unicode + '/'  
      for dossier in liste_dossiers:
        chaine = prefix + dossier
        u_page = unicode(s_page, 'utf-8')
        if chaine in u_page:
	  liste_cible.append(page)
      index_car = len(cible_unicode) + 7
      chaine = str(page)
      fin = chaine[index_car : ]
      print fin
      if '/' in fin:
        pass
      else:
        liste_cible.append(page)
  return liste_cible

### Fonction scantemplate() cherche les modèles pron et trad dans les pages 
# sur la base de liste_cible retourne les deux listes de modèles
def scantemplate(liste_cible):
  lPron = []   # Liste des modèles Prononcition
  lTrad = []   # Liste des modèles Traduction
  rePron = re.compile('[P|p]rononciation\w*')   # recherche les modèles "Prononciaition(s)"
  reTrad = re.compile('[T|t]raduction\w*')      # recherche les modèles "Traduction(s)"
  for page in liste_cible: # chaque pages
    print page
    gen = page.templatesWithParams() # liste les modèles et contenu
    if gen:                            # si l'objet generator existe
      for template in gen:             # pour chaque item du generator
        template_name = template[0]    # Le nom de la pge du modele
        template_params = template[1]  # liste des parametres
        template_name = str(template_name)
        moTrad = reTrad.search(template_name) # cherche trad dans liste des modeles
        if moTrad:
	  if u'indexation = non' in template_params: # strictement |indexation = non|
	    print 'Le modèle suivant est marqué pour ne pas être indexé (indexation = non)\n'
	    print page           # implémentation rapide du parametre
	    print template_name   # indexation = non
	    print template_params # utiliser regex pour améliorer
	    pass
	  else:
	    lTrad.append(template)      # si trad enregistre dans LISTE TRAD
        moPron = rePron.search(template_name) # cherche prononciation dans liste des modèles
        if moPron:
          if u'indexation = non' in template_params: # strictement |indexation = non|
	    print 'Le modèle suivant est marqué pour ne pas être indexé (indexation = non)\n'
	    print page          # implémentation rapide du parametre
	    print template_name   # indexation = non
	    print template_params # utiliser regex pour améliorer
	    pass 
	  else:
	    lPron.append(template)      # si pron enregistre dans LISTE PRON
  templates = [lPron, lTrad]
  return templates

### TRAITEMENT LISTE PRONONCIATION
# scanpron() retourner une liste qui sera revèrsée dans lTrad
# Ce modèle propose une quatrième colonne transcritpion
# quand cette 4èmme colonne existe, les données ne sont pas collectée cf log
# Il faudrait detecter la quatrième colonne si existe
def scanpron(lPron, lTrad):
  reEq = re.compile('=')  # recherche des parametres
  lAudio = []             # Liste pour la 3ème colonne du modèle Prononciation
  for template_object in lPron: # LPRON
    template_name = template_object[0]   # Nom du modele
    template_params = template_object[1] # Liste des parametres
    lrm = []   # liste des elements à supprimer
    count = 1  # initialise le compteur
    for param in template_params:  # pour chaque parametre
      moEq = reEq.search(param)    # cherche symbol egual, param nommé
      if moEq: # Si le param est nommé
	pass    
      else:    # c'est une cellule
	if count % 3 == 0:     # si elle est multiple de trois
	  lAudio.append(param) # copie dans la liste lAudio
	  lrm.append(param)    # copie dans liste à supprmer
      count = count + 1        # prochain param
    for rm in lrm:             #  chaque element
      template_params.remove(rm)   # est supprimé
    lTrad.append(template_object)  # copie les objets restants dans lTrad
  prononciation = []
  prononciation.append(lTrad)#, lAudio)
  prononciation.append(lAudio)
  return prononciation

### TRAITEMENT LISTE TRADUCTION
# Fonction scantrad() scanne le(s) modèle(s) Traduction(s)
# sur la base de lTrad construit et retourne le dictionnaire principal
def scantrad(lTrad, lang_dest, site_lang):
  globalDict = {} # Dictionnaire global 
  re_langue1 = re.compile('langue1')     # re pour chercher le paramètre dans les modèles
  re_langue2 = re.compile('langue2')     # re pour chercher le paramètre dans les modèles
  reEq = re.compile('=')                 # recherche des parametres
  for template_object in lTrad:    # LTRAD
    template_name = template_object[0]   # Nom du modèle
    template_params = template_object[1] # Liste des paramètres
    named_params = []  # Liste pour les parametres nommés
    raw1 = lang_dest   # initialise les langues
    raw2 = site_lang   # avec paramètres par défaut
    for param in template_params:  # PARAMETRES
    # ATTENTION API retourne lzh pour chinois mais wikversité utilise zh
      moEq = reEq.search(param)    # cherche symbole egal param nommés
      if moEq:     # Si symbol
        named_params.append(template_params.index(param)) # enregistre son index dans liste named_params
        mo_langue2 = re_langue2.search(param)             # Cherche langue2
        if mo_langue2:   # SI langue2
	  spl_langue2 = param.split('=')  # split sur symbol=
	  raw2 = spl_langue2[1]           # enregistre dans raw2
	  raw2 = raw2.strip()             # retire éspaces inutiles
        mo_langue1 = re_langue1.search(param)    # Cherche langue1
        if mo_langue1:   # SI langue1
          spl_langue1 = param.split('=') # split egual
	  raw1 = spl_langue1[1]          # stock valeur
	  raw1 = raw1.strip() # enleve espaces
    code_langues = raw1+'-'+raw2         # variable code_langues = langue1-langue2
    iMaxData = min(named_params)         # Calcul dernière donnée = premier paramètre nommé ???
    data = template_params[0:iMaxData]   # Calcul la zone de données
    nb_cel = len(data)       # Pour vérifier parité du nombre de cellule
    tpl_params = [code_langues, iMaxData, nb_cel]    # langue1-langue2, dernier index de donnée, nombre de cellules
    template_params.append(tpl_params)     # Stoque les paramètres dans template_params
    if nb_cel %2 <> 0:   # Si le nombre de cellule n'est pas paire verifier si dernière cellule vide
      error_nbCel_log = 'Template error:\nVérifier le nombre de cellules: '
      log = log + error_nbCel_log + str(nb_cel)
      last_cel = template_params[iMaxData-1]
      print '######'
      print last_cel
      print '#######'
      reSpaces = re.compile('\s\n') # resoud le cas Anglais/Grammaire/Conjugaison/Impératif
      # Attention le problème reste relatif à la 4ème colonne de prononciation
      moSpaces = reSpaces.match(last_cel)
      if last_cel == '':
        print 'DERNIERE CELLULE VIDE A DETRUIRE'
        # resoud le cas de la dernière cellule vide sans espaces ni saut de ligne
        # il reste à supprimer l'element de la liste lb
      if moSpaces:
        print 'Celule vide à détruire'
        print moSpaces.group()
        #template_params.remove[last_cel]        
    if code_langues == lang_dest + '-' + site_lang and nb_cel % 2 == 0:   # Si langues par defaut et nombre cellule paire
      for cellule in data:                # Pour chaque donnée dans dataZone
        if data.index(cellule) % 2 == 0:     # Si son index est paire
	  index_next = data.index(cellule)+1   # Calcul index prochaine valeur
	  next_cell = data[index_next]         # next_cell = prochaine valeur
	  globalDict[cellule] = next_cell      # Dictionnaire Global reçoit mot_PT : mot_FR
        else:          # Ce n'est pas une clé mais une valeur (deja traité)
	  pass
    elif code_langues == site_lang + '-' + lang_dest and nb_cel % 2 == 0: # Si langues INVERSE fr-pt celulles paire
      for cellule in data:                # Pour chaque donnée dans dataZone
        if data.index(cellule) % 2 == 0:     # Si son index est paire
	  index_next = data.index(cellule) + 1   # Calcul index prochaine valeur
	  next_cell = data[index_next]           # next_cell = prochaine valeur
	  globalDict[next_cell] = cellule        # On inverse cellule et next_cell dans le dictionnaire
        else: # IMPAIR PASS
          pass
    else:
      error_codes_langues = 'Titres de colonnes: \n' + str(code_langues)
      log = log + error_codes_langues
      print code_langues
      print template_name
      print data
      # chinois code langue sur 3 caractères tronque le l, lzh devient zh
  return globalDict

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



### Abandon momentané des fonctions write position et insert
### Même en programmant l'ecriture du sommaire, les liens ne seraient pas triés correctement
### c-à-d selon leur position dans les index des leçons. Si reprise du travail, considérer la liste 
### path_elemt
#def write_position(list_sections, sommaire): #Verfifie si le titr-section existe
  #section_index = 0
  
  #title = sommaire   
  #page = pywikibot.Page(site, title) # PWB variable
  #wikitext = page.get()
  #for section in list_sections:
    #section_uni = unicode(section, 'utf-8') # UNICODE
    #reSection = re.compile('=+ ' + section + ' =+') # ATTENTION il faudrait determiner le nombre precis de symbole = à chercherla section encadré de plusieurs = ou ===
    #moSection = reSection.search(wikitext)   # cherche les titres du sommaire 
    #if moSection:  
      #sommaire = title + '#' + section_uni  # defini la titre-section où écrire le lien
      #section_index = list_sections.index(section) +1 # position dans liste pour fx insert
  #return sommaire, section_index

#def insert(section_index, list_sections):  # ecrit les sections `a inserer
  #filtred_sections = list_sections[ section_index : ]  # Ne pas ecrire les sections déjà présentes
  #insert_txt = u''
  #for section in filtred_sections:
    #section_uni = unicode(section, 'utf-8') # UNICODE
    #title_level = section_index + 2
    #fix = ''
    #count =1
    #while count <= title_level: # ajoute le nombre de symbole egal necessaire
      #fix = fix + '='
      #count = count + 1
    #insert_txt = insert_txt + '\n' + fix + ' ' + section_uni + ' ' + fix # Compile les sections
  #return insert_txt
