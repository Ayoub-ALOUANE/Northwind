"""
Script de génération des diagrammes graphiques pour le rapport académique :
1. images/fig_02_gantt_planning_stage.png : Diagramme de Gantt (Août 2026 présentiel + Septembre 2026 en ligne)
2. images/fig_01b_organigramme_tython.png : Organigramme de l'organisme d'accueil Tython
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# S'assurer que le répertoire images existe
output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "report_latex", "images")
os.makedirs(output_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. DIAGRAMME DE GANTT (Août 2026 Présentiel - Septembre 2026 En ligne)
# -----------------------------------------------------------------------------
def generate_gantt():
    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)

    # Données des tâches
    tasks = [
        ("T1. Cadrage, état de l'art & architecture cible", 1, 1.9, "#1a5276", "Présentiel"),
        ("T2. Infrastructure conteneurisée Docker Compose", 1.8, 2.9, "#1f618d", "Présentiel"),
        ("T3. Base OLTP source & prototype générateur v1", 2.8, 3.9, "#2471a3", "Présentiel"),
        ("T4. Ingestion asynchrone ELT avec Airbyte", 3.8, 4.9, "#2980b9", "Présentiel"),
        ("T5. Modélisation dbt Core (Silver, Gold, Star)", 4.8, 6.0, "#117864", "En Ligne"),
        ("T6. Historisation SCD Type 2 & 121 tests dbt", 5.8, 6.9, "#16a085", "En Ligne"),
        ("T7. Orchestration Airflow & gouvernance dbt-docs", 6.8, 7.9, "#1abc9c", "En Ligne"),
        ("T8. BI Superset 6.0 & simulateur de marché v2.0", 7.6, 8.8, "#27ae60", "En Ligne"),
        ("T9. Rédaction finale du mémoire & validation", 7.0, 8.9, "#8e44ad", "En Ligne"),
    ]

    y_pos = list(range(len(tasks)))

    # Zones de fond pour différencier Présentiel (Août) et En Ligne (Septembre)
    ax.axvspan(0.8, 4.9, color="#ebf5fb", alpha=0.9, zorder=0)
    ax.axvspan(4.9, 9.2, color="#e8f8f5", alpha=0.9, zorder=0)

    # Ligne verticale de séparation des modes
    ax.axvline(4.9, color="#c0392b", linestyle="--", linewidth=1.8, zorder=2)
    ax.text(4.9, len(tasks) - 0.2, "  Bascule Présentiel → Télétravail (Fin Semaine 4)", 
            color="#922b21", fontweight="bold", fontsize=10, va="bottom", ha="left")

    # Barres de tâches
    for i, (name, start, end, color, mode) in enumerate(tasks):
        bar_height = 0.52
        ax.barh(i, end - start, left=start, height=bar_height, color=color, edgecolor="#2c3e50", linewidth=0.8, zorder=3)
        # Texte à l'intérieur ou à côté
        duration = end - start
        ax.text(start + duration / 2, i, f"S{int(start)} → S{int(end)} ({mode})", 
                ha="center", va="center", color="white", fontweight="bold", fontsize=9, zorder=4)

    # Libellés verticaux
    ax.set_yticks(y_pos)
    ax.set_yticklabels([t[0] for t in tasks], fontsize=10, fontweight="bold", color="#1c2833")
    ax.invert_yaxis()  # Première tâche en haut

    # Axe horizontal (Semaines & Mois)
    ax.set_xlim(0.8, 9.2)
    ax.set_xticks([1, 2, 3, 4, 5, 6, 7, 8])
    ax.set_xticklabels(["Semaine 1\n(01-07 Août)", "Semaine 2\n(08-14 Août)", "Semaine 3\n(15-21 Août)", "Semaine 4\n(22-28 Août)",
                        "Semaine 5\n(01-07 Sept)", "Semaine 6\n(08-14 Sept)", "Semaine 7\n(15-21 Sept)", "Semaine 8\n(22-28 Sept)"],
                       fontsize=9.5, fontweight="bold", color="#1c2833")

    # Bannière supérieure : Août Présentiel vs Septembre En Ligne
    ax.text(2.85, -1.2, "MOIS 1 : AOÛT 2026 — MODE PRÉSENTIEL (CASABLANCA)",
            ha="center", va="center", fontsize=11, fontweight="bold", color="#1a5276",
            bbox=dict(boxstyle="round,pad=0.4", fc="#d4e6f1", ec="#1a5276", lw=1.2))
    ax.text(7.05, -1.2, "MOIS 2 : SEPTEMBRE 2026 — MODE EN LIGNE (TÉLÉTRAVAIL)",
            ha="center", va="center", fontsize=11, fontweight="bold", color="#117864",
            bbox=dict(boxstyle="round,pad=0.4", fc="#d1f2eb", ec="#117864", lw=1.2))

    # Titre général
    plt.title("Planning Chronologique du Projet de Stage (8 Semaines - Période Août-Septembre 2026)\n"
              "Northwind Modern Data Platform — Organisme d'Accueil : Tython (Casablanca)",
              fontsize=13, fontweight="bold", pad=40, color="#1a5276")

    # Grille et styles
    ax.grid(axis="x", linestyle=":", alpha=0.6, color="#7f8c8d", zorder=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#bdc3c7')
    ax.spines['bottom'].set_color('#bdc3c7')

    plt.tight_layout()
    gantt_path = os.path.join(output_dir, "fig_02_gantt_planning_stage.png")
    plt.savefig(gantt_path, bbox_inches="tight")
    plt.close()
    print(f"[OK] Diagramme de Gantt généré : {gantt_path}")


# -----------------------------------------------------------------------------
# 2. ORGANIGRAMME DE TYTHON (Casablanca)
# -----------------------------------------------------------------------------
def generate_organigramme():
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def draw_box(x, y, w, h, title, subtitle="", bg="#1a5276", fg="white", border="#154360"):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1.2,rounding_size=2.0",
                                      facecolor=bg, edgecolor=border, linewidth=1.5, zorder=3)
        ax.add_patch(rect)
        if subtitle:
            ax.text(x + w / 2, y + h * 0.62, title, color=fg, fontsize=10.5, fontweight="bold", ha="center", va="center", zorder=4)
            ax.text(x + w / 2, y + h * 0.28, subtitle, color=fg, fontsize=8.5, ha="center", va="center", zorder=4)
        else:
            ax.text(x + w / 2, y + h * 0.5, title, color=fg, fontsize=10.5, fontweight="bold", ha="center", va="center", zorder=4)

    # Titre en tête
    ax.text(50, 96, "ORGANIGRAMME STRUCTUREL DE L'ORGANISME D'ACCUEIL", 
            ha="center", va="center", fontsize=14, fontweight="bold", color="#1a5276")
    ax.text(50, 92, "Tython (Venture Studio & AI Startup — Casablanca, Maroc)", 
            ha="center", va="center", fontsize=11, fontstyle="italic", color="#2c3e50")

    # 1. Direction Générale (Top)
    draw_box(30, 77, 40, 11, "DIRECTION GÉNÉRALE & FONDATION", 
             "Othmane Benslimane & Aziz Benslimane\nCo-fondateurs & Dirigeants", 
             bg="#1a5276", fg="white", border="#0e2f44")

    # Ligne verticale principale depuis la direction
    ax.plot([50, 50], [77, 67], color="#34495e", linewidth=2, zorder=2)
    # Ligne horizontale de distribution vers les 4 pôles
    ax.plot([12.5, 87.5], [67, 67], color="#34495e", linewidth=2, zorder=2)

    # Descentes vers les 4 pôles
    ax.plot([12.5, 12.5], [67, 60], color="#34495e", linewidth=2, zorder=2)
    ax.plot([37.5, 37.5], [67, 60], color="#34495e", linewidth=2, zorder=2)
    ax.plot([62.5, 62.5], [67, 60], color="#34495e", linewidth=2, zorder=2)
    ax.plot([87.5, 87.5], [67, 60], color="#34495e", linewidth=2, zorder=2)

    # 2. Pôles Opérationnels (Niveau 2)
    # Pôle 1 : IA & Produits
    draw_box(2.5, 48, 20, 12, "Pôle Venture Studio\n& Produits IA", 
             "Solutions : TyBot, AppAll,\nToknRouter", 
             bg="#2471a3", fg="white", border="#1b4f72")

    # Pôle 2 : Data Engineering & Cloud (Pôle du Stage)
    draw_box(27.5, 48, 20, 12, "Pôle Data Engineering\n& Infrastructures IT", 
             "Architecture Cloud, Modern\nData Stack & Pipelines", 
             bg="#117864", fg="white", border="#0e6251")

    # Pôle 3 : ERP & Solutions Industrielles
    draw_box(52.5, 48, 20, 12, "Pôle ERP & Solutions\nIndustrielles", 
             "CRM/ERP Personnalisés,\nServeurs & Capteurs IoT", 
             bg="#b7950b", fg="white", border="#7d6608")

    # Pôle 4 : Incubation & Talents
    draw_box(77.5, 48, 20, 12, "Pôle Incubation &\nTransformation Digitale", 
             "Accompagnement Entreprises,\nProgrammes PFE & Scaling", 
             bg="#7d3c98", fg="white", border="#512e5f")

    # Mise en exergue du projet de stage sous le Pôle Data Engineering
    ax.plot([37.5, 37.5], [48, 38], color="#117864", linewidth=2, zorder=2)
    
    # Encadré du projet de stage
    stage_box = patches.FancyBboxPatch((20, 15), 35, 23, boxstyle="round,pad=1.2,rounding_size=2.0",
                                       facecolor="#e8f8f5", edgecolor="#117864", linewidth=2, linestyle="--", zorder=3)
    ax.add_patch(stage_box)
    ax.text(37.5, 33, "CADRE DU PROJET DE STAGE DE FIN D'ÉTUDES", color="#0e6251", fontsize=9.5, fontweight="bold", ha="center")
    ax.text(37.5, 29, "Modern Data Platform Northwind Traders", color="#1c2833", fontsize=10.5, fontweight="bold", ha="center")
    ax.text(37.5, 24, "• Stagiaire : Ayoub ALOUANE (Data Engineer)", color="#2c3e50", fontsize=9, ha="center")
    ax.text(37.5, 20, "• Encadrement : Lead Data Architect (Tython)", color="#2c3e50", fontsize=9, ha="center")
    ax.text(37.5, 16.5, "• Période : Août 2026 (Présentiel) - Septembre 2026 (En Ligne)", color="#784212", fontsize=8.5, fontweight="bold", ha="center")

    # Encadré d'identité Tython en bas à droite
    id_box = patches.FancyBboxPatch((60, 15), 37, 23, boxstyle="round,pad=1.2,rounding_size=2.0",
                                    facecolor="#fcf3cf", edgecolor="#b7950b", linewidth=1.5, zorder=3)
    ax.add_patch(id_box)
    ax.text(78.5, 33, "FICHE D'IDENTITÉ DE L'ENTREPRISE", color="#7d6608", fontsize=9.5, fontweight="bold", ha="center")
    ax.text(78.5, 28.5, "• Siège : 55 Bd Zerktouni, N°3, Casablanca", color="#2c3e50", fontsize=8.5, ha="center")
    ax.text(78.5, 25, "• Slogan : « Innovate Now »", color="#2c3e50", fontsize=8.5, fontweight="bold", ha="center")
    ax.text(78.5, 21.5, "• Contact : hello@tython.org | https://tython.org", color="#2c3e50", fontsize=8.5, ha="center")
    ax.text(78.5, 18, "• Concept : Startup Studio & Venture Studio IA", color="#2c3e50", fontsize=8.5, ha="center")

    plt.tight_layout()
    organigramme_path = os.path.join(output_dir, "fig_01b_organigramme_tython.png")
    plt.savefig(organigramme_path, bbox_inches="tight")
    plt.close()
    print(f"[OK] Organigramme généré : {organigramme_path}")


if __name__ == "__main__":
    generate_gantt()
    generate_organigramme()

