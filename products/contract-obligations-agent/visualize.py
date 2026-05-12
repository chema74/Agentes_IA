"""Generador de reporte visual HTML para el agente de obligaciones contractuales."""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def generate_visual_report(input_data: dict = None, output_file: str = "reporte_visual.html"): # type: ignore
    """
    Genera un reporte HTML estático con visualizaciones del agente.
    
    Args:
        input_data: Datos de ejemplo o resultado real del agente
        output_file: Nombre del archivo HTML de salida
    """
    # Datos de ejemplo si no se proporcionan
    if input_data is None:
        input_data = {
            "contract_id": "CONT-2026-001",
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "obligations": [
                {"type": "Pago", "amount": "€50,000", "deadline": "2026-06-30", "risk": "Bajo"},
                {"type": "Entrega", "description": "Módulo de reporting", "deadline": "2026-05-15", "risk": "Medio"},
                {"type": "Confidencialidad", "duration": "24 meses post-contrato", "risk": "Alto"}
            ],
            "risk_summary": {"bajo": 1, "medio": 1, "alto": 1},
            "alerts": [
                "⚠️ Fecha de entrega cercana (15 días)",
                "🔒 Cláusula de confidencialidad requiere revisión legal"
            ]
        }
    
    # Generar HTML
    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Visual: {input_data['contract_id']}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f8f9fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .card {{ background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .obligation {{ border-left: 4px solid #667eea; padding-left: 15px; margin: 10px 0; }}
        .risk-bajo {{ border-color: #10b981; }}
        .risk-medio {{ border-color: #f59e0b; }}
        .risk-alto {{ border-color: #ef4444; }}
        .alert {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 10px; margin: 5px 0; border-radius: 0 4px 4px 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; }}
        .chart-container {{ width: 100%; max-width: 400px; margin: 20px auto; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 0.875rem; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Agente de Obligaciones Contractuales</h1>
        <p>Contract ID: <strong>{input_data['contract_id']}</strong> | Análisis: {input_data['analysis_date']}</p>
    </div>

    <div class="card">
        <h2>🎯 Resumen de Riesgos</h2>
        <div class="chart-container">
            <canvas id="riskChart"></canvas>
        </div>
    </div>

    <div class="card">
        <h2>📌 Obligaciones Detectadas</h2>
        <table>
            <thead><tr><th>Tipo</th><th>Detalle</th><th>Plazo</th><th>Riesgo</th></tr></thead>
            <tbody>
"""
    
    # Añadir filas de obligaciones
    for obs in input_data['obligations']:
        risk_class = f"risk-{obs['risk'].lower()}"
        detalle = obs.get('amount') or obs.get('description') or obs.get('duration')
        html += f"""
                <tr class="obligation {risk_class}">
                    <td>{obs['type']}</td>
                    <td>{detalle}</td>
                    <td>{obs.get('deadline', 'N/A')}</td>
                    <td><span style="color: {'#10b981' if obs['risk']=='Bajo' else '#f59e0b' if obs['risk']=='Medio' else '#ef4444'}">●</span> {obs['risk']}</td>
                </tr>"""
    
    html += """
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>⚠️ Alertas y Recomendaciones</h2>
"""
    for alert in input_data['alerts']:
        html += f'        <div class="alert">{alert}</div>\n'
    
    html += """
    </div>

    <div class="footer">
        <p>Generado por Agentes_IA • Arquitectura local-first • CC BY-SA 4.0</p>
    </div>

    <script>
        // Gráfico de riesgos con Chart.js
        const ctx = document.getElementById('riskChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Bajo', 'Medio', 'Alto'],
                datasets: [{
                    data: [""" + f"{input_data['risk_summary']['bajo']}, {input_data['risk_summary']['medio']}, {input_data['risk_summary']['alto']}" + """],
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    title: { display: true, text: 'Distribución de Riesgos' }
                }
            }
        });
    </script>
</body>
</html>
"""
    
    # Guardar archivo
    Path(output_file).write_text(html, encoding='utf-8')
    print(f"✅ Reporte visual generado: {output_file}")
    print(f"🌐 Ábrelo en tu navegador: file:///{Path(output_file).resolve()}")
    return output_file

if __name__ == "__main__":
    generate_visual_report()