'''Módulo de utilidades acústicas para el Simulador Pro.'''

import numpy as np
from typing import Tuple, List, Dict

MATERIALES: Dict[str, float] = {
    "Concreto (Paredes duras)": 0.05,
    "Madera (Paneles)": 0.15,
    "Revoque de Yeso / Durlock": 0.10,
    "Alfombra gruesa (Suelo)": 0.30,
    "Vidrio (Ventanas)": 0.03,
    "Paneles Acústicos de alta densidad": 0.85,
    "Cortinas gruesas": 0.50
}

def velocidad_sonido(temp_celsius: float) -> float:
    '''Calcula la velocidad del sonido en el aire según la temperatura.'''
    return 331.4 + (0.6 * temp_celsius)

def calcular_delay(distancia_m: float, velocidad_ms: float) -> float:
    '''Calcula el retardo (delay) en milisegundos.'''
    if velocidad_ms <= 0:
        return 0.0
    return (distancia_m / velocidad_ms) * 1000.0

def atenuacion_spl(spl_referencia: float, distancia_objetivo: float, distancia_ref: float = 1.0) -> float:
    '''Ley de la inversa del cuadrado: Pérdida de SPL para uso escalar.
    
    Fórmula: $$ SPL = SPL_0 - 20 \\log_{10}\\left(\\frac{r}{r_0}\\right) $$
    '''
    if distancia_objetivo <= 0:
        return spl_referencia
    return spl_referencia - 20 * np.log10(distancia_objetivo / distancia_ref)

def atenuacion_spl_array(spl_referencia: float, distancia_objetivo: np.ndarray, distancia_ref: float = 1.0) -> np.ndarray:
    '''Ley de la inversa del cuadrado para uso con arrays de Numpy (superficies 3D).'''
    d_segura = np.where(distancia_objetivo < 0.1, 0.1, distancia_objetivo)
    return spl_referencia - 20 * np.log10(d_segura / distancia_ref)

def suma_spl_arrays(spl_list: List[np.ndarray]) -> np.ndarray:
    '''Suma logarítmica (incoherente) de N mapas de SPL (múltiples parlantes).'''
    if not spl_list:
        return np.array([0.0])
    spl_stack = np.array(spl_list)
    return 10 * np.log10(np.sum(10**(spl_stack / 10), axis=0))

def frec_resonancia_axial(dimension: float, velocidad_ms: float) -> float:
    '''Calcula el modo axial fundamental de una dimensión.'''
    if dimension <= 0:
        return 0.0
    return velocidad_ms / (2 * dimension)

def calcular_rt60_sabine(volumen: float, area_absorcion_total: float) -> float:
    '''Tiempo de Reverberación (RT60) usando la fórmula estadística de Sabine.
    
    Volumen en m³, absorción en sabines (m²).
    
    Fórmula: $$ RT_{60} = 0.161 \\frac{V}{A} $$
    '''
    if area_absorcion_total <= 0:
        return 0.0
    return 0.161 * (volumen / area_absorcion_total)

def calcular_reflexiones_1er_orden(Sx: float, Sy: float, Sz: float, 
                                   Rx: float, Ry: float, Rz: float, 
                                   L: float, W: float, H: float) -> List[Tuple[List[float], List[float], List[float]]]:
    '''Mapeo de rayos de rebote primario usando Image Source Method.
    
    Devuelve coordenadas para Plotly.
    '''
    rayos = []

    # Suelo (z=0)
    Ix_fz, Iy_fz, Iz_fz = Sx, Sy, -Sz
    if Rz != Iz_fz:
        t = -Iz_fz / (Rz - Iz_fz)
        Cx = Ix_fz + t * (Rx - Ix_fz)
        Cy = Iy_fz + t * (Ry - Iy_fz)
        if 0 <= Cx <= L and 0 <= Cy <= W:
            rayos.append(([Sx, Cx, Rx], [Sy, Cy, Ry], [Sz, 0, Rz]))

    # Techo (z=H)
    Ix_cz, Iy_cz, Iz_cz = Sx, Sy, 2*H - Sz
    if Rz != Iz_cz:
        t = (H - Iz_cz) / (Rz - Iz_cz)
        Cx = Ix_cz + t * (Rx - Ix_cz)
        Cy = Iy_cz + t * (Ry - Iy_cz)
        if 0 <= Cx <= L and 0 <= Cy <= W:
            rayos.append(([Sx, Cx, Rx], [Sy, Cy, Ry], [Sz, H, Rz]))

    # Pared Izquierda (x=0)
    Ix_lx, Iy_lx, Iz_lz = -Sx, Sy, Sz
    if Rx != Ix_lx:
        t = -Ix_lx / (Rx - Ix_lx)
        Cy = Iy_lx + t * (Ry - Iy_lx)
        Cz = Iz_lz + t * (Rz - Iz_lz)
        if 0 <= Cy <= W and 0 <= Cz <= H:
            rayos.append(([Sx, 0, Rx], [Sy, Cy, Ry], [Sz, Cz, Rz]))

    # Pared Derecha (x=L)
    Ix_rx, Iy_rx, Iz_rz = 2*L - Sx, Sy, Sz
    if Rx != Ix_rx:
        t = (L - Ix_rx) / (Rx - Ix_rx)
        Cy = Iy_rx + t * (Ry - Iy_rx)
        Cz = Iz_rz + t * (Rz - Iz_rz)
        if 0 <= Cy <= W and 0 <= Cz <= H:
            rayos.append(([Sx, L, Rx], [Sy, Cy, Ry], [Sz, Cz, Rz]))

    # Pared Frontal (y=0)
    Ix_fy, Iy_fy, Iz_fy = Sx, -Sy, Sz
    if Ry != Iy_fy:
        t = -Iy_fy / (Ry - Iy_fy)
        Cx = Ix_fy + t * (Rx - Ix_fy)
        Cz = Iz_fy + t * (Rz - Iz_fy)
        if 0 <= Cx <= L and 0 <= Cz <= H:
            rayos.append(([Sx, Cx, Rx], [Sy, 0, Ry], [Sz, Cz, Rz]))

    # Pared Trasera (y=W)
    Ix_ty, Iy_ty, Iz_ty = Sx, 2*W - Sy, Sz
    if Ry != Iy_ty:
        t = (W - Iy_ty) / (Ry - Iy_ty)
        Cx = Ix_ty + t * (Rx - Ix_ty)
        Cz = Iz_ty + t * (Rz - Iz_ty)
        if 0 <= Cx <= L and 0 <= Cz <= H:
            rayos.append(([Sx, Cx, Rx], [Sy, W, Ry], [Sz, Cz, Rz]))

    return rayos

