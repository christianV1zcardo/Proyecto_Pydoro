# -*- coding: utf-8 -*-
# Este script implementa un temporador Pomodoro personalizable con una interfaz
# de usuario básica en la terminal, incluyendo una barra de progreso, colores
# y reproducción de sonido al final de cada fase.

# Importamos los módulos necesarios
import time  # Para manejar las pausas en la ejecución del programa
import os    # Para interactuar con el sistema operativo (ej. limpiar la pantalla de la consola)
import random # Para seleccionar frases motivadoras aleatorias
from playsound import playsound # Para reproducir sonidos al final de cada fase
import datetime # Para registrar la fecha y hora y manejar el tiempo en el historial (aunque no se guarda en archivo)

# Importaciones para lectura de teclado no bloqueante (esencial para la pausa)
import sys
# select y termios/tty son para sistemas Unix/Linux (como Ubuntu, macOS)
import select
if os.name == 'posix': # Solo importar para sistemas POSIX (Linux, macOS)
    import termios, tty
elif os.name == 'nt': # Solo importar para Windows
    import msvcrt

# Nuevo: Registra el tiempo de inicio del script
script_start_time = datetime.datetime.now()

# ==============================================================================
# Definición de códigos ANSI para colores y estilos en la terminal
# Estos códigos son interpretados por la terminal para cambiar el formato del texto.
# ==============================================================================
RESET = "\033[0m"       # Código para restablecer el color y estilo a los valores por defecto
BOLD = "\033[1m"         # Código para texto en negrita
GREEN = "\033[92m"       # Código para color verde brillante
YELLOW = "\033[93m"      # Código para color amarillo brillante
BLUE = "\033[94m"        # Código para color azul brillante
RED = "\033[91m"         # Código para color rojo brillante
ORANGE = "\033[33m"      # Código para color naranja (estándar)
LIGHT_GRAY = "\033[37m" # Gris claro (para texto secundario)
CYAN = "\033[96m"        # Cian para un nuevo grupo de categorías
MAGENTA = "\033[95m"     # Magenta para otro nuevo grupo de categorías
# La barra de progreso es VERDE como solicitado.

# ==============================================================================
# Listas de frases motivadoras (Traducidas al Castellano)
# ==============================================================================
WORK_QUOTES = [
    "¿Ves lo infinito que eres?",
    "Piensa solo en tu arte.",
    "Blande tu espada como si no tuvieras manos.",
    "Dentro de ti, hay una infinidad de cosas sucediendo.",
    "Sé libre. Sé infinito.",
    "No hay luz para quienes no conocen la oscuridad.",
    "Invencible es solo una palabra.",
    "Preocupado por un solo árbol, te perderás todo el bosque.",
    "No busques seguir los pasos de los sabios. Busca lo que ellos buscaron.",
    "Estar incompleto es lo que nos impulsa hacia lo siguiente.",
    "El camino de un guerrero es solitario.",
    "El miedo es el verdadero enemigo de un guerrero.",
    "Sigue viviendo y soporta las sombras.",
    "Si alguna vez estuviéramos perfectamente satisfechos, ¿qué sentido tendría el resto de nuestras vidas?",
    "El cielo no ríe. Solo sonríe y observa.",
    "Mira todo en su totalidad, sin esfuerzo."
]

BREAK_QUOTES = [
    "El descanso es parte del viaje.",
    "Incluso el guerrero más fuerte debe dormir.",
    "Un momento de quietud puede revelar el camino a seguir.",
    "El cuerpo se mueve, pero la mente debe descansar.",
    "En el silencio, el corazón encuentra la paz.",
    "Un guerrero que nunca descansa, nunca verá el mañana.",
    "El viento no se apresura, sin embargo, lo mueve todo.",
    "La fuerza es saber cuándo detenerse.",
    "El río fluye sin esfuerzo, sin embargo, talla montañas.",
    "El descanso no es debilidad, sino sabiduría.",
    "Incluso la espada debe ser envainada.",
    "Una mente en calma ve más que una mente en batalla.",
    "Los guerreros más grandes saben cuándo pausar.",
    "El sueño es el puente entre hoy y mañana.",
    "Un espíritu descansado es más afilado que cualquier espada.",
    "Las estrellas no se apresuran, sin embargo, brillan.",
    "Luchar sin fin es perderse a uno mismo.",
    "La montaña permanece porque no persigue al viento.",
    "Un guerrero que nunca se detiene nunca entenderá el camino.",
    "La verdadera fuerza se encuentra en el equilibrio."
]

# --- Variables globales para el tiempo categorizado por subcategorías específicas ---
# Almacena el tiempo en minutos
total_specific_category_times = {
    "Programación": 0,
    "Matemáticas": 0,
    "Inclub": 0,
    "Vegenanito": 0,
    "Manga": 0,
    "Libro": 0
}

# --- Variables globales para el seguimiento de actividades diarias (con marcas de tiempo) ---
daily_activity_log = [] # Lista para almacenar segmentos de actividad: [{'category': 'Estudio', 'start': datetime_obj, 'end': datetime_obj, 'duration': seconds}]
current_daily_activity = None # La categoría de actividad diaria que Pydoro está rastreando actualmente
last_activity_start_time = None # Marca de tiempo (datetime object) de cuándo comenzó la actividad diaria actual

# Nuevas categorías diarias y su orden (¡'Ejercicio' añadido aquí!)
DEFAULT_DAILY_CATEGORIES = [
    'Estudio', 'Desayuno', 'Trabajo', 'Almuerzo', 'Siesta', 'Ejercicio', 'Ducha', 'Lectura', 'Cena', 'Otros'
]

# Mapeo de categorías principales a sus subcategorías específicas y colores para la vista de resumen
SPECIFIC_SUBCATEGORY_MAPPING = {
    'Estudio': {'subcats': ['Programación', 'Matemáticas'], 'color': GREEN},
    'Trabajo': {'subcats': ['Inclub', 'Vegenanito'], 'color': CYAN},
    'Lectura': {'subcats': ['Manga', 'Libro'], 'color': MAGENTA}
}

# Mapeo de colores para las categorías diarias generales (para la línea de tiempo)
# ¡Color para 'Ejercicio' añadido aquí!
DAILY_CATEGORY_COLORS = {
    'Estudio': GREEN,
    'Desayuno': ORANGE,
    'Trabajo': BLUE,
    'Almuerzo': ORANGE,
    'Siesta': YELLOW,
    'Ejercicio': YELLOW, # Usamos YELLOW para Ejercicio
    'Ducha': CYAN,
    'Lectura': MAGENTA,
    'Cena': ORANGE,
    'Otros': LIGHT_GRAY
}

# ==============================================================================
# Funciones auxiliares para la limpieza de pantalla, colores y temporizador
# ==============================================================================
def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_time_hh_mm_minutes(total_minutes):
    """
    Formatea el tiempo total en minutos a un formato de Horas y Minutos (Hh Mm).
    """
    if total_minutes < 0:
        total_minutes = 0
    hours = total_minutes // 60
    remaining_minutes = total_minutes % 60
    if hours > 0:
        return f"{hours}h {remaining_minutes}m"
    else:
        return f"{remaining_minutes}m"

def display_timer(total_seconds):
    """
    Formatea el tiempo total en segundos a un formato de minutos:segundos (MM:SS)
    y le aplica color según el tiempo restante (o transcurrido para temporizador simple).
    """
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    
    if total_seconds <= 10:
        color = RED
    elif total_seconds <= 60 and total_seconds > 0:
        color = YELLOW
    elif total_seconds > 0:
        color = GREEN
    else:
        color = GREEN # For 0 seconds or completed timer

    return f"{BOLD}{color}{minutes:02d}:{seconds:02d}{RESET}"

def create_progress_bar(current_seconds, total_duration_seconds, bar_length=40):
    """
    Crea una cadena de barra de progreso que representa el avance visualmente.
    """
    if total_duration_seconds == 0:
        percentage_completed = 100
    else:
        # Calculate percentage based on time ELAPSED, not remaining, for the bar
        elapsed_seconds = total_duration_seconds - current_seconds
        percentage_completed = (elapsed_seconds / total_duration_seconds) * 100

    filled_chars = int(bar_length * percentage_completed / 100)
    
    colored_bar = f"{GREEN}█{RESET}" * filled_chars + f"{LIGHT_GRAY}-{RESET}" * (bar_length - filled_chars)
    
    percent_color = GREEN
    if percentage_completed < 25: # Less than 25% completed (more than 75% remaining)
        percent_color = RED
    elif percentage_completed < 50: # Less than 50% completed (more than 50% remaining)
        percent_color = YELLOW

    return f"[{colored_bar}] {percent_color}{percentage_completed:.0f}%{RESET}"

def get_total_script_run_time():
    """
    Calcula el tiempo total transcurrido desde que se inició el script.
    Returns:
        str: Tiempo formateado en Hh Mm.
    """
    elapsed = datetime.datetime.now() - script_start_time
    total_seconds = int(elapsed.total_seconds())
    total_minutes = total_seconds // 60
    return format_time_hh_mm_minutes(total_minutes)

# ==============================================================================
# Funciones auxiliares para la lectura de teclado no bloqueante
# ==============================================================================
def kbhit_os_specific():
    """
    Verifica si una tecla ha sido presionada sin bloquear la ejecución.
    Funciona tanto en Windows como en sistemas Unix/Linux.
    """
    if os.name == 'nt': # Para Windows
        return msvcrt.kbhit()
    else: # Para Linux/macOS
        # select.select on sys.stdin works on Unix-like systems
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(rlist)

def getch_os_specific():
    """
    Lee un solo carácter desde stdin sin mostrarlo en la consola.
    Funciona para Windows y sistemas Unix/Linux.
    """
    if os.name == 'nt': # Para Windows
        return msvcrt.getch().decode('utf-8')
    else: # Para Linux/macOS
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

# ==============================================================================
# Funciones para categorización de tiempo de estudio/trabajo/lectura
# ==============================================================================
def prompt_specific_work_category(main_category):
    """
    Permite al usuario seleccionar una subcategoría específica (ej. Programación/Matemáticas para Estudio).
    Args:
        main_category (str): La categoría general activa (ej. 'Estudio', 'Trabajo', 'Lectura').
    Returns:
        str: El nombre de la subcategoría seleccionada, o None si no se selecciona.
    """
    subcategories_info = SPECIFIC_SUBCATEGORY_MAPPING.get(main_category)
    if not subcategories_info:
        return None # Should not happen if called correctly

    subcategories = subcategories_info['subcats']
    
    while True:
        print(f"\n{BOLD}¿A qué subcategoría de {main_category} quieres asignar este tiempo?{RESET}")
        for i, subcat in enumerate(subcategories):
            print(f"  {GREEN}{i+1}. {subcat}{RESET}")
        print(f"  {LIGHT_GRAY}0. No asignar (General de {main_category}){RESET}")
        
        opcion = input(f"{BOLD}Elige una opción (0-{len(subcategories)}): {RESET}").strip()
        try:
            opcion_int = int(opcion)
            if opcion_int == 0:
                return None
            elif 1 <= opcion_int <= len(subcategories):
                return subcategories[opcion_int - 1]
            else:
                print(f"{RED}Opción no válida. Intenta de nuevo.{RESET}")
                time.sleep(1)
        except ValueError:
            print(f"{RED}Entrada inválida. Por favor, ingresa SOLO NÚMEROS enteros.{RESET}")
            time.sleep(1)

def assign_time_to_specific_category(duration_minutes, specific_category):
    """
    Asigna el tiempo a la subcategoría específica global.
    Args:
        duration_minutes (int): Duración en minutos.
        specific_category (str): Nombre de la subcategoría (ej. "Programación", "Inclub").
    """
    global total_specific_category_times
    if specific_category in total_specific_category_times:
        total_specific_category_times[specific_category] += duration_minutes
    else:
        total_specific_category_times[specific_category] = duration_minutes # Should not happen if pre-defined

def display_specific_category_times():
    """
    Muestra el tiempo de trabajo categorizado por subcategorías (Estudio, Trabajo, Lectura).
    Organiza por categoría principal y aplica colores.
    """
    clear_screen()
    print(f"{BOLD}{BLUE}--- Tiempo Productivo Categorizado (Sesión Actual) ---{RESET}")
    has_data = False

    for main_cat, info in SPECIFIC_SUBCATEGORY_MAPPING.items():
        subcategories = info['subcats']
        color = info['color']
        
        category_has_data = False
        category_total_minutes = 0
        
        subcat_display_lines = []
        for subcat in subcategories:
            minutes = total_specific_category_times.get(subcat, 0)
            if minutes > 0:
                subcat_display_lines.append(f"  {color}- {subcat}: {format_time_hh_mm_minutes(minutes)}{RESET}")
                category_total_minutes += minutes
                category_has_data = True
                has_data = True

        if category_has_data:
            print(f"\n{BOLD}{color}{main_cat}:{RESET}")
            for line in subcat_display_lines:
                print(line)
            print(f"  {color}Total {main_cat}: {BOLD}{format_time_hh_mm_minutes(category_total_minutes)}{RESET}")

    if not has_data:
        print(f"{LIGHT_GRAY}Aún no hay tiempo registrado en categorías específicas en esta sesión.{RESET}")
    
    # Nuevo: Muestra el tiempo total transcurrido del script
    print(f"\n{BOLD}{CYAN}Total de Tiempo Registrado: {get_total_script_run_time()}{RESET}")

    print(f"{LIGHT_GRAY}(Estos totales de categorías se reinician al cerrar el programa){RESET}")
    input(f"\n{BOLD}{LIGHT_GRAY}Presiona Enter para volver al menú principal...{RESET}")


# ==============================================================================
# Función principal para la cuenta regresiva de cualquier período
# ==============================================================================
def countdown_period(duration_seconds, phase_name, quote,
                     pomodoros_completed_session, short_breaks_completed_session, long_breaks_completed_session,
                     daily_activity_name=None):
    """
    Realiza una cuenta regresiva para un período dado, mostrando el tiempo restante,
    una barra de progreso, contadores de sesión acumulados y una frase motivadora.
    Permite pausar/reanudar presionando Enter.
    Permite terminar un Pomodoro de TRABAJO anticipadamente presionando 'Q'.
    Al finalizar, reproduce un sonido.

    Returns:
        tuple: (actual_seconds_elapsed_in_phase, status)
            actual_seconds_elapsed_in_phase (int): Segundos reales que pasaron en esta fase.
            status (str):
                'completed': El temporizador llegó a 0.
                'early_end_registered': Usuario presionó 'Q' y optó por registrar el tiempo.
                'early_end_not_registered': Usuario presionó 'Q' y optó por NO registrar el tiempo.
                'user_cancelled_all': Usuario presionó Ctrl+C y eligió cancelar todos los ciclos.
                'user_skip_phase': Usuario presionó Ctrl+C y eligió saltar solo esta fase.
    """
    phase_color = BLUE if "TRABAJO" in phase_name else ORANGE if "DESCANSO" in phase_name else RESET
    
    total_duration_seconds_initial = duration_seconds
    current_seconds = duration_seconds
    start_time_phase = datetime.datetime.now() # Marca de tiempo cuando la fase actual comienza
    
    is_paused = False

    display_phase_name = phase_name
    if daily_activity_name:
        display_phase_name = f"{phase_name} ({daily_activity_name})"

    try: # Bloque principal para capturar KeyboardInterrupt (Ctrl+C)
        while current_seconds >= 0:
            clear_screen()
            print(f"{BOLD}{phase_color}--- FASE DE {display_phase_name} ---{RESET}")
            
            print(f"{BOLD}Sesión: {GREEN}Pomodoros: {pomodoros_completed_session}{RESET} | {ORANGE}Descansos: {short_breaks_completed_session}{RESET} | {BLUE}Descansos largos: {long_breaks_completed_session}{RESET}") 
            print("-" * 60)

            print(f"\n{LIGHT_GRAY}\"{quote}\"{RESET}\n")

            print(f"{create_progress_bar(current_seconds, total_duration_seconds_initial)} Tiempo restante: {display_timer(current_seconds)}")
            
            # Instrucción de acción para el usuario
            action_prompt = ""
            if "TRABAJO" in phase_name:
                action_prompt = f"{BOLD}{LIGHT_GRAY}Presiona [ENTER] para pausar. Presiona [Q] para terminar este {phase_name} anticipadamente.{RESET}"
            else:
                action_prompt = f"{BOLD}{LIGHT_GRAY}Presiona [ENTER] para pausar...{RESET}"
            print(action_prompt)

            # Bucle para verificar la entrada del teclado de forma no bloqueante
            for _ in range(10): # Reduce el tiempo de sleep y bucle más para mayor capacidad de respuesta (10 * 0.1s = 1s)
                if kbhit_os_specific():
                    key = getch_os_specific().lower() # Lee la tecla y la convierte a minúscula
                    if key in ('\r', '\n'): # Tecla Enter para pausar/reanudar
                        is_paused = not is_paused 
                        # Limpia cualquier tecla en el búfer para evitar múltiples activaciones
                        while kbhit_os_specific():
                            getch_os_specific()
                        break 
                    elif key == 'q' and "TRABAJO" in phase_name: # Tecla 'Q' para terminar anticipadamente (solo en TRABAJO)
                        elapsed_seconds_during_phase = int((datetime.datetime.now() - start_time_phase).total_seconds())
                        clear_screen()
                        print(f"\n{BOLD}{YELLOW}¡{phase_name} terminado con anticipación!{RESET}")
                        
                        if elapsed_seconds_during_phase > 0: # Solo pregunta si hay tiempo transcurrido
                            print(f"{BOLD}{LIGHT_GRAY}Tiempo transcurrido en esta fase: {format_time_hh_mm_minutes(elapsed_seconds_during_phase // 60)}{RESET}")
                            confirm_early_end = input(f"\n{BOLD}¿Quieres registrar estos {format_time_hh_mm_minutes(elapsed_seconds_during_phase // 60)} como tiempo productivo? {GREEN}[S]{RESET}/{RED}[N]{RESET}: ").lower().strip()
                            if confirm_early_end == 's':
                                return (elapsed_seconds_during_phase, 'early_end_registered')
                            else:
                                print(f"{LIGHT_GRAY}Tiempo no registrado. Continuando con los ciclos.{RESET}")
                                time.sleep(1) # Pequeña pausa antes de continuar
                                return (elapsed_seconds_during_phase, 'early_end_not_registered')
                        else: # Si no pasó tiempo, no hay nada que registrar
                            print(f"{LIGHT_GRAY}No se registró tiempo. Continuando con los ciclos.{RESET}")
                            time.sleep(1)
                            return (0, 'early_end_not_registered')

                time.sleep(0.1) # Pausa breve para no consumir CPU

            if not is_paused:
                current_seconds -= 1

        # Si el bucle termina, el período se completó naturalmente
        elapsed_seconds_during_phase = total_duration_seconds_initial # Se completó la duración total
        clear_screen()
        print(f"{BOLD}{phase_color}--- FASE DE {display_phase_name} TERMINADA ---{RESET}")
        print(f"¡{BOLD}{phase_color}{display_phase_name}{RESET} completado! Es hora de cambiar de fase.\n")

        # Reproducir sonido
        try:
            sound_file = 'bell.wav' if "TRABAJO" in phase_name else 'notif.wav'
            playsound(sound_file) 
        except Exception as e:
            print(f"{RED}ADVERTENCIA: No se pudo reproducir el sonido de notificación '{sound_file}': {e}{RESET}")
            print(f"{RED}Asegúrate de que '{sound_file}' exista en la misma carpeta y playsound esté instalado correctamente.{RESET}")

        time.sleep(3) # Pausa para que el usuario lea el mensaje
        return (elapsed_seconds_during_phase, 'completed')

    except KeyboardInterrupt: # Captura Ctrl+C
        clear_screen()
        choice = input(f"{RED}{BOLD}¡{phase_name} interrumpido por el usuario!{RESET}\n{BOLD}¿Qué quieres hacer? {YELLOW}[S]{RESET}altar a siguiente fase / {RED}[C]{RESET}ancelar todos los ciclos: ").lower().strip()
        elapsed_seconds_during_phase = int((datetime.datetime.now() - start_time_phase).total_seconds()) # Calcular tiempo transcurrido hasta la interrupción
        if choice == 'c':
            print(f"{BOLD}{RED}¡Ciclos cancelados! Vuelve cuando estés listo. 👋{RESET}")
            time.sleep(1)
            return (elapsed_seconds_during_phase, 'user_cancelled_all')
        else:
            print(f"{BOLD}{GREEN}Saltando al siguiente período...{RESET}")
            time.sleep(1)
            return (elapsed_seconds_during_phase, 'user_skip_phase')

# ==============================================================================
# Función principal para ejecutar los ciclos Pomodoro
# ==============================================================================
def run_pomodoro(work_minutes=90, short_break_minutes=15, long_break_minutes=45, num_cycles=4, # ¡Nuevos valores predeterminados!
                 pomodoros_completed_session_total=0, short_breaks_completed_session_total=0, long_breaks_completed_session_total=0,
                 daily_activity_name=None):
    """
    Ejecuta un conjunto de ciclos Pomodoro con la configuración dada.
    Permite al usuario controlar el inicio de cada fase.
    Gestiona y retorna los contadores de Pomodoros y descansos completados en este set de ciclos.
    """
    clear_screen()
    print(f"{BOLD}Iniciando un nuevo conjunto de ciclos Pomodoro...{RESET}")
    print(f"Configuración: {work_minutes} min de trabajo, {short_break_minutes} min de descanso corto, {long_break_minutes} min de descanso largo cada {num_cycles} ciclos.")
    time.sleep(2)

    current_set_pomodoros = 0
    current_set_short_breaks = 0
    current_set_long_breaks = 0

    work_seconds = work_minutes * 60
    short_break_seconds = short_break_minutes * 60
    long_break_seconds = long_break_minutes * 60

    input(f"{BOLD}{GREEN}Presiona Enter para iniciar el primer período de TRABAJO...{RESET}")

    for i in range(1, num_cycles + 1):
        clear_screen() # Limpia la pantalla al inicio de cada iteración del ciclo
        print(f"\n{BOLD}--- CICLO {i}/{num_cycles} ---{RESET}")
        
        # --- Fase de TRABAJO ---
        work_quote = random.choice(WORK_QUOTES)
        
        elapsed_seconds_work, work_outcome = countdown_period(work_seconds, "TRABAJO", work_quote,
                                                              pomodoros_completed_session_total + current_set_pomodoros, 
                                                              short_breaks_completed_session_total + current_set_short_breaks, 
                                                              long_breaks_completed_session_total + current_set_long_breaks,
                                                              daily_activity_name=daily_activity_name)
        
        # Procesar el resultado de la fase de trabajo
        if work_outcome == 'completed':
            current_set_pomodoros += 1
            # Lógica de asignación de subcategoría específica (para pomodoros COMPLETADOS naturalmente)
            if daily_activity_name and daily_activity_name in SPECIFIC_SUBCATEGORY_MAPPING:
                specific_category_assigned = prompt_specific_work_category(daily_activity_name)
                if specific_category_assigned:
                    assign_time_to_specific_category(work_minutes, specific_category_assigned) # Asigna minutos completos
                    print(f"Tiempo de {work_minutes} minutos asignado a {specific_category_assigned}.")
                else:
                    print(f"Tiempo no asignado a una subcategoría específica de {daily_activity_name}.")
            elif daily_activity_name:
                 print(f"Tiempo de {work_minutes} minutos registrado como {daily_activity_name}.")
            time.sleep(1) # Pausa breve para que el usuario vea el mensaje
        
        elif work_outcome == 'early_end_registered':
            elapsed_minutes_work = elapsed_seconds_work // 60
            if elapsed_minutes_work > 0: # Solo si hubo tiempo significativo transcurrido para registrar
                if daily_activity_name and daily_activity_name in SPECIFIC_SUBCATEGORY_MAPPING:
                    specific_category_assigned = prompt_specific_work_category(daily_activity_name)
                    if specific_category_assigned:
                        assign_time_to_specific_category(elapsed_minutes_work, specific_category_assigned)
                        print(f"Tiempo de {elapsed_minutes_work} minutos asignado a {specific_category_assigned} (finalizado anticipadamente).")
                    else:
                        print(f"Tiempo de {elapsed_minutes_work} minutos registrado como {daily_activity_name} (finalizado anticipadamente).")
                elif daily_activity_name:
                    print(f"Tiempo de {elapsed_minutes_work} minutos registrado como {daily_activity_name} (finalizado anticipadamente).")
            else: # No se registra tiempo si no transcurrió un minuto completo
                print(f"{LIGHT_GRAY}Menos de un minuto transcurrido. Tiempo no registrado.{RESET}")
            # No se incrementa current_set_pomodoros si se finaliza anticipadamente, solo se registra el tiempo.
            time.sleep(1) 
        
        elif work_outcome == 'early_end_not_registered':
            # El usuario eligió no registrar el tiempo, simplemente se procede al descanso o al siguiente ciclo
            time.sleep(1) 

        elif work_outcome == 'user_cancelled_all':
            # Si el usuario eligió cancelar todos los ciclos, salimos de la función principal
            return current_set_pomodoros, current_set_short_breaks, current_set_long_breaks 

        elif work_outcome == 'user_skip_phase':
            # Si el usuario eligió saltar la fase actual, vamos a la siguiente iteración del bucle.
            # Esto significa que el descanso asociado a este ciclo también se salta.
            if i < num_cycles:
                input(f"{BOLD}{GREEN}Presiona Enter para iniciar el próximo período de TRABAJO...{RESET}")
            continue # Salta al siguiente ciclo (próxima iteración del bucle for)

        # --- Fase de DESCANSO (corto o largo) ---
        # Esta lógica solo se ejecuta si la fase de trabajo no fue cancelada completamente o saltada.
        is_long_break = (i % num_cycles == 0) # El descanso largo es cada 'num_cycles' pomodoros
        break_message = "DESCANSO LARGO" if is_long_break else "DESCANSO CORTO"
        break_duration = long_break_seconds if is_long_break else short_break_seconds
        break_quote = random.choice(BREAK_QUOTES)

        input(f"{BOLD}{ORANGE}Presiona Enter para iniciar el {break_message}...{RESET}")
        
        elapsed_seconds_break, break_outcome = countdown_period(break_duration, break_message, break_quote,
                                                                pomodoros_completed_session_total + current_set_pomodoros, 
                                                                short_breaks_completed_session_total + current_set_short_breaks, 
                                                                long_breaks_completed_session_total + current_set_long_breaks,
                                                                daily_activity_name=daily_activity_name)
        
        # Procesar el resultado de la fase de descanso
        if break_outcome == 'completed':
            if is_long_break:
                current_set_long_breaks += 1
            else:
                current_set_short_breaks += 1
        
        elif break_outcome == 'user_cancelled_all':
            return current_set_pomodoros, current_set_short_breaks, current_set_long_breaks # Salir de la función

        elif break_outcome == 'user_skip_phase':
            pass # Continúa al siguiente ciclo como si el descanso hubiera terminado (no se añade al contador de descansos)

        if i < num_cycles:
            input(f"{BOLD}{GREEN}Presiona Enter para iniciar el próximo período de TRABAJO...{RESET}")

    clear_screen()
    print(f"{BOLD}{BLUE}¡Todos los ciclos Pomodoro completados en este conjunto! ¡Excelente trabajo! ✨{RESET}")
    return current_set_pomodoros, current_set_short_breaks, current_set_long_breaks

# ==============================================================================
# Función para el temporizador simple (cuenta hacia arriba)
# ==============================================================================
def run_simple_timer(total_pomodoros_session, total_short_breaks_session, total_long_breaks_session,
                     daily_activity_name=None):
    """
    Ejecuta un temporizador simple que cuenta hacia arriba desde 0.
    Es cancelable con Ctrl+C.
    Retorna el tiempo total en minutos transcurrido para poder sumarlo.
    """
    clear_screen()
    display_title = "TEMPORIZADOR SIMPLE"
    if daily_activity_name:
        display_title = f"TEMPORIZADOR SIMPLE ({daily_activity_name})"

    print(f"{BOLD}{BLUE}--- {display_title} ---{RESET}")
    print(f"{BOLD}{LIGHT_GRAY}Presiona Ctrl+C en cualquier momento para detener.{RESET}\n")

    current_elapsed_seconds = 0
    is_paused = False
    
    try:
        while True:
            clear_screen()
            print(f"{BOLD}{BLUE}--- {display_title} ---{RESET}")
            print(f"{BOLD}Sesión: {GREEN}Pomodoros: {total_pomodoros_session}{RESET} | {ORANGE}Descansos: {total_short_breaks_session}{RESET} | {BLUE}Descansos largos: {total_long_breaks_session}{RESET}") 
            print("-" * 60)

            display_str = display_timer(current_elapsed_seconds)
            
            print(f"\n{BOLD}Tiempo transcurrido: {display_str}{RESET}")
            
            # Nuevo: Muestra el tiempo total transcurrido del script
            print(f"{BOLD}{CYAN}Total de Tiempo Registrado (Script): {get_total_script_run_time()}{RESET}")

            if is_paused:
                print(f"\n{BOLD}{YELLOW}PAUSADO. Presiona [ENTER] para reanudar...{RESET}")
            else:
                print(f"\n{BOLD}{LIGHT_GRAY}Presiona [ENTER] para pausar...{RESET}") 

            for _ in range(10): # Reduce sleep time and loop more for responsiveness
                if kbhit_os_specific():
                    key = getch_os_specific()
                    if key in ('\r', '\n'):
                        is_paused = not is_paused 
                        # Clear any buffered keys
                        while kbhit_os_specific():
                            getch_os_specific()
                        break 
                    else:
                        pass 
                time.sleep(0.1) # Sleep for a short interval


            if not is_paused:
                current_elapsed_seconds += 1

    except KeyboardInterrupt:
        clear_screen()
        # Modificación para que el temporizador simple también ofrezca asignar tiempo
        elapsed_minutes = int(current_elapsed_seconds / 60) # Calculate minutes here
        
        print(f"{RED}{BOLD}¡Temporizador Simple interrumpido!{RESET}")
        choice = input(f"{BOLD}Tiempo transcurrido: {display_timer(current_elapsed_seconds)}. ¿Qué quieres hacer? {YELLOW}[S]{RESET}umar tiempo y volver al menú principal / {RED}[C]{RESET}ancelar y no sumar tiempo: ").lower().strip()
        if choice == 'c':
            print(f"{BOLD}{RED}Temporizador cancelado. Tiempo no sumado. 👋{RESET}")
            time.sleep(1)
            return 0 # Retorna 0 minutos si se cancela
        else:
            print(f"{BOLD}{GREEN}Sumando tiempo al total de trabajo...{RESET}")
            if daily_activity_name in SPECIFIC_SUBCATEGORY_MAPPING: # Use daily_activity_name to check mapping
                specific_category_assigned = prompt_specific_work_category(daily_activity_name)
                if specific_category_assigned:
                    assign_time_to_specific_category(elapsed_minutes, specific_category_assigned) # Pass minutes directly
                    print(f"Tiempo de {elapsed_minutes} minutos asignado a {specific_category_assigned}.")
                else:
                    print(f"Tiempo no asignado a una subcategoría específica de {daily_activity_name}.")
            elif daily_activity_name: # Si es una categoría general pero no tiene subcategorías específicas
                print(f"Tiempo de {elapsed_minutes} minutos registrado como {daily_activity_name}.")
            else: # Si no hay actividad diaria asignada, solo informa
                print("La categoría diaria actual no tiene subcategorías específicas para asignar tiempo.")

            time.sleep(1)
            return elapsed_minutes # Retorna el tiempo transcurrido para que se sume en main()
    
    # If timer completes naturally (not interrupted by Ctrl+C)
    # This part will rarely be reached unless current_elapsed_seconds is capped and reaches max.
    # Given its nature as an "upward" timer, it's typically interrupted by Ctrl+C.
    # However, if it were to complete (e.g., if it had a target duration), the logic below would apply.
    elapsed_minutes = int(current_elapsed_seconds / 60) # Calculate minutes here
    print(f"{BOLD}{BLUE}Temporizador Simple finalizado automáticamente. Tiempo transcurrido: {display_timer(current_elapsed_seconds)}{RESET}")
    if daily_activity_name in SPECIFIC_SUBCATEGORY_MAPPING: # Use daily_activity_name to check mapping
        specific_category_assigned = prompt_specific_work_category(daily_activity_name)
        if specific_category_assigned:
            assign_time_to_specific_category(elapsed_minutes, specific_category_assigned) # Pass minutes directly
            print(f"Tiempo de {elapsed_minutes} minutos asignado a {specific_category_assigned}.")
        else:
            print(f"Tiempo no asignado a una subcategoría específica de {daily_activity_name}.")
    elif daily_activity_name:
        print(f"Tiempo de {elapsed_minutes} minutos registrado como {daily_activity_name}.")
    else:
        print("La categoría diaria actual no tiene subcategorías específicas para asignar tiempo.")
    
    time.sleep(1)
    return elapsed_minutes


# ==============================================================================
# Funciones auxiliares para formatear tiempos (Mantengo las funciones auxiliares aquí)
# ==============================================================================
def format_time_hh_mm_seconds(total_seconds): 
    """
    Convierte el total de segundos a formato HH:MM (solo horas y minutos).
    """
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    return f"{hours:02d}:{minutes:02d}"

def format_time_hh_mm_ss(total_seconds):
    """
    Convierte el total de segundos a formato HH:MM:SS.
    """
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# ==============================================================================
# Funciones para el seguimiento de actividades diarias generales (actualizadas)
# ==============================================================================
def change_current_daily_activity(new_category_name):
    """
    Logs the currently active segment if any, and then sets up the new activity segment.
    This function is responsible for creating new entries in daily_activity_log.
    Args:
        new_category_name (str): The name of the new activity category, or None to just log and stop tracking.
    """
    global daily_activity_log, current_daily_activity, last_activity_start_time

    current_time = datetime.datetime.now()

    # Log the segment that is *ending* (if there was one)
    # Only log if new_category_name is DIFFERENT from current_daily_activity OR if we are explicitly stopping (new_category_name is None)
    if current_daily_activity is not None and last_activity_start_time is not None and \
       (new_category_name != current_daily_activity or new_category_name is None):
        
        duration_seconds = (current_time - last_activity_start_time).total_seconds()
        # Only log if there was actual time spent (e.g., more than a very tiny fraction of a second)
        if duration_seconds >= 1.0: # Consider a threshold to avoid logging negligible time, now 1 second
            daily_activity_log.append({
                'category': current_daily_activity,
                'start': last_activity_start_time,
                'end': current_time,
                'duration': duration_seconds
            })
            # print(f"DEBUG: Logged segment: {current_daily_activity} ({last_activity_start_time.strftime('%H:%M:%S')} - {current_time.strftime('%H:%M:%S')}) Dur: {format_time_hh_mm_ss(duration_seconds)}") # Debug

    # Start the new segment (only if a new category name is provided OR if current_daily_activity was None and we're starting fresh)
    if new_category_name is not None and new_category_name != current_daily_activity:
        current_daily_activity = new_category_name
        last_activity_start_time = current_time # The new segment starts from THIS moment
        # print(f"DEBUG: New activity started: {current_daily_activity} at {last_activity_start_time.strftime('%H:%M:%S')}") # Debug
    elif new_category_name is None: # Explicitly stopping
        current_daily_activity = None
        last_activity_start_time = None
    # If new_category_name is the same as current_daily_activity, we do nothing.
    # This ensures no new log entry is created and last_activity_start_time is not reset.


def prompt_activity_category_choice(categories_list, is_initial_setup=False):
    """
    Prompts the user to select an activity category.
    Returns the chosen category name or None if cancelled.
    """
    while True:
        clear_screen()
        if is_initial_setup:
            print(f"{BOLD}{GREEN}--- Selecciona tu Actividad Diaria Actual ---{RESET}\n")
            print(f"{LIGHT_GRAY}Para empezar a registrar el tiempo, elige la actividad que estás realizando ahora.{RESET}\n")
        else:
            print(f"{BOLD}{GREEN}--- Cambiar Actividad Diaria General ---{RESET}\n")
            print(f"{LIGHT_GRAY}Tu actividad actual es: {BOLD}{BLUE}{current_daily_activity}{RESET}\n")
            print(f"{LIGHT_GRAY}Selecciona la nueva actividad que vas a realizar:{RESET}\n")
            
        print(f"{BOLD}{YELLOW}Opciones de Actividad:{RESET}")
        for i, cat in enumerate(categories_list):
            print(f"  {BOLD}{i+1}. {CYAN}{cat}{RESET}")
        
        # Option 0 is only for returning to menu if tracking is already active and it's not initial setup
        if not is_initial_setup and current_daily_activity is not None:
            print(f"\n  {BOLD}{0}. {RED}Cancelar / Volver al Menú (Mantener '{current_daily_activity}') {RESET}")

        try:
            choice_str = input(f"\n{BOLD}Elige una opción ({'0-' if not is_initial_setup and current_daily_activity is not None else ''}1-{len(categories_list)}): {RESET}").strip()
            choice = int(choice_str)

            if choice == 0 and not is_initial_setup and current_daily_activity is not None:
                return None # Indicates cancellation
            elif choice == 0 and is_initial_setup: # If user tries to cancel initial setup
                return None 

            if 1 <= choice <= len(categories_list):
                return categories_list[choice - 1]
            else:
                print(f"{RED}Opción no válida. Intenta de nuevo.{RESET}")
                time.sleep(1)
        except ValueError:
            print(f"{RED}Entrada inválida. Por favor, ingresa un número entero.{RESET}")
            time.sleep(1)


def show_daily_activity_summary(daily_activity_data_log, current_active_category, last_active_start_time, final_summary=False):
    """
    Muestra el resumen de tiempo para todas las categorías diarias, tanto por segmento como acumulado.
    Calcula el tiempo de la actividad actual en curso para el resumen acumulado.
    """
    clear_screen()
    print(f"{BOLD}{BLUE}--- Resumen de Actividades Diarias Generales ({'Sesión Actual' if not final_summary else 'Final'}) ---{RESET}\n")
    
    # Detalle de Segmentos de Actividad (Moved to top as requested)
    print(f"{BOLD}Detalle de Segmentos de Actividad:{RESET}")
    # Add the current running segment to the display list temporarily if not final summary
    temp_display_log = list(daily_activity_data_log) # Make a copy
    if not final_summary and current_active_category is not None and last_active_start_time is not None:
        current_dt_for_display = datetime.datetime.now()
        # Make sure 'start' is a datetime object when adding to temp_display_log
        temp_display_log.append({
            'category': current_active_category,
            'start': last_active_start_time, 
            'end': current_dt_for_display, # Display up to now
            'duration': (current_dt_for_display - last_active_start_time).total_seconds()
        })

    if not temp_display_log:
        print(f"  {LIGHT_GRAY}No hay segmentos de actividad registrados en esta sesión.{RESET}")
    else:
        # Sort by start time for chronological order
        sorted_segments = sorted(temp_display_log, key=lambda x: x['start'])
        for entry in sorted_segments:
            category_color = DAILY_CATEGORY_COLORS.get(entry['category'], LIGHT_GRAY) # Get color for category
            start_str = entry['start'].strftime('%H:%M') # Format to HH:MM
            end_str = entry['end'].strftime('%H:%M')     # Format to HH:MM
            duration_seconds_segment = entry['duration'] # Get duration in seconds
            duration_str = format_time_hh_mm_ss(duration_seconds_segment) # Format duration to HH:MM:SS
            print(f"  {category_color}{entry['category']}: {duration_str} ({start_str} - {end_str}){RESET}")

    print(f"\n{BOLD}Tiempo Acumulado por Categoría:{RESET}")
    # Calculate accumulated time per category
    accumulated_times = {cat: 0 for cat in DEFAULT_DAILY_CATEGORIES}
    # Add any activity not in default categories
    for entry in daily_activity_data_log:
        accumulated_times[entry['category']] = accumulated_times.get(entry['category'], 0) + entry['duration']

    # Add the duration of the current partial segment that is still running
    if current_active_category is not None and last_active_start_time is not None:
        current_running_duration = (datetime.datetime.now() - last_active_start_time).total_seconds()
        if current_running_duration > 0:
            accumulated_times[current_active_category] = accumulated_times.get(current_active_category, 0) + current_running_duration
            
    sorted_accumulated = sorted(accumulated_times.items(), key=lambda item: item[1], reverse=True)
    has_accumulated_data = False
    for category, seconds in sorted_accumulated:
        if seconds > 0:
            category_color = DAILY_CATEGORY_COLORS.get(category, LIGHT_GRAY) # Get color for category
            # Convert seconds to minutes for HH:MM format
            total_minutes = int(seconds / 60)
            print(f"  {category_color}{category}: {BOLD}{format_time_hh_mm_minutes(total_minutes)}{RESET}") # Use format_time_hh_mm_minutes
            has_accumulated_data = True
    
    if not has_accumulated_data:
        print(f"  {LIGHT_GRAY}Aún no hay tiempo registrado en categorías generales en esta sesión.{RESET}")

    # Nuevo: Muestra el tiempo total transcurrido del script en el resumen de actividades
    print(f"\n{BOLD}{CYAN}Total de Tiempo Registrado (Script): {get_total_script_run_time()}{RESET}")

    if not final_summary:
        input(f"\n{BOLD}{LIGHT_GRAY}Presiona Enter para volver al menú principal...{RESET}")
    else:
        print(f"\n{LIGHT_GRAY}¡Estos totales se reinician al cerrar el programa!{RESET}")
        time.sleep(2) # Give user time to read final message

# ==============================================================================
# Función principal para manejar la configuración del usuario y el bucle de sesión
# ==============================================================================
def main():
    """
    Permite al usuario configurar el temporador Pomodoro o usar los valores por defecto.
    Maneja entradas inválidas con un bloque try-except.
    Mantiene un bucle para permitir múltiples conjuntos de ciclos en una sesión.
    También gestiona el seguimiento del tiempo de actividades diarias generales.
    """
    # Contadores de la sesión de Pomodoro (existentes)
    total_pomodoros_session = 0
    total_short_breaks_session = 0
    total_long_breaks_session = 0
    total_work_minutes_session = 0
    total_break_minutes_session = 0

    # Inicialización de variables globales para el seguimiento de actividades diarias y específicas
    global daily_activity_log, current_daily_activity, last_activity_start_time, total_specific_category_times
    daily_activity_log = [] # Reset for new session
    current_daily_activity = None
    last_activity_start_time = None
    # Reset specific category times for a new session
    total_specific_category_times = {key: 0 for key in total_specific_category_times}


    # Solicitar la actividad inicial al comenzar Pydoro
    clear_screen()
    print(f"{BOLD}{GREEN}--- Iniciando Pydoro para el Seguimiento Diario ---{RESET}")
    initial_activity_choice = prompt_activity_category_choice(DEFAULT_DAILY_CATEGORIES, is_initial_setup=True)
    
    if initial_activity_choice is None: # If user cancels initial selection
        print(f"{RED}No se seleccionó una actividad inicial. Pydoro se cerrará.{RESET}")
        time.sleep(2)
        return # Exit main if no initial activity is set

    # Set the initial activity and start tracking
    change_current_daily_activity(initial_activity_choice) # This will set current_daily_activity and last_activity_start_time
    print(f"{BOLD}{GREEN}Actividad inicial establecida: {current_daily_activity}{RESET}")
    time.sleep(1)

    while True:
        try:
            # Calculate and display current segment's elapsed time *for display only*
            current_segment_display_duration_seconds = 0
            if last_activity_start_time:
                current_segment_display_duration_seconds = (datetime.datetime.now() - last_activity_start_time).total_seconds()
            
            clear_screen()
            print(f"{BOLD}{GREEN}--- Bienvenido al Temporador Pydoro Personalizado ---{RESET}")
            print(f"{BOLD}{LIGHT_GRAY}Outwork others consistently.{RESET}\n")

            # Mostrar la actividad diaria actual y la duración de su segmento actual
            # NOTA: Este tiempo no se actualiza en tiempo real cada segundo mientras esperas input
            print(f"{BOLD}{BLUE}Actividad Diaria Actual: {current_daily_activity} (Duración en este segmento: {format_time_hh_mm_ss(current_segment_display_duration_seconds)}){RESET}\n")

            # REEMPLAZO: Resumen de la Sesión Actual (Pomodoro) por Tiempo Acumulado por Categoría
            print(f"{BOLD}{BLUE}--- Tiempo Acumulado por Categoría General (Sesión Actual) ---{RESET}")
            # Calculate accumulated time per category for main menu display
            current_accumulated_times = {cat: 0 for cat in DEFAULT_DAILY_CATEGORIES}
            for entry in daily_activity_log:
                current_accumulated_times[entry['category']] = current_accumulated_times.get(entry['category'], 0) + entry['duration']
            
            # Add the duration of the current partial segment that is still running
            if current_daily_activity is not None and last_activity_start_time is not None:
                current_running_duration_main_menu = (datetime.datetime.now() - last_activity_start_time).total_seconds()
                if current_running_duration_main_menu > 0:
                    current_accumulated_times[current_daily_activity] = current_accumulated_times.get(current_daily_activity, 0) + current_running_duration_main_menu
            
            sorted_current_accumulated = sorted(current_accumulated_times.items(), key=lambda item: item[1], reverse=True)
            has_current_accumulated_data = False
            for category, seconds in sorted_current_accumulated:
                if seconds > 0:
                    category_color = DAILY_CATEGORY_COLORS.get(category, LIGHT_GRAY)
                    total_minutes = int(seconds / 60)
                    print(f"  {category_color}{category}: {BOLD}{format_time_hh_mm_minutes(total_minutes)}{RESET}")
                    has_current_accumulated_data = True
            
            if not has_current_accumulated_data:
                print(f"  {LIGHT_GRAY}Aún no hay tiempo registrado en categorías generales.{RESET}")
            print(f"{BOLD}----------------------------------{RESET}\n")

            # Nuevo: Muestra el tiempo total transcurrido del script en el menú principal
            print(f"{BOLD}{CYAN}Total de Tiempo Registrado (Script): {get_total_script_run_time()}{RESET}")
            print("\n") # Espacio para separar


            print(f"{BOLD}Selecciona una opción:{RESET}")
            # Determine if Pomodoro/Simple Timer options should be shown
            allow_pomodoro_timer = current_daily_activity in SPECIFIC_SUBCATEGORY_MAPPING

            menu_options = []
            option_counter = 1 # Start option numbering from 1

            # Only add Pomodoro and Simple Timer options if allowed by current activity
            if allow_pomodoro_timer:
                menu_options.append(f"  {GREEN}{option_counter}. Iniciar nuevo conjunto de ciclos Pomodoro{RESET}")
                option_pomodoro = str(option_counter)
                option_counter += 1
                menu_options.append(f"  {BLUE}{option_counter}. Iniciar Temporizador Simple (cuenta hacia arriba){RESET}")
                option_simple_timer = str(option_counter)
                option_counter += 1

            # Common options always available
            menu_options.append(f"  {ORANGE}{option_counter}. Ver Tiempo Productivo Categorizado (Estudio/Trabajo/Lectura){RESET}") # Renamed
            option_specific_cat_summary = str(option_counter)
            option_counter += 1

            menu_options.append(f"  {YELLOW}{option_counter}. Cambiar Actividad Diaria General{RESET}")
            option_change_daily_activity = str(option_counter)
            option_counter += 1
            
            menu_options.append(f"  {MAGENTA}{option_counter}. Actualizar Vista del Menú (refresca duración){RESET}") # Nueva opción
            option_refresh_view = str(option_counter)
            option_counter += 1

            menu_options.append(f"  {LIGHT_GRAY}{option_counter}. Ver Resumen de Actividades Diarias Generales{RESET}")
            option_daily_summary = str(option_counter)
            option_counter += 1

            menu_options.append(f"  {RED}{option_counter}. Salir del programa{RESET}")
            option_exit = str(option_counter)

            for option_text in menu_options:
                print(option_text)
            
            valid_choices = [str(i) for i in range(1, option_counter + 1)] # All available options

            # Revert to standard blocking input for stability
            choice = input(f"{BOLD}Tu elección (1-{option_counter -1}): {RESET}").strip() # Corrected range in prompt
            
            # Input validation loop
            while choice not in valid_choices:
                print(f"{RED}Opción no válida. Por favor, ingresa un número entre 1 y {option_counter - 1}.{RESET}") # Corrected range in error
                time.sleep(1) # Give user time to read error message
                clear_screen() # Redraw menu
                
                # Recalculate duration for redrawn menu
                if last_activity_start_time:
                    current_segment_display_duration_seconds = (datetime.datetime.now() - last_activity_start_time).total_seconds()
                
                print(f"{BOLD}{GREEN}--- Bienvenido al Temporador Pydoro Personalizado ---{RESET}")
                print(f"{BOLD}{LIGHT_GRAY}Outwork others consistently.{RESET}\n")
                print(f"{BOLD}{BLUE}Actividad Diaria Actual: {current_daily_activity} (Duración en este segmento: {format_time_hh_mm_ss(current_segment_display_duration_seconds)}){RESET}\n")
                
                # Re-display accumulated time for categories
                print(f"{BOLD}{BLUE}--- Tiempo Acumulado por Categoría General (Sesión Actual) ---{RESET}")
                # Recalculate accumulated time per category for main menu display
                current_accumulated_times_redraw = {cat: 0 for cat in DEFAULT_DAILY_CATEGORIES}
                for entry in daily_activity_log:
                    current_accumulated_times_redraw[entry['category']] = current_accumulated_times_redraw.get(entry['category'], 0) + entry['duration']
                
                if current_daily_activity is not None and last_activity_start_time is not None:
                    current_running_duration_main_menu_redraw = (datetime.datetime.now() - last_activity_start_time).total_seconds()
                    if current_running_duration_main_menu_redraw > 0:
                        current_accumulated_times_redraw[current_daily_activity] = current_accumulated_times_redraw.get(current_daily_activity, 0) + current_running_duration_main_menu_redraw
                
                sorted_current_accumulated_redraw = sorted(current_accumulated_times_redraw.items(), key=lambda item: item[1], reverse=True)
                has_current_accumulated_data_redraw = False
                for category, seconds in sorted_current_accumulated_redraw:
                    if seconds > 0:
                        category_color = DAILY_CATEGORY_COLORS.get(category, LIGHT_GRAY)
                        total_minutes = int(seconds / 60)
                        print(f"  {category_color}{category}: {BOLD}{format_time_hh_mm_minutes(total_minutes)}{RESET}")
                        has_current_accumulated_data_redraw = True
                
                if not has_current_accumulated_data_redraw:
                    print(f"  {LIGHT_GRAY}Aún no hay tiempo registrado en categorías generales.{RESET}")
                print(f"{BOLD}----------------------------------{RESET}\n")

                # Re-display total script run time
                print(f"{BOLD}{CYAN}Total de Tiempo Registrado (Script): {get_total_script_run_time()}{RESET}")
                print("\n") # Espacio para separar


                print(f"{BOLD}Selecciona una opción:{RESET}")
                for option_text in menu_options:
                    print(option_text)
                choice = input(f"{BOLD}Tu elección (1-{option_counter - 1}): {RESET}").strip() # Corrected range in prompt
            
            # --- Manejo de acciones basadas en la elección del usuario ---
            
            if allow_pomodoro_timer and choice == option_pomodoro:
                # No llamar a change_current_daily_activity aquí.
                # El Pomodoro es parte del segmento de la actividad diaria actual.
                # Los valores por defecto ahora vienen de la definición de run_pomodoro
                
                work, short_break, long_break, cycles = 90, 15, 45, 4 # Default values (aligned with run_pomodoro defaults)

                while True:
                    customize_choice = input(f"{BOLD}¿Quieres personalizar la configuración para este conjunto de ciclos? ({GREEN}s{RESET}/{RED}n{RESET}): {RESET}").lower().strip()
                    if customize_choice in ['s', 'n']:
                        break
                    else:
                        print(f"{RED}Opción no válida. Por favor, ingresa 's' o 'n'.{RESET}")
                        time.sleep(1)
                
                if customize_choice == 's':
                    while True:
                        try:
                            work = int(input(f"{YELLOW}Duración del período de TRABAJO (minutos): {RESET}"))
                            short_break = int(input(f"{YELLOW}Duración del DESCANSO CORTO (minutos): {RESET}"))
                            long_break = int(input(f"{YELLOW}Duración del DESCANSO LARGO (minutos): {RESET}"))
                            cycles = int(input(f"{YELLOW}Número de ciclos Pomodoro (ej. 4 para descanso largo): {RESET}"))
                            
                            if work <= 0 or short_break <= 0 or long_break <= 0 or cycles <= 0:
                                print(f"{RED}Las duraciones y el número de ciclos deben ser valores POSITIVOS. Intenta de nuevo.{RESET}")
                                time.sleep(1)
                            else:
                                break
                        except ValueError:
                            print(f"{RED}Entrada inválida. Por favor, ingresa SOLO NÚMEROS enteros.{RESET}")
                            time.sleep(1)
                            
                completed_pom, completed_short_break, completed_long_break = run_pomodoro(
                    work, short_break, long_break, cycles,
                    total_pomodoros_session, total_short_breaks_session, total_long_breaks_session,
                    daily_activity_name=current_daily_activity # Pass daily category to countdown for display
                )
                
                total_pomodoros_session += completed_pom
                total_short_breaks_session += completed_short_break
                total_long_breaks_session += completed_long_break
                # total_work_minutes_session and total_break_minutes_session are now updated
                # directly by assign_time_to_specific_category if specific,
                # or not tracked at this higher level if the user chose not to sum to specific.
                # The Pomodoros completed counter is the main high-level metric here.

                clear_screen()
                print(f"{BOLD}{BLUE}¡Conjunto de ciclos Pomodoro completado!{RESET}")
                print(f"{BOLD}Resumen de este conjunto:{RESET}")
                print(f"{GREEN}Pomodoros completados: {completed_pom}{RESET}")
                print(f"{ORANGE}Descansos cortos completados: {completed_short_break}{RESET}")
                print(f"{BLUE}Descansos largos completados: {completed_long_break}{RESET}")
                input(f"\n{BOLD}{LIGHT_GRAY}Presiona Enter para volver al menú principal...{RESET}")
                # ELIMINADO: No reiniciar last_activity_start_time aquí.
                # last_activity_start_time = datetime.datetime.now()
                
            elif allow_pomodoro_timer and choice == option_simple_timer: 
                # No llamar a change_current_daily_activity aquí.
                # El temporizador simple es parte del segmento de la actividad diaria actual.
                elapsed_minutes_simple = run_simple_timer(
                    total_pomodoros_session, total_short_breaks_session, total_long_breaks_session,
                    daily_activity_name=current_daily_activity # Pass daily category to simple timer for display
                )
                # total_work_minutes_session += elapsed_minutes_simple # Sumamos el tiempo reportado por el simple timer
                # This sum is now handled within run_simple_timer's logic for assignment
                # if the user chooses to register time.

                clear_screen()
                print(f"{BOLD}{BLUE}¡Temporizador Simple finalizado!{RESET}")
                # Now correctly displaying the added time if any was assigned by run_simple_timer
                if elapsed_minutes_simple > 0:
                    print(f"{BOLD}Tiempo añadido al trabajo: {GREEN}{format_time_hh_mm_minutes(elapsed_minutes_simple)}{RESET}") 
                else:
                    print(f"{LIGHT_GRAY}No se añadió tiempo al trabajo.{RESET}")

                input(f"\n{BOLD}{LIGHT_GRAY}Presiona Enter para volver al menú principal...{RESET}")
                # ELIMINADO: No reiniciar last_activity_start_time aquí.
                # last_activity_start_time = datetime.datetime.now()

            elif choice == option_specific_cat_summary: 
                display_specific_category_times()
                # NO se modifica last_activity_start_time aquí. La actividad general actual continúa.

            elif choice == option_change_daily_activity: 
                new_activity_choice = prompt_activity_category_choice(DEFAULT_DAILY_CATEGORIES, is_initial_setup=False)
                if new_activity_choice: # Si el usuario seleccionó una nueva actividad (no canceló)
                    # Registra el segmento actual SOLO SI la actividad es DIFERENTE
                    if new_activity_choice != current_daily_activity:
                        # change_current_daily_activity se encarga de loguear el segmento saliente
                        # y de iniciar el nuevo con un nuevo last_activity_start_time.
                        change_current_daily_activity(new_activity_choice) 
                        print(f"{BOLD}{YELLOW}Actividad diaria cambiada a: {current_daily_activity}{RESET}")
                    else: # El usuario eligió la misma actividad o canceló y la actividad sigue siendo la misma
                        print(f"{BOLD}{LIGHT_GRAY}La actividad ya es '{current_daily_activity}'. No se realizó ningún cambio.{RESET}")
                        # No hay cambio de actividad general, last_activity_start_time no se toca.
                else: # User cancelled from category selection (new_activity_choice is None)
                    print(f"{RED}No se cambió la actividad diaria.{RESET}")
                    # No hay cambio de actividad general, last_activity_start_time no se toca.
                input(f"\n{BOLD}{LIGHT_GRAY}Presiona Enter para volver al menú principal...{RESET}")
                # Si se vuelve de este menú sin un cambio efectivo de actividad,
                # last_activity_start_time no debe haberse modificado.

            elif choice == option_refresh_view: # New option to refresh the menu view
                # No log segment change needed. Just re-calculate display duration and loop.
                print(f"{BOLD}{GREEN}Vista del menú actualizada.{RESET}")
                time.sleep(0.5) # Small pause for user to see message
                # The outer loop will clear_screen and redraw automatically
            
            elif choice == option_daily_summary: 
                show_daily_activity_summary(daily_activity_log, current_daily_activity, last_activity_start_time, final_summary=False)
                # NO se modifica last_activity_start_time aquí. La actividad general actual continúa.
            
            elif choice == option_exit: 
                clear_screen()
                print(f"{BOLD}{BLUE}¡Gracias por usar el Temporador Pydoro!{RESET}")
                print(f"{BOLD}Resumen final de la Sesión de Pomodoro:{RESET}")
                print(f"{GREEN}Pomodoros completados: {total_pomodoros_session}{RESET}")
                print(f"{ORANGE}Descansos cortos completados: {total_short_breaks_session}{RESET}")
                print(f"{BLUE}Descansos largos completados: {total_long_breaks_session}{RESET}")
                # Las variables total_work_minutes_session y total_break_minutes_session
                # ya no se usan para mostrar aquí, ya que el tiempo productivo se asigna
                # directamente a las categorías específicas o generales mediante daily_activity_log.
                # Si se desea un total general de minutos de Pomodoro/Breaks, se necesitaría
                # recalcularlo a partir de las categorías específicas o de los pomodoros/breaks completados.
                
                # Loguear el segmento final antes de salir.
                change_current_daily_activity(None) # Esto loguea el último segmento y pone las variables globales a None

                # Mostrar resumen final de actividades diarias
                show_daily_activity_summary(daily_activity_log, None, None, final_summary=True) # Pasamos None para actividad activa ya que se logueó

                print(f"\n{BOLD}{LIGHT_GRAY}¡Hasta pronto! 👋{RESET}")
                time.sleep(3)
                break # Exit main loop

        except KeyboardInterrupt:
            print(f"\n{RED}¡CTRL+C detectado en el menú principal!{RESET}")
            print(f"{RED}Por favor, usa la opción '{option_exit}' para salir de forma segura.{RESET}")
            time.sleep(1)
            continue # Vuelve al inicio del bucle

        except Exception as e:
            print(f"{RED}Ocurrió un error inesperado: {e}{RESET}")
            print(f"{RED}Volviendo al menú principal.{RESET}")
            time.sleep(1)

# ==============================================================================
# Punto de entrada del programa
# ==============================================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}¡Pydoro se cerró abruptamente con CTRL+C fuera del menú!{RESET}")
        # Intentar loguear el último segmento activo al salir abruptamente
        if current_daily_activity is not None and last_activity_start_time is not None:
            change_current_daily_activity(None) # Loguea el último segmento
        show_daily_activity_summary(daily_activity_log, None, None, final_summary=True) # Mostrar resumen al salir abruptamente
    finally:
        print("Gracias por usar Pydoro.")

