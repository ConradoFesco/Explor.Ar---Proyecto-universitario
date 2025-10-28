#!/usr/bin/env python3
"""
Script para migrar templates existentes a la nueva estructura refactorizada.
Este script ayuda a identificar qué templates necesitan ser actualizados.
"""

import os
import re
from pathlib import Path

def analyze_template(template_path):
    """Analiza un template y sugiere mejoras"""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    suggestions = []
    
    # Verificar longitud del archivo
    lines = content.split('\n')
    if len(lines) > 500:
        issues.append(f"Template muy largo: {len(lines)} líneas")
        suggestions.append("Considerar dividir en componentes más pequeños")
    
    # Verificar JavaScript inline
    js_pattern = r'<script[^>]*>(.*?)</script>'
    js_matches = re.findall(js_pattern, content, re.DOTALL)
    total_js_lines = sum(len(js.split('\n')) for js in js_matches)
    
    if total_js_lines > 100:
        issues.append(f"Mucho JavaScript inline: {total_js_lines} líneas")
        suggestions.append("Mover JavaScript a archivos separados")
    
    # Verificar código duplicado común
    if 'pagination' in content.lower() and 'pagination' not in str(template_path):
        issues.append("Código de paginación duplicado")
        suggestions.append("Usar componente shared/components/pagination.html")
    
    if 'search-input' in content and 'search_filters' not in str(template_path):
        issues.append("Filtros de búsqueda duplicados")
        suggestions.append("Usar componente shared/components/search_filters.html")
    
    if 'table' in content.lower() and 'data_table' not in str(template_path):
        issues.append("Tabla de datos duplicada")
        suggestions.append("Usar componente shared/components/data_table.html")
    
    if 'modal' in content.lower() and 'modal' not in str(template_path):
        issues.append("Modales duplicados")
        suggestions.append("Usar componente shared/components/modal.html")
    
    # Verificar uso de filtros personalizados
    if 'toLocaleDateString' in content:
        issues.append("Formateo de fechas en JavaScript")
        suggestions.append("Usar filtro Jinja format_date")
    
    if 'innerHTML' in content and 'map(' in content:
        issues.append("Generación de HTML en JavaScript")
        suggestions.append("Usar Jinja para renderizado de datos")
    
    return {
        'path': template_path,
        'lines': len(lines),
        'js_lines': total_js_lines,
        'issues': issues,
        'suggestions': suggestions
    }

def main():
    """Función principal del script"""
    templates_dir = Path('src/web/templates')
    
    if not templates_dir.exists():
        print("❌ Directorio de templates no encontrado")
        return
    
    print("🔍 Analizando templates para refactorización...\n")
    
    all_templates = []
    
    # Analizar todos los templates HTML
    for template_file in templates_dir.rglob('*.html'):
        if 'refactored' in str(template_file):
            continue  # Saltar templates ya refactorizados
            
        analysis = analyze_template(template_file)
        all_templates.append(analysis)
    
    # Ordenar por número de líneas (más problemáticos primero)
    all_templates.sort(key=lambda x: x['lines'], reverse=True)
    
    print("📊 RESUMEN DE ANÁLISIS\n")
    print("=" * 80)
    
    for template in all_templates:
        print(f"\n📄 {template['path']}")
        print(f"   Líneas: {template['lines']}")
        print(f"   JavaScript: {template['js_lines']} líneas")
        
        if template['issues']:
            print("   ⚠️  PROBLEMAS:")
            for issue in template['issues']:
                print(f"      - {issue}")
        
        if template['suggestions']:
            print("   💡 SUGERENCIAS:")
            for suggestion in template['suggestions']:
                print(f"      - {suggestion}")
    
    # Estadísticas generales
    total_templates = len(all_templates)
    problematic_templates = len([t for t in all_templates if t['issues']])
    total_lines = sum(t['lines'] for t in all_templates)
    total_js_lines = sum(t['js_lines'] for t in all_templates)
    
    print(f"\n📈 ESTADÍSTICAS GENERALES")
    print("=" * 80)
    print(f"Total de templates: {total_templates}")
    print(f"Templates problemáticos: {problematic_templates}")
    print(f"Total de líneas: {total_lines:,}")
    print(f"Total de JavaScript: {total_js_lines:,}")
    print(f"Porcentaje de JS: {(total_js_lines/total_lines)*100:.1f}%")
    
    # Recomendaciones de prioridad
    print(f"\n🎯 RECOMENDACIONES DE PRIORIDAD")
    print("=" * 80)
    
    high_priority = [t for t in all_templates if t['lines'] > 800 or len(t['issues']) > 3]
    medium_priority = [t for t in all_templates if 400 < t['lines'] <= 800 or len(t['issues']) == 2]
    low_priority = [t for t in all_templates if t['lines'] <= 400 and len(t['issues']) <= 1]
    
    print(f"\n🔴 ALTA PRIORIDAD ({len(high_priority)} templates):")
    for template in high_priority[:5]:  # Mostrar solo los 5 más problemáticos
        print(f"   - {template['path']} ({template['lines']} líneas)")
    
    print(f"\n🟡 MEDIA PRIORIDAD ({len(medium_priority)} templates):")
    for template in medium_priority[:5]:
        print(f"   - {template['path']} ({template['lines']} líneas)")
    
    print(f"\n🟢 BAJA PRIORIDAD ({len(low_priority)} templates):")
    for template in low_priority[:5]:
        print(f"   - {template['path']} ({template['lines']} líneas)")
    
    print(f"\n✨ BENEFICIOS ESPERADOS DE LA REFACTORIZACIÓN:")
    print("=" * 80)
    print("• Reducción de ~60% en líneas de código")
    print("• Eliminación de ~80% del JavaScript duplicado")
    print("• Mejora en mantenibilidad y consistencia")
    print("• Mejor aprovechamiento de las capacidades de Jinja2")
    print("• Componentes reutilizables para futuras funcionalidades")

if __name__ == '__main__':
    main()
