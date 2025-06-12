"""
Fichier contenant tous les textes d'accompagnement utilisés dans les différentes pages de l'application Dash.

Chaque variable texte est une chaîne de caractères (souvent multiligne) servant à :
- Expliquer une section de saisie à l'utilisateur (ex : langues, options, professeurs...) ;
- Fournir un résumé du contexte ou des consignes (ex : page d'accueil, page résultats) ;
- Structurer les différentes parties de l'interface avec des textes explicatifs cohérents et homogènes.

Ces chaînes sont utilisées dans les composants Dash sous forme de `html.P(...)`, `html.H*`, ou autres éléments visuels.

"""

texte_entete = "Cette page vous permet de renseigner les informations de votre établissement : le programme national, les horaires, les langues, les options, les classes, les salles ainsi que les professeurs. " \
    "Les données saisies s'enregistrent automatiquement, il pourra vous être demandé si vous souhaitez les conserver si vous tentez de revenir à la page d'accueil. " \
    "Grâce à l'enregistrement automatique vous pouvez reprendre automatiquement votre précédente saisie et la remodifier suivant vos besoins. " \
    "Vous pouvez aussi éffacer toutes les données grâce au bouton suivant : "

texte_explications_programme = "Cette section vous permet de valider le programme national de votre établissement, vous pouvez le modifier si besoin. On considéra les volumes horaires des options ultérieurement. "

texte_explications_horaires = "Les horaires sont à renseigner en heures et minutes (par tranches de 5 minutes) pour les journées de cours sélectionnés. Par exemple, pour 8h30, vous devez mettre 8 dans la case \"Heures\" et 30 dans la case \"Minutes\"."

texte_explications_informations = "Cette section vous permet de renseigner les horaires de votre établissement ainsi que les langues disponibles."

texte_explications_cantine = "Cette section vous permet de renseigner les informations relatives au réfectoire de votre établissement. "

texte_explications_permanences = "Cette section vous permet de renseigner la capacité en simultanée relative aux permanences de votre établissement. "
texte_explications_langues = "Les langues de l'établissement sont à renseigner dans cette section. Vous pouvez sélectionner plusieurs langues pour chaque niveau (LV1, LV2, etc.). " \
    "Vous pouvez saisir dans \"Autre\" si certaines langues de l'établissement ne sont pas dans les propositions de réponse."

texte_explications_options = "Les options de l'établissement sont à renseigner dans cette section. Vous pouvez sélectionner plusieurs options pour chaque catégorie et en saisir dans \"Autre\"."

texte_explications_ressources = "Cette section vous permet de renseigner les ressources de l'établissement (classes/ groupes, professeurs et salles) ainsi que de vérifier le volume horaire à appliquer du programme national."

texte_explications_classes = "Vous pouvez importer un fichier Excel ou CSV contenant les classes (un exemple de structure de fichier est disponible ci-dessous), ou les renseigner/modifier manuellement."

texte_explications_professeurs = "Vous pouvez importer un fichier Excel ou CSV contenant les professeurs (un exemple de structure de fichier est disponible ci-dessous), ou les renseigner/modifier manuellement."

texte_explications_salles = "Vous pouvez importer un fichier Excel ou CSV contenant les salles (un exemple de structure de fichier est disponible ci-dessous), ou les renseigner/modifier manuellement."

texte_explications_page_contrainte_optionnelles = "Sur cette page vous pouvez définir des contraintes optionnelles pour votre emploi du temps. " \
    "Ces contraintes sont facultatives et ne sont pas nécessaires pour générer un emploi du temps. " \
    "Elles permettent d'affiner la génération de l'emploi du temps en fonction des besoins spécifiques de votre établissement. " 

texte_explications_poids_materiel = "Cette section vous permet de renseigner le poids du matériel scolaire par matière et par niveau. " \
    "Vous pouvez ajuster les poids estimés pour chaque matière et définir un poids maximal autorisé par jour."

texte_explications_page_calculs_1 = "Appuyez sur le bouton ci-dessous pour lancer le solveur à partir des données saisies."
texte_explications_page_calculs_2 = "Vous pouvez demander la génération de plusieurs emplois du temps (solutions), ce qui permet de comparer différentes configurations possibles. Le solveur explorera plusieurs chemins d'optimisation et retiendra les meilleurs selon les critères définis (plus haut taux de respects des contraintes obligatooires et optionnelles)." 
texte_explications_page_calculs_3 = "Par exemple, si vous saisissez 10, le système testera 10 solutions différentes, puis sélectionnera la meilleure à afficher. Cela permet d'améliorer la qualité finale, au prix d'un temps de calcul plus long, c'est pour cela que c'est à vous de moduler selon vos besoins." 
texte_explications_page_calculs_4 = "Attention, l'outil ne conserve qu'une seule solution finale."
texte_explications_page_calculs_5 = "Plus vous en demandez, plus le solveur aura de chances de trouver un emploi du temps optimal, mais le calcul sera aussi plus long."

texte_explications_page_refectoire_permanences = "Dans cette partie, vous pouvez renseigner la capicité maximale du réfectoire et des permanences, ainsi que le pourcentage d'élèves mangeant au réfectoire. " \
    "Ces données sont utilisées pour répartir les élèves dans les lieux disponibles en tenant compte de leur âge et du temps de midi disponible."


texte_explications_ordre = "Pour finir, vous devez organiser les contraintes optionnelles dans votre ordre de priorité / d'importance. Le solveur tentera de satisfaire les contraintes les plus prioritaires en premier."

page_contraintes = "Sur cette page, vous allez pouvoir renseigner les contraintes de votre établissement concernant les professeurs, les groupes / classes, les salles ainsi que les contraintes de planning. Vous pourrez sur la page suivante définir l'ordre de priorité des contraintes optionnelles, telles que les préférences des professeurs, par exemple."

texte_page_resultats = "Sur cette page vous allez pouvoir visualiser les résultats de l'emploi du temps généré, ainsi que les statistiques associées."
texte_stats = "Dans cette section, vous trouverez les statistiques de complétion de l'emploi du temps généré par l'outil."
texte_page_resultats = "Sur cette page vous allez pouvoir visualiser les résultats de l'emploi du temps généré, ainsi que les statistiques associées."
texte_page_resultats_2 = "Statistiques de complétion : Visualisation les performances de l'emploi du temps à travers des indicateurs clés (volume horaire, contraintes obligatoires et optionnelles, taux global de respect) et un tableau détaillé des contraintes, avec une section repliable pour les détails des violations."
texte_page_resultats_3 = "Gestion des emplois du temps : Interaction avec les emplois du temps des semaines A et B, en sélectionnant une vue par classe, professeur ou salle. Modifier, déplacer ou exporter les créneaux horaires en PDF via l'interface."
