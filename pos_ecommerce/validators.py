"""
Validadores personalizados para el sistema POS
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


def validar_rut_chileno(rut):
    """
    Valida un RUT chileno con su dígito verificador.
    Acepta formatos: 12345678-9, 12.345.678-9, 12345678
    
    Algoritmo del módulo 11 para calcular el DV.
    """
    # Limpiar el RUT: quitar puntos y guiones
    rut_limpio = rut.replace('.', '').replace('-', '').upper()
    
    # Debe tener al menos 2 caracteres (número + DV)
    if len(rut_limpio) < 2:
        raise ValidationError('RUT inválido: demasiado corto')
    
    # Separar cuerpo y dígito verificador
    cuerpo = rut_limpio[:-1]
    dv_proporcionado = rut_limpio[-1]
    
    # Verificar que el cuerpo sea numérico
    if not cuerpo.isdigit():
        raise ValidationError('RUT inválido: el cuerpo debe ser numérico')
    
    # Calcular dígito verificador
    suma = 0
    multiplo = 2
    
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    # Convertir DV calculado a string
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
    
    # Comparar
    if dv_proporcionado != dv_calculado:
        raise ValidationError(
            f'RUT inválido: dígito verificador incorrecto. '
            f'Esperado: {dv_calculado}, Recibido: {dv_proporcionado}'
        )
    
    return True


def validar_fecha_no_futura(fecha):
    """
    Valida que una fecha no sea futura.
    Usado para ventas, compras, etc.
    """
    if fecha > timezone.now():
        raise ValidationError('La fecha no puede ser futura')
    return True


def validar_numero_positivo(valor):
    """
    Valida que un número sea mayor o igual a 0.
    Usado para precios, stocks, cantidades, etc.
    """
    if valor < 0:
        raise ValidationError('El valor debe ser mayor o igual a 0')
    return True


def validar_precio_positivo(precio):
    """
    Valida que un precio sea mayor o igual a 0.
    """
    if precio < Decimal('0.00'):
        raise ValidationError('El precio debe ser mayor o igual a 0')
    return True


def validar_stock_no_negativo(stock):
    """
    Valida que el stock no sea negativo.
    """
    if stock < 0:
        raise ValidationError('El stock no puede ser negativo')
    return True


def validar_cantidad_positiva(cantidad):
    """
    Valida que una cantidad sea al menos 1.
    """
    if cantidad < 1:
        raise ValidationError('La cantidad debe ser al menos 1')
    return True


def validar_rango_fechas(fecha_inicio, fecha_fin):
    """
    Valida que fecha_fin sea posterior a fecha_inicio.
    """
    if fecha_fin <= fecha_inicio:
        raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio')
    return True


def validar_texto_no_vacio(texto):
    """
    Valida que un texto no esté vacío después de quitar espacios.
    """
    if not texto or not texto.strip():
        raise ValidationError('El texto no puede estar vacío')
    return True
