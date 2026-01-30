"""
Script d'automatisation pour la génération de rapports hebdomadaires.
Ce script peut être planifié (cron/Task Scheduler) pour s'exécuter automatiquement.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import csv

# Ajouter le répertoire src au path pour les imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from business_logic import MaintenanceService
from data_access import InterventionDAO, StatistiquesDAO

def generer_rapport_hebdo():
    """Génère un rapport CSV des activités de la semaine écoulée."""
    print("Début de la génération du rapport hebdomadaire...")
    
    date_fin = datetime.now()
    date_debut = date_fin - timedelta(days=7)
    
    # Récupérer les données
    stats_globales = MaintenanceService.generer_rapport_synthese()
    kpis = MaintenanceService.calculer_kpis_avances()
    
    # Nom du fichier avec timestamp
    filename = f"rapport_hebdo_{date_fin.strftime('%Y%m%d')}.csv"
    filepath = PROJECT_ROOT / "reports" / filename
    
    # Créer le dossier reports s'il n'existe pas
    filepath.parent.mkdir(exist_ok=True)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # En-tête Rapport
        writer.writerow(["RAPPORT HEBDOMADAIRE MAINTENANCE", f"Semaine du {date_debut.date()} au {date_fin.date()}"])
        writer.writerow([])
        
        # Section 1: Indicateurs Globaux
        writer.writerow(["INDICATEURS GLOBAUX"])
        ig = stats_globales['indicateurs_globaux']
        writer.writerow(["Coût Total Maintenance", f"{ig['cout_total']} EUR"])
        writer.writerow(["Nombre Interventions", ig['nombre_interventions']])
        writer.writerow(["Durée Moyenne", f"{ig['duree_moyenne_minutes']} min"])
        writer.writerow([])
        
        # Section 2: KPIs Avancés
        writer.writerow(["PERFORMANCE & FIABILITÉ"])
        writer.writerow(["Coût/Heure Fonctionnement", f"{kpis['cout_heure_moyen']} EUR/h"])
        writer.writerow(["Prévision Budget (6 mois)", f"{kpis['prevision_budget_6mois']} EUR"])
        writer.writerow([])
        
        # Section 3: Alertes en cours
        writer.writerow(["ALERTES ACTIVES"])
        alertes = stats_globales['alertes']
        if alertes:
            writer.writerow(["Niveau", "Équipement", "Message"])
            for a in alertes:
                writer.writerow([a['niveau'], a['equipement'], a['message']])
        else:
            writer.writerow(["Aucune alerte active"])
            
    print(f"Rapport généré avec succès : {filepath}")

if __name__ == "__main__":
    try:
        generer_rapport_hebdo()
    except Exception as e:
        print(f"Erreur lors de la génération du rapport: {e}", file=sys.stderr)
        sys.exit(1)
