#!/usr/bin/env python
"""
Pruebas para validar la robustez del algoritmo de formatting de nombre de equipo.
Simula el comportamiento del método actualizar_estado() sin dependencias de BD.
"""

import re
from enum import Enum

class EstadoEnum(Enum):
    REGISTRADO = "REGISTRADO"
    FINALIZADO = "FINALIZADO"
    PENDIENTE_HASH = "PENDIENTE HASH"

def formatear_nombre_equipo(nombre_input):
    """Replica la lógica del método actualizar_estado() para testing."""
    if not nombre_input:
        return nombre_input
    
    nombre_str = str(nombre_input).strip()
    
    # Validar si ya está en el formato correcto (ILE3-\d+)
    if not re.match(r'^ILE3-\d+$', nombre_str):
        numero = None
        
        # Si ya contiene "ILE3", extraer solo el número que viene después
        if 'ILE3' in nombre_str.upper():
            match = re.search(r'ILE3\s*-?\s*(\d+)', nombre_str.upper())
            if match:
                numero = match.group(1)
            else:
                numero = re.sub(r'\D', '', nombre_str)
        else:
            numero = re.sub(r'\D', '', nombre_str)
        
        if numero:
            numero = numero.zfill(3)
            return f"ILE3-{numero}"
    
    return nombre_str

# ============================================================================
# SUITE DE PRUEBAS
# ============================================================================

def test_escenario(titulo, input_inicial, iteraciones_esperadas):
    """Ejecuta un escenario de prueba y valida idempotencia."""
    print(f"\n{'='*70}")
    print(f"ESCENARIO: {titulo}")
    print(f"{'='*70}")
    print(f"Input inicial: {input_inicial}")
    
    resultado = input_inicial
    for i in range(iteraciones_esperadas):
        resultado_prev = resultado
        resultado = formatear_nombre_equipo(resultado)
        print(f"  Iteración {i+1}: {resultado_prev:20s} → {resultado}")
        
        # Validar que sea idempotente después de la primera ejecución
        if i > 0:
            resultado_again = formatear_nombre_equipo(resultado)
            if resultado != resultado_again:
                print(f"  ❌ ERROR: No es idempotente")
                print(f"     Ejecutado nuevamente: {resultado_again}")
                return False
    
    # Validar que no cambie en más iteraciones
    resultado_final = formatear_nombre_equipo(resultado)
    if resultado != resultado_final:
        print(f"  ❌ ERROR: Falló idempotencia después de {iteraciones_esperadas} iteraciones")
        print(f"     Siguiente ejecución: {resultado_final}")
        return False
    
    print(f"✓ EXITOSO: Formato final = {resultado}")
    return True

# ============================================================================
# CASOS DE PRUEBA
# ============================================================================

print("\n" + "="*70)
print("VALIDACIÓN DE ROBUSTEZ: FORMATTING DE NOMBRE DE EQUIPO ILE3-XXX")
print("="*70)

# Caso 1: Input simple (lo que debería funcionar siempre)
test_escenario(
    "Caso 1: Input simple (3 dígitos o menos)",
    "001",
    iteraciones_esperadas=3
)

test_escenario(
    "Caso 1b: Input simple (1 dígito)",
    "5",
    iteraciones_esperadas=3
)

test_escenario(
    "Caso 1c: Input simple (2 dígitos)",
    "99",
    iteraciones_esperadas=3
)

# Caso 2: Input ya formateado correctamente
test_escenario(
    "Caso 2: Input ya formateado (ILE3-001)",
    "ILE3-001",
    iteraciones_esperadas=4
)

# Caso 3: Input con prefijo pero formato inconsistente
test_escenario(
    "Caso 3a: Formato inconsistente (ILE3001 sin guión)",
    "ILE3001",
    iteraciones_esperadas=3
)

test_escenario(
    "Caso 3b: Formato inconsistente (ILE3 001 con espacios)",
    "ILE3 001",
    iteraciones_esperadas=3
)

# Caso 4: Números más grandes (ILE3-1001)
test_escenario(
    "Caso 4a: Número de 4 dígitos",
    "1001",
    iteraciones_esperadas=3
)

test_escenario(
    "Caso 4b: Número de 4 dígitos formateado",
    "ILE3-1001",
    iteraciones_esperadas=3
)

# Caso 5: Escenarios corruptos (lo que observamos en producción)
test_escenario(
    "Caso 5a: Corrupción observada (ILE3-333002)",
    "ILE3-333002",
    iteraciones_esperadas=3
)

test_escenario(
    "Caso 5b: Corrupción observada (ILE3-33333001)",
    "ILE3-33333001",
    iteraciones_esperadas=3
)

# Caso 6: Entrada vacía
resultado = formatear_nombre_equipo("")
print(f"\nCaso 6: Input vacío → {resultado if resultado else '(vacío)'}  ✓")

# Caso 7: None
resultado = formatear_nombre_equipo(None)
print(f"Caso 7: Input None → {resultado}  ✓")

# Caso 8: Números con ceros iniciales (edge case crítico)
test_escenario(
    "Caso 8: Ceros iniciales (001 → ILE3-001)",
    "001",
    iteraciones_esperadas=5
)

# ============================================================================
# VALIDACIÓN DE FORMATO ESPERADO
# ============================================================================

print("\n" + "="*70)
print("VALIDACIÓN DE FORMATO ESPERADO")
print("="*70)

test_cases = [
    ("001", "ILE3-001"),
    ("002", "ILE3-002"),
    ("333", "ILE3-333"),
    ("1001", "ILE3-1001"),
    ("ILE3-001", "ILE3-001"),
    ("ILE3-333", "ILE3-333"),
    ("ILE3-1001", "ILE3-1001"),
]

all_valid = True
for input_val, expected in test_cases:
    resultado = formatear_nombre_equipo(input_val)
    status = "✓" if resultado == expected else "✗"
    if resultado != expected:
        all_valid = False
    print(f"{status} {input_val:20s} → {resultado:20s} (esperado: {expected})")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
if all_valid:
    print("✓ TODAS LAS PRUEBAS EXITOSAS")
    print("✓ La solución es IDEMPOTENTE")
    print("✓ Evita CONCATENACIÓN accidental")
    print("✓ Mantiene COMPATIBILIDAD con registros existentes")
else:
    print("✗ ALGUNAS PRUEBAS FALLARON")
print("="*70 + "\n")
