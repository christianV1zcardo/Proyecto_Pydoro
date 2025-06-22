# Mejoras post DEL 22/06/2025

Pydoro ha evolucionado de un simple temporizador y Pomodoro a una herramienta integral para la gestión de la productividad diaria. Ahora, permite al usuario registrar en todo momento la actividad que esté realizando (como desayunar, trabajar o estudiar), midiendo el tiempo dedicado a cada una a lo largo de la sesión. Esto facilita que el usuario conozca de forma específica la distribución de su tiempo diario.

Además, se han implementado subcategorías personalizables para las actividades de 'Estudio', 'Trabajo' y 'Lectura', permitiendo un seguimiento más granular del tiempo productivo. Es importante destacar que los temporizadores Pomodoro y los temporizadores "internos" solo pueden iniciarse dentro de estas tres categorías principales, que requieren un enfoque estructurado. Para otras actividades, como desayunar o tomar una siesta, el sistema registrará automáticamente el tiempo dedicado desde el momento en que se selecciona la actividad, sin la necesidad de activar un temporizador específico. Finalmente, Pydoro ofrece una opción para visualizar la línea de tiempo de actividades (en formato lista), mostrando la duración y los rangos horarios de cada una, complementada con un resumen claro de las horas y minutos acumulados por actividad en la sesión.

# Mejoras AL 22/06/2025

De la mano a lo anterior mencionado (que pydoro más que un proyecto para mi portafolio, es mi proyecto personal porque ninguno de los temporizadores ni medidores de productividad disponibles en el mercado me convence) Hice un par de mejoras hace varios días que recién cargaré, actualmente estudio programación y matemáticas, por lo que le di a pydoro la capacidad de asignar el tiempo que paso tanto en pomodoros cómo en el temporizador simple a las 2 categorías, para tenr claridad de cuánto tiempo le dediqué a cada una en el día. Añado este commit porque estoy a punto de hacer un par de mejoras más grandes por sobre esta y necesito tener esto guardado en caso lo que intente no funcione y todo explote :p

# Pydoro - Tu Temporizador Pomodoro Personalizado

Pydoro es un temporizador Pomodoro personalizable y una herramienta de gestión del tiempo, diseñada para funcionar completamente en la terminal. Nace no tanto como un proyecto para mostrar al público, sino como una **herramienta personal**. La razón es que ningún pomodoro o medidor de tiempo existente en el mercado cumplía con mis necesidades y mi propia forma de trabajar y estudiar. Por ello, Pydoro ha sido desarrollado para ser mi compañero diario en la búsqueda de la concentración y la productividad.

## Características

* **Temporizador Pomodoro Completo:** Permite configurar ciclos de trabajo, descansos cortos y descansos largos.
* **Temporizador Simple:** Una opción para contar el tiempo hacia arriba, ideal para sesiones de trabajo fluidas o de duración indefinida.
* **Contadores de Sesión:** Mantiene un registro detallado de los Pomodoros completados, descansos cortos completados y descansos largos completados durante toda la ejecución del script.
* **Resumen de Tiempo Total:** Calcula y muestra el tiempo total acumulado de trabajo y descanso en formato `HH:MM`.
* **Frases Motivadoras:** Muestra frases inspiradoras aleatorias durante los períodos de trabajo y descanso.
* **Interfaz de Terminal Estética:**
    * Utiliza colores ANSI para mejorar la legibilidad y la experiencia visual.
    * Incluye una barra de progreso que se actualiza en tiempo real.
* **Notificaciones Auditivas:** Reproduce sonidos (`bell.wav` para fin de trabajo, `notif.wav` para fin de descanso) para indicar el cambio de fase.
* **Control de Flujo Interactivo:** El usuario controla el inicio de cada fase (trabajo o descanso) y la navegación por el menú principal.
* **Manejo de Interrupciones:** Permite interrumpir cualquier fase con `Ctrl+C`, ofreciendo la opción de saltar a la siguiente fase o cancelar la sesión actual.

## Filosofía de Diseño

Este temporizador ha sido desarrollado con una clara preferencia por la interfaz de línea de comandos. **No se planea en ningún momento integrar una interfaz gráfica de usuario (GUI)**, ya que el uso directo desde la terminal ofrece un control directo, agilidad y un entorno libre de distracciones, lo cual se alinea con un enfoque de productividad centrado en la concentración. Fue hecho de esta manera para priorizar la funcionalidad y la eficiencia en un entorno de texto puro, y **es la herramienta que uso a diario** para mis propias necesidades.

## Futuras Mejoras

Conforme pase el tiempo y en caso requiera añadirle más cosas para mi propio uso, se las añadiré poco a poco, lo primero que tengo en mente es una pequeña BD con **SQLITE** para tener un registro de las sesiones, horas de estudio y fechas en las que se estudió, las cuáles tal vez poder visualizar en un heatmap con seaborn. ***(Solo pensando en voz alta)***.

## Instalación

Para configurar y ejecutar Pydoro en tu sistema, sigue estos pasos:

1.  **Clonar el Repositorio (o descargar el archivo `pydoro.py`):**
    Si tienes Git, puedes clonar el repositorio:
    ```bash
    git clone [URL_DE_TU_REPOSITORIO]
    cd proyect_pydoro
    ```
    Si no, descarga el archivo `pydoro.py` y colócalo en una carpeta dedicada a tu proyecto (ej. `proyect_pydoro`).

2.  **Crear un Entorno Virtual (Recomendado):**
    Navega a la carpeta de tu proyecto en la terminal y crea un entorno virtual para aislar las dependencias:
    ```bash
    python -m venv pydoro_venv
    ```

3.  **Activar el Entorno Virtual:**
    * **Windows (PowerShell/CMD):**
        ```powershell
        .\pydoro_venv\Scripts\activate.bat
        ```
    * **Linux/macOS (Bash/Zsh):**
        ```bash
        source pydoro_venv/bin/activate
        ```
    Verás `(pydoro_venv)` en tu prompt, indicando que el entorno está activo.

4.  **Instalar Dependencias:**
    Con el entorno virtual activado, instala la librería `playsound`:
    ```bash
    pip install playsound
    ```

5.  **Archivos de Sonido:**
    Descarga dos archivos de sonido cortos (ej., un "ding" para `bell.wav` y una "notificación" para `notif.wav`). Coloca ambos archivos en la **misma carpeta** donde se encuentra `pydoro.py`.

## Uso

Para ejecutar Pydoro, abre tu terminal (PowerShell en Windows, o tu terminal favorita en Linux/macOS), navega a la carpeta de tu proyecto, activa tu entorno virtual y ejecuta el script:

```bash
# 1. Navega a tu carpeta de proyecto (ejemplo)
cd C:\Users\TuUsuario\Downloads\proyects\proyect_pydoro

# 2. Activa el entorno virtual
.\pydoro_venv\Scripts\activate.bat # Para Windows
# source pydoro_venv/bin/activate   # Para Linux/macOS

# 3. Ejecuta el script
python pydoro.py
```

## 🧑‍💻 Autor

[Christian Vizcardo]
[www.linkedin.com/in/christian-vizcardo]