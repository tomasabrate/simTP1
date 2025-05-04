# File: distributions.py
"""
Módulo de generación de variables aleatorias:
Funciones para distribuciones Uniforme, Exponencial y Normal.
"""
import random
import math

def generar_uniforme(n, a, b):
    """
    Genera n valores con distribución uniforme en [a, b], redondeados a 4 decimales.
    """
    return [round(a + u * (b - a), 4) for u in (random.random() for _ in range(n))]

def generar_exponencial(n, lam):
    """
    Genera n valores con distribución exponencial de tasa λ (lambda), redondeados a 4 decimales.
    """
    return [round(-math.log(1 - random.random()) / lam, 4) for _ in range(n)]

def generar_normal(n, mu, sigma):
    """
    Genera n valores con distribución normal N(mu, sigma) usando Box–Muller, redondeados a 4 decimales.
    """
    datos = []
    i = 0
    while i < n:
        u1 = random.random()
        u2 = random.random()
        z1 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        datos.append(round(mu + sigma * z1, 4))
        i += 1
        # Genera segundo valor si es necesario
        if i < n:
            z2 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)
            datos.append(round(mu + sigma * z2, 4))
            i += 1
    return datos
