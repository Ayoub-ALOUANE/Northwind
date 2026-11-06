"""
Générateur graphique pour fig_05_global_data_platform_architecture.png
Rendu haute résolution (300 DPI) pour le Chapitre 3 du rapport académique.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "report_latex", "images")
os.makedirs(output_dir, exist_ok=True)
png_path = os.path.join(output_dir, "fig_05_global_data_platform_architecture.png")

fig, ax = plt.subplots(figsize=(16, 9.5), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Fond général
fig.patch.set_facecolor('#0F172A')
ax.set_facecolor('#0F172A')

def draw_card(x, y, w, h, bg="#1E293B", border="#334155", lw=1.2, radius=1.0):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.5,rounding_size={radius}",
                                  facecolor=bg, edgecolor=border, linewidth=lw, zorder=2)
    ax.add_patch(rect)

# 1. En-tête
draw_card(2, 90, 96, 8, bg="#1E293B", border="#3B82F6", lw=1.5, radius=1.2)
ax.text(3.5, 95.2, "ARCHITECTURE TECHNIQUE GLOBALE — NORTHWIND MODERN DATA PLATFORM", 
        color="#F8FAFC", fontsize=13, fontweight="bold", va="center")
ax.text(3.5, 92.2, "Flux End-to-End : Source OLTP & Simulateur v2 ➔ Ingestion Airbyte ➔ Entrepôt Médaillon dbt Core ➔ Orchestration Airflow ➔ BI Superset", 
        color="#94A3B8", fontsize=9.5, va="center")
ax.text(96.5, 94, "TYTHON CASABLANCA • ENSET MOHAMMEDIA\n15 Services Conteneurisés Docker", 
        color="#60A5FA", fontsize=8.5, fontweight="bold", ha="right", va="center")

# 2. Les 5 Colonnes Métiers
# Col 1 : Source OLTP & Simulateur (x=2 to 19, w=17)
draw_card(2, 17, 17, 71, bg="#1E293B", border="#2563EB", lw=1.5)
ax.text(10.5, 85.5, "1. SOURCE TRANSACTIONNELLE\n& SIMULATEUR MARCHÉ", color="white", fontsize=9.5, fontweight="bold", ha="center", va="center")

draw_card(3, 56, 15, 26, bg="#0F172A", border="#38BDF8", lw=1.2)
ax.text(10.5, 78.5, "Simulateur Marché v2.0\n(Python 3.11)", color="#38BDF8", fontsize=9, fontweight="bold", ha="center")
ax.text(3.8, 67, "• Loi de Pareto (80/20)\n• Commandes B2B Tier 1/2\n• Réassort auto si stock bas\n• Calcul dynamique de fret\n• Statuts de livraison", color="#CBD5E1", fontsize=7.5, va="center")

draw_card(3, 19, 15, 33, bg="#0F172A", border="#2563EB", lw=1.2)
ax.text(10.5, 48.5, "PostgreSQL Source (OLTP)\nConteneur : postgres-source", color="#60A5FA", fontsize=9, fontweight="bold", ha="center")
ax.text(3.8, 35, "Port : 55432:5432\nBase : northwind\nVolume : source_data\nMode : wal_level = logical\n\n14 Tables Relationnelles :\norders, order_details,\nproducts, customers,\nemployees, suppliers,\nshippers, categories...", color="#93C5FD", fontsize=7.5, va="center")

# Flèche Générateur -> Source
ax.annotate("", xy=(10.5, 52), xytext=(10.5, 56),
            arrowprops=dict(arrowstyle="->", color="#38BDF8", lw=1.8))

# Col 2 : Airbyte ELT (x=21 to 38, w=17)
draw_card(21, 17, 17, 71, bg="#1E293B", border="#8B5CF6", lw=1.5)
ax.text(29.5, 85.5, "2. INGESTION ASYNCHRONE\n& CDC (AIRBYTE)", color="white", fontsize=9.5, fontweight="bold", ha="center", va="center")

draw_card(22, 19, 15, 63, bg="#0F172A", border="#A78BFA", lw=1.2)
ax.text(29.5, 78.5, "Airbyte Cluster v0.50.36\nWeb UI : Port 8000", color="#C4B5FD", fontsize=9, fontweight="bold", ha="center")
ax.text(22.8, 51, "Microservices Coordonnés :\n• airbyte-webapp (Port 8000)\n• airbyte-server (Port 8001)\n• airbyte-worker (Docker sock)\n• airbyte-temporal (Port 7233)\n• airbyte-db (PostgreSQL 13)\n\nMode de Réplication :\n• Incrémentale CDC\n• Append + Deduped\n• Audit : _airbyte_raw_id,\n  _airbyte_extracted_at\n\nZéro impact sur la vente OLTP", color="#DDD6FE", fontsize=7.5, va="center")

# Flèche Col 1 -> Col 2
ax.annotate("", xy=(21, 35), xytext=(19, 35),
            arrowprops=dict(arrowstyle="->", color="#8B5CF6", lw=2.2))
ax.text(20, 37.5, "CDC", color="#C4B5FD", fontsize=8, fontweight="bold", ha="center")

# Col 3 : Warehouse & Médaillon dbt (x=40 to 67, w=27)
draw_card(40, 17, 27, 71, bg="#1E293B", border="#10B981", lw=1.5)
ax.text(53.5, 85.5, "3. ENTREPÔT DE DONNÉES BIVALENT & MÉDAILLON (DBT)", color="white", fontsize=9.5, fontweight="bold", ha="center", va="center")

draw_card(41, 74, 25, 8, bg="#0F172A", border="#14B8A6", lw=1)
ax.text(53.5, 78, "Cible Hybride : PostgreSQL OLAP (55433) & Snowflake Cloud", color="#5EEAD4", fontsize=8, fontweight="bold", ha="center")

# Bronze
draw_card(41, 62, 25, 10, bg="#291F1D", border="#B45309", lw=1)
ax.text(42, 69, "BRONZE : Raw Tables (Append only)", color="#FBBF24", fontsize=8, fontweight="bold")
ax.text(42, 65, "14 tables sources avec métadonnées d'ingestion brutes", color="#FDE68A", fontsize=7.2)

# Silver & Snapshots
draw_card(41, 45, 25, 15, bg="#1E293B", border="#64748B", lw=1)
ax.text(42, 57, "SILVER : 12 Vues Cleaned & Snapshots SCD2", color="#94A3B8", fontsize=8, fontweight="bold")
ax.text(42, 50, "• Typage strict, trim, déduplication, substitution NULLs\n• SCD Type 2 : products_snapshot, customers, orders\n• Tables seeds : country_region_mapping, discount_tiers", color="#E2E8F0", fontsize=7.2)

# Gold
draw_card(41, 24, 25, 19, bg="#1E241E", border="#10B981", lw=1.2)
ax.text(42, 39.5, "GOLD : Schéma en Étoile Kimball & 5 Data Marts", color="#34D399", fontsize=8, fontweight="bold")
ax.text(42, 31, "★ fact_sales (Lignes de commande, SK, CA Brut, Remises, CA Net)\n• Dimensions : dim_customers, dim_products, dim_employees, dim_date\n• 5 Marts : mart_sales_summary, mart_customer_segments (RFM),\n  mart_product_performance, mart_employee, mart_shipping", color="#A7F3D0", fontsize=7)

# Badge 121 Tests
draw_card(41, 18.5, 25, 4.5, bg="#064E3B", border="#10B981", lw=1)
ax.text(53.5, 20.7, "🛡️ Suite de 121 Tests dbt Automatisés (100% Validés)", color="#ECFDF5", fontsize=7.8, fontweight="bold", ha="center")

# Flèche Col 2 -> Col 3
ax.annotate("", xy=(40, 67), xytext=(38, 67),
            arrowprops=dict(arrowstyle="->", color="#10B981", lw=2.2))
ax.text(39, 69.5, "Raw", color="#6EE7B7", fontsize=8, fontweight="bold", ha="center")

# Col 4 : Airflow Orchestration (x=69 to 83, w=14)
draw_card(69, 17, 14, 71, bg="#1E293B", border="#0284C7", lw=1.5)
ax.text(76, 85.5, "4. ORCHESTRATION\n(AIRFLOW 2.x)", color="white", fontsize=9.5, fontweight="bold", ha="center", va="center")

draw_card(70, 19, 12, 63, bg="#0F172A", border="#38BDF8", lw=1.2)
ax.text(76, 78.5, "Apache Airflow\nWeb UI : 8081", color="#38BDF8", fontsize=9, fontweight="bold", ha="center")
ax.text(70.8, 50, "DAG quotidien (02:00 UTC) :\nnorthwind_dbt_pipeline\n\n10 Tâches Séquentielles :\n1. freshness_check (<24h)\n2. dbt_deps (packages)\n3. dbt_seed (lookup)\n4. dbt_run_silver\n5. dbt_test_silver\n6. dbt_snapshot (SCD2)\n7. dbt_run_gold\n8. dbt_test_gold (121 tests)\n9. dbt_docs_generate\n10. superset_sync", color="#BAE6FD", fontsize=7.2, va="center")

# Flèche Pilotage Airflow -> dbt
ax.annotate("", xy=(67, 50), xytext=(69, 50),
            arrowprops=dict(arrowstyle="->", color="#0284C7", lw=2.0))
ax.text(68, 52.5, "CLI", color="#38BDF8", fontsize=8, fontweight="bold", ha="center")

# Col 5 : Superset BI & Governance (x=85 to 98, w=13)
draw_card(85, 17, 13, 71, bg="#1E293B", border="#0D9488", lw=1.5)
ax.text(91.5, 85.5, "5. RESTITUTION BI\n& GOUVERNANCE", color="white", fontsize=9.5, fontweight="bold", ha="center", va="center")

draw_card(85.8, 48, 11.4, 34, bg="#0F172A", border="#14B8A6", lw=1.2)
ax.text(91.5, 78.5, "Apache Superset 6.0\nWeb UI : Port 8088", color="#2DD4BF", fontsize=8.5, fontweight="bold", ha="center")
ax.text(86.5, 62, "Dashboard Exécutif :\n• 14 Visualisations REST\n• 6 Cartes KPI (CA Net,\n  Brut, Commandes...)\n• Tendance Net vs Gross\n• Donut RFM Marketing\n• Leaderboard Commerciaux\n• Matrice Produits", color="#CCFBF1", fontsize=7.2, va="center")

draw_card(85.8, 28, 11.4, 18, bg="#0F172A", border="#10B981", lw=1)
ax.text(91.5, 42.5, "dbt-docs (Nginx)\nPort 8085", color="#34D399", fontsize=8.5, fontweight="bold", ha="center")
ax.text(86.5, 34.5, "• Catalogue interactif\n• Graphe de lignage DAG\n• Dictionnaire de données", color="#A7F3D0", fontsize=7.2, va="center")

draw_card(85.8, 19, 11.4, 8, bg="#0F172A", border="#38BDF8", lw=1)
ax.text(91.5, 24.5, "pgAdmin 4 (Port 5051)", color="#60A5FA", fontsize=8, fontweight="bold", ha="center")
ax.text(86.5, 21.2, "Console d'administration SQL", color="#BAE6FD", fontsize=7, va="center")

# Flèche Gold -> Superset
ax.annotate("", xy=(85.8, 62), xytext=(67, 35),
            arrowprops=dict(arrowstyle="->", color="#14B8A6", lw=2.2, connectionstyle="arc3,rad=-0.15"))
ax.text(77, 40, "Requêtes OLAP Marts", color="#5EEAD4", fontsize=7.5, fontweight="bold", ha="center")

# 3. Bandeau Inférieur : Infrastructure Conteneurisée Docker
draw_card(2, 2, 96, 13, bg="#1E293B", border="#2496ED", lw=1.5, radius=1.0)
ax.text(50, 12.8, "INFRASTRUCTURE CONTENEURISÉE DOCKER (RÉSEAU VIRTUEL data-platform)", 
        color="#60A5FA", fontsize=10, fontweight="bold", ha="center")

draw_card(3, 4, 22, 7.5, bg="#0F172A", border="#3B82F6", lw=1)
ax.text(14, 9, "Réseau Virtuel Pont Isolé", color="#93C5FD", fontsize=8, fontweight="bold", ha="center")
ax.text(14, 6.2, "Driver bridge : data-platform\nRésolution DNS interne inter-services", color="#CBD5E1", fontsize=7, ha="center")

draw_card(27, 4, 22, 7.5, bg="#0F172A", border="#8B5CF6", lw=1)
ax.text(38, 9, "Persistance par Volumes Managés", color="#C4B5FD", fontsize=8, fontweight="bold", ha="center")
ax.text(38, 6.2, "source_data, warehouse_data, airflow_data,\nsuperset_home, airbyte_data, pgadmin_data", color="#CBD5E1", fontsize=7, ha="center")

draw_card(51, 4, 22, 7.5, bg="#0F172A", border="#10B981", lw=1)
ax.text(62, 9, "15 Services Micro-segmentés", color="#6EE7B7", fontsize=8, fontweight="bold", ha="center")
ax.text(62, 6.2, "docker-compose up -d (7 modules)\nPolitique restart : unless-stopped & healthchecks", color="#CBD5E1", fontsize=7, ha="center")

draw_card(75, 4, 22, 7.5, bg="#0F172A", border="#F59E0B", lw=1)
ax.text(86, 9, "Reproductibilité & Versionnement", color="#FCD34D", fontsize=8, fontweight="bold", ha="center")
ax.text(86, 6.2, "Dépôt Git, variables .env, profils dbt\nZéro divergence entre Dev local et Cloud", color="#CBD5E1", fontsize=7, ha="center")

plt.tight_layout()
plt.savefig(png_path, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()

print(f"[OK] Image PNG architecture générée : {png_path}")

