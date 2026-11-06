"""
Script de génération de l'architecture globale en format draw.io XML :
Fichier produit : report_latex/architecture_globale.drawio.xml
Génère l'architecture complète avec les logos SVG officiels de chaque outil technique.
"""

import os
import urllib.parse
import xml.etree.ElementTree as ET

# Répertoire de sortie
out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "report_latex")
os.makedirs(out_dir, exist_ok=True)
xml_file_path = os.path.join(out_dir, "architecture_globale.drawio.xml")

# -----------------------------------------------------------------------------
# Définition des logos SVG vectoriels ultra-propres et légers (encodés data URI)
# -----------------------------------------------------------------------------
def make_svg_uri(svg_content):
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg_content)

SVGS = {
    "docker": make_svg_uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#2496ED"/><path fill="#ffffff" d="M11 20h4v4h-4zm5 0h4v4h-4zm5 0h4v4h-4zm5 0h4v4h-4zm-10-5h4v4h-4zm5 0h4v4h-4zm5 0h4v4h-4zm5 0h4v4h-4zm-5-5h4v4h-4z"/><path fill="#ffffff" d="M39 24.5c-.8-.5-2.2-.7-3.3-.2-.4-1.2-1.5-2.1-2.9-2.3l-.8.1-.5.7c-.5.7-.9 1.6-1.1 2.6H8c-.6 0-1 .4-1 1 0 5 3.5 9.5 8.7 10.8 7.3 1.8 15.1.3 19.5-3.8 3.5-3.2 4.2-7.5 4.1-8.2l-.3-.5-.6-.2z"/></svg>'''),
    "postgres": make_svg_uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#336791"/><path fill="#ffffff" d="M24 10c-6.6 0-12 5.4-12 12 0 4.1 2.1 7.7 5.3 9.8l1.7-2.6c-2.4-1.6-4-4.2-4-7.2 0-4.9 4-8.9 9-8.9s9 4 9 8.9c0 3-1.6 5.6-4 7.2l1.7 2.6c3.2-2.1 5.3-5.7 5.3-9.8 0-6.6-5.4-12-12-12zm-3 8c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm6 0c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm-3 6c-2.8 0-5 2.2-5 5v5h3v-5c0-1.1.9-2 2-2s2 .9 2 2v5h3v-5c0-2.8-2.2-5-5-5z"/></svg>'''),
    "python": make_svg_uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#1E293B"/><path fill="#387EB8" d="M23.5 10c-5.8 0-5.5 2.5-5.5 2.5l.01 2.6H24v.8h-7.8c-3.6 0-6.2 2.2-6.2 6.2s2.5 6 6.2 6h1.8v-2.6c0-3.6 3.1-3.6 3.1-3.6h5.4c2.8 0 2.5-2.5 2.5-2.5V13.8c0-3.8-5.5-3.8-5.5-3.8zm-1.8 1.9a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/><path fill="#FFE052" d="M24.5 38c5.8 0 5.5-2.5 5.5-2.5l-.01-2.6H24v-.8h7.8c3.6 0 6.2-2.2 6.2-6.2s-2.5-6-6.2-6h-1.8v2.6c0 3.6-3.1 3.6-3.1 3.6h-5.4c-2.8 0-2.5 2.5-2.5 2.5v5.6c0 3.8 5.5 3.8 5.5 3.8zm1.8-1.9a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/></svg>'''),
    "airbyte": make_svg_uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#655CFC"/><path fill="#ffffff" d="M13 28a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm22-8a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm0 15a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm-11-7a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm-8-1.5l5-2.5m5.5-3l5-2.5m-5 8.5l5 2.5" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/></svg>'''),
    "dbt": make_svg_uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#FF694B"/><path fill="#ffffff" d="M24 10l11 11-11 11-11-11 11-11zm0 7l-4 4 4 4 4-4-4-4zm-8 15h16v4H16z"/></svg>'''),
    "snowflake": make_svg_uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#29B5E8"/><path fill="#ffffff" d="M24 8v32m-11-27l22 22m-22 0l22-22m-16 11h32" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round"/><circle cx="24" cy="24" r="3" fill="#ffffff"/></svg>'''),
    "airflow": make_svg_uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#017CEE"/><circle cx="24" cy="24" r="14" fill="none" stroke="#ffffff" stroke-width="3"/><path fill="#ffffff" d="M24 14v10l8 4"/></svg>'''),
    "superset": make_svg_uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#20A39E"/><path fill="#ffffff" d="M12 36h24v3H12zm2-8h6v6h-6zm7-6h6v12h-6zm7-7h6v19h-6z"/></svg>'''),
    "nginx": make_svg_uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#009639"/><path fill="#ffffff" d="M16 13v22l16-22v22h-3.5V19.5L19.5 35H16z"/></svg>'''),
    "pgadmin": make_svg_uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#326690"/><path fill="#ffffff" d="M12 15h24v5H12zm0 7h24v5H12zm0 7h24v5H12z"/><circle cx="16" cy="17.5" r="1.5" fill="#326690"/><circle cx="16" cy="24.5" r="1.5" fill="#326690"/><circle cx="16" cy="31.5" r="1.5" fill="#326690"/></svg>'''),
    "git": make_svg_uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#F05032"/><path fill="#ffffff" d="M34.5 22.1l-8.6-8.6a2 2 0 0 0-2.8 0l-2.1 2.1 3.5 3.5a2.5 2.5 0 0 1 3.2 3.2l3.4 3.4a2.5 2.5 0 1 1-1.4 1.4l-3.2-3.2v6.6a2.5 2.5 0 1 1-2 0v-6.7a2.5 2.5 0 0 1-1.4-3.3l-3.4-3.4-6.1 6.1a2 2 0 0 0 0 2.8l8.6 8.6a2 2 0 0 0 2.8 0l11.5-11.5a2 2 0 0 0 0-2.8z"/></svg>'''),
}

# -----------------------------------------------------------------------------
# Construction du code XML
# -----------------------------------------------------------------------------
xml = ['<mxfile host="app.diagrams.net" modified="2026-11-03T11:00:00.000Z" agent="Antigravity" version="22.0.0" type="device">']
xml.append('  <diagram id="northwind-global-architecture" name="Architecture Globale Modern Data Platform">')
xml.append('    <mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1640" pageHeight="1080" background="#0F172A" math="0" shadow="1">')
xml.append('      <root>')
xml.append('        <mxCell id="0" />')
xml.append('        <mxCell id="1" parent="0" />')

# --- BANNIÈRE TITRE ---
xml.append('''
        <!-- BANNIÈRE SUPÉRIEURE DE TITRE -->
        <mxCell id="main_title_card" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#334155;shadow=1;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="40" y="20" width="1560" height="75" as="geometry" />
        </mxCell>
        <mxCell id="logo_docker_top" value="" style="shape=image;html=1;verticalAlign=top;aspect=fixed;image={docker};" vertex="1" parent="1">
          <mxGeometry x="60" y="32" width="50" height="50" as="geometry" />
        </mxCell>
        <mxCell id="title_text" value="ARCHITECTURE TECHNIQUE GLOBALE — NORTHWIND MODERN DATA PLATFORM" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=18;fontStyle=1;fontColor=#F8FAFC;letterSpacing=0.5;" vertex="1" parent="1">
          <mxGeometry x="125" y="30" width="1050" height="28" as="geometry" />
        </mxCell>
        <mxCell id="subtitle_text" value="Pipeline ELT End-to-End : Source OLTP &amp; Simulateur Python ➔ Ingestion Airbyte ➔ Entrepôt Médaillon dbt Core ➔ Orchestration Airflow ➔ BI Superset &amp; dbt-docs" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=11.5;fontColor=#94A3B8;" vertex="1" parent="1">
          <mxGeometry x="125" y="58" width="1050" height="22" as="geometry" />
        </mxCell>
        <mxCell id="badge_context" value="Tython Venture Studio • ENSET Mohammedia II-BDCC&#xa;Infrastructure Conteneurisée Docker • 15 Services" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#3B82F6;fontFamily=Helvetica;fontSize=10;fontColor=#60A5FA;fontStyle=1;arcSize=12;align=center;" vertex="1" parent="1">
          <mxGeometry x="1200" y="30" width="380" height="52" as="geometry" />
        </mxCell>
'''.format(docker=SVGS["docker"]))

# --- COLONNE 1 : SOURCES TRANSACTIONNELLES & SIMULATION (x=40, w=280) ---
xml.append('''
        <!-- ======================================================== -->
        <!-- COLONNE 1 : SOURCES TRANSACTIONNELLES & SIMULATEUR       -->
        <!-- ======================================================== -->
        <mxCell id="col1_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#334155;strokeWidth=1.5;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="40" y="115" width="280" height="745" as="geometry" />
        </mxCell>
        <mxCell id="col1_hdr" value="1. SOURCES TRANSACTIONNELLES&#xa;&amp; SIMULATEUR DE MARCHÉ" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1D4ED8;strokeColor=none;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#FFFFFF;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="50" y="125" width="260" height="42" as="geometry" />
        </mxCell>

        <!-- Carte Simulateur Python v2.0 -->
        <mxCell id="c1_sim_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#3B82F6;strokeWidth=1.5;arcSize=8;" vertex="1" parent="1">
          <mxGeometry x="55" y="180" width="250" height="240" as="geometry" />
        </mxCell>
        <mxCell id="c1_sim_logo" value="" style="shape=image;html=1;verticalAlign=top;aspect=fixed;image={python};" vertex="1" parent="1">
          <mxGeometry x="68" y="192" width="38" height="38" as="geometry" />
        </mxCell>
        <mxCell id="c1_sim_title" value="Simulateur Marché v2.0&#xa;&lt;font color=&#39;#94A3B8&#39; style=&#39;font-size:10px;&#39;&gt;scripts/data_generator.py&lt;/font&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#F8FAFC;" vertex="1" parent="1">
          <mxGeometry x="115" y="192" width="180" height="38" as="geometry" />
        </mxCell>
        <mxCell id="c1_sim_desc" value="• Génération continue de flux B2B&#xa;• Règle de Pareto (80/20 clients &amp; articles)&#xa;• Commandes volumineuses Tier 1/2&#xa;• Réapprovisionnement automatique&#xa;  sur seuil (units_on_order &gt; 0)&#xa;• Calcul dynamique de fret &amp; remises&#xa;• Transition d&#39;états (Ordered ➔ Shipped)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#334155;fontFamily=Helvetica;fontSize=10;fontColor=#CBD5E1;align=left;spacingLeft=8;" vertex="1" parent="1">
          <mxGeometry x="65" y="240" width="230" height="165" as="geometry" />
        </mxCell>

        <!-- Ligne flux générateur vers source -->
        <mxCell id="edge_gen_to_source" value="Insertions SQL directes&#xa;Transactions continues" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#38BDF8;strokeWidth=2;endArrow=block;endFill=1;fontFamily=Helvetica;fontSize=9.5;fontColor=#38BDF8;labelBackgroundColor=#0F172A;" edge="1" parent="1" source="c1_sim_box" target="c1_src_box">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- Carte Base PostgreSQL Source (OLTP) -->
        <mxCell id="c1_src_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#2563EB;strokeWidth=2;arcSize=8;" vertex="1" parent="1">
          <mxGeometry x="55" y="475" width="250" height="365" as="geometry" />
        </mxCell>
        <mxCell id="c1_src_logo" value="" style="shape=image;html=1;verticalAlign=top;aspect=fixed;image={postgres};" vertex="1" parent="1">
          <mxGeometry x="68" y="488" width="40" height="40" as="geometry" />
        </mxCell>
        <mxCell id="c1_src_title" value="PostgreSQL Source (OLTP)&#xa;&lt;font color=&#39;#38BDF8&#39; style=&#39;font-size:10px;&#39;&gt;Conteneur : postgres-source&lt;/font&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#F8FAFC;" vertex="1" parent="1">
          <mxGeometry x="115" y="488" width="180" height="40" as="geometry" />
        </mxCell>

        <mxCell id="c1_src_spec" value="Port Hôte : 55432:5432&#xa;Base : northwind | User : postgres&#xa;Volume : source_postgresql_data&#xa;Paramètre : wal_level = logical (CDC)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#334155;fontFamily=Helvetica;fontSize=10;fontColor=#93C5FD;align=left;spacingLeft=8;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="65" y="538" width="230" height="70" as="geometry" />
        </mxCell>

        <mxCell id="c1_src_tables" value="14 Tables Relationnelles Source :&#xa;• orders &amp; order_details&#xa;• products &amp; categories&#xa;• customers &amp; employees&#xa;• shippers &amp; suppliers&#xa;• employee_territories&#xa;• customer_demographics&#xa;• us_states, region, territories" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#334155;fontFamily=Helvetica;fontSize=10;fontColor=#CBD5E1;align=left;spacingLeft=8;" vertex="1" parent="1">
          <mxGeometry x="65" y="620" width="230" height="150" as="geometry" />
        </mxCell>

        <mxCell id="c1_src_badge" value="Verrouillage Évité par Architecture ELT" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E3A8A;strokeColor=#3B82F6;fontFamily=Helvetica;fontSize=9.5;fontColor=#BFDBFE;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="65" y="785" width="230" height="35" as="geometry" />
        </mxCell>
'''.format(python=SVGS["python"], postgres=SVGS["postgres"]))

# --- COLONNE 2 : INGESTION & CDC AIRBYTE (x=350, w=250) ---
xml.append('''
        <!-- ======================================================== -->
        <!-- COLONNE 2 : INGESTION ASYNCHRONE & CDC AIRBYTE           -->
        <!-- ======================================================== -->
        <mxCell id="col2_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#334155;strokeWidth=1.5;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="350" y="115" width="250" height="745" as="geometry" />
        </mxCell>
        <mxCell id="col2_hdr" value="2. INGESTION ASYNCHRONE&#xa;&amp; CDC (AIRBYTE CLUSTER)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#6D28D9;strokeColor=none;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#FFFFFF;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="360" y="125" width="230" height="42" as="geometry" />
        </mxCell>

        <mxCell id="c2_ab_main" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#8B5CF6;strokeWidth=2;arcSize=8;" vertex="1" parent="1">
          <mxGeometry x="360" y="180" width="230" height="660" as="geometry" />
        </mxCell>
        <mxCell id="c2_ab_logo" value="" style="shape=image;html=1;verticalAlign=top;aspect=fixed;image={airbyte};" vertex="1" parent="1">
          <mxGeometry x="375" y="195" width="42" height="42" as="geometry" />
        </mxCell>
        <mxCell id="c2_ab_title" value="Airbyte v0.50.36&#xa;&lt;font color=&#39;#A78BFA&#39; style=&#39;font-size:10px;&#39;&gt;Interface Web : Port 8000&lt;/font&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=12.5;fontStyle=1;fontColor=#F8FAFC;" vertex="1" parent="1">
          <mxGeometry x="425" y="195" width="155" height="42" as="geometry" />
        </mxCell>

        <mxCell id="c2_ab_sub1" value="🖥️ airbyte-webapp (Port 8000:80)&#xa;IHM de configuration des connexions" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#475569;fontFamily=Helvetica;fontSize=10;fontColor=#E2E8F0;align=left;spacingLeft=8;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="370" y="250" width="210" height="45" as="geometry" />
        </mxCell>
        <mxCell id="c2_ab_sub2" value="⚙️ airbyte-server (Port 8001)&#xa;Moteur API &amp; orchestrateur de jobs" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#475569;fontFamily=Helvetica;fontSize=10;fontColor=#E2E8F0;align=left;spacingLeft=8;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="370" y="305" width="210" height="45" as="geometry" />
        </mxCell>
        <mxCell id="c2_ab_sub3" value="⚡ airbyte-worker (Docker Sock)&#xa;Conteneurs éphémères source/dest" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#475569;fontFamily=Helvetica;fontSize=10;fontColor=#E2E8F0;align=left;spacingLeft=8;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="370" y="360" width="210" height="45" as="geometry" />
        </mxCell>
        <mxCell id="c2_ab_sub4" value="🔄 airbyte-temporal (Port 7233)&#xa;Gestionnaire de flux &amp; reprises" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#475569;fontFamily=Helvetica;fontSize=10;fontColor=#E2E8F0;align=left;spacingLeft=8;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="370" y="415" width="210" height="45" as="geometry" />
        </mxCell>
        <mxCell id="c2_ab_sub5" value="💾 airbyte-db (PostgreSQL 13)&#xa;Métadonnées d&#39;état de réplication" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#475569;fontFamily=Helvetica;fontSize=10;fontColor=#E2E8F0;align=left;spacingLeft=8;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="370" y="470" width="210" height="45" as="geometry" />
        </mxCell>

        <mxCell id="c2_ab_modes" value="Modalités de Réplication :&#xa;• Mode : Incremental Sync (CDC)&#xa;• Typage : Append + Deduped&#xa;• Débit : Zero Impact sur les ventes&#xa;• Audit : Ajout colonnes méta :&#xa;  - _airbyte_raw_id&#xa;  - _airbyte_extracted_at&#xa;  - _airbyte_meta" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#6D28D9;fontFamily=Helvetica;fontSize=10;fontColor=#DDD6FE;align=left;spacingLeft=8;" vertex="1" parent="1">
          <mxGeometry x="370" y="530" width="210" height="165" as="geometry" />
        </mxCell>

        <mxCell id="c2_ab_badge" value="Chargement Direct dans Bronze (DWH)&#xa;Sans transformation préalable (ELT)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2E1065;strokeColor=#8B5CF6;fontFamily=Helvetica;fontSize=9.5;fontColor=#E9D5FF;fontStyle=1;align=center;" vertex="1" parent="1">
          <mxGeometry x="370" y="785" width="210" height="35" as="geometry" />
        </mxCell>
'''.format(airbyte=SVGS["airbyte"]))

# --- FLUX 1 -> 2 ---
xml.append('''
        <!-- Connexion Source vers Airbyte -->
        <mxCell id="edge_src_to_ab" value="Extraction CDC&#xa;(Port 5432)" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#8B5CF6;strokeWidth=2.5;endArrow=block;endFill=1;fontFamily=Helvetica;fontSize=10;fontColor=#C4B5FD;labelBackgroundColor=#0F172A;" edge="1" parent="1" source="c1_src_box" target="c2_ab_main">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
''')

# --- COLONNE 3 : DATA WAREHOUSE & ARCHITECTURE MÉDAILLON DBT (x=630, w=440) ---
xml.append('''
        <!-- ======================================================== -->
        <!-- COLONNE 3 : ENTREPÔT DE DONNÉES & ARCHITECTURE MÉDAILLON -->
        <!-- ======================================================== -->
        <mxCell id="col3_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#334155;strokeWidth=1.5;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="630" y="115" width="440" height="745" as="geometry" />
        </mxCell>
        <mxCell id="col3_hdr" value="3. ENTREPÔT DE DONNÉES BIVALENT &amp; ARCHITECTURE MÉDAILLON (DBT CORE)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F766E;strokeColor=none;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#FFFFFF;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="640" y="125" width="420" height="42" as="geometry" />
        </mxCell>

        <!-- Deux Moteurs DWH : PostgreSQL OLAP & Snowflake -->
        <mxCell id="c3_dwh_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#14B8A6;strokeWidth=1.5;arcSize=8;" vertex="1" parent="1">
          <mxGeometry x="640" y="175" width="420" height="75" as="geometry" />
        </mxCell>
        <mxCell id="c3_dwh_logo1" value="" style="shape=image;html=1;verticalAlign=top;aspect=fixed;image={postgres};" vertex="1" parent="1">
          <mxGeometry x="652" y="185" width="35" height="35" as="geometry" />
        </mxCell>
        <mxCell id="c3_dwh_txt1" value="PostgreSQL Warehouse (OLAP)&#xa;&lt;font color=&#39;#2DD4BF&#39; style=&#39;font-size:9.5px;&#39;&gt;Port 55433:5432 • Volume warehouse_data&lt;/font&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=11;fontStyle=1;fontColor=#F8FAFC;" vertex="1" parent="1">
          <mxGeometry x="692" y="185" width="165" height="35" as="geometry" />
        </mxCell>
        <mxCell id="c3_dwh_logo2" value="" style="shape=image;html=1;verticalAlign=top;aspect=fixed;image={snowflake};" vertex="1" parent="1">
          <mxGeometry x="865" y="185" width="35" height="35" as="geometry" />
        </mxCell>
        <mxCell id="c3_dwh_txt2" value="Snowflake Data Cloud&#xa;&lt;font color=&#39;#38BDF8&#39; style=&#39;font-size:9.5px;&#39;&gt;DWH MPP Cloud Enterprise (Target)&lt;/font&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=11;fontStyle=1;fontColor=#F8FAFC;" vertex="1" parent="1">
          <mxGeometry x="905" y="185" width="145" height="35" as="geometry" />
        </mxCell>

        <!-- NIVEAU BRONZE -->
        <mxCell id="c3_bronze_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#B45309;strokeWidth=1.5;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="640" y="260" width="420" height="95" as="geometry" />
        </mxCell>
        <mxCell id="c3_bronze_badge" value="COUCHE BRONZE (RAW LAKE)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#B45309;strokeColor=none;fontFamily=Helvetica;fontSize=10;fontStyle=1;fontColor=#FFFFFF;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="650" y="268" width="180" height="20" as="geometry" />
        </mxCell>
        <mxCell id="c3_bronze_desc" value="14 Tables Brutes répliquées par Airbyte (Append only) :&#xa;• Schéma bronze.* (orders, order_details, products, customers...)&#xa;• Métadonnées d&#39;ingestion intégrées (_airbyte_raw_id, _airbyte_extracted_at)&#xa;• Données conservées sans altération pour rejeu et traçabilité" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=9.5;fontColor=#FDE68A;" vertex="1" parent="1">
          <mxGeometry x="650" y="290" width="400" height="58" as="geometry" />
        </mxCell>

        <!-- Ligne Bronze -> Silver -->
        <mxCell id="edge_brz_slv" value="dbt run --select silver.*" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#94A3B8;strokeWidth=1.8;endArrow=block;endFill=1;fontFamily=Helvetica;fontSize=9;fontColor=#94A3B8;labelBackgroundColor=#0F172A;" edge="1" parent="1" source="c3_bronze_box" target="c3_silver_box">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- NIVEAU SILVER & SNAPSHOTS SCD2 -->
        <mxCell id="c3_silver_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#64748B;strokeWidth=1.5;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="640" y="375" width="420" height="150" as="geometry" />
        </mxCell>
        <mxCell id="c3_silver_badge" value="COUCHE SILVER (CLEANED &amp; CONFORMED) &amp; SNAPSHOTS SCD TYPE 2" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#475569;strokeColor=none;fontFamily=Helvetica;fontSize=10;fontStyle=1;fontColor=#FFFFFF;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="650" y="383" width="400" height="20" as="geometry" />
        </mxCell>
        <mxCell id="c3_silver_desc" value="12 Vues SQL dbt de Nettoyage &amp; Normalisation :&#xa;• Standardisation des types, trim des chaînes, remplacement des NULLs&#xa;• Tables référentielles (Seeds) : country_region_mapping, discount_tiers&#xa;&#xa;SCD Type 2 (Snapshots dbt avec valid_from / valid_to) :&#xa;• products_snapshot (variations historiques des tarifs de vente)&#xa;• customers_snapshot (changements d&#39;adresse / contact)&#xa;• orders_snapshot (cycles de vie et états de commandes)" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=9.5;fontColor=#E2E8F0;" vertex="1" parent="1">
          <mxGeometry x="650" y="405" width="400" height="115" as="geometry" />
        </mxCell>

        <!-- Ligne Silver -> Gold -->
        <mxCell id="edge_slv_gld" value="dbt run --select gold.*" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#F59E0B;strokeWidth=2;endArrow=block;endFill=1;fontFamily=Helvetica;fontSize=9;fontColor=#FCD34D;labelBackgroundColor=#0F172A;" edge="1" parent="1" source="c3_silver_box" target="c3_gold_box">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- NIVEAU GOLD & MARTS -->
        <mxCell id="c3_gold_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#D97706;strokeWidth=2;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="640" y="545" width="420" height="225" as="geometry" />
        </mxCell>
        <mxCell id="c3_gold_badge" value="COUCHE GOLD (STAR SCHEMA KIMBALL &amp; 5 DATA MARTS)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#D97706;strokeColor=none;fontFamily=Helvetica;fontSize=10.5;fontStyle=1;fontColor=#FFFFFF;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="650" y="553" width="400" height="22" as="geometry" />
        </mxCell>
        <mxCell id="c3_gold_fact" value="★ Table de Faits Centrale : fact_sales (Granularité ligne de commande)&#xa;   Clés Substituts SK • CA Brut • Montant Remise • CA Net • Délais Livraison" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#F59E0B;fontFamily=Helvetica;fontSize=9.5;fontColor=#FEF3C7;align=left;spacingLeft=8;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="650" y="582" width="400" height="36" as="geometry" />
        </mxCell>
        <mxCell id="c3_gold_dims" value="Dimensions Conformes : dim_customers, dim_products, dim_employees,&#xa;dim_date (calendrier 1996-2026), dim_shippers, dim_suppliers, bridge_employee_territories" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#475569;fontFamily=Helvetica;fontSize=9.5;fontColor=#CBD5E1;align=left;spacingLeft=8;" vertex="1" parent="1">
          <mxGeometry x="650" y="624" width="400" height="34" as="geometry" />
        </mxCell>
        <mxCell id="c3_gold_marts" value="5 Data Marts Métiers Prêts pour la BI :&#xa;1. mart_sales_summary (Revenus globaux, TVA, remises mensuelles)&#xa;2. mart_customer_segments (Segmentation marketing RFM Champions/Lost)&#xa;3. mart_product_performance (Rotation des stocks, Price Gap catalogue)&#xa;4. mart_employee_performance (Leaderboard vendeurs &amp; objectifs)&#xa;5. mart_shipping_performance (Taux de respect SLA transporteurs)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#10B981;fontFamily=Helvetica;fontSize=9.5;fontColor=#A7F3D0;align=left;spacingLeft=8;" vertex="1" parent="1">
          <mxGeometry x="650" y="664" width="400" height="98" as="geometry" />
        </mxCell>

        <!-- BADGE TESTS AUTOMATISÉS -->
        <mxCell id="c3_tests_badge" value="🛡️ Suite de 121 Tests dbt Automatisés (0 Échec) : Unicité, Non-Null, FK, Intégrité Comptable" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#065F46;strokeColor=#10B981;fontFamily=Helvetica;fontSize=9.5;fontColor=#ECFDF5;fontStyle=1;align=center;" vertex="1" parent="1">
          <mxGeometry x="640" y="785" width="420" height="35" as="geometry" />
        </mxCell>
'''.format(postgres=SVGS["postgres"], snowflake=SVGS["snowflake"]))

# --- FLUX 2 -> 3 ---
xml.append('''
        <!-- Connexion Airbyte vers Warehouse Bronze -->
        <mxCell id="edge_ab_to_dwh" value="Chargement Bronze&#xa;(Port 55433 / Cloud)" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#10B981;strokeWidth=2.5;endArrow=block;endFill=1;fontFamily=Helvetica;fontSize=10;fontColor=#6EE7B7;labelBackgroundColor=#0F172A;" edge="1" parent="1" source="c2_ab_main" target="c3_bronze_box">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
''')

# --- COLONNE 4 : ORCHESTRATION APACHE AIRFLOW (x=1090, w=240) ---
xml.append('''
        <!-- ======================================================== -->
        <!-- COLONNE 4 : ORCHESTRATION APACHE AIRFLOW                 -->
        <!-- ======================================================== -->
        <mxCell id="col4_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#334155;strokeWidth=1.5;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="1090" y="115" width="240" height="745" as="geometry" />
        </mxCell>
        <mxCell id="col4_hdr" value="4. ORCHESTRATION &amp; QUALITÉ&#xa;(APACHE AIRFLOW 2.x)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0284C7;strokeColor=none;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#FFFFFF;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="1100" y="125" width="220" height="42" as="geometry" />
        </mxCell>

        <mxCell id="c4_af_main" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#0284C7;strokeWidth=2;arcSize=8;" vertex="1" parent="1">
          <mxGeometry x="1100" y="180" width="220" height="640" as="geometry" />
        </mxCell>
        <mxCell id="c4_af_logo" value="" style="shape=image;html=1;verticalAlign=top;aspect=fixed;image={airflow};" vertex="1" parent="1">
          <mxGeometry x="1112" y="192" width="40" height="40" as="geometry" />
        </mxCell>
        <mxCell id="c4_af_title" value="Apache Airflow&#xa;&lt;font color=&#39;#38BDF8&#39; style=&#39;font-size:10px;&#39;&gt;Port 8081:8080 (Web UI)&lt;/font&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#F8FAFC;" vertex="1" parent="1">
          <mxGeometry x="1160" y="192" width="150" height="40" as="geometry" />
        </mxCell>

        <mxCell id="c4_af_spec" value="Scheduler : Port 8586&#xa;Base Meta : postgres-airflow:5432&#xa;DAG : northwind_dbt_pipeline&#xa;Fréquence : 0 2 * * * (02:00 UTC)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#0369A1;fontFamily=Helvetica;fontSize=9.5;fontColor=#BAE6FD;align=left;spacingLeft=8;" vertex="1" parent="1">
          <mxGeometry x="1110" y="242" width="200" height="65" as="geometry" />
        </mxCell>

        <!-- Séquence des 10 tâches du DAG -->
        <mxCell id="c4_af_dag_hdr" value="Séquence DAG (10 Tâches) :" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=10;fontStyle=1;fontColor=#F8FAFC;" vertex="1" parent="1">
          <mxGeometry x="1110" y="315" width="200" height="18" as="geometry" />
        </mxCell>

        <mxCell id="t_t1" value="1. bronze_freshness_check (SLA &lt;24h)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#10B981;fontFamily=Helvetica;fontSize=8.5;fontColor=#A7F3D0;align=left;spacingLeft=5;" vertex="1" parent="1">
          <mxGeometry x="1110" y="335" width="200" height="26" as="geometry" />
        </mxCell>
        <mxCell id="t_t2" value="2. dbt_deps (Packages dbt-utils)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#475569;fontFamily=Helvetica;fontSize=8.5;fontColor=#CBD5E1;align=left;spacingLeft=5;" vertex="1" parent="1">
          <mxGeometry x="1110" y="367" width="200" height="26" as="geometry" />
        </mxCell>
        <mxCell id="t_t3" value="3. dbt_seed (country &amp; discount tiers)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#475569;fontFamily=Helvetica;fontSize=8.5;fontColor=#CBD5E1;align=left;spacingLeft=5;" vertex="1" parent="1">
          <mxGeometry x="1110" y="399" width="200" height="26" as="geometry" />
        </mxCell>
        <mxCell id="t_t4" value="4. dbt_run_silver (12 vues nettoyées)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#38BDF8;fontFamily=Helvetica;fontSize=8.5;fontColor=#BAE6FD;align=left;spacingLeft=5;" vertex="1" parent="1">
          <mxGeometry x="1110" y="431" width="200" height="26" as="geometry" />
        </mxCell>
        <mxCell id="t_t5" value="5. dbt_test_silver (Intégrité Silver)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#10B981;fontFamily=Helvetica;fontSize=8.5;fontColor=#A7F3D0;align=left;spacingLeft=5;" vertex="1" parent="1">
          <mxGeometry x="1110" y="463" width="200" height="26" as="geometry" />
        </mxCell>
        <mxCell id="t_t6" value="6. dbt_snapshot (SCD Type 2)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#8B5CF6;fontFamily=Helvetica;fontSize=8.5;fontColor=#DDD6FE;align=left;spacingLeft=5;" vertex="1" parent="1">
          <mxGeometry x="1110" y="495" width="200" height="26" as="geometry" />
        </mxCell>
        <mxCell id="t_t7" value="7. dbt_run_gold (Étoile &amp; 5 Marts)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#F59E0B;fontFamily=Helvetica;fontSize=8.5;fontColor=#FDE68A;align=left;spacingLeft=5;" vertex="1" parent="1">
          <mxGeometry x="1110" y="527" width="200" height="26" as="geometry" />
        </mxCell>
        <mxCell id="t_t8" value="8. dbt_test_gold (121 tests passants)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#10B981;fontFamily=Helvetica;fontSize=8.5;fontColor=#A7F3D0;align=left;spacingLeft=5;" vertex="1" parent="1">
          <mxGeometry x="1110" y="559" width="200" height="26" as="geometry" />
        </mxCell>
        <mxCell id="t_t9" value="9. dbt_docs_generate (Catalogue)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#059669;fontFamily=Helvetica;fontSize=8.5;fontColor=#A7F3D0;align=left;spacingLeft=5;" vertex="1" parent="1">
          <mxGeometry x="1110" y="591" width="200" height="26" as="geometry" />
        </mxCell>
        <mxCell id="t_t10" value="10. superset_sync_dashboards (REST)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#14B8A6;fontFamily=Helvetica;fontSize=8.5;fontColor=#99F6E4;align=left;spacingLeft=5;" vertex="1" parent="1">
          <mxGeometry x="1110" y="623" width="200" height="26" as="geometry" />
        </mxCell>

        <mxCell id="c4_af_badge" value="Orchestration End-to-End&#xa;Gestion Automatisée des Échecs &amp; Retries" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#075985;strokeColor=#38BDF8;fontFamily=Helvetica;fontSize=9.5;fontColor=#E0F2FE;fontStyle=1;align=center;" vertex="1" parent="1">
          <mxGeometry x="1110" y="785" width="200" height="35" as="geometry" />
        </mxCell>
'''.format(airflow=SVGS["airflow"]))

# --- FLUX 3 -> 4 ---
xml.append('''
        <!-- Pilotage dbt par Airflow -->
        <mxCell id="edge_af_to_dbt" value="Exécution dbt CLI&#xa;&amp; Tests Qualité" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#0284C7;strokeWidth=2;endArrow=block;endFill=1;fontFamily=Helvetica;fontSize=9.5;fontColor=#38BDF8;labelBackgroundColor=#0F172A;" edge="1" parent="1" source="col4_box" target="col3_box">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
''')

# --- COLONNE 5 : RESTITUTION BI & GOUVERNANCE (x=1350, w=250) ---
xml.append('''
        <!-- ======================================================== -->
        <!-- COLONNE 5 : RESTITUTION DÉCISIONNELLE & GOUVERNANCE      -->
        <!-- ======================================================== -->
        <mxCell id="col5_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#334155;strokeWidth=1.5;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="1350" y="115" width="250" height="745" as="geometry" />
        </mxCell>
        <mxCell id="col5_hdr" value="5. RESTITUTION DÉCISIONNELLE&#xa;&amp; GOUVERNANCE (SUPERSET)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0D9488;strokeColor=none;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#FFFFFF;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="1360" y="125" width="230" height="42" as="geometry" />
        </mxCell>

        <!-- APACHE SUPERSET 6.0 -->
        <mxCell id="c5_sup_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#14B8A6;strokeWidth=2;arcSize=8;" vertex="1" parent="1">
          <mxGeometry x="1360" y="180" width="230" height="340" as="geometry" />
        </mxCell>
        <mxCell id="c5_sup_logo" value="" style="shape=image;html=1;verticalAlign=top;aspect=fixed;image={superset};" vertex="1" parent="1">
          <mxGeometry x="1372" y="192" width="38" height="38" as="geometry" />
        </mxCell>
        <mxCell id="c5_sup_title" value="Apache Superset 6.0&#xa;&lt;font color=&#39;#2DD4BF&#39; style=&#39;font-size:10px;&#39;&gt;Port 8088:8088 (Web UI)&lt;/font&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#F8FAFC;" vertex="1" parent="1">
          <mxGeometry x="1420" y="192" width="160" height="38" as="geometry" />
        </mxCell>

        <mxCell id="c5_sup_desc" value="Dashboard Exécutif B2B Analytics :&#xa;• 14 Visualisations synchronisées API REST&#xa;• 6 Cartes KPIs : CA Net, CA Brut,&#xa;  Commandes, Articles, Panier Moyen, Retard&#xa;• Graphique de tendance temporelle mensuelle&#xa;• Segmentation RFM (Donut Chart)&#xa;• Tableau Stock &amp; Gap Prix Catalogue&#xa;• Leaderboard Employés &amp; Performance" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#0F766E;fontFamily=Helvetica;fontSize=9.5;fontColor=#CCFBF1;align=left;spacingLeft=8;" vertex="1" parent="1">
          <mxGeometry x="1370" y="240" width="210" height="150" as="geometry" />
        </mxCell>

        <mxCell id="c5_sup_badge" value="Dataset Connecté sur Marts Gold&#xa;Requêtes OLAP &lt; 80ms" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#134E4A;strokeColor=#14B8A6;fontFamily=Helvetica;fontSize=9.5;fontColor=#5EEAD4;fontStyle=1;align=center;" vertex="1" parent="1">
          <mxGeometry x="1370" y="405" width="210" height="35" as="geometry" />
        </mxCell>

        <!-- SERVEUR NGINX : PORTAIL DBT DOCS -->
        <mxCell id="c5_nginx_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#10B981;strokeWidth=1.5;arcSize=8;" vertex="1" parent="1">
          <mxGeometry x="1360" y="455" width="230" height="165" as="geometry" />
        </mxCell>
        <mxCell id="c5_nginx_logo" value="" style="shape=image;html=1;verticalAlign=top;aspect=fixed;image={nginx};" vertex="1" parent="1">
          <mxGeometry x="1372" y="468" width="38" height="38" as="geometry" />
        </mxCell>
        <mxCell id="c5_nginx_title" value="Portail dbt-docs (Nginx)&#xa;&lt;font color=&#39;#34D399&#39; style=&#39;font-size:10px;&#39;&gt;Port 8085:80 (Web UI)&lt;/font&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#F8FAFC;" vertex="1" parent="1">
          <mxGeometry x="1420" y="468" width="160" height="38" as="geometry" />
        </mxCell>
        <mxCell id="c5_nginx_desc" value="• Catalogue interactif des données&#xa;• Graphe de lignage complet (Lineage DAG)&#xa;• Dictionnaire des tables et colonnes&#xa;• Visualisation des nœuds Exposures" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=9.5;fontColor=#A7F3D0;" vertex="1" parent="1">
          <mxGeometry x="1370" y="515" width="210" height="65" as="geometry" />
        </mxCell>

        <!-- CONSOLE D'ADMINISTRATION PGADMIN 4 -->
        <mxCell id="c5_pgad_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#38BDF8;strokeWidth=1.5;arcSize=8;" vertex="1" parent="1">
          <mxGeometry x="1360" y="635" width="230" height="140" as="geometry" />
        </mxCell>
        <mxCell id="c5_pgad_logo" value="" style="shape=image;html=1;verticalAlign=top;aspect=fixed;image={pgadmin};" vertex="1" parent="1">
          <mxGeometry x="1372" y="647" width="38" height="38" as="geometry" />
        </mxCell>
        <mxCell id="c5_pgad_title" value="pgAdmin 4 (DBA Console)&#xa;&lt;font color=&#39;#38BDF8&#39; style=&#39;font-size:10px;&#39;&gt;Port 5051:5050 (Web UI)&lt;/font&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#F8FAFC;" vertex="1" parent="1">
          <mxGeometry x="1420" y="647" width="160" height="38" as="geometry" />
        </mxCell>
        <mxCell id="c5_pgad_desc" value="• Inspection interactive SQL&#xa;• Monitoring des verrous OLTP &amp; OLAP&#xa;• Validation visuelle des données répliquées" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Helvetica;fontSize=9.5;fontColor=#BAE6FD;" vertex="1" parent="1">
          <mxGeometry x="1370" y="692" width="210" height="50" as="geometry" />
        </mxCell>

        <mxCell id="c5_bi_badge" value="Décisionnel &amp; Gouvernance Déployés" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#064E3B;strokeColor=#10B981;fontFamily=Helvetica;fontSize=9.5;fontColor=#A7F3D0;fontStyle=1;align=center;" vertex="1" parent="1">
          <mxGeometry x="1360" y="785" width="230" height="35" as="geometry" />
        </mxCell>
'''.format(superset=SVGS["superset"], nginx=SVGS["nginx"], pgadmin=SVGS["pgadmin"]))

# --- FLUX 3 -> 5 ---
xml.append('''
        <!-- Connexion Gold vers Superset -->
        <mxCell id="edge_gold_to_sup" value="Requêtes Analytiques BI&#xa;(Gold Marts)" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#14B8A6;strokeWidth=2.5;endArrow=block;endFill=1;fontFamily=Helvetica;fontSize=10;fontColor=#5EEAD4;labelBackgroundColor=#0F172A;" edge="1" parent="1" source="c3_gold_box" target="c5_sup_box">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <!-- Connexion dbt docs vers Nginx -->
        <mxCell id="edge_dbt_to_nginx" value="Volume target/&#xa;(HTML/JSON)" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#10B981;strokeWidth=1.8;endArrow=block;endFill=1;fontFamily=Helvetica;fontSize=9;fontColor=#6EE7B7;labelBackgroundColor=#0F172A;" edge="1" parent="1" source="c3_silver_box" target="c5_nginx_box">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
''')

# --- BANDEAU INFÉRIEUR : COUCHE INFRASTRUCTURE DOCKER (x=40, w=1560) ---
xml.append('''
        <!-- ======================================================== -->
        <!-- BANDEAU INFÉRIEUR : INFRASTRUCTURE CONTENEURISÉE DOCKER  -->
        <!-- ======================================================== -->
        <mxCell id="infra_bg" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#334155;strokeWidth=1.5;shadow=1;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="40" y="875" width="1560" height="150" as="geometry" />
        </mxCell>
        <mxCell id="infra_badge" value="COUCHE D&#39;INFRASTRUCTURE CONTENEURISÉE DOCKER &amp; RÉSEAU VIRTUEL ISOLÉ" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#2496ED;fontFamily=Helvetica;fontSize=11;fontStyle=1;fontColor=#60A5FA;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="540" y="887" width="560" height="26" as="geometry" />
        </mxCell>

        <!-- 4 Cartouches Techniques Infra -->
        <mxCell id="inf_b1" value="🌐 RÉSEAU VIRTUEL ISOLÉ&#xa;Driver : bridge | Nom : data-platform&#xa;Résolution DNS interne inter-conteneurs&#xa;Isolation étanche des flux inter-services" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#3B82F6;fontFamily=Helvetica;fontSize=10;fontColor=#BFDBFE;align=left;spacingLeft=10;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="60" y="925" width="350" height="80" as="geometry" />
        </mxCell>

        <mxCell id="inf_b2" value="💾 VOLUMES PERSISTANTS MANAGÉS&#xa;• source_postgresql_data (Données OLTP)&#xa;• warehouse_warehouse_data (Entrepôt OLAP)&#xa;• airflow_data &amp; superset_home (États)&#xa;• airbyte_workspace &amp; airbyte_db_data" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#8B5CF6;fontFamily=Helvetica;fontSize=9.5;fontColor=#DDD6FE;align=left;spacingLeft=10;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="430" y="925" width="360" height="80" as="geometry" />
        </mxCell>

        <mxCell id="inf_b3" value="🐳 15 SERVICES CONTENEURISÉS DOCKER&#xa;docker compose -f docker-compose.yml up -d&#xa;7 Fichiers Compose inclus (postgres, airflow,&#xa;airbyte, superset, dbt_docs, pgadmin, infra)&#xa;Politique restart : unless-stopped &amp; healthchecks" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#10B981;fontFamily=Helvetica;fontSize=9.5;fontColor=#A7F3D0;align=left;spacingLeft=10;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="810" y="925" width="370" height="80" as="geometry" />
        </mxCell>

        <mxCell id="inf_b4" value="🚀 GOUVERNANCE CI/CD &amp; GIT&#xa;Dépôt Git versionné, profils dbt isolés&#xa;Validation de schéma automatisée&#xa;Reproductibilité intégrale multi-environnements&#xa;Dev (PostgreSQL Local) ➔ Prod (Snowflake)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#F59E0B;fontFamily=Helvetica;fontSize=9.5;fontColor=#FDE68A;align=left;spacingLeft=10;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="1200" y="925" width="380" height="80" as="geometry" />
        </mxCell>
''')

xml.append('      </root>')
xml.append('    </mxGraphModel>')
xml.append('  </diagram>')
xml.append('</mxfile>')

full_xml = "\n".join(xml)

# Validation XML
ET.fromstring(full_xml)
print("[OK] XML valide et bien formé !")

# Sauvegarde
with open(xml_file_path, "w", encoding="utf-8") as f:
    f.write(full_xml)

print(f"[OK] Fichier enregistré : {xml_file_path}")
print(f"Taille du fichier : {len(full_xml)} octets")

