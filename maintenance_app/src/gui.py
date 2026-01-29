"""
Interface graphique Tkinter pour l'application de maintenance.
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from db_connection import init_database, database_exists, DatabaseConnection
from data_access import (
    TechnicienDAO, EquipementDAO, InterventionDAO,
    StatistiquesDAO, IndicateursDAO
)
from business_logic import MaintenanceService


class MaintenanceApp:
    """Application principale de suivi de maintenance."""

    def __init__(self, root):
        self.root = root
        self.root.title("Suivi de Maintenance")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)

        # Couleurs
        self.bg_color = "#f5f5f5"
        self.sidebar_color = "#2c3e50"
        self.button_color = "#34495e"
        self.button_hover = "#4a6278"
        self.accent_color = "#3498db"
        self.text_color = "#2c3e50"

        self.root.configure(bg=self.bg_color)

        # Initialiser la base de donnees
        self._init_database()

        # Creer l'interface
        self._create_widgets()

        # Afficher le message de bienvenue
        self._show_welcome()

    def _init_database(self):
        """Initialise la base de donnees si necessaire."""
        if not database_exists():
            init_database()

    def _create_widgets(self):
        """Cree tous les widgets de l'interface."""
        # Frame principale
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar (menu)
        self._create_sidebar()

        # Zone de contenu
        self._create_content_area()

    def _create_sidebar(self):
        """Cree la barre laterale avec les boutons de menu."""
        self.sidebar = tk.Frame(self.main_frame, bg=self.sidebar_color, width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Titre
        title_frame = tk.Frame(self.sidebar, bg=self.sidebar_color)
        title_frame.pack(fill=tk.X, pady=(20, 30))

        tk.Label(
            title_frame,
            text="Maintenance",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg=self.sidebar_color
        ).pack()

        tk.Label(
            title_frame,
            text="Gestion du parc materiel",
            font=("Segoe UI", 9),
            fg="#bdc3c7",
            bg=self.sidebar_color
        ).pack()

        # Separateur
        ttk.Separator(self.sidebar, orient="horizontal").pack(fill=tk.X, padx=15, pady=10)

        # Boutons de menu
        menu_items = [
            ("Indicateurs globaux", self.show_indicateurs_globaux),
            ("Equipements sollicites", self.show_equipements_sollicites),
            ("Frequence par type", self.show_frequence_par_type),
            ("Cout par equipement", self.show_cout_par_type),
            ("Taux disponibilite", self.show_taux_disponibilite),
            ("Indice fiabilite", self.show_indice_fiabilite),
            ("Tendance des couts", self.show_tendance_couts),
            ("Alertes maintenance", self.show_alertes),
            ("Interventions/mois", self.show_interventions_mois),
            ("Performance techniciens", self.show_performance_techniciens),
            ("Historique equipement", self.show_historique_equipement),
            ("Rapport complet", self.show_rapport_synthese),
        ]

        for text, command in menu_items:
            btn = tk.Button(
                self.sidebar,
                text=text,
                font=("Segoe UI", 10),
                fg="white",
                bg=self.button_color,
                activebackground=self.button_hover,
                activeforeground="white",
                bd=0,
                padx=20,
                pady=8,
                anchor="w",
                cursor="hand2",
                command=command
            )
            btn.pack(fill=tk.X, padx=10, pady=2)

            # Effet hover
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=self.button_hover))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self.button_color))

        # Bouton Quitter en bas
        tk.Frame(self.sidebar, bg=self.sidebar_color).pack(fill=tk.BOTH, expand=True)

        quit_btn = tk.Button(
            self.sidebar,
            text="Quitter",
            font=("Segoe UI", 10),
            fg="white",
            bg="#c0392b",
            activebackground="#e74c3c",
            activeforeground="white",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.quit_app
        )
        quit_btn.pack(fill=tk.X, padx=10, pady=(0, 20))

    def _create_content_area(self):
        """Cree la zone de contenu principale."""
        self.content_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Titre de la section
        self.section_title = tk.Label(
            self.content_frame,
            text="Bienvenue",
            font=("Segoe UI", 18, "bold"),
            fg=self.text_color,
            bg=self.bg_color,
            anchor="w"
        )
        self.section_title.pack(fill=tk.X, pady=(0, 10))

        # Separateur
        ttk.Separator(self.content_frame, orient="horizontal").pack(fill=tk.X, pady=(0, 15))

        # Zone de texte avec scrollbar
        text_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(text_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area = tk.Text(
            text_frame,
            font=("Consolas", 11),
            fg=self.text_color,
            bg="white",
            bd=1,
            relief="solid",
            padx=15,
            pady=15,
            wrap=tk.WORD,
            yscrollcommand=self.scrollbar.set
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.text_area.yview)

    def _clear_and_set_title(self, title: str):
        """Efface la zone de texte et met a jour le titre."""
        self.section_title.config(text=title)
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)

    def _append_text(self, text: str):
        """Ajoute du texte a la zone d'affichage."""
        self.text_area.insert(tk.END, text)

    def _finalize_text(self):
        """Finalise l'affichage du texte."""
        self.text_area.config(state=tk.DISABLED)

    def _format_table(self, headers: list, rows: list, col_widths: list = None) -> str:
        """Formate un tableau en texte."""
        if not rows:
            return "  Aucune donnee\n"

        if col_widths is None:
            col_widths = [max(len(str(h)), max(len(str(row[i])) for row in rows))
                          for i, h in enumerate(headers)]

        result = ""
        header_line = " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers))
        result += f"  {header_line}\n"
        result += f"  {'-' * len(header_line)}\n"

        for row in rows:
            line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers)))
            result += f"  {line}\n"

        return result

    def _show_welcome(self):
        """Affiche le message de bienvenue."""
        self._clear_and_set_title("Bienvenue")
        self._append_text("""
  Application de Suivi de Maintenance
  ====================================

  Bienvenue dans l'application de gestion du parc materiel.

  Utilisez le menu a gauche pour naviguer entre les differentes
  fonctionnalites:

    - Indicateurs globaux : Vue d'ensemble des couts et interventions
    - Equipements sollicites : Les equipements les plus maintenus
    - Frequence par type : Analyse des types d'intervention
    - Cout par equipement : Repartition des couts
    - Taux disponibilite : Disponibilite par type (calcul Python)
    - Indice fiabilite : Score de fiabilite (calcul Python)
    - Tendance des couts : Evolution des depenses (calcul Python)
    - Alertes maintenance : Equipements a surveiller (calcul Python)
    - Interventions/mois : Historique mensuel
    - Performance techniciens : Evaluation des equipes
    - Historique equipement : Detail par equipement
    - Rapport complet : Synthese globale

  Les indicateurs marques "(calcul Python)" sont calcules
  cote application, pas en SQL.
""")
        self._finalize_text()

    def show_indicateurs_globaux(self):
        """Affiche les indicateurs globaux."""
        self._clear_and_set_title("Indicateurs Globaux")

        cout_total = MaintenanceService.get_cout_total_maintenance()
        nb_interventions = MaintenanceService.get_nombre_interventions()
        duree_moyenne = MaintenanceService.get_duree_moyenne_intervention()

        self._append_text(f"""
  Cout total de maintenance     : {cout_total:,.2f} EUR
  Nombre total d'interventions  : {nb_interventions}
  Duree moyenne d'intervention  : {duree_moyenne:.1f} minutes ({duree_moyenne/60:.1f} heures)
""")
        self._finalize_text()

    def show_equipements_sollicites(self):
        """Affiche les equipements les plus sollicites."""
        self._clear_and_set_title("Equipements les Plus Sollicites")

        equipements = MaintenanceService.get_equipements_plus_sollicites(10)

        headers = ["Equipement", "Type", "Nb Interv.", "Cout Total", "Duree (min)"]
        rows = [
            (eq['nom'][:25], eq['type'], eq['nombre_interventions'],
             f"{eq['cout_total']:.2f} EUR", eq['duree_totale'])
            for eq in equipements
        ]

        self._append_text("\n")
        self._append_text(self._format_table(headers, rows, [25, 18, 10, 12, 12]))
        self._finalize_text()

    def show_frequence_par_type(self):
        """Affiche la frequence des interventions par type."""
        self._clear_and_set_title("Frequence des Interventions par Type")

        frequences = MaintenanceService.get_frequence_par_type()

        headers = ["Type", "Nombre", "Cout Total", "Cout Moyen", "Duree Moy."]
        rows = [
            (f['type_intervention'], f['nombre'], f"{f['cout_total']:.2f} EUR",
             f"{f['cout_moyen']:.2f} EUR", f"{f['duree_moyenne']:.0f} min")
            for f in frequences
        ]

        self._append_text("\n")
        self._append_text(self._format_table(headers, rows, [15, 8, 12, 12, 12]))
        self._finalize_text()

    def show_cout_par_type(self):
        """Affiche le cout par type d'equipement."""
        self._clear_and_set_title("Cout de Maintenance par Type d'Equipement")

        couts = IndicateursDAO.get_cout_par_type_equipement()

        headers = ["Type Equipement", "Nb Equip.", "Nb Interv.", "Cout Total", "Cout Moy."]
        rows = [
            (c['type'], c['nombre_equipements'], c['nombre_interventions'],
             f"{c['cout_total'] or 0:.2f} EUR", f"{c['cout_moyen_intervention'] or 0:.2f} EUR")
            for c in couts
        ]

        self._append_text("\n")
        self._append_text(self._format_table(headers, rows, [20, 10, 10, 12, 12]))
        self._finalize_text()

    def show_taux_disponibilite(self):
        """Affiche le taux de disponibilite."""
        self._clear_and_set_title("Taux de Disponibilite par Type (Calcul Python)")

        taux = MaintenanceService.calculer_taux_disponibilite_equipements()

        self._append_text("\n  [Indicateur calcule cote Python, pas en SQL]\n\n")

        for type_eq, pourcentage in taux.items():
            barre = "=" * int(pourcentage / 5) + "-" * (20 - int(pourcentage / 5))
            self._append_text(f"  {type_eq:22} : [{barre}] {pourcentage:.1f}%\n")

        self._finalize_text()

    def show_indice_fiabilite(self):
        """Affiche l'indice de fiabilite."""
        self._clear_and_set_title("Indice de Fiabilite des Equipements (Calcul Python)")

        fiabilite = MaintenanceService.calculer_indice_fiabilite_equipements()

        self._append_text("\n  [Indicateur calcule cote Python: score base sur pannes, couts et age]\n\n")

        headers = ["Equipement", "Type", "Age", "Pannes", "Cout", "Indice"]
        rows = [
            (f['nom'][:22], f['type'][:15], f"{f['age_annees']}a",
             f['nb_pannes'], f"{f['cout_total']:.0f} EUR", f"{f['indice_fiabilite']}/100")
            for f in fiabilite
        ]

        self._append_text(self._format_table(headers, rows, [22, 15, 5, 7, 10, 8]))
        self._finalize_text()

    def show_tendance_couts(self):
        """Affiche la tendance des couts."""
        self._clear_and_set_title("Tendance des Couts 2024 (Calcul Python)")

        tendance = MaintenanceService.calculer_tendance_couts(2024)

        self._append_text("\n  [Indicateur calcule cote Python: analyse semestrielle]\n")
        self._append_text(f"""
  Tendance globale    : {tendance['tendance'].upper()}
  Variation S1 -> S2  : {tendance['variation_pct']:+.1f}%
  Cout 1er semestre   : {tendance.get('cout_s1', 0):,.2f} EUR
  Cout 2nd semestre   : {tendance.get('cout_s2', 0):,.2f} EUR
""")

        self._append_text("\n  Detail par mois:\n")
        noms_mois = ['', 'Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun',
                     'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec']

        for mois, cout in tendance['detail_mois'].items():
            barre = "=" * int(cout / 50) if cout > 0 else ""
            self._append_text(f"    {noms_mois[mois]:3} : {barre} {cout:.0f} EUR\n")

        self._finalize_text()

    def show_alertes(self):
        """Affiche les alertes de maintenance."""
        self._clear_and_set_title("Alertes de Maintenance (Calcul Python)")

        alertes = MaintenanceService.generer_alertes_maintenance()

        self._append_text("\n  [Alertes generees par analyse Python des donnees]\n\n")

        if not alertes:
            self._append_text("  Aucune alerte\n")
        else:
            for niveau in ['CRITIQUE', 'ATTENTION', 'INFO']:
                alertes_niveau = [a for a in alertes if a['niveau'] == niveau]
                if alertes_niveau:
                    symbole = {'CRITIQUE': '[!]', 'ATTENTION': '[*]', 'INFO': '[i]'}[niveau]
                    self._append_text(f"  {symbole} {niveau}:\n")
                    for alerte in alertes_niveau:
                        self._append_text(f"     - {alerte['equipement']}: {alerte['message']}\n")
                    self._append_text("\n")

        self._finalize_text()

    def show_interventions_mois(self):
        """Affiche les interventions par mois."""
        self._clear_and_set_title("Interventions par Mois (2024)")

        interventions = IndicateursDAO.get_interventions_par_mois(2024)

        noms_mois = {
            '01': 'Janvier', '02': 'Fevrier', '03': 'Mars', '04': 'Avril',
            '05': 'Mai', '06': 'Juin', '07': 'Juillet', '08': 'Aout',
            '09': 'Septembre', '10': 'Octobre', '11': 'Novembre', '12': 'Decembre'
        }

        headers = ["Mois", "Nb Interv.", "Cout Total", "Duree Totale"]
        rows = [
            (noms_mois.get(i['mois'], i['mois']), i['nombre_interventions'],
             f"{i['cout_total']:.2f} EUR", f"{i['duree_totale']} min")
            for i in interventions
        ]

        self._append_text("\n")
        self._append_text(self._format_table(headers, rows, [12, 12, 12, 14]))
        self._finalize_text()

    def show_performance_techniciens(self):
        """Affiche la performance des techniciens."""
        self._clear_and_set_title("Performance des Techniciens")

        perf = IndicateursDAO.get_performance_techniciens()

        headers = ["Technicien", "Specialite", "Nb Interv.", "Temps Total", "Valeur"]
        rows = [
            (p['technicien'], p['specialite'][:12], p['nombre_interventions'],
             f"{p['temps_total'] or 0} min", f"{p['valeur_interventions'] or 0:.0f} EUR")
            for p in perf
        ]

        self._append_text("\n")
        self._append_text(self._format_table(headers, rows, [20, 12, 10, 12, 10]))
        self._finalize_text()

    def show_historique_equipement(self):
        """Affiche l'historique d'un equipement."""
        self._clear_and_set_title("Historique d'un Equipement")

        # Lister les equipements
        equipements = EquipementDAO.get_all()

        # Creer la liste pour le choix
        choix_list = [f"{eq['id']}. {eq['nom']} ({eq['type']})" for eq in equipements]

        # Boite de dialogue pour choisir
        choix = simpledialog.askstring(
            "Choix de l'equipement",
            "Entrez le numero de l'equipement:\n\n" + "\n".join(choix_list),
            parent=self.root
        )

        if not choix:
            self._append_text("\n  Operation annulee.\n")
            self._finalize_text()
            return

        try:
            eq_id = int(choix)
            equipement = EquipementDAO.get_by_id(eq_id)

            if not equipement:
                self._append_text("\n  Equipement non trouve.\n")
                self._finalize_text()
                return

            self._append_text(f"\n  Historique de: {equipement['nom']}\n")
            self._append_text(f"  Type: {equipement['type']} | Localisation: {equipement['localisation']}\n")
            self._append_text(f"  Statut actuel: {equipement['statut']}\n\n")

            historique = IndicateursDAO.get_historique_equipement(eq_id)

            if historique:
                headers = ["Date", "Type", "Description", "Duree", "Cout", "Technicien"]
                rows = [
                    (h['date_intervention'], h['type_intervention'][:10],
                     h['description'][:25], f"{h['duree_minutes']}m",
                     f"{h['cout']:.0f} EUR", h['technicien'][:15])
                    for h in historique
                ]
                self._append_text(self._format_table(headers, rows, [12, 10, 25, 6, 8, 15]))
            else:
                self._append_text("  Aucune intervention enregistree.\n")

        except ValueError:
            self._append_text("\n  Entree invalide.\n")

        self._finalize_text()

    def show_rapport_synthese(self):
        """Affiche le rapport de synthese complet."""
        self._clear_and_set_title("Rapport de Synthese Complet")

        rapport = MaintenanceService.generer_rapport_synthese()

        # Indicateurs globaux
        self._append_text("\n  INDICATEURS GLOBAUX\n")
        self._append_text("  " + "-" * 40 + "\n")
        ig = rapport['indicateurs_globaux']
        self._append_text(f"    Cout total        : {ig['cout_total']:,.2f} EUR\n")
        self._append_text(f"    Interventions     : {ig['nombre_interventions']}\n")
        self._append_text(f"    Duree moyenne     : {ig['duree_moyenne_minutes']:.1f} min\n")

        # Taux de disponibilite
        self._append_text("\n  TAUX DE DISPONIBILITE\n")
        self._append_text("  " + "-" * 40 + "\n")
        for type_eq, taux in rapport['taux_disponibilite'].items():
            self._append_text(f"    {type_eq:22} : {taux:.1f}%\n")

        # Tendance
        self._append_text("\n  TENDANCE DES COUTS\n")
        self._append_text("  " + "-" * 40 + "\n")
        tend = rapport['tendance_couts']
        self._append_text(f"    Tendance  : {tend['tendance'].upper()}\n")
        self._append_text(f"    Variation : {tend['variation_pct']:+.1f}%\n")

        # Top equipements
        self._append_text("\n  TOP 5 EQUIPEMENTS SOLLICITES\n")
        self._append_text("  " + "-" * 40 + "\n")
        for i, eq in enumerate(rapport['top_equipements_sollicites'][:5], 1):
            self._append_text(f"    {i}. {eq['nom'][:25]} - {eq['nombre_interventions']} interv. ({eq['cout_total']:.0f} EUR)\n")

        # Alertes
        self._append_text("\n  ALERTES\n")
        self._append_text("  " + "-" * 40 + "\n")
        alertes_critiques = [a for a in rapport['alertes'] if a['niveau'] == 'CRITIQUE']
        if alertes_critiques:
            for a in alertes_critiques[:3]:
                self._append_text(f"    [!] {a['equipement']}: {a['message'][:45]}\n")
        else:
            self._append_text("    Aucune alerte critique\n")

        self._finalize_text()

    def quit_app(self):
        """Ferme l'application."""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter?"):
            DatabaseConnection().close()
            self.root.destroy()


def main():
    """Point d'entree principal."""
    root = tk.Tk()
    app = MaintenanceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
