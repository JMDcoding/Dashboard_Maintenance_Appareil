-- ============================================================================
-- SCHEMA DE LA BASE DE DONNEES - SUIVI DE MAINTENANCE DE MATERIEL
-- ============================================================================

-- Suppression des tables existantes (ordre inverse des dépendances)
DROP TABLE IF EXISTS interventions;
DROP TABLE IF EXISTS equipements;
DROP TABLE IF EXISTS techniciens;

-- ============================================================================
-- CREATION DES TABLES
-- ============================================================================

-- Table des techniciens
CREATE TABLE techniciens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    specialite TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    date_embauche DATE NOT NULL
);

-- Table des équipements
CREATE TABLE equipements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('ordinateur', 'machine', 'equipement_technique')),
    marque TEXT,
    modele TEXT,
    numero_serie TEXT UNIQUE NOT NULL,
    date_acquisition DATE NOT NULL,
    localisation TEXT NOT NULL,
    statut TEXT NOT NULL DEFAULT 'actif' CHECK (statut IN ('actif', 'en_panne', 'en_maintenance', 'reforme'))
);

-- Table des interventions (table de liaison avec attributs)
CREATE TABLE interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipement_id INTEGER NOT NULL,
    technicien_id INTEGER NOT NULL,
    date_intervention DATE NOT NULL,
    type_intervention TEXT NOT NULL CHECK (type_intervention IN ('preventive', 'corrective', 'installation', 'mise_a_jour')),
    description TEXT NOT NULL,
    duree_minutes INTEGER NOT NULL CHECK (duree_minutes > 0),
    cout REAL NOT NULL CHECK (cout >= 0),
    statut TEXT NOT NULL DEFAULT 'terminee' CHECK (statut IN ('planifiee', 'en_cours', 'terminee', 'annulee')),
    FOREIGN KEY (equipement_id) REFERENCES equipements(id) ON DELETE RESTRICT,
    FOREIGN KEY (technicien_id) REFERENCES techniciens(id) ON DELETE RESTRICT
);

-- Index pour optimiser les requêtes fréquentes
CREATE INDEX idx_interventions_equipement ON interventions(equipement_id);
CREATE INDEX idx_interventions_technicien ON interventions(technicien_id);
CREATE INDEX idx_interventions_date ON interventions(date_intervention);
CREATE INDEX idx_equipements_type ON equipements(type);

-- ============================================================================
-- INSERTION DES DONNEES DE TEST
-- ============================================================================

-- Insertion des techniciens (5 techniciens)
INSERT INTO techniciens (nom, prenom, specialite, email, date_embauche) VALUES
    ('Dupont', 'Jean', 'Informatique', 'jean.dupont@maintenance.fr', '2020-03-15'),
    ('Martin', 'Sophie', 'Électromécanique', 'sophie.martin@maintenance.fr', '2019-07-01'),
    ('Bernard', 'Pierre', 'Informatique', 'pierre.bernard@maintenance.fr', '2021-01-10'),
    ('Petit', 'Marie', 'Équipements industriels', 'marie.petit@maintenance.fr', '2018-09-20'),
    ('Leroy', 'Thomas', 'Polyvalent', 'thomas.leroy@maintenance.fr', '2022-02-28');

-- Insertion des équipements (10 équipements)
INSERT INTO equipements (nom, type, marque, modele, numero_serie, date_acquisition, localisation, statut) VALUES
    ('PC Bureau Direction', 'ordinateur', 'Dell', 'OptiPlex 7090', 'DELL-2023-001', '2023-01-15', 'Bureau 101', 'actif'),
    ('PC Bureau Comptabilité', 'ordinateur', 'HP', 'EliteDesk 800', 'HP-2022-042', '2022-06-20', 'Bureau 102', 'actif'),
    ('Serveur Principal', 'ordinateur', 'Dell', 'PowerEdge R740', 'DELL-SRV-2021', '2021-03-10', 'Salle serveur', 'actif'),
    ('Imprimante Multifonction', 'equipement_technique', 'Canon', 'imageRUNNER C3530i', 'CANON-2022-007', '2022-08-05', 'Couloir principal', 'actif'),
    ('Tour CNC', 'machine', 'Haas', 'ST-10', 'HAAS-CNC-2020', '2020-11-30', 'Atelier A', 'actif'),
    ('Fraiseuse numérique', 'machine', 'DMG Mori', 'CMX 600 V', 'DMG-2019-003', '2019-04-22', 'Atelier A', 'en_maintenance'),
    ('PC Portable Technicien 1', 'ordinateur', 'Lenovo', 'ThinkPad T14', 'LEN-2023-015', '2023-04-01', 'Mobile', 'actif'),
    ('Climatisation Salle Serveur', 'equipement_technique', 'Daikin', 'RZAG140MV1', 'DAI-CLIM-2021', '2021-06-15', 'Salle serveur', 'actif'),
    ('Robot de soudure', 'machine', 'Fanuc', 'Arc Mate 100iD', 'FAN-ROBO-2022', '2022-01-10', 'Atelier B', 'actif'),
    ('Onduleur Serveur', 'equipement_technique', 'APC', 'Smart-UPS 3000', 'APC-UPS-2021', '2021-03-10', 'Salle serveur', 'actif');

-- Insertion des interventions (25 interventions pour des statistiques pertinentes)
INSERT INTO interventions (equipement_id, technicien_id, date_intervention, type_intervention, description, duree_minutes, cout, statut) VALUES
    -- Interventions sur PC Bureau Direction (équipement 1)
    (1, 1, '2024-01-15', 'preventive', 'Nettoyage système et mise à jour Windows', 45, 50.00, 'terminee'),
    (1, 3, '2024-06-20', 'corrective', 'Remplacement disque SSD défaillant', 120, 180.00, 'terminee'),
    (1, 1, '2024-11-10', 'mise_a_jour', 'Migration vers Windows 11', 90, 75.00, 'terminee'),

    -- Interventions sur PC Bureau Comptabilité (équipement 2)
    (2, 1, '2024-02-10', 'preventive', 'Maintenance préventive annuelle', 60, 55.00, 'terminee'),
    (2, 3, '2024-08-05', 'corrective', 'Réparation alimentation', 90, 120.00, 'terminee'),

    -- Interventions sur Serveur Principal (équipement 3)
    (3, 1, '2024-01-20', 'preventive', 'Vérification RAID et sauvegardes', 120, 100.00, 'terminee'),
    (3, 3, '2024-04-15', 'mise_a_jour', 'Mise à jour firmware et patches sécurité', 180, 200.00, 'terminee'),
    (3, 1, '2024-07-22', 'corrective', 'Remplacement ventilateur défectueux', 60, 85.00, 'terminee'),
    (3, 3, '2024-10-30', 'preventive', 'Audit sécurité et optimisation', 240, 300.00, 'terminee'),

    -- Interventions sur Imprimante Multifonction (équipement 4)
    (4, 5, '2024-03-12', 'preventive', 'Nettoyage têtes et calibration', 45, 40.00, 'terminee'),
    (4, 5, '2024-07-18', 'corrective', 'Remplacement kit tambour', 90, 250.00, 'terminee'),
    (4, 5, '2024-12-01', 'preventive', 'Maintenance trimestrielle', 30, 35.00, 'terminee'),

    -- Interventions sur Tour CNC (équipement 5)
    (5, 2, '2024-02-28', 'preventive', 'Lubrification et contrôle axes', 180, 150.00, 'terminee'),
    (5, 4, '2024-05-15', 'corrective', 'Recalibration après dérive', 240, 350.00, 'terminee'),
    (5, 2, '2024-09-10', 'preventive', 'Révision semestrielle complète', 300, 400.00, 'terminee'),
    (5, 4, '2024-12-05', 'corrective', 'Remplacement broche usée', 360, 1200.00, 'terminee'),

    -- Interventions sur Fraiseuse numérique (équipement 6)
    (6, 2, '2024-01-08', 'preventive', 'Contrôle géométrique', 120, 100.00, 'terminee'),
    (6, 4, '2024-04-20', 'corrective', 'Réparation système hydraulique', 240, 450.00, 'terminee'),
    (6, 2, '2024-08-12', 'corrective', 'Panne moteur axe Z', 180, 800.00, 'terminee'),
    (6, 4, '2024-11-25', 'corrective', 'Diagnostic panne électronique en cours', 120, 200.00, 'en_cours'),

    -- Interventions sur PC Portable Technicien (équipement 7)
    (7, 3, '2024-05-02', 'installation', 'Configuration initiale et logiciels métier', 180, 100.00, 'terminee'),
    (7, 1, '2024-10-15', 'mise_a_jour', 'Mise à jour suite logicielle', 45, 40.00, 'terminee'),

    -- Interventions sur Climatisation (équipement 8)
    (8, 2, '2024-03-20', 'preventive', 'Nettoyage filtres et contrôle fluide', 90, 120.00, 'terminee'),
    (8, 2, '2024-09-25', 'preventive', 'Maintenance saisonnière', 60, 80.00, 'terminee'),

    -- Interventions sur Robot de soudure (équipement 9)
    (9, 4, '2024-02-14', 'preventive', 'Calibration bras et vérification soudures test', 150, 180.00, 'terminee'),
    (9, 4, '2024-06-30', 'mise_a_jour', 'Mise à jour programme de soudure', 120, 150.00, 'terminee'),
    (9, 2, '2024-11-08', 'corrective', 'Remplacement torche de soudure', 90, 320.00, 'terminee'),

    -- Interventions sur Onduleur (équipement 10)
    (10, 5, '2024-04-05', 'preventive', 'Test batteries et autonomie', 60, 50.00, 'terminee'),
    (10, 5, '2024-10-20', 'corrective', 'Remplacement batterie défectueuse', 45, 280.00, 'terminee');
