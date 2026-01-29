"""
Module de connexion à la base de données SQLite.
Gère les connexions, les transactions (commit/rollback) et le context manager.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager


# Chemin vers la base de données (relatif au module)
DATABASE_PATH = Path(__file__).parent.parent / "database" / "maintenance.db"
SCHEMA_PATH = Path(__file__).parent.parent / "database" / "schema.sql"


class DatabaseConnection:
    """
    Gestionnaire de connexion à la base de données SQLite.
    Implémente le pattern Singleton pour une connexion unique.
    """

    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        """
        Retourne la connexion active ou en crée une nouvelle.
        Active les clés étrangères et configure le row_factory.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(DATABASE_PATH)
            # Activer les clés étrangères (désactivées par défaut dans SQLite)
            self._connection.execute("PRAGMA foreign_keys = ON")
            # Retourner les résultats sous forme de dictionnaires
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self):
        """Ferme la connexion à la base de données."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def commit(self):
        """Valide la transaction en cours."""
        if self._connection:
            self._connection.commit()

    def rollback(self):
        """Annule la transaction en cours."""
        if self._connection:
            self._connection.rollback()


@contextmanager
def get_db_cursor():
    """
    Context manager pour obtenir un curseur avec gestion automatique des transactions.

    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM techniciens")
            results = cursor.fetchall()

    En cas d'exception, effectue un rollback automatique.
    Sinon, effectue un commit automatique.
    """
    db = DatabaseConnection()
    connection = db.get_connection()
    cursor = connection.cursor()

    try:
        yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e


@contextmanager
def transaction():
    """
    Context manager pour une transaction explicite.

    Usage:
        with transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(...)
            cursor.execute(...)
        # Commit automatique si pas d'erreur
    """
    db = DatabaseConnection()
    connection = db.get_connection()

    try:
        yield connection
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e


def init_database():
    """
    Initialise la base de données en exécutant le script schema.sql.
    Crée les tables et insère les données de test.
    """
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Fichier schema.sql introuvable: {SCHEMA_PATH}")

    # Lire le script SQL
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Exécuter le script
    db = DatabaseConnection()
    connection = db.get_connection()

    try:
        connection.executescript(schema_sql)
        connection.commit()
        print(f"Base de données initialisée avec succès: {DATABASE_PATH}")
    except Exception as e:
        connection.rollback()
        raise RuntimeError(f"Erreur lors de l'initialisation de la base: {e}")


def database_exists() -> bool:
    """Vérifie si la base de données existe et contient les tables requises."""
    if not DATABASE_PATH.exists():
        return False

    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name IN ('techniciens', 'equipements', 'interventions')
            """)
            tables = cursor.fetchall()
            return len(tables) == 3
    except Exception:
        return False


if __name__ == "__main__":
    # Script de test pour initialiser la base
    print("Initialisation de la base de données...")
    init_database()

    # Vérification
    if database_exists():
        print("[OK] Base de donnees prete a l'emploi")

        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM techniciens")
            print(f"  - Techniciens: {cursor.fetchone()['count']}")

            cursor.execute("SELECT COUNT(*) as count FROM equipements")
            print(f"  - Équipements: {cursor.fetchone()['count']}")

            cursor.execute("SELECT COUNT(*) as count FROM interventions")
            print(f"  - Interventions: {cursor.fetchone()['count']}")
