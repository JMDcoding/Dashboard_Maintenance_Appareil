"""
Module d'accès aux données (DAO - Data Access Object).
Contient toutes les requêtes SQL organisées par niveau de complexité.
Toutes les requêtes utilisent des paramètres (jamais de f-string).
"""

from typing import List, Dict, Any, Optional
from db_connection import get_db_cursor


# =============================================================================
# NIVEAU 1 : INSERT, SELECT avec WHERE
# =============================================================================

class TechnicienDAO:
    """Accès aux données des techniciens."""

    @staticmethod
    def get_all() -> List[Dict]:
        """Récupère tous les techniciens."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM techniciens ORDER BY nom, prenom")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(technicien_id: int) -> Optional[Dict]:
        """Récupère un technicien par son ID."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM techniciens WHERE id = ?",
                (technicien_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_by_specialite(specialite: str) -> List[Dict]:
        """Récupère les techniciens par spécialité (Niveau 1: SELECT WHERE)."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM techniciens WHERE specialite = ? ORDER BY nom",
                (specialite,)
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def insert(nom: str, prenom: str, specialite: str, email: str, date_embauche: str) -> int:
        """Insère un nouveau technicien (Niveau 1: INSERT)."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """INSERT INTO techniciens (nom, prenom, specialite, email, date_embauche)
                   VALUES (?, ?, ?, ?, ?)""",
                (nom, prenom, specialite, email, date_embauche)
            )
            return cursor.lastrowid


class EquipementDAO:
    """Accès aux données des équipements."""

    @staticmethod
    def get_all() -> List[Dict]:
        """Récupère tous les équipements."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM equipements ORDER BY nom")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(equipement_id: int) -> Optional[Dict]:
        """Récupère un équipement par son ID."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM equipements WHERE id = ?",
                (equipement_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_by_type(type_equipement: str) -> List[Dict]:
        """Récupère les équipements par type (Niveau 1: SELECT WHERE)."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM equipements WHERE type = ? ORDER BY nom",
                (type_equipement,)
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_statut(statut: str) -> List[Dict]:
        """Récupère les équipements par statut (Niveau 1: SELECT WHERE)."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM equipements WHERE statut = ? ORDER BY nom",
                (statut,)
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def insert(nom: str, type_eq: str, marque: str, modele: str,
               numero_serie: str, date_acquisition: str, localisation: str, heures_utilisation: int = 0) -> int:
        """Insère un nouvel équipement (Niveau 1: INSERT)."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """INSERT INTO equipements
                   (nom, type, marque, modele, numero_serie, date_acquisition, localisation, heures_utilisation)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (nom, type_eq, marque, modele, numero_serie, date_acquisition, localisation, heures_utilisation)
            )
            return cursor.lastrowid

    @staticmethod
    def update_heures(equipement_id: int, heures: int):
        """Met à jour le nombre d'heures d'utilisation d'un équipement."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "UPDATE equipements SET heures_utilisation = ? WHERE id = ?",
                (heures, equipement_id)
            )

    @staticmethod
    def update_statut(equipement_id: int, nouveau_statut: str):
        """Met à jour le statut d'un équipement."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "UPDATE equipements SET statut = ? WHERE id = ?",
                (nouveau_statut, equipement_id)
            )


class InterventionDAO:
    """Accès aux données des interventions."""

    @staticmethod
    def get_all() -> List[Dict]:
        """Récupère toutes les interventions."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM interventions ORDER BY date_intervention DESC"
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(intervention_id: int) -> Optional[Dict]:
        """Récupère une intervention par son ID."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM interventions WHERE id = ?",
                (intervention_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_by_type(type_intervention: str) -> List[Dict]:
        """Récupère les interventions par type (Niveau 1: SELECT WHERE)."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM interventions WHERE type_intervention = ? ORDER BY date_intervention DESC",
                (type_intervention,)
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def insert(equipement_id: int, technicien_id: int, date_intervention: str,
               type_intervention: str, description: str, duree_minutes: int,
               cout: float, statut: str = 'terminee') -> int:
        """Insère une nouvelle intervention (Niveau 1: INSERT)."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """INSERT INTO interventions
                   (equipement_id, technicien_id, date_intervention, type_intervention,
                    description, duree_minutes, cout, statut)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (equipement_id, technicien_id, date_intervention, type_intervention,
                 description, duree_minutes, cout, statut)
            )
            return cursor.lastrowid


# =============================================================================
# NIVEAU 2 : Jointures, Agrégats (SUM, COUNT, AVG)
# =============================================================================

class StatistiquesDAO:
    """Requêtes statistiques avec jointures et agrégats."""

    @staticmethod
    def get_cout_total_maintenance() -> float:
        """Calcule le coût total de maintenance (Niveau 2: SUM)."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT SUM(cout) as total FROM interventions WHERE statut = 'terminee'"
            )
            result = cursor.fetchone()
            return result['total'] if result['total'] else 0.0

    @staticmethod
    def get_nombre_interventions() -> int:
        """Compte le nombre total d'interventions (Niveau 2: COUNT)."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM interventions")
            return cursor.fetchone()['count']

    @staticmethod
    def get_duree_moyenne_intervention() -> float:
        """Calcule la durée moyenne des interventions en minutes (Niveau 2: AVG)."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT AVG(duree_minutes) as moyenne FROM interventions WHERE statut = 'terminee'"
            )
            result = cursor.fetchone()
            return round(result['moyenne'], 2) if result['moyenne'] else 0.0

    @staticmethod
    def get_interventions_avec_details() -> List[Dict]:
        """
        Récupère les interventions avec les détails des équipements et techniciens.
        (Niveau 2: Jointures multiples)
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    i.id,
                    i.date_intervention,
                    i.type_intervention,
                    i.description,
                    i.duree_minutes,
                    i.cout,
                    i.statut,
                    e.nom as equipement_nom,
                    e.type as equipement_type,
                    e.localisation,
                    t.nom as technicien_nom,
                    t.prenom as technicien_prenom,
                    t.specialite
                FROM interventions i
                INNER JOIN equipements e ON i.equipement_id = e.id
                INNER JOIN techniciens t ON i.technicien_id = t.id
                ORDER BY i.date_intervention DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_interventions_par_technicien() -> List[Dict]:
        """
        Compte les interventions par technicien.
        (Niveau 2: Jointure + COUNT)
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    t.id,
                    t.nom,
                    t.prenom,
                    t.specialite,
                    COUNT(i.id) as nombre_interventions,
                    SUM(i.cout) as cout_total
                FROM techniciens t
                LEFT JOIN interventions i ON t.id = i.technicien_id
                GROUP BY t.id
                ORDER BY nombre_interventions DESC
            """)
            return [dict(row) for row in cursor.fetchall()]


# =============================================================================
# NIVEAU 3 : GROUP BY, Indicateurs métier, Conditions combinées
# =============================================================================

class IndicateursDAO:
    """Requêtes avancées pour les indicateurs métier."""

    @staticmethod
    def get_equipements_plus_sollicites(limit: int = 5) -> List[Dict]:
        """
        Identifie les équipements les plus sollicités.
        (Niveau 3: GROUP BY + ORDER BY + LIMIT + Jointure)
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    e.id,
                    e.nom,
                    e.type,
                    e.localisation,
                    COUNT(i.id) as nombre_interventions,
                    SUM(i.cout) as cout_total,
                    SUM(i.duree_minutes) as duree_totale
                FROM equipements e
                LEFT JOIN interventions i ON e.id = i.equipement_id
                GROUP BY e.id
                HAVING COUNT(i.id) > 0
                ORDER BY nombre_interventions DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_frequence_interventions_par_type() -> List[Dict]:
        """
        Analyse la fréquence des interventions par type.
        (Niveau 3: GROUP BY avec agrégats multiples)
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    type_intervention,
                    COUNT(*) as nombre,
                    SUM(cout) as cout_total,
                    AVG(cout) as cout_moyen,
                    AVG(duree_minutes) as duree_moyenne
                FROM interventions
                WHERE statut = 'terminee'
                GROUP BY type_intervention
                ORDER BY nombre DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_cout_par_type_equipement() -> List[Dict]:
        """
        Calcule le coût de maintenance par type d'équipement.
        (Niveau 3: GROUP BY + Jointure + SUM)
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    e.type,
                    COUNT(DISTINCT e.id) as nombre_equipements,
                    COUNT(i.id) as nombre_interventions,
                    SUM(i.cout) as cout_total,
                    AVG(i.cout) as cout_moyen_intervention
                FROM equipements e
                LEFT JOIN interventions i ON e.id = i.equipement_id AND i.statut = 'terminee'
                GROUP BY e.type
                ORDER BY cout_total DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_interventions_par_mois(annee: int) -> List[Dict]:
        """
        Analyse les interventions par mois pour une année donnée.
        (Niveau 3: GROUP BY avec extraction de date + conditions)
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    strftime('%m', date_intervention) as mois,
                    COUNT(*) as nombre_interventions,
                    SUM(cout) as cout_total,
                    SUM(duree_minutes) as duree_totale
                FROM interventions
                WHERE strftime('%Y', date_intervention) = ?
                  AND statut = 'terminee'
                GROUP BY strftime('%m', date_intervention)
                ORDER BY mois
            """, (str(annee),))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_equipements_critiques(seuil_interventions: int = 3, seuil_cout: float = 500) -> List[Dict]:
        """
        Identifie les équipements critiques (beaucoup d'interventions OU coût élevé).
        (Niveau 3: Conditions combinées avec OR + HAVING)
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    e.id,
                    e.nom,
                    e.type,
                    e.date_acquisition,
                    e.statut,
                    COUNT(i.id) as nombre_interventions,
                    SUM(i.cout) as cout_total,
                    MAX(i.date_intervention) as derniere_intervention
                FROM equipements e
                INNER JOIN interventions i ON e.id = i.equipement_id
                WHERE i.statut = 'terminee'
                GROUP BY e.id
                HAVING COUNT(i.id) >= ? OR SUM(i.cout) >= ?
                ORDER BY cout_total DESC
            """, (seuil_interventions, seuil_cout))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_performance_techniciens() -> List[Dict]:
        """
        Évalue la performance des techniciens.
        (Niveau 3: Agrégats multiples + GROUP BY)
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    t.id,
                    t.nom || ' ' || t.prenom as technicien,
                    t.specialite,
                    COUNT(i.id) as nombre_interventions,
                    SUM(i.duree_minutes) as temps_total,
                    AVG(i.duree_minutes) as temps_moyen,
                    SUM(i.cout) as valeur_interventions,
                    COUNT(DISTINCT i.equipement_id) as equipements_traites
                FROM techniciens t
                LEFT JOIN interventions i ON t.id = i.technicien_id AND i.statut = 'terminee'
                GROUP BY t.id
                ORDER BY nombre_interventions DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_historique_equipement(equipement_id: int) -> List[Dict]:
        """
        Récupère l'historique complet d'un équipement.
        (Niveau 3: Jointure + WHERE + ORDER BY)
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    i.date_intervention,
                    i.type_intervention,
                    i.description,
                    i.duree_minutes,
                    i.cout,
                    i.statut,
                    t.nom || ' ' || t.prenom as technicien
                FROM interventions i
                INNER JOIN techniciens t ON i.technicien_id = t.id
                WHERE i.equipement_id = ?
                ORDER BY i.date_intervention DESC
            """, (equipement_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_all_interventions_raw() -> List[Dict]:
        """
        Récupère toutes les interventions brutes pour calculs Python.
        Utilisé par la couche métier pour les calculs côté Python.
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    i.*,
                    e.nom as equipement_nom,
                    e.type as equipement_type
                FROM interventions i
                INNER JOIN equipements e ON i.equipement_id = e.id
                WHERE i.statut = 'terminee'
                ORDER BY i.date_intervention
            """)
            return [dict(row) for row in cursor.fetchall()]


# =============================================================================
# NOUVEAUX MODULES (Users, Stocks, Filtres)
# =============================================================================

class UserDAO:
    """Gestion des utilisateurs."""

    @staticmethod
    def get_by_username(username: str) -> Optional[Dict]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM utilisateurs WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None

class PieceDAO:
    """Gestion des pièces détachées."""

    @staticmethod
    def get_all() -> List[Dict]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM pieces_detachees ORDER BY nom")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_alertes_stock() -> List[Dict]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM pieces_detachees WHERE quantite_stock <= seuil_alerte")
            return [dict(row) for row in cursor.fetchall()]
            
    @staticmethod
    def update_stock(piece_id: int, quantite_change: int):
        with get_db_cursor() as cursor:
            cursor.execute(
                "UPDATE pieces_detachees SET quantite_stock = quantite_stock + ? WHERE id = ?",
                (quantite_change, piece_id)
            )

    @staticmethod
    def insert(nom: str, reference: str, quantite: int, seuil: int, cout: float):
        with get_db_cursor() as cursor:
            cursor.execute(
                """INSERT INTO pieces_detachees (nom, reference, quantite_stock, seuil_alerte, cout_unitaire)
                   VALUES (?, ?, ?, ?, ?)""",
                (nom, reference, quantite, seuil, cout)
            )

class PieceUtiliseeDAO:
    """Gestion des pièces utilisées dans les interventions."""
    
    @staticmethod
    def add_piece_to_intervention(intervention_id: int, piece_id: int, quantite: int):
        with get_db_cursor() as cursor:
            # 1. Enregistrer l'utilisation
            cursor.execute(
                "INSERT INTO pieces_utilisees (intervention_id, piece_id, quantite) VALUES (?, ?, ?)",
                (intervention_id, piece_id, quantite)
            )
            # 2. Décrémenter le stock
            cursor.execute(
                "UPDATE pieces_detachees SET quantite_stock = quantite_stock - ? WHERE id = ?",
                (quantite, piece_id)
            )

    @staticmethod
    def get_by_intervention(intervention_id: int) -> List[Dict]:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT p.nom, p.reference, u.quantite, p.cout_unitaire
                FROM pieces_utilisees u
                JOIN pieces_detachees p ON u.piece_id = p.id
                WHERE u.intervention_id = ?
            """, (intervention_id,))
            return [dict(row) for row in cursor.fetchall()]

class InterventionFiltreDAO:
    """Recherche avancée d'interventions."""
    
    @staticmethod
    def search(technicien_id: int = None, type_inter: str = None, 
               date_debut: str = None, date_fin: str = None) -> List[Dict]:
        query = """
            SELECT i.*, e.nom as equipement_nom, t.nom as technicien_nom, t.prenom as technicien_prenom
            FROM interventions i
            JOIN equipements e ON i.equipement_id = e.id
            JOIN techniciens t ON i.technicien_id = t.id
            WHERE 1=1
        """
        params = []
        
        if technicien_id:
            query += " AND i.technicien_id = ?"
            params.append(technicien_id)
        if type_inter:
            query += " AND i.type_intervention = ?"
            params.append(type_inter)
        if date_debut:
            query += " AND i.date_intervention >= ?"
            params.append(date_debut)
        if date_fin:
            query += " AND i.date_intervention <= ?"
            params.append(date_fin)
            
        query += " ORDER BY i.date_intervention DESC"
        
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
