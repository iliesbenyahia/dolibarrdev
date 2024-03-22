**README**

# Utilitaire de Serveur de Développement Dolibarr

## Aperçu
Cet utilitaire simplifie la mise en place d'un serveur de développement pour Dolibarr, un logiciel ERP (Planification des ressources de l'entreprise) et CRM (Gestion de la relation client) open-source. Il permet aux développeurs de déployer rapidement un environnement serveur local pour tester, déboguer et développer des extensions ou des personnalisations Dolibarr.

## Qu'est-ce que Dolibarr ?
Dolibarr est un suite logicielle ERP et CRM open-source conçue pour les petites et moyennes entreprises (PME), les travailleurs indépendants et les associations. Il propose une gamme étendue de fonctionnalités incluant la comptabilité, la facturation, la gestion des stocks, le CRM, la gestion de projets, et plus encore. Dolibarr est hautement personnalisable, permettant aux utilisateurs d'étendre sa fonctionnalité à travers des modules et des développements sur mesure.

## Utilité ?
La configuration d'un environnement serveur de développement pour Dolibarr peut être fastidieuse et complexe. Cet utilitaire simplifie ce processus en automatisant la configuration d'un environnement de développement local adapté spécifiquement au développement Dolibarr.

## Statut du Projet
Cet utilitaire est pour l'instant abandonné. Le but de ce développement était de lancer des commandes depuis un terminal linux qui permettait de configurer la stack LAMP exécutant Dolibarr, et aussi d'automatiser la phase d'installation pour proposer un dolibarr vierge prêt à être utilisé pour du développement de modules externes.

## Détails techniques
Utilisation de python et du SDK docker pour lancer l'environnement d'exécution conteneurisé du serveur de développement. Utilisation de la librairie typer (https://typer.tiangolo.com/) pour construire un CLI. 


