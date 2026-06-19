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

    # Read file
    csv_path = 'data/telemetry.csv'
    pdf_path = 'data/simulation_results.pdf'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        exit(1)
    df = pd.read_csv(csv_path)

    # Retrives the max distance parameter.
    try:
        headeglobal_parameters_path = 'src/inference/include/global_parameters.hpp'
        if os.path.exists(headeglobal_parameters_path):
            with open(headeglobal_parameters_path, 'r') as file:
                for line in file:
                    if 'MAX_DISTANCE' in line and '=' in line:
                        val_str = line.split('=')[1].replace(';', '').strip()
                        max_distance = float(val_str)
                        break
    except Exception:
        exit(1)

    # Distance Plot
    plt.figure(figsize=(6.5, 3))
    plt.plot(df['time'], df['distance'], label='Real Distance', color='#1f77b4', linewidth=2)
    plt.plot(df['time'], df['critical_distance'], label='Critical Distance', color='#d62728', linestyle='--', linewidth=1.5)
    plt.axhline(y=max_distance, label='Maximum Distance', color='#d62728', linestyle=':', linewidth=1.5)
    # Highlight RTA active zones
    rta_active = False
    start_time = 0
    for i in range(len(df)):
        if df.loc[i, 'rta_active'] == 1 and not rta_active:
            rta_active = True
            start_time = df.loc[i, 'time']
        elif (df.loc[i, 'rta_active'] == 0 or i == len(df) - 1) and rta_active:
            rta_active = False
            plt.axvspan(start_time, df.loc[i, 'time'], color='#ffcccc', alpha=0.6, label='RTA Intervention' if 'RTA Intervention' not in plt.gca().get_legend_handles_labels()[1] else "")
    plt.title('Distance Chart', fontsize=12, fontweight='bold', pad=10)
    plt.xlabel('Time (s)', fontsize=10)
    plt.ylabel('Distance (m)', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plot_dist_path = 'data/plot_distance.png'
    plt.savefig(plot_dist_path, dpi=200)
    plt.close()

    # Velocity Plot
    plt.figure(figsize=(6.5, 3))
    plt.plot(df['time'], df['ego_velocity'], label='Ego Velocity', color='#2ca02c', linewidth=2)
    plt.plot(df['time'], df['leader_velocity'], label='Leader Velocity', color='#ff7f0e', linewidth=2)
    plt.title('Velocity Chart', fontsize=12, fontweight='bold', pad=10)
    plt.xlabel('Time (s)', fontsize=10)
    plt.ylabel('Velocity (m/s)', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plot_vel_path = 'data/plot_velocity.png'
    plt.savefig(plot_vel_path, dpi=200)
    plt.close()

    # Metrics
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

    # Simulation outcome
    final_distance = df['distance'].iloc[-1]
    if final_distance <= 0.0:
        outcome = "Collision detected!"
    elif final_distance >= max_distance:
        outcome = "Leader vehicle lost (tracking failed)!"
    else:
        outcome = "Simulation completed sucessfully!"

    # PDF Report crating
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#000000'),
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#000000'),
        spaceBefore=10,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#333333')
    )

    # Document crafting
    story = []
    # Title
    story.append(Paragraph("AI Safety Critical Runtime Monitoring", title_style))
    # Outcome
    story.append(Paragraph(f"{outcome}", section_style))
    # Metrics
    metrics = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Value</b>", body_style)],
        [Paragraph("Total Time", body_style), f"{total_time:.2f} s ({total_ticks} ticks)"],
        [Paragraph("AI Decisions", body_style), f"{ai_calls} ({100.0 - rta_percentage:.1f}%)"],
        [Paragraph("RTA Interventions", body_style), f"{rta_calls} ({rta_percentage:.1f}%)"],
        [Paragraph("Minimum Distance", body_style), f"{min_dist:.2f} m"],
        [Paragraph("Average Distance", body_style), f"{avg_dist:.2f} m (Target: 10m)"],
        [Paragraph("Maximum Distance", body_style), f"{max_dist:.2f} m"],
        [Paragraph("Maximum Ego Velocity", body_style), f"{max_ego_vel:.2f} m/s ({max_ego_vel*3.6:.1f} km/h)"],
        [Paragraph("Average Ego Velocity", body_style), f"{avg_ego_vel:.2f} m/s ({avg_ego_vel*3.6:.1f} km/h)"]
    ]
    metrics_table = Table(metrics, colWidths=[250, 280])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e6e6e6')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(metrics_table)
    # Plots
    story.append(Image(plot_dist_path, width=530, height=210))
    story.append(Image(plot_vel_path, width=530, height=210))

    # Build and clean up.
    doc.build(story)
    try:
        os.remove(plot_dist_path)
        os.remove(plot_vel_path)
    except OSError:
        print("error")
        exit(1)

if __name__ == "__main__":
    generate_pdf()
