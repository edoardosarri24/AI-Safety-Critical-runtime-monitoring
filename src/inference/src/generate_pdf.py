# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pandas",
#     "matplotlib",
#     "reportlab"
# ]
# ///

import os
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf():
    csv_path = 'data/telemetry.csv'
    pdf_path = 'data/simulation_results.pdf'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)

    # 1. Generate Distance Plot
    plt.figure(figsize=(6.5, 3))
    plt.plot(df['time'], df['distance'], label='Distanza Reale', color='#1f77b4', linewidth=2)
    plt.plot(df['time'], df['critical_distance'], label='Distanza Critica', color='#d62728', linestyle='--', linewidth=1.5)
    
    # Highlight RTA active zones
    rta_active = False
    start_time = 0
    for i in range(len(df)):
        if df.loc[i, 'rta_active'] == 1 and not rta_active:
            rta_active = True
            start_time = df.loc[i, 'time']
        elif (df.loc[i, 'rta_active'] == 0 or i == len(df) - 1) and rta_active:
            rta_active = False
            plt.axvspan(start_time, df.loc[i, 'time'], color='#ffcccc', alpha=0.6, label='Intervento RTA' if 'Intervento RTA' not in plt.gca().get_legend_handles_labels()[1] else "")

    plt.title('Andamento delle Distanze Ego vs Leader', fontsize=12, fontweight='bold', pad=10)
    plt.xlabel('Tempo (s)', fontsize=10)
    plt.ylabel('Distanza (m)', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plot_dist_path = 'data/plot_distance.png'
    plt.savefig(plot_dist_path, dpi=200)
    plt.close()

    # 2. Generate Velocity Plot
    plt.figure(figsize=(6.5, 3))
    plt.plot(df['time'], df['ego_velocity'], label='Velocità Ego', color='#2ca02c', linewidth=2)
    plt.plot(df['time'], df['leader_velocity'], label='Velocità Leader', color='#ff7f0e', linewidth=2)
    plt.title('Andamento delle Velocità', fontsize=12, fontweight='bold', pad=10)
    plt.xlabel('Tempo (s)', fontsize=10)
    plt.ylabel('Velocità (m/s)', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plot_vel_path = 'data/plot_velocity.png'
    plt.savefig(plot_vel_path, dpi=200)
    plt.close()

    # Calculate summary metrics
    total_ticks = len(df)
    total_time = df['time'].iloc[-1] if total_ticks > 0 else 0.0
    rta_calls = int(df['rta_active'].sum())
    ai_calls = total_ticks - rta_calls
    rta_percentage = (rta_calls * 100.0) / total_ticks if total_ticks > 0 else 0.0
    min_dist = df['distance'].min()
    max_dist = df['distance'].max()
    avg_dist = df['distance'].mean()
    max_ego_vel = df['ego_velocity'].max()
    avg_ego_vel = df['ego_velocity'].mean()
    
    # Calculate Jerk (change in acceleration)
    df['jerk'] = df['acceleration'].diff().abs()
    avg_jerk = df['jerk'].mean() if len(df) > 1 else 0.0

    # Determine final outcome
    final_distance = df['distance'].iloc[-1]
    if final_distance <= 0.0:
        outcome = "COLLISIONE RILEVATA!"
        outcome_color = colors.HexColor('#d62728')
    elif final_distance >= 50.0:
        outcome = "VEICOLO LEADER PERSO (Inseguimento fallito)"
        outcome_color = colors.HexColor('#e08b00')
    else:
        outcome = "SIMULAZIONE COMPLETATA CON SUCCESSO!"
        outcome_color = colors.HexColor('#2ca02c')

    # 3. Create PDF Report
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#2b6cb0'),
        spaceBefore=10,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2d3748')
    )
    outcome_style = ParagraphStyle(
        'OutcomeText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=outcome_color
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("ADAS Runtime Assurance (RTA) Report", title_style))
    story.append(Paragraph("<b>Modulo di Analisi e Certificazione di Sicurezza Funzionale (ISO 5469 Class II)</b>", body_style))
    story.append(Spacer(1, 15))

    # Outcome Banner Table
    outcome_data = [
        [Paragraph(f"<b>ESITO SIMULAZIONE:</b>", outcome_style), Paragraph(outcome, outcome_style)]
    ]
    outcome_table = Table(outcome_data, colWidths=[150, 380])
    outcome_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f7fafc')),
        ('BOX', (0,0), (-1,-1), 1.5, outcome_color),
        ('PADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(outcome_table)
    story.append(Spacer(1, 15))

    # Metrics Table
    story.append(Paragraph("Metriche Prestazionali di Inseguimento", section_style))
    metrics_data = [
        [Paragraph("<b>Metrica</b>", body_style), Paragraph("<b>Valore</b>", body_style), Paragraph("<b>Metrica</b>", body_style), Paragraph("<b>Valore</b>", body_style)],
        [Paragraph("Tempo Totale", body_style), f"{total_time:.2f} s ({total_ticks} tick)", Paragraph("Decisioni AI", body_style), f"{ai_calls} ({100.0 - rta_percentage:.1f}%)"],
        [Paragraph("Interventi RTA (Safety)", body_style), f"{rta_calls} ({rta_percentage:.1f}%)", Paragraph("Distanza Minima", body_style), f"{min_dist:.2f} m"],
        [Paragraph("Distanza Media", body_style), f"{avg_dist:.2f} m (Target: 10m)", Paragraph("Distanza Massima", body_style), f"{max_dist:.2f} m"],
        [Paragraph("Velocità Ego Massima", body_style), f"{max_ego_vel:.2f} m/s ({max_ego_vel*3.6:.1f} km/h)", Paragraph("Velocità Ego Media", body_style), f"{avg_ego_vel:.2f} m/s ({avg_ego_vel*3.6:.1f} km/h)"],
        [Paragraph("Jerk Medio (Comfort)", body_style), f"{avg_jerk:.3f} m/s³", Paragraph("Configurazione Modello", body_style), "adas_model.onnx"]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[140, 125, 140, 125])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#edf2f7')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 15))

    # Add Plots
    story.append(Paragraph("Grafico Telemetria Distanze", section_style))
    story.append(Image(plot_dist_path, width=530, height=245))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Grafico Telemetria Velocità", section_style))
    story.append(Image(plot_vel_path, width=530, height=245))

    # Build PDF
    doc.build(story)

    # Clean up temporary plots
    try:
        os.remove(plot_dist_path)
        os.remove(plot_vel_path)
    except OSError:
        pass

    print(f"PDF successfully generated at: {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
