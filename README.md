# Application de Suivi de Maintenance

Application Python/SQLite pour le suivi et l'analyse de la maintenance d'un parc matériel.

## Structure du projet

```
maintenance_app/
├── database/
│   ├── schema.sql          # Script de création des tables et données de test
│   └── maintenance.db      # Base de données SQLite (générée à l'exécution)
├── src/
│   ├── db_connection.py    # Couche connexion et gestion des transactions
│   ├── data_access.py      # Couche DAO (Data Access Object)
│   ├── business_logic.py   # Couche logique métier
│   └── main.py             # Interface/Déclencheur
└── README.md
```

## Installation et exécution

```bash
cd maintenance_app/src
python main.py
```

La base de données est initialisée automatiquement au premier lancement.

## Choix techniques

### 1. Modèle relationnel (SQLite)

**Tables créées :**

- `techniciens` : Informations sur les techniciens de maintenance
- `equipements` : Parc matériel à maintenir
- `interventions` : Historique des interventions (table de liaison)

**Relations :**

- `interventions.equipement_id` → `equipements.id` (FK)
- `interventions.technicien_id` → `techniciens.id` (FK)

**Contraintes :**

- Clés primaires auto-incrémentées
- Clés étrangères avec `ON DELETE RESTRICT`
- Contraintes `CHECK` pour valider les types et statuts
- Contraintes `UNIQUE` sur numéro de série et email
- Index sur les colonnes fréquemment interrogées

### 2. Architecture en 3 couches

| Couche | Fichier | Responsabilité |
|--------|---------|----------------|
| **Interface** | `main.py` | Interaction utilisateur, affichage des résultats |
| **Métier** | `business_logic.py` | Calculs, indicateurs, règles métier |
| **Accès données** | `data_access.py` | Requêtes SQL, pattern DAO |
| **Infrastructure** | `db_connection.py` | Connexion, transactions, context managers |

### 3. Requêtes SQL par niveau

#### Niveau 1 : INSERT, SELECT avec WHERE

```python
# Exemple : Récupérer les équipements par type
cursor.execute(
    "SELECT * FROM equipements WHERE type = ? ORDER BY nom",
    (type_equipement,)
)
```

#### Niveau 2 : Jointures, Agrégats (SUM, COUNT, AVG)

```python
# Exemple : Interventions avec détails (jointures multiples)
cursor.execute("""
    SELECT i.*, e.nom as equipement_nom, t.nom as technicien_nom
    FROM interventions i
    INNER JOIN equipements e ON i.equipement_id = e.id
    INNER JOIN techniciens t ON i.technicien_id = t.id
""")
```

#### Niveau 3 : GROUP BY, Indicateurs, Conditions combinées

```python
# Exemple : Équipements critiques (GROUP BY + HAVING avec OR)
cursor.execute("""
    SELECT e.id, e.nom, COUNT(i.id) as nb_interventions, SUM(i.cout) as cout_total
    FROM equipements e
    INNER JOIN interventions i ON e.id = i.equipement_id
    GROUP BY e.id
    HAVING COUNT(i.id) >= ? OR SUM(i.cout) >= ?
""", (seuil_interventions, seuil_cout))
```

### 4. Sécurité des requêtes

**Toutes les requêtes utilisent des paramètres (`?`)** pour éviter les injections SQL :

```python
# ✅ CORRECT : Requête paramétrée
cursor.execute("SELECT * FROM techniciens WHERE id = ?", (technicien_id,))

# ❌ INTERDIT : f-string (vulnérable aux injections)
# cursor.execute(f"SELECT * FROM techniciens WHERE id = {technicien_id}")
```

### 5. Gestion des transactions

Utilisation de context managers pour garantir commit/rollback :

```python
@contextmanager
def get_db_cursor():
    db = DatabaseConnection()
    connection = db.get_connection()
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()      # Commit automatique si succès
    except Exception as e:
        connection.rollback()    # Rollback automatique si erreur
        raise e
```

### 6. Indicateurs calculés côté Python

Conformément aux exigences, plusieurs indicateurs sont calculés en Python (pas en SQL) :

| Indicateur | Description | Méthode |
|------------|-------------|---------|
| **Taux de disponibilité** | % d'équipements actifs par type | `calculer_taux_disponibilite_equipements()` |
| **MTBF** | Temps moyen entre pannes | `calculer_mtbf()` |
| **Tendance des coûts** | Analyse S1 vs S2 avec variation % | `calculer_tendance_couts()` |
| **Indice de fiabilité** | Score 0-100 basé sur pannes, coûts, âge | `calculer_indice_fiabilite_equipements()` |
| **Alertes maintenance** | Détection équipements problématiques | `generer_alertes_maintenance()` |

**Exemple de calcul Python (Indice de fiabilité) :**

```python
def calculer_indice_fiabilite_equipements():
    equipements = EquipementDAO.get_all()
    interventions = IndicateursDAO.get_all_interventions_raw()

    for eq in equipements:
        score = 100
        score -= nb_correctives * 15        # Pénalité pannes
        score -= (cout_total // 500) * 10   # Pénalité coût
        if age_annees < 2: score += 10      # Bonus récent
        elif age_annees > 5: score -= 10    # Pénalité ancien
        score = max(0, min(100, score))     # Normalisation
```

## Données de test

Le fichier `schema.sql` inclut :

- **5 techniciens** avec différentes spécialités
- **10 équipements** (ordinateurs, machines, équipements techniques)
- **29 interventions** réparties sur 2024 (préventives, correctives, installations, mises à jour)

## Analyses disponibles

1. **Indicateurs globaux** : Coût total, nombre d'interventions, durée moyenne
2. **Équipements sollicités** : Classement par nombre d'interventions
3. **Fréquence par type** : Répartition préventif/correctif/etc.
4. **Coût par type d'équipement** : Analyse par catégorie
5. **Taux de disponibilité** : Équipements opérationnels vs en panne
6. **Indice de fiabilité** : Score de fiabilité par équipement
7. **Tendance des coûts** : Évolution sur l'année
8. **Alertes** : Détection proactive des problèmes
9. **Interventions mensuelles** : Répartition temporelle
10. **Performance techniciens** : Activité et valeur générée
11. **Historique équipement** : Détail par équipement
12. **Rapport de synthèse** : Vue consolidée

## Technologies utilisées

- **Python 3.x** : Langage principal
- **SQLite 3** : Base de données embarquée
- **sqlite3** : Driver Python natif (pas de dépendance externe)
