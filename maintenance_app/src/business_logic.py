"""
Module de logique métier.
Contient les calculs et indicateurs métier, incluant des calculs côté Python.
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from data_access import (
    TechnicienDAO, EquipementDAO, InterventionDAO,
    StatistiquesDAO, IndicateursDAO,
    UserDAO, PieceDAO, PieceUtiliseeDAO, InterventionFiltreDAO
)
import csv
import io


class MaintenanceService:
    """Service métier pour la gestion de la maintenance."""

    @staticmethod
    def get_annee_reference() -> int:
        """Détermine l'année de référence (dernière année avec données ou année courante)."""
        annees = StatistiquesDAO.get_annees_disponibles()
        if annees:
            return int(annees[0])
        return datetime.now().year

    # =========================================================================
    # INDICATEURS SIMPLES (délégués au DAO)
    # =========================================================================

    @staticmethod
    def get_cout_total_maintenance() -> float:
        """Retourne le coût total de maintenance."""
        return StatistiquesDAO.get_cout_total_maintenance()

    @staticmethod
    def get_nombre_interventions() -> int:
        """Retourne le nombre total d'interventions."""
        return StatistiquesDAO.get_nombre_interventions()

    @staticmethod
    def get_duree_moyenne_intervention() -> float:
        """Retourne la durée moyenne des interventions (en minutes)."""
        return StatistiquesDAO.get_duree_moyenne_intervention()

    @staticmethod
    def get_equipements_plus_sollicites(limit: int = 5) -> List[Dict]:
        """Retourne les équipements les plus sollicités."""
        return IndicateursDAO.get_equipements_plus_sollicites(limit)

    @staticmethod
    def get_frequence_par_type() -> List[Dict]:
        """Retourne la fréquence des interventions par type."""
        return IndicateursDAO.get_frequence_interventions_par_type()

    # =========================================================================
    # INDICATEURS CALCULÉS CÔTÉ PYTHON (requis par le projet)
    # =========================================================================

    @staticmethod
    def calculer_taux_disponibilite_equipements() -> Dict[str, float]:
        """
        Calcule le taux de disponibilité par type d'équipement.
        INDICATEUR CALCULÉ CÔTÉ PYTHON

        Le taux est calculé comme:
        (Nombre équipements actifs / Nombre total équipements) * 100
        """
        equipements = EquipementDAO.get_all()

        if not equipements:
            return {}

        # Comptage par type et statut côté Python
        stats_par_type = defaultdict(lambda: {'total': 0, 'actifs': 0})

        for eq in equipements:
            type_eq = eq['type']
            stats_par_type[type_eq]['total'] += 1
            if eq['statut'] == 'actif':
                stats_par_type[type_eq]['actifs'] += 1

        # Calcul du taux de disponibilité
        taux = {}
        for type_eq, stats in stats_par_type.items():
            if stats['total'] > 0:
                taux[type_eq] = round((stats['actifs'] / stats['total']) * 100, 2)

        return taux

    @staticmethod
    def calculer_mtbf() -> Dict[str, float]:
        """
        Calcule le MTBF (Mean Time Between Failures) par équipement.
        INDICATEUR CALCULÉ CÔTÉ PYTHON

        MTBF = Temps total de fonctionnement / Nombre de pannes
        Ici simplifié: Jours entre première et dernière intervention / Nombre d'interventions correctives
        """
        interventions = IndicateursDAO.get_all_interventions_raw()

        if not interventions:
            return {}

        # Grouper les interventions par équipement
        interventions_par_equipement = defaultdict(list)
        for inter in interventions:
            interventions_par_equipement[inter['equipement_nom']].append(inter)

        mtbf_resultats = {}

        for equipement, inters in interventions_par_equipement.items():
            # Compter les interventions correctives (pannes)
            correctives = [i for i in inters if i['type_intervention'] == 'corrective']
            nb_pannes = len(correctives)

            if nb_pannes < 2:
                # Pas assez de données pour calculer un MTBF significatif
                mtbf_resultats[equipement] = None
                continue

            # Calculer la période entre première et dernière intervention
            dates = [datetime.strptime(i['date_intervention'], '%Y-%m-%d') for i in inters]
            periode_jours = (max(dates) - min(dates)).days

            if periode_jours > 0:
                # MTBF en jours
                mtbf_resultats[equipement] = round(periode_jours / nb_pannes, 1)
            else:
                mtbf_resultats[equipement] = None

        return mtbf_resultats

    @staticmethod
    def calculer_tendance_couts(annee: int = None) -> Dict[str, any]:
        """
        Analyse la tendance des coûts de maintenance sur l'année.
        INDICATEUR CALCULÉ CÔTÉ PYTHON

        Retourne: tendance (hausse/baisse/stable), variation en %, détail par mois
        """
        if annee is None:
            annee = MaintenanceService.get_annee_reference()

        interventions = IndicateursDAO.get_all_interventions_raw()

        # Filtrer par année et grouper par mois
        couts_par_mois = defaultdict(float)
        for inter in interventions:
            date_inter = datetime.strptime(inter['date_intervention'], '%Y-%m-%d')
            if date_inter.year == annee:
                mois = date_inter.month
                couts_par_mois[mois] += inter['cout']

        if len(couts_par_mois) < 2:
            return {
                'tendance': 'données insuffisantes',
                'variation_pct': 0,
                'detail_mois': dict(couts_par_mois)
            }

        # Calcul de la tendance (comparaison premier/second semestre)
        s1 = sum(couts_par_mois.get(m, 0) for m in range(1, 7))
        s2 = sum(couts_par_mois.get(m, 0) for m in range(7, 13))

        if s1 > 0:
            variation = ((s2 - s1) / s1) * 100
        else:
            variation = 100 if s2 > 0 else 0

        if variation > 10:
            tendance = 'hausse'
        elif variation < -10:
            tendance = 'baisse'
        else:
            tendance = 'stable'

        return {
            'tendance': tendance,
            'variation_pct': round(variation, 2),
            'cout_s1': round(s1, 2),
            'cout_s2': round(s2, 2),
            'detail_mois': {k: round(v, 2) for k, v in sorted(couts_par_mois.items())}
        }

    @staticmethod
    def calculer_indice_fiabilite_equipements() -> List[Dict]:
        """
        Calcule un indice de fiabilité pour chaque équipement.
        INDICATEUR CALCULÉ CÔTÉ PYTHON

        Indice basé sur:
        - Nombre d'interventions correctives (moins = mieux)
        - Coût moyen par intervention
        - Âge de l'équipement

        Score de 0 à 100 (100 = très fiable)
        """
        equipements = EquipementDAO.get_all()
        interventions = IndicateursDAO.get_all_interventions_raw()

        # Indexer les interventions par équipement
        inter_par_eq = defaultdict(list)
        for inter in interventions:
            inter_par_eq[inter['equipement_id']].append(inter)

        resultats = []
        date_reference = datetime.now()

        for eq in equipements:
            eq_id = eq['id']
            inters = inter_par_eq.get(eq_id, [])

            # Calcul des métriques
            nb_correctives = sum(1 for i in inters if i['type_intervention'] == 'corrective')
            cout_total = sum(i['cout'] for i in inters)
            nb_interventions = len(inters)

            # Âge en années
            date_acq = datetime.strptime(eq['date_acquisition'], '%Y-%m-%d')
            age_jours = (date_reference - date_acq).days
            age_annees = age_jours / 365

            # Calcul de l'indice (formule métier)
            # Base 100, pénalités pour pannes et coûts élevés
            score = 100

            # Pénalité pour interventions correctives (-15 points par panne)
            score -= nb_correctives * 15

            # Pénalité pour coût élevé (> 500€ = -10 points par tranche de 500€)
            score -= (cout_total // 500) * 10

            # Bonus pour équipement récent (< 2 ans = +10)
            if age_annees < 2:
                score += 10
            # Pénalité pour équipement ancien (> 5 ans = -10)
            elif age_annees > 5:
                score -= 10

            # Normaliser entre 0 et 100
            score = max(0, min(100, score))

            resultats.append({
                'equipement_id': eq_id,
                'nom': eq['nom'],
                'type': eq['type'],
                'age_annees': round(age_annees, 1),
                'nb_interventions': nb_interventions,
                'nb_pannes': nb_correctives,
                'cout_total': round(cout_total, 2),
                'indice_fiabilite': int(score)
            })

        # Trier par indice de fiabilité (plus fiable en premier)
        resultats.sort(key=lambda x: x['indice_fiabilite'], reverse=True)

        return resultats

    @staticmethod
    def generer_alertes_maintenance() -> List[Dict]:
        """
        Génère des alertes pour les équipements nécessitant une attention.
        INDICATEUR CALCULÉ CÔTÉ PYTHON

        Alertes basées sur:
        - Heures d'utilisation élevées (> 2000h)
        - Maintenance préventive programmée ou en retard
        - Équipements avec beaucoup de pannes récentes
        - Équipements sans maintenance depuis longtemps
        - Coûts anormalement élevés
        """
        equipements = EquipementDAO.get_all()
        interventions_terminees = IndicateursDAO.get_all_interventions_raw()
        toutes_interventions = StatistiquesDAO.get_interventions_avec_details()

        alertes = []
        date_reference = datetime.now()

        # --- 1. Alertes Maintenance Préventive Programmée ---
        for inter in toutes_interventions:
            if inter['type_intervention'] == 'preventive' and inter['statut'] == 'planifiee':
                try:
                    date_prevue = datetime.strptime(inter['date_intervention'], '%Y-%m-%d')
                    jours_restants = (date_prevue - date_reference).days + 1  # +1 pour inclure aujourd'hui

                    if 0 <= jours_restants <= 7:
                        alertes.append({
                            'equipement': inter['equipement_nom'],
                            'niveau': 'INFO',
                            'message': f"Maintenance préventive prévue le {inter['date_intervention']} (dans {jours_restants} jours)"
                        })
                    elif jours_restants < 0:
                        alertes.append({
                            'equipement': inter['equipement_nom'],
                            'niveau': 'ATTENTION',
                            'message': f"Maintenance préventive en retard de {abs(jours_restants)} jours (prévue le {inter['date_intervention']})"
                        })
                except ValueError:
                    pass

        # Indexer les interventions terminées par équipement pour les analyses historiques
        inter_par_eq = defaultdict(list)
        for inter in interventions_terminees:
            inter_par_eq[inter['equipement_id']].append(inter)

        for eq in equipements:
            # --- 2. Alerte Heures d'Utilisation ---
            heures = eq.get('heures_utilisation', 0)
            if heures and heures > 2000:
                alertes.append({
                    'equipement': eq['nom'],
                    'niveau': 'ATTENTION',
                    'message': f"Utilisation élevée: {heures} heures (> 2000h)"
                })

            eq_id = eq['id']
            inters = inter_par_eq.get(eq_id, [])

            if not inters:
                # Alerte: aucune intervention enregistrée
                alertes.append({
                    'equipement': eq['nom'],
                    'niveau': 'INFO',
                    'message': "Aucune intervention enregistrée - vérifier si maintenance préventive nécessaire"
                })
                continue

            # Dernière intervention
            dates = [datetime.strptime(i['date_intervention'], '%Y-%m-%d') for i in inters]
            derniere = max(dates)
            jours_depuis = (date_reference - derniere).days

            # Alerte si pas de maintenance depuis > 180 jours
            if jours_depuis > 180:
                alertes.append({
                    'equipement': eq['nom'],
                    'niveau': 'ATTENTION',
                    'message': f"Pas de maintenance depuis {jours_depuis} jours"
                })

            # Compter les pannes récentes (6 derniers mois)
            six_mois = date_reference - timedelta(days=180)
            pannes_recentes = sum(
                1 for i in inters
                if i['type_intervention'] == 'corrective'
                and datetime.strptime(i['date_intervention'], '%Y-%m-%d') >= six_mois
            )

            if pannes_recentes >= 2:
                alertes.append({
                    'equipement': eq['nom'],
                    'niveau': 'CRITIQUE',
                    'message': f"{pannes_recentes} pannes sur les 6 derniers mois - envisager remplacement"
                })

            # Coût total élevé
            cout_total = sum(i['cout'] for i in inters)
            if cout_total > 1000:
                alertes.append({
                    'equipement': eq['nom'],
                    'niveau': 'ATTENTION',
                    'message': f"Coût de maintenance élevé: {cout_total:.2f}€"
                })

        # Trier par niveau de criticité
        ordre_niveaux = {'CRITIQUE': 0, 'ATTENTION': 1, 'INFO': 2}
        alertes.sort(key=lambda x: ordre_niveaux.get(x['niveau'], 3))

        return alertes

    @staticmethod
    def calculer_kpis_avances() -> Dict:
        """
        Calcule les indicateurs avancés (KPIs).
        """
        # 1. Performance Techniciens (Efficacité)
        perf_techs = IndicateursDAO.get_performance_techniciens()
        techniciens_kpi = []
        for p in perf_techs:
            if p['nombre_interventions'] > 0:
                # Efficacité = Valeur produite / Temps (Ex: Euro par minute)
                # Ou Coût moyen par intervention
                cout_moyen = p['valeur_interventions'] / p['nombre_interventions']
                techniciens_kpi.append({
                    'technicien': p['technicien'],
                    'nb': p['nombre_interventions'],
                    'duree_moy': round(p['temps_moyen'], 1),
                    'cout_moy': round(cout_moyen, 2)
                })

        # 2. Ratio Correctif / Préventif
        freq = IndicateursDAO.get_frequence_interventions_par_type()
        total = sum(f['nombre'] for f in freq)
        correctif = next((f['nombre'] for f in freq if f['type_intervention'] == 'corrective'), 0)
        preventif = next((f['nombre'] for f in freq if f['type_intervention'] == 'preventive'), 0)
        
        ratio_cp = {
            'correctif_pct': round((correctif / total * 100), 1) if total > 0 else 0,
            'preventif_pct': round((preventif / total * 100), 1) if total > 0 else 0,
            'total_interventions': total
        }

        # 3. Coût par heure de fonctionnement (Global)
        equipements = EquipementDAO.get_all()
        interventions = IndicateursDAO.get_all_interventions_raw()
        
        # Ce calcul est approximatif car 'heures_utilisation' est un snapshot actuel
        # et le coût est historique.
        total_heures = sum(e.get('heures_utilisation', 0) for e in equipements)
        total_cout = sum(i['cout'] for i in interventions)
        
        cout_heure_moyen = round(total_cout / total_heures, 4) if total_heures > 0 else 0

        # 4. Simulation Budget (Basé sur moyenne mensuelle historique)
        # On regarde les 12 derniers mois
        current_year = MaintenanceService.get_annee_reference()
        couts_mensuels = IndicateursDAO.get_interventions_par_mois(current_year)
        if couts_mensuels:
            moyenne_mensuelle = sum(c['cout_total'] for c in couts_mensuels) / len(couts_mensuels)
        else:
            moyenne_mensuelle = 0
            
        prevision_6_mois = round(moyenne_mensuelle * 6, 2) * 1.1 # Marge 10%

        return {
            'techniciens': techniciens_kpi,
            'ratio_cp': ratio_cp,
            'cout_heure_moyen': cout_heure_moyen,
            'prevision_budget_6mois': prevision_6_mois,
            'mtbf': MaintenanceService.calculer_mtbf()
        }

    # =========================================================================
    # RAPPORTS COMPOSITES
    # =========================================================================

    @staticmethod
    def generer_rapport_synthese() -> Dict:
        """
        Génère un rapport de synthèse complet.
        Combine indicateurs SQL et calculs Python.
        """
        return {
            'indicateurs_globaux': {
                'cout_total': MaintenanceService.get_cout_total_maintenance(),
                'nombre_interventions': MaintenanceService.get_nombre_interventions(),
                'duree_moyenne_minutes': MaintenanceService.get_duree_moyenne_intervention(),
            },
            'taux_disponibilite': MaintenanceService.calculer_taux_disponibilite_equipements(),
            'tendance_couts': MaintenanceService.calculer_tendance_couts(),
            'top_equipements_sollicites': MaintenanceService.get_equipements_plus_sollicites(5),
            'frequence_par_type': MaintenanceService.get_frequence_par_type(),
            'alertes': MaintenanceService.generer_alertes_maintenance()
        }


class AuthService:
    """Service d'authentification."""
    
    @staticmethod
    def login(username, password):
        user = UserDAO.get_by_username(username)
        if user and user['password_hash'] == password: # WARNING: En prod, utiliser hashage
            return user
        return None

class StockService:
    """Service de gestion des stocks."""
    
    @staticmethod
    def get_stock_status():
        pieces = PieceDAO.get_all()
        alertes = PieceDAO.get_alertes_stock()
        return pieces, alertes

    @staticmethod
    def get_alertes_stock_message() -> List[str]:
        alertes = PieceDAO.get_alertes_stock()
        messages = []
        for p in alertes:
            messages.append(f"STOCK FAIBLE: {p['nom']} (Réf: {p['reference']}) - Reste: {p['quantite_stock']}")
        return messages

class ExportService:
    """Service d'export de données."""
    
    @staticmethod
    def export_interventions_csv(interventions: List[Dict]) -> str:
        output = io.StringIO()
        if not interventions:
            return ""
            
        # Filtrer keys pour un CSV propre
        fieldnames = ['id', 'date_intervention', 'type_intervention', 'description', 
                      'duree_minutes', 'cout', 'equipement_nom', 'technicien_nom', 'statut']
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(interventions)
        
        return output.getvalue()
