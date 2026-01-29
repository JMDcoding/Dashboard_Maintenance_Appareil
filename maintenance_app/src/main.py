"""
Module principal - Interface/Déclencheur.
Affiche les résultats des analyses de maintenance.
"""

import sys
from pathlib import Path

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from db_connection import init_database, database_exists, DatabaseConnection
from data_access import (
    TechnicienDAO, EquipementDAO, InterventionDAO,
    StatistiquesDAO, IndicateursDAO
)
from business_logic import MaintenanceService


def print_separator(title: str = "", char: str = "=", width: int = 70):
    """Affiche un séparateur avec titre optionnel."""
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"\n{char * padding} {title} {char * padding}")
    else:
        print(char * width)


def print_table(headers: list, rows: list, col_widths: list = None):
    """Affiche un tableau formaté."""
    if not rows:
        print("  Aucune donnée")
        return

    if col_widths is None:
        col_widths = [max(len(str(h)), max(len(str(row[i])) for row in rows))
                      for i, h in enumerate(headers)]

    # En-têtes
    header_line = " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers))
    print(f"  {header_line}")
    print(f"  {'-' * len(header_line)}")

    # Lignes
    for row in rows:
        line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers)))
        print(f"  {line}")


def afficher_menu():
    """Affiche le menu principal."""
    print_separator("MENU PRINCIPAL")
    print("""
  1. Indicateurs globaux
  2. Équipements les plus sollicités
  3. Fréquence des interventions par type
  4. Coût par type d'équipement
  5. Taux de disponibilité (calcul Python)
  6. Indice de fiabilité (calcul Python)
  7. Tendance des coûts (calcul Python)
  8. Alertes de maintenance (calcul Python)
  9. Interventions par mois (2024)
  10. Performance des techniciens
  11. Historique d'un équipement
  12. Rapport de synthèse complet
  0. Quitter
""")


def afficher_indicateurs_globaux():
    """Affiche les indicateurs globaux."""
    print_separator("INDICATEURS GLOBAUX")

    cout_total = MaintenanceService.get_cout_total_maintenance()
    nb_interventions = MaintenanceService.get_nombre_interventions()
    duree_moyenne = MaintenanceService.get_duree_moyenne_intervention()

    print(f"""
  Coût total de maintenance     : {cout_total:,.2f} €
  Nombre total d'interventions  : {nb_interventions}
  Durée moyenne d'intervention  : {duree_moyenne:.1f} minutes ({duree_moyenne/60:.1f} heures)
""")


def afficher_equipements_sollicites():
    """Affiche les équipements les plus sollicités."""
    print_separator("ÉQUIPEMENTS LES PLUS SOLLICITÉS")

    equipements = MaintenanceService.get_equipements_plus_sollicites(10)

    headers = ["Équipement", "Type", "Nb Interv.", "Coût Total", "Durée (min)"]
    rows = [
        (eq['nom'][:25], eq['type'], eq['nombre_interventions'],
         f"{eq['cout_total']:.2f}€", eq['duree_totale'])
        for eq in equipements
    ]
    print_table(headers, rows, [25, 18, 10, 12, 12])


def afficher_frequence_par_type():
    """Affiche la fréquence des interventions par type."""
    print_separator("FRÉQUENCE DES INTERVENTIONS PAR TYPE")

    frequences = MaintenanceService.get_frequence_par_type()

    headers = ["Type", "Nombre", "Coût Total", "Coût Moyen", "Durée Moy."]
    rows = [
        (f['type_intervention'], f['nombre'], f"{f['cout_total']:.2f}€",
         f"{f['cout_moyen']:.2f}€", f"{f['duree_moyenne']:.0f} min")
        for f in frequences
    ]
    print_table(headers, rows, [15, 8, 12, 12, 12])


def afficher_cout_par_type_equipement():
    """Affiche le coût par type d'équipement."""
    print_separator("COÛT DE MAINTENANCE PAR TYPE D'ÉQUIPEMENT")

    couts = IndicateursDAO.get_cout_par_type_equipement()

    headers = ["Type Équipement", "Nb Équip.", "Nb Interv.", "Coût Total", "Coût Moy."]
    rows = [
        (c['type'], c['nombre_equipements'], c['nombre_interventions'],
         f"{c['cout_total'] or 0:.2f}€", f"{c['cout_moyen_intervention'] or 0:.2f}€")
        for c in couts
    ]
    print_table(headers, rows, [20, 10, 10, 12, 12])


def afficher_taux_disponibilite():
    """Affiche le taux de disponibilité (calculé en Python)."""
    print_separator("TAUX DE DISPONIBILITÉ PAR TYPE (Calcul Python)")

    taux = MaintenanceService.calculer_taux_disponibilite_equipements()

    print("\n  [Indicateur calculé côté Python, pas en SQL]")
    print()

    for type_eq, pourcentage in taux.items():
        barre = "█" * int(pourcentage / 5) + "░" * (20 - int(pourcentage / 5))
        print(f"  {type_eq:22} : {barre} {pourcentage:.1f}%")
    print()


def afficher_indice_fiabilite():
    """Affiche l'indice de fiabilité (calculé en Python)."""
    print_separator("INDICE DE FIABILITÉ DES ÉQUIPEMENTS (Calcul Python)")

    fiabilite = MaintenanceService.calculer_indice_fiabilite_equipements()

    print("\n  [Indicateur calculé côté Python: score basé sur pannes, coûts et âge]")
    print()

    headers = ["Équipement", "Type", "Âge", "Pannes", "Coût", "Indice"]
    rows = [
        (f['nom'][:22], f['type'][:15], f"{f['age_annees']}a",
         f['nb_pannes'], f"{f['cout_total']:.0f}€", f"{f['indice_fiabilite']}/100")
        for f in fiabilite
    ]
    print_table(headers, rows, [22, 15, 5, 7, 10, 8])


def afficher_tendance_couts():
    """Affiche la tendance des coûts (calculée en Python)."""
    print_separator("TENDANCE DES COÛTS 2024 (Calcul Python)")

    tendance = MaintenanceService.calculer_tendance_couts(2024)

    print("\n  [Indicateur calculé côté Python: analyse semestrielle]")
    print(f"""
  Tendance globale    : {tendance['tendance'].upper()}
  Variation S1 → S2   : {tendance['variation_pct']:+.1f}%
  Coût 1er semestre   : {tendance.get('cout_s1', 0):,.2f} €
  Coût 2nd semestre   : {tendance.get('cout_s2', 0):,.2f} €
""")

    print("  Détail par mois:")
    noms_mois = ['', 'Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

    for mois, cout in tendance['detail_mois'].items():
        barre = "█" * int(cout / 50) if cout > 0 else ""
        print(f"    {noms_mois[mois]:3} : {barre} {cout:.0f}€")
    print()


def afficher_alertes():
    """Affiche les alertes de maintenance (calculées en Python)."""
    print_separator("ALERTES DE MAINTENANCE (Calcul Python)")

    alertes = MaintenanceService.generer_alertes_maintenance()

    print("\n  [Alertes générées par analyse Python des données]")
    print()

    if not alertes:
        print("  Aucune alerte")
        return

    # Grouper par niveau
    for niveau in ['CRITIQUE', 'ATTENTION', 'INFO']:
        alertes_niveau = [a for a in alertes if a['niveau'] == niveau]
        if alertes_niveau:
            symbole = {'CRITIQUE': '[!]', 'ATTENTION': '[*]', 'INFO': '[i]'}[niveau]
            print(f"  {symbole} {niveau}:")
            for alerte in alertes_niveau:
                print(f"     • {alerte['equipement']}: {alerte['message']}")
            print()


def afficher_interventions_par_mois():
    """Affiche les interventions par mois."""
    print_separator("INTERVENTIONS PAR MOIS (2024)")

    interventions = IndicateursDAO.get_interventions_par_mois(2024)

    noms_mois = {
        '01': 'Janvier', '02': 'Février', '03': 'Mars', '04': 'Avril',
        '05': 'Mai', '06': 'Juin', '07': 'Juillet', '08': 'Août',
        '09': 'Septembre', '10': 'Octobre', '11': 'Novembre', '12': 'Décembre'
    }

    headers = ["Mois", "Nb Interv.", "Coût Total", "Durée Totale"]
    rows = [
        (noms_mois.get(i['mois'], i['mois']), i['nombre_interventions'],
         f"{i['cout_total']:.2f}€", f"{i['duree_totale']} min")
        for i in interventions
    ]
    print_table(headers, rows, [12, 12, 12, 14])


def afficher_performance_techniciens():
    """Affiche la performance des techniciens."""
    print_separator("PERFORMANCE DES TECHNICIENS")

    perf = IndicateursDAO.get_performance_techniciens()

    headers = ["Technicien", "Spécialité", "Nb Interv.", "Temps Total", "Valeur"]
    rows = [
        (p['technicien'], p['specialite'][:12], p['nombre_interventions'],
         f"{p['temps_total'] or 0} min", f"{p['valeur_interventions'] or 0:.0f}€")
        for p in perf
    ]
    print_table(headers, rows, [20, 12, 10, 12, 10])


def afficher_historique_equipement():
    """Affiche l'historique d'un équipement spécifique."""
    print_separator("HISTORIQUE D'UN ÉQUIPEMENT")

    # Lister les équipements disponibles
    equipements = EquipementDAO.get_all()
    print("\n  Équipements disponibles:")
    for eq in equipements:
        print(f"    {eq['id']:2}. {eq['nom']} ({eq['type']})")

    try:
        choix = input("\n  Numéro de l'équipement (ou 0 pour annuler): ")
        eq_id = int(choix)

        if eq_id == 0:
            return

        equipement = EquipementDAO.get_by_id(eq_id)
        if not equipement:
            print("  Équipement non trouvé")
            return

        print(f"\n  Historique de: {equipement['nom']}")
        print(f"  Type: {equipement['type']} | Localisation: {equipement['localisation']}")
        print(f"  Statut actuel: {equipement['statut']}")

        historique = IndicateursDAO.get_historique_equipement(eq_id)

        if historique:
            headers = ["Date", "Type", "Description", "Durée", "Coût", "Technicien"]
            rows = [
                (h['date_intervention'], h['type_intervention'][:10],
                 h['description'][:25], f"{h['duree_minutes']}m",
                 f"{h['cout']:.0f}€", h['technicien'][:15])
                for h in historique
            ]
            print()
            print_table(headers, rows, [12, 10, 25, 6, 8, 15])
        else:
            print("  Aucune intervention enregistrée")

    except ValueError:
        print("  Entrée invalide")


def afficher_rapport_synthese():
    """Affiche le rapport de synthèse complet."""
    print_separator("RAPPORT DE SYNTHÈSE COMPLET", "=", 70)

    rapport = MaintenanceService.generer_rapport_synthese()

    # Indicateurs globaux
    print("\n  INDICATEURS GLOBAUX")
    print("  " + "-" * 40)
    ig = rapport['indicateurs_globaux']
    print(f"    Coût total        : {ig['cout_total']:,.2f} €")
    print(f"    Interventions     : {ig['nombre_interventions']}")
    print(f"    Durée moyenne     : {ig['duree_moyenne_minutes']:.1f} min")

    # Taux de disponibilité
    print("\n  TAUX DE DISPONIBILITÉ")
    print("  " + "-" * 40)
    for type_eq, taux in rapport['taux_disponibilite'].items():
        print(f"    {type_eq:22} : {taux:.1f}%")

    # Tendance
    print("\n  TENDANCE DES COÛTS")
    print("  " + "-" * 40)
    tend = rapport['tendance_couts']
    print(f"    Tendance  : {tend['tendance'].upper()}")
    print(f"    Variation : {tend['variation_pct']:+.1f}%")

    # Top équipements
    print("\n  TOP 5 ÉQUIPEMENTS SOLLICITÉS")
    print("  " + "-" * 40)
    for i, eq in enumerate(rapport['top_equipements_sollicites'][:5], 1):
        print(f"    {i}. {eq['nom'][:25]} - {eq['nombre_interventions']} interv. ({eq['cout_total']:.0f}€)")

    # Alertes
    print("\n  ALERTES")
    print("  " + "-" * 40)
    alertes_critiques = [a for a in rapport['alertes'] if a['niveau'] == 'CRITIQUE']
    if alertes_critiques:
        for a in alertes_critiques[:3]:
            print(f"    [!] {a['equipement']}: {a['message'][:45]}")
    else:
        print("    Aucune alerte critique")

    print()


def main():
    """Point d'entrée principal de l'application."""
    print_separator("APPLICATION DE SUIVI DE MAINTENANCE", "=", 70)
    print("        Gestion du parc matériel et indicateurs de fiabilité")

    # Vérifier/initialiser la base de données
    if not database_exists():
        print("\n  Base de données non trouvée. Initialisation...")
        init_database()
        print("  Base de données initialisée avec les données de test.")
    else:
        print("\n  Base de données connectée.")

    # Boucle principale
    while True:
        afficher_menu()

        try:
            choix = input("  Votre choix: ").strip()

            if choix == '0':
                print("\n  Au revoir!")
                DatabaseConnection().close()
                break
            elif choix == '1':
                afficher_indicateurs_globaux()
            elif choix == '2':
                afficher_equipements_sollicites()
            elif choix == '3':
                afficher_frequence_par_type()
            elif choix == '4':
                afficher_cout_par_type_equipement()
            elif choix == '5':
                afficher_taux_disponibilite()
            elif choix == '6':
                afficher_indice_fiabilite()
            elif choix == '7':
                afficher_tendance_couts()
            elif choix == '8':
                afficher_alertes()
            elif choix == '9':
                afficher_interventions_par_mois()
            elif choix == '10':
                afficher_performance_techniciens()
            elif choix == '11':
                afficher_historique_equipement()
            elif choix == '12':
                afficher_rapport_synthese()
            else:
                print("  Choix invalide")

            input("\n  Appuyez sur Entrée pour continuer...")

        except KeyboardInterrupt:
            print("\n\n  Interruption. Au revoir!")
            DatabaseConnection().close()
            break
        except Exception as e:
            print(f"\n  Erreur: {e}")
            input("\n  Appuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    main()
