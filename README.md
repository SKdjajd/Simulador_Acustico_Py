[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-orange.svg)](https://streamlit.io/)

# Simulador Acústico Pro 🎛️

Un simulador acústico avanzado en Python para el diseño y análisis técnico de recintos sonorizados. Emplea fundamentos clave de psicoacústica, termodinámica y trazado de rayos simulando comportamientos de las presiones sonoras sobre el espacio físico a través de modelado 3D interactivo.

## 📋 Índice

- [Características Principales](#-características-principales)
- [Tecnologías Utilizadas](#️-tecnologías-utilizadas)
- [Instalación](#-instalación)
- [Ejecución y Uso](#️-ejecución-y-uso)
- [Estructura del Repositorio](#️-estructura-del-repositorio)
- [Licencia](#licencia)
- [Contribuciones](#-contribuciones)
- [Demo](#demo)
- [Autor](#autor)

## 🚀 Características Principales

- **Multi-Altavoces Dinámicos:** Agrega una cantidad variable de parlantes (*Subwoofers, Woofers, Line Arrays*) y modifícalos individualmente con precisión sobre una matriz espacial.
- **Ray Tracing 3D Integrado:** Incorpora el *Image Source Method* renderizado sobre Plotly, capaz de modelar los niveles combinados SPL (Sound Pressure Level) y mostrar reflexiones directas (Eco y Haas) individualmente. 
- **Analíticas Psicoacústicas:** Cálculos heurísticos automatizados de:
  - Tiempo de Reverberación Estimado (RT60 Fórmula de Sabine).
  - Modos de Resonancia Axial (Efectos de Modos en Sala).
  - Precedencia Temporal (Efecto Haas) de sistemas de Relevo (Delay Towers).
- **Atenuación Bidimensional Realista:** Cálculo por la 'Ley Inversa del Cuadrado' y somatoria incoherente interactiva (NumPy & SciPy math).
- **Exportables Interactivos:** Puedes descargar el modelo tridimensional de la sala de simulación a un formato `.html` puro, listo para ser entregado a un cliente o integrarse a tu web.

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.9+ | Lenguaje principal |
| Streamlit | >=1.30.0 | Interfaz gráfica responsiva |
| NumPy & Pandas | >=1.24.0 / >=2.0.0 | Núcleo analítico vectorial |
| Plotly | >=5.18.0 | Gráficos 2D/3D interactivos |
| PyYAML | >=6.0 | Configuraciones |

Ver [requirements.txt](requirements.txt) para detalles.

## 📦 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/TU_USUARIO/simulador-acustico-pro.git
   cd simulador-acustico-pro
   ```

2. Crea un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   # Windows:
   venv\\Scripts\\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Ejecución y Uso

Ejecuta la app:
```bash
streamlit run app.py
```

Abre http://localhost:8501 en tu navegador.

## 🗺️ Estructura del Repositorio

| Archivo | Descripción |
|---------|-------------|
| `app.py` | Interfaz principal Streamlit (ex `Sist. Audio.py`). |
| `utils_acustica.py` | Lógica física acústica y matemáticas. |
| `requirements.txt` | Dependencias. |
| `LICENSE` | Licencia MIT. |
| `README.md` | Este archivo. |

## 📱 Demo

<!-- Agrega aquí un GIF o video demo. Ejemplo: -->
<!-- ![Demo](demo.gif) -->

Ejecuta localmente para probar interactivamente.

## 📄 Licencia

Este proyecto está licenciado bajo la [MIT License](LICENSE) - ver archivo [LICENSE](LICENSE) para detalles.

## 🤝 Contribuciones

¡Pull requests bienvenidos! Para cambios grandes, abre un [issue](https://github.com/TU_USUARIO/simulador-acustico-pro/issues) primero.

1. Fork el proyecto.
2. Crea tu feature branch (`git checkout -b feature/AlgoAñadido`).
3. Commit cambios (`git commit -m 'Add some Feature'`).
4. Push al branch (`git push origin feature/AlgoAñadido`).
5. Abre Pull Request.

## 👨‍💻 Autor

- **Tu Nombre** - *Ingeniero de Sonido* - [Tu GitHub](https://github.com/TU_USUARIO)

*Hecho con ❤️ en Python para Ingeniería de Sonido Profesional y Arquitectura.*

