# -*- coding: utf-8 -*-
# Este script implementa un temporador Pomodoro personalizable con una interfaz
# de usuario básica en la terminal, incluyendo una barra de progreso, colores
# y reproducción de sonido al final de cada fase.

# Importamos los módulos necesarios
import time  # Para manejar las pausas en la ejecución del programa
import os    # Para interactuar con el sistema operativo (ej. limpiar la pantalla de la consola)
import random # Para seleccionar frases motivadoras aleatorias
from playsound import playsound # Para reproducir sonidos al final de cada fase
import datetime # Para registrar la fecha y hora en el historial (aunque el historial no se guarda en archivo)

# Importaciones para lectura de teclado no bloqueante (esencial para la pausa)
import sys
# select y termios/tty son para sistemas Unix/Linux (como Ubuntu, macOS)
import select
if os.name == 'posix': # Solo importar para sistemas POSIX (Linux, macOS)
    import termios, tty
elif os.name == 'nt': # Solo importar para Windows
    import msvcrt

# ==============================================================================
# Definición de códigos ANSI para colores y estilos en la terminal
# Estos códigos son interpretados por la terminal para cambiar el formato del texto.
# ==============================================================================
RESET = "\033[0m"       # Código para restablecer el color y estilo a los valores por defecto
BOLD = "\033[1m"        # Código para texto en negrita
GREEN = "\033[92m"      # Código para color verde brillante
YELLOW = "\033[93m"     # Código para color amarillo brillante
BLUE = "\033[94m"       # Código para color azul brillante
RED = "\033[91m"        # Código para color rojo brillante
ORANGE = "\033[33m"     # Código para color naranja (estándar)
LIGHT_GRAY = "\033[37m" # Gris claro (para texto secundario)
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

# --- Variables globales para el tiempo categorizado (NO PERSISTENTE en archivo) ---
total_work_time_programming = 0
total_work_time_mathematics = 0

# ==============================================================================
# Funciones auxiliares para la limpieza de pantalla, colores y temporizador
# ==============================================================================
def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')

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
        color = GREEN

    return f"{BOLD}{color}{minutes:02d}:{seconds:02d}{RESET}"

def create_progress_bar(current_seconds, total_duration_seconds, bar_length=40):
    """
    Crea una cadena de barra de progreso que representa el avance visualmente.
    """
    if total_duration_seconds == 0:
        percentage = 100
    else:
        percentage = ((total_duration_seconds - current_seconds) / total_duration_seconds) * 100

    filled_chars = int(bar_length * percentage / 100)
    
    colored_bar = f"{GREEN}█{RESET}" * filled_chars + f"{LIGHT_GRAY}-{RESET}" * (bar_length - filled_chars)
    
    percent_color = GREEN
    if percentage < 25:
        percent_color = RED
    elif percentage < 50:
        percent_color = YELLOW

    return f"[{colored_bar}] {percent_color}{percentage:.0f}%{RESET}"

# ==============================================================================
# Funciones auxiliares para la lectura de teclado no bloqueante
# ==============================================================================
def kbhit():
    """
    Verifica si una tecla ha sido presionada sin bloquear la ejecución.
    Funciona tanto en Windows como en sistemas Unix/Linux.
    """
    if os.name == 'nt': # Para Windows
        return msvcrt.kbhit()
    else: # Para Linux/macOS
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(rlist)

def getch():
    """
    Lee una tecla presionada sin esperar Enter.
    Funciona tanto en Windows como en sistemas Unix/Linux (requiere tty).
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
# Funciones para categorización de tiempo (sin guardar en archivo)
# ==============================================================================
def seleccionar_categoria():
    """Permite al usuario seleccionar una categoría para asignar el tiempo."""
    while True:
        print(f"\n{BOLD}¿A qué categoría quieres asignar este tiempo?{RESET}")
        print(f"  {GREEN}1. Programación{RESET}")
        print(f"  {BLUE}2. Matemáticas{RESET}")
        print(f"  {LIGHT_GRAY}3. No asignar (General){RESET}")
        opcion = input(f"{BOLD}Elige una opción (1-3): {RESET}").strip()
        if opcion == '1':
            return "Programacion"
        elif opcion == '2':
            return "Matematicas"
        elif opcion == '3':
            return None
        else:
            print(f"{RED}Opción no válida. Intenta de nuevo.{RESET}")
            time.sleep(1)

def asignar_tiempo_a_categoria(duracion_minutos, categoria):
    """Asigna el tiempo a la categoría global (NO se guarda en archivo)."""
    global total_work_time_programming, total_work_time_mathematics
    if categoria == "Programacion":
        total_work_time_programming += duracion_minutos
    elif categoria == "Matematicas":
        total_work_time_mathematics += duracion_minutos

def mostrar_tiempo_categorizado():
    """
    Muestra el tiempo de trabajo categorizado para la sesión actual.
    Este tiempo NO se guarda persistentemente en un archivo.
    """
    clear_screen()
    print(f"{BOLD}{BLUE}--- Tiempo de Trabajo Categorizado (Sesión Actual) ---{RESET}")
    print(f"{GREEN}Total Programación: {format_time_hh_mm(total_work_time_programming)}{RESET}")
    print(f"{BLUE}Total Matemáticas: {format_time_hh_mm(total_work_time_mathematics)}{RESET}")
    print(f"{LIGHT_GRAY}(Estos totales se reinician al cerrar el programa){RESET}")
    input(f"\n{BOLD}{LIGHT_GRAY}Presiona Enter para volver al menú principal...{RESET}")


# ==============================================================================
# Función principal para la cuenta regresiva de cualquier período
# ==============================================================================
def countdown_period(duration_seconds, phase_name, quote,
                     pomodoros_completed_session, short_breaks_completed_session, long_breaks_completed_session):
    """
    Realiza una cuenta regresiva para un período dado, mostrando el tiempo restante,
    una barra de progreso, contadores de sesión acumulados y una frase motivadora.
    Permite pausar/reanudar presionando Enter.
    Al finalizar, reproduce un sonido.

    Returns:
        bool: True si el período se completó naturalmente, False si fue interrumpido.
    """
    phase_color = BLUE if "TRABAJO" in phase_name else ORANGE if "DESCANSO" in phase_name else RESET
    
    total_duration_seconds_initial = duration_seconds
    current_seconds = duration_seconds
    
    is_paused = False

    while current_seconds >= 0:
        clear_screen()
        print(f"{BOLD}{phase_color}--- FASE DE {phase_name} ---{RESET}")
        
        print(f"{BOLD}Sesión: {GREEN}Pomodoros: {pomodoros_completed_session}{RESET} | {ORANGE}Descansos: {short_breaks_completed_session}{RESET} | {BLUE}Descansos largos: {long_breaks_completed_session}{RESET}") 
        print("-" * 60)

        print(f"\n{LIGHT_GRAY}\"{quote}\"{RESET}\n")

        print(f"{create_progress_bar(current_seconds, total_duration_seconds_initial)} Tiempo restante: {display_timer(current_seconds)}")
        
        if is_paused:
            print(f"\n{BOLD}{YELLOW}PAUSADO. Presiona [ENTER] para reanudar...{RESET}")
        else:
            print(f"\n{BOLD}{LIGHT_GRAY}Presiona [ENTER] para pausar...{RESET}") 

        for _ in range(10):
            if kbhit():
                key = getch()
                if key in ('\r', '\n'):
                    is_paused = not is_paused 
                    while kbhit():
                        getch()
                    break 
                else:
                    pass
            time.sleep(0.1)

        if not is_paused:
            current_seconds -= 1

    clear_screen()
    print(f"{BOLD}{phase_color}--- FASE DE {phase_name} TERMINADA ---{RESET}")
    print(f"¡{BOLD}{phase_color}{phase_name}{RESET} completado! Es hora de cambiar de fase.\n")

    try:
        if "TRABAJO" in phase_name:
            sound_file = 'bell.wav'
        else:
            sound_file = 'notif.wav'
            
        playsound(sound_file) 
    except Exception as e:
        print(f"{RED}ADVERTENCIA: No se pudo reproducir el sonido de notificación '{sound_file}': {e}{RESET}")
        print(f"{RED}Asegúrate de que '{sound_file}' exista en la misma carpeta y playsound esté instalado correctamente.{RESET}")

    time.sleep(3)
    return True

# ==============================================================================
# Función principal para ejecutar los ciclos Pomodoro
# ==============================================================================
def run_pomodoro(work_minutes=60, short_break_minutes=10, long_break_minutes=25, num_cycles=4,
                 pomodoros_completed_session_total=0, short_breaks_completed_session_total=0, long_breaks_completed_session_total=0):
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
        print(f"\n{BOLD}--- CICLO {i}/{num_cycles} ---{RESET}")
        
        # --- Fase de TRABAJO ---
        work_quote = random.choice(WORK_QUOTES)
        try:
            completed_naturally = countdown_period(work_seconds, "TRABAJO", work_quote,
                                                   pomodoros_completed_session_total + current_set_pomodoros, 
                                                   short_breaks_completed_session_total + current_set_short_breaks, 
                                                   long_breaks_completed_session_total + current_set_long_breaks)
            if completed_naturally:
                current_set_pomodoros += 1
                # --- Lógica de asignación de categoría para el tiempo de trabajo ---
                categoria_asignada = seleccionar_categoria()
                if categoria_asignada:
                    asignar_tiempo_a_categoria(work_minutes, categoria_asignada)
                    print(f"Tiempo de {work_minutes} minutos asignado a {categoria_asignada}.")
                else:
                    print("Tiempo no asignado a una categoría específica.")
                # No se registra en archivo: registrar_sesion("Trabajo Pomodoro", work_minutes, categoria_asignada)
            else:
                pass
        except KeyboardInterrupt:
            clear_screen()
            choice = input(f"{RED}{BOLD}¡Pomodoro interrumpido durante el TRABAJO!{RESET}\n{BOLD}¿Qué quieres hacer? {YELLOW}[S]{RESET}altar a siguiente fase / {RED}[C]{RESET}ancelar todos los ciclos: ").lower().strip()
            if choice == 'c':
                print(f"{BOLD}{RED}¡Pomodoro cancelado! Vuelve cuando estés listo. 👋{RESET}")
                return current_set_pomodoros, current_set_short_breaks, current_set_long_breaks 
            else:
                print(f"{BOLD}{GREEN}Saltando al descanso...{RESET}")
                
        # --- Fase de DESCANSO (corto o largo) ---
        is_long_break = (i % num_cycles == 0)
        break_message = "DESCANSO LARGO" if is_long_break else "DESCANSO CORTO"
        break_duration = long_break_seconds if is_long_break else short_break_seconds
        break_quote = random.choice(BREAK_QUOTES)

        input(f"{BOLD}{ORANGE}Presiona Enter para iniciar el {break_message}...{RESET}")
        
        try:
            completed_naturally = countdown_period(break_duration, break_message, break_quote,
                                                   pomodoros_completed_session_total + current_set_pomodoros, 
                                                   short_breaks_completed_session_total + current_set_short_breaks, 
                                                   long_breaks_completed_session_total + current_set_long_breaks)
            if completed_naturally:
                if is_long_break:
                    current_set_long_breaks += 1
                else:
                    current_set_short_breaks += 1
                # No se registra en archivo: registrar_sesion(break_message, break_duration / 60)
            else:
                pass
        except KeyboardInterrupt:
            clear_screen()
            choice = input(f"{RED}{BOLD}¡Pomodoro interrumpido durante el {break_message}!{RESET}\n{BOLD}¿Qué quieres hacer? {YELLOW}[S]{RESET}altar a siguiente fase / {RED}[C]{RESET}ancelar todos los ciclos: ").lower().strip()
            if choice == 'c':
                print(f"{BOLD}{RED}¡Pomodoro cancelado! Vuelve cuando estés listo. 👋{RESET}")
                return current_set_pomodoros, current_set_short_breaks, current_set_long_breaks 
            else:
                print(f"{BOLD}{GREEN}Saltando al próximo período de trabajo...{RESET}")

        if i < num_cycles:
            input(f"{BOLD}{GREEN}Presiona Enter para iniciar el próximo período de TRABAJO...{RESET}")

    clear_screen()
    print(f"{BOLD}{BLUE}¡Todos los ciclos Pomodoro completados en este conjunto! ¡Excelente trabajo! ✨{RESET}")
    return current_set_pomodoros, current_set_short_breaks, current_set_long_breaks

# ==============================================================================
# Función para el temporizador simple (cuenta hacia arriba)
# ==============================================================================
def run_simple_timer(total_pomodoros_session, total_short_breaks_session, total_long_breaks_session):
    """
    Ejecuta un temporizador simple que cuenta hacia arriba desde 0.
    Es cancelable con Ctrl+C.
    Retorna el tiempo total en minutos transcurrido.
    """
    clear_screen()
    print(f"{BOLD}{BLUE}--- TEMPORIZADOR SIMPLE ---{RESET}")
    print(f"{BOLD}{LIGHT_GRAY}Presiona Ctrl+C en cualquier momento para detener.{RESET}\n")

    current_elapsed_seconds = 0
    is_paused = False
    
    try:
        while True:
            clear_screen()
            print(f"{BOLD}{BLUE}--- TEMPORIZADOR SIMPLE ---{RESET}")
            print(f"{BOLD}Sesión: {GREEN}Pomodoros: {total_pomodoros_session}{RESET} | {ORANGE}Descansos: {total_short_breaks_session}{RESET} | {BLUE}Descansos largos: {total_long_breaks_session}{RESET}") 
            print("-" * 60)

            display_str = display_timer(current_elapsed_seconds)
            
            print(f"\n{BOLD}Tiempo transcurrido: {display_str}{RESET}")
            
            if is_paused:
                print(f"\n{BOLD}{YELLOW}PAUSADO. Presiona [ENTER] para reanudar...{RESET}")
            else:
                print(f"\n{BOLD}{LIGHT_GRAY}Presiona [ENTER] para pausar...{RESET}") 

            for _ in range(10):
                if kbhit():
                    key = getch()
                    if key in ('\r', '\n'):
                        is_paused = not is_paused 
                        while kbhit():
                            getch()
                        break 
                    else:
                        pass 
                time.sleep(0.1)

            if not is_paused:
                current_elapsed_seconds += 1

    except KeyboardInterrupt:
        clear_screen()
        elapsed_minutes = int(current_elapsed_seconds / 60)
        
        print(f"{RED}{BOLD}¡Temporizador Simple interrumpido!{RESET}")
        choice = input(f"{BOLD}Tiempo transcurrido: {display_timer(current_elapsed_seconds)}. ¿Qué quieres hacer? {YELLOW}[S]{RESET}umar tiempo y volver al menú principal / {RED}[C]{RESET}ancelar y no sumar tiempo: ").lower().strip()
        if choice == 'c':
            print(f"{BOLD}{RED}Temporizador cancelado. Tiempo no sumado. 👋{RESET}")
            return 0
        else:
            print(f"{BOLD}{GREEN}Sumando tiempo al total de trabajo...{RESET}")
            categoria_asignada = seleccionar_categoria()
            if categoria_asignada:
                asignar_tiempo_a_categoria(elapsed_minutes, categoria_asignada)
                print(f"Tiempo de {elapsed_minutes} minutos asignado a {categoria_asignada}.")
            else:
                print("Tiempo no asignado a una categoría específica.")
            # No se registra en archivo: registrar_sesion("Timer Simple", elapsed_minutes, categoria_asignada)
            return elapsed_minutes
    
    elapsed_minutes = int(current_elapsed_seconds / 60)
    categoria_asignada = seleccionar_categoria()
    if categoria_asignada:
        asignar_tiempo_a_categoria(elapsed_minutes, categoria_asignada)
        print(f"Tiempo de {elapsed_minutes} minutos asignado a {categoria_asignada}.")
    else:
        print("Tiempo no asignado a una categoría específica.")
    # No se registra en archivo: registrar_sesion("Timer Simple", elapsed_minutes, categoria_asignada)
    return elapsed_minutes


# ==============================================================================
# Función auxiliar para formatear minutos en HH:MM
# ==============================================================================
def format_time_hh_mm(total_minutes):
    """Convierte el total de minutos a formato HH:MM."""
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"

# ==============================================================================
# Función principal para manejar la configuración del usuario y el bucle de sesión
# ==============================================================================
def main():
    """
    Permite al usuario configurar el temporador Pomodoro o usar los valores por defecto.
    Maneja entradas inválidas con un bloque try-except.
    Mantiene un bucle para permitir múltiples conjuntos de ciclos en una sesión.
    """
    total_pomodoros_session = 0
    total_short_breaks_session = 0
    total_long_breaks_session = 0
    total_work_minutes_session = 0
    total_break_minutes_session = 0

    while True:
        clear_screen()
        print(f"{BOLD}{GREEN}--- Bienvenido al Temporador Pydoro Personalizado ---{RESET}")
        print(f"{BOLD}{LIGHT_GRAY}Outwork others consistently.{RESET}\n")


        if total_pomodoros_session > 0 or total_short_breaks_session > 0 or total_long_breaks_session > 0:
            print(f"{BOLD}{BLUE}--- Resumen de la Sesión Actual ---{RESET}")
            print(f"{GREEN}Pomodoros completados: {total_pomodoros_session}{RESET}")
            print(f"{ORANGE}Descansos cortos completados: {total_short_breaks_session}{RESET}")
            print(f"{BLUE}Descansos largos completados: {total_long_breaks_session}{RESET}")
            print(f"{BOLD}Tiempo total de trabajo: {GREEN}{format_time_hh_mm(total_work_minutes_session)}{RESET}")
            print(f"{BOLD}Tiempo total de descanso: {ORANGE}{format_time_hh_mm(total_break_minutes_session)}{RESET}")
            print(f"{BOLD}----------------------------------{RESET}\n")

        try:
            print(f"{BOLD}Selecciona una opción:{RESET}")
            print(f"  {GREEN}1. Iniciar nuevo conjunto de ciclos Pomodoro{RESET}")
            print(f"  {BLUE}2. Iniciar Temporizador Simple (cuenta hacia arriba){RESET}")
            print(f"  {ORANGE}3. Ver Tiempo de Trabajo Categorizado{RESET}") # Opción 3 ahora es ver tiempo categorizado
            print(f"  {RED}4. Salir del programa{RESET}") # Opción 4 ahora es salir
            
            while True:
                choice = input(f"{BOLD}Tu elección (1-4): {RESET}").strip()
                if choice in ['1', '2', '3', '4']:
                    break
                else:
                    print(f"{RED}Opción no válida. Por favor, ingresa un número entre 1 y 4.{RESET}")
                    time.sleep(1)
            
            if choice == '1':
                while True:
                    customize_choice = input(f"{BOLD}¿Quieres personalizar la configuración para este conjunto de ciclos? ({GREEN}s{RESET}/{RED}n{RESET}): {RESET}").lower().strip()
                    if customize_choice in ['s', 'n']:
                        break
                    else:
                        print(f"{RED}Opción no válida. Por favor, ingresa 's' o 'n'.{RESET}")
                        time.sleep(1)
                
                work, short_break, long_break, cycles = 60, 10, 25, 4

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
                    total_pomodoros_session, total_short_breaks_session, total_long_breaks_session
                )
                
                total_pomodoros_session += completed_pom
                total_short_breaks_session += completed_short_break
                total_long_breaks_session += completed_long_break
                total_work_minutes_session += completed_pom * work
                total_break_minutes_session += (completed_short_break * short_break) + (completed_long_break * long_break)

                clear_screen()
                print(f"{BOLD}{BLUE}¡Conjunto de ciclos Pomodoro completado!{RESET}")
                print(f"{BOLD}Resumen de este conjunto:{RESET}")
                print(f"{GREEN}Pomodoros completados: {completed_pom}{RESET}")
                print(f"{ORANGE}Descansos cortos completados: {completed_short_break}{RESET}")
                print(f"{BLUE}Descansos largos completados: {completed_long_break}{RESET}")
                input(f"\n{BOLD}{LIGHT_GRAY}Presiona Enter para volver al menú principal...{RESET}")
                
            elif choice == '2':
                elapsed_minutes_simple = run_simple_timer(total_pomodoros_session, total_short_breaks_session, total_long_breaks_session)
                total_work_minutes_session += elapsed_minutes_simple
                clear_screen()
                print(f"{BOLD}{BLUE}¡Temporizador Simple finalizado!{RESET}")
                print(f"{BOLD}Tiempo añadido al trabajo: {GREEN}{format_time_hh_mm(elapsed_minutes_simple)}{RESET}")
                input(f"\n{BOLD}{LIGHT_GRAY}Presiona Enter para volver al menú principal...{RESET}")

            elif choice == '3': # Era opción 4, ahora es 3
                mostrar_tiempo_categorizado()

            elif choice == '4': # Era opción 5, ahora es 4
                clear_screen()
                print(f"{BOLD}{BLUE}¡Gracias por usar el Temporador Pydoro!{RESET}")
                print(f"{BOLD}Resumen final de la Sesión:{RESET}")
                print(f"{GREEN}Pomodoros completados: {total_pomodoros_session}{RESET}")
                print(f"{ORANGE}Descansos cortos completados: {total_short_breaks_session}{RESET}")
                print(f"{BLUE}Descansos largos completados: {total_long_breaks_session}{RESET}")
                print(f"{BOLD}Tiempo total de trabajo: {GREEN}{format_time_hh_mm(total_work_minutes_session)}{RESET}")
                print(f"{BOLD}Tiempo total de descanso: {ORANGE}{format_time_hh_mm(total_break_minutes_session)}{RESET}")
                print(f"\n{BOLD}{LIGHT_GRAY}¡Hasta pronto! 👋{RESET}")
                time.sleep(3)
                break

        except KeyboardInterrupt:
            print(f"\n{RED}¡CTRL+C detectado en el menú principal!{RESET}")
            print(f"{RED}Por favor, usa la opción '4' para salir de forma segura.{RESET}")
            time.sleep(1)
            continue

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
    finally:
        print("Gracias por usar Pydoro.")