# -*- coding: utf-8 -*-
# Este script implementa un temporador Pomodoro personalizable con una interfaz
# de usuario básica en la terminal, incluyendo una barra de progreso, colores
# y reproducción de sonido al final de cada fase.

# Importamos los módulos necesarios
import time  # Para manejar las pausas en la ejecución del programa
import os    # Para interactuar con el sistema operativo (ej. limpiar la pantalla de la consola)
import random # Para seleccionar frases motivadoras aleatorias
from playsound import playsound # Para reproducir sonidos al final de cada fase

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

# ==============================================================================
# Función auxiliar para limpiar la pantalla de la consola
# ==============================================================================
def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')

# ==============================================================================
# Función para formatear y mostrar el tiempo restante/transcurrido
# ==============================================================================
def display_timer(total_seconds):
    """
    Formatea el tiempo total en segundos a un formato de minutos:segundos (MM:SS)
    y le aplica color según el tiempo restante (o transcurrido para temporizador simple).
    """
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    
    # Aplica color al tiempo restante/transcurrido
    if total_seconds <= 10:
        color = RED
    elif total_seconds <= 60 and total_seconds > 0: # Para temporizador regresivo
        color = YELLOW
    elif total_seconds > 0: # Para temporizador progresivo o regresivo en fase normal
        color = GREEN
    else: # Cuando el tiempo llega a 0 (para regresivo)
        color = GREEN # Color al finalizar

    return f"{BOLD}{color}{minutes:02d}:{seconds:02d}{RESET}"

# ==============================================================================
# Función para generar la barra de progreso visual en la terminal
# ==============================================================================
def create_progress_bar(current_seconds, total_duration_seconds, bar_length=40):
    """
    Crea una cadena de barra de progreso que representa el avance visualmente.
    """
    if total_duration_seconds == 0:
        percentage = 100
    else:
        percentage = ((total_duration_seconds - current_seconds) / total_duration_seconds) * 100

    filled_chars = int(bar_length * percentage / 100)
    
    # La parte llena de la barra será VERDE, el resto gris claro
    colored_bar = f"{GREEN}█{RESET}" * filled_chars + f"{LIGHT_GRAY}-{RESET}" * (bar_length - filled_chars)
    
    percent_color = GREEN
    if percentage < 25:
        percent_color = RED
    elif percentage < 50:
        percent_color = YELLOW

    return f"[{colored_bar}] {percent_color}{percentage:.0f}%{RESET}"

# ==============================================================================
# Funciones auxiliares para la lectura de teclado no bloqueante (REINTEGRADAS Y AJUSTADAS)
# ==============================================================================
def kbhit():
    """
    Verifica si una tecla ha sido presionada sin bloquear la ejecución.
    Funciona tanto en Windows como en sistemas Unix/Linux.
    """
    if os.name == 'nt': # Para Windows
        return msvcrt.kbhit()
    else: # Para Linux/macOS
        # select.select espera a que el sys.stdin esté listo para leer
        # y tiene un timeout de 0 para que no bloquee
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
        # Configura la terminal para modo crudo (raw mode) para leer caracteres individuales
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd) # Guarda la configuración actual de la terminal
        try:
            tty.setraw(fd) # Cambia a modo "raw"
            ch = sys.stdin.read(1) # Lee un solo carácter
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) # Restaura la configuración original
        return ch


# ==============================================================================
# Función principal para la cuenta regresiva de cualquier período (AJUSTADA PARA PAUSA)
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

    # Bucle principal de la cuenta regresiva
    while current_seconds >= 0:
        clear_screen()
        print(f"{BOLD}{phase_color}--- FASE DE {phase_name} ---{RESET}")
        
        # Muestra los contadores de la sesión en la parte superior
        print(f"{BOLD}Sesión: {GREEN}Pomodoros: {pomodoros_completed_session}{RESET} | {ORANGE}Descansos: {short_breaks_completed_session}{RESET} | {BLUE}Descansos largos: {long_breaks_completed_session}{RESET}") 
        print("-" * 60) # Línea separadora estática para consistencia

        # Muestra la frase motivadora
        print(f"\n{LIGHT_GRAY}\"{quote}\"{RESET}\n")

        # Muestra la barra de progreso y el temporizador
        print(f"{create_progress_bar(current_seconds, total_duration_seconds_initial)} Tiempo restante: {display_timer(current_seconds)}")
        
        # Mensaje de pausa / reanudación
        if is_paused:
            print(f"\n{BOLD}{YELLOW}PAUSADO. Presiona [ENTER] para reanudar...{RESET}")
        else:
            print(f"\n{BOLD}{LIGHT_GRAY}Presiona [ENTER] para pausar...{RESET}") 

        # --- Lógica de Pausa/Reanudar con Enter ---
        # Dividimos el sleep de 1 segundo en pequeños intervalos para chequear la entrada
        for _ in range(10): # 10 iteraciones de 0.1 segundos = 1 segundo total
            if kbhit(): # Si se ha presionado una tecla
                key = getch() # Lee la tecla
                # Si la tecla es Enter, alternar estado de pausa
                if key in ('\r', '\n'): # '\r' es Enter en Windows, '\n' es Enter en Linux/macOS
                    is_paused = not is_paused 
                    # Consumir el resto de los caracteres en el buffer después de Enter
                    # Esto evita múltiples pausas/reanudos por una sola pulsación rápida
                    while kbhit():
                        getch()
                    # Romper el bucle de sleep fraccionado para actualizar la pantalla inmediatamente
                    break 
                else: # Si es otra tecla, consúmela para que no aparezca en pantalla, pero no pauses
                    pass # Opcionalmente, podrías agregar un mensaje como "Ignorando tecla..."
            time.sleep(0.1) # Pausa pequeña para no consumir CPU y permitir chequeo de entrada

        if not is_paused: # Solo decrementa el tiempo si NO estamos en pausa
            current_seconds -= 1

    clear_screen()
    print(f"{BOLD}{phase_color}--- FASE DE {phase_name} TERMINADA ---{RESET}")
    print(f"¡{BOLD}{phase_color}{phase_name}{RESET} completado! Es hora de cambiar de fase.\n")

    # ==========================================================================
    # Lógica para reproducir el sonido de notificación
    # ==========================================================================
    try:
        if "TRABAJO" in phase_name:
            sound_file = 'bell.wav' # Sonido para el final del trabajo
        else:
            sound_file = 'notif.wav' # Sonido para el final de los descansos
            
        playsound(sound_file) 
    except Exception as e:
        print(f"{RED}ADVERTENCIA: No se pudo reproducir el sonido de notificación '{sound_file}': {e}{RESET}")
        print(f"{RED}Asegúrate de que '{sound_file}' exista en la misma carpeta y playsound esté instalado correctamente.{RESET}")

    time.sleep(3)
    return True # El período se completó naturalmente

# ==============================================================================
# Función principal para ejecutar los ciclos Pomodoro (AJUSTADA PARA BLOQUEO CON INPUT)
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

    # Siempre pide confirmación para iniciar el primer período de trabajo
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
        except KeyboardInterrupt:
            clear_screen()
            choice = input(f"{RED}{BOLD}¡Pomodoro interrumpido durante el TRABAJO!{RESET}\n{BOLD}¿Qué quieres hacer? {YELLOW}[S]{RESET}altar a siguiente fase / {RED}[C]{RESET}ancelar todos los ciclos: ").lower()
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

        # Siempre pide confirmación para iniciar todos los descansos
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
        except KeyboardInterrupt:
            clear_screen()
            choice = input(f"{RED}{BOLD}¡Pomodoro interrumpido durante el {break_message}!{RESET}\n{BOLD}¿Qué quieres hacer? {YELLOW}[S]{RESET}altar a siguiente fase / {RED}[C]{RESET}ancelar todos los ciclos: ").lower()
            if choice == 'c':
                print(f"{BOLD}{RED}¡Pomodoro cancelado! Vuelve cuando estés listo. 👋{RESET}")
                return current_set_pomodoros, current_set_short_breaks, current_set_long_breaks 
            else:
                print(f"{BOLD}{GREEN}Saltando al próximo período de trabajo...{RESET}")

        # Siempre pide confirmación para iniciar el próximo período de trabajo
        if i < num_cycles:
            input(f"{BOLD}{GREEN}Presiona Enter para iniciar el próximo período de TRABAJO...{RESET}")

    clear_screen()
    print(f"{BOLD}{BLUE}¡Todos los ciclos Pomodoro completados en este conjunto! ¡Excelente trabajo! ✨{RESET}")
    return current_set_pomodoros, current_set_short_breaks, current_set_long_breaks

# ==============================================================================
# Función para el temporizador simple (cuenta hacia arriba) (AJUSTADA PARA PAUSA)
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

    current_elapsed_seconds = 0 # Inicia contando desde 0
    is_paused = False # Estado de pausa para el temporizador simple
    # No necesitamos pause_start_time aquí ya que current_elapsed_seconds
    # solo se incrementa cuando no está en pausa.

    try:
        while True:
            clear_screen()
            print(f"{BOLD}{BLUE}--- TEMPORIZADOR SIMPLE ---{RESET}")
            # Muestra los contadores de la sesión
            print(f"{BOLD}Sesión: {GREEN}Pomodoros: {total_pomodoros_session}{RESET} | {ORANGE}Descansos: {total_short_breaks_session}{RESET} | {BLUE}Descansos largos: {total_long_breaks_session}{RESET}") 
            print("-" * 60) # Línea separadora estática

            # Calcula y muestra el tiempo transcurrido
            # current_elapsed_seconds se actualiza al final del ciclo si no está pausado
            display_str = display_timer(current_elapsed_seconds) # Reutiliza display_timer
            
            print(f"\n{BOLD}Tiempo transcurrido: {display_str}{RESET}")
            
            # Mensaje de pausa / reanudación
            if is_paused:
                print(f"\n{BOLD}{YELLOW}PAUSADO. Presiona [ENTER] para reanudar...{RESET}")
            else:
                print(f"\n{BOLD}{LIGHT_GRAY}Presiona [ENTER] para pausar...{RESET}") 

            # --- Lógica de Pausa/Reanudar con Enter para temporizador simple ---
            for _ in range(10): # 10 iteraciones de 0.1 segundos = 1 segundo total
                if kbhit(): # Si se ha presionado una tecla
                    key = getch() # Lee la tecla
                    if key in ('\r', '\n'): # Si la tecla es Enter
                        is_paused = not is_paused 
                        # Consumir el resto de los caracteres en el buffer después de Enter
                        while kbhit():
                            getch()
                        break 
                    else: # Si es otra tecla, consúmela para que no aparezca en pantalla
                        pass 
                time.sleep(0.1) # Pausa pequeña para no consumir CPU y permitir chequeo de entrada

            if not is_paused: # Solo incrementa el tiempo si NO estamos en pausa
                current_elapsed_seconds += 1 # Incrementa el tiempo transcurrido

    except KeyboardInterrupt:
        clear_screen()
        # current_elapsed_seconds ya tiene el valor correcto del tiempo no pausado
        elapsed_minutes = int(current_elapsed_seconds / 60) # Convertir a minutos
        
        print(f"{RED}{BOLD}¡Temporizador Simple interrumpido!{RESET}")
        choice = input(f"{BOLD}Tiempo transcurrido: {display_timer(current_elapsed_seconds)}. ¿Qué quieres hacer? {YELLOW}[S]{RESET}umar tiempo y volver al menú principal / {RED}[C]{RESET}ancelar y no sumar tiempo: ").lower()
        if choice == 'c':
            print(f"{BOLD}{RED}Temporizador cancelado. Tiempo no sumado. 👋{RESET}")
            return 0 # No se suma tiempo al cancelar
        else: # Por defecto, si no es 'c', se suma el tiempo
            print(f"{BOLD}{GREEN}Sumando tiempo al total de trabajo...{RESET}")
            return elapsed_minutes
    
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
    total_break_minutes_session = 0 # Incluye cortos y largos

    while True: # Bucle infinito para mantener el script activo
        clear_screen()
        print(f"{BOLD}{GREEN}--- Bienvenido al Temporador Pydoro Personalizado ---{RESET}")
        print(f"{BOLD}{LIGHT_GRAY}Outwork others consistently.{RESET}\n")


        # Muestra el resumen de la sesión si ya se ha completado algo
        if total_pomodoros_session > 0 or total_short_breaks_session > 0 or total_long_breaks_session > 0:
            print(f"{BOLD}{BLUE}--- Resumen de la Sesión Actual ---{RESET}")
            print(f"{GREEN}Pomodoros completados: {total_pomodoros_session}{RESET}")
            print(f"{ORANGE}Descansos cortos completados: {total_short_breaks_session}{RESET}")
            print(f"{BLUE}Descansos largos completados: {total_long_breaks_session}{RESET}")
            print(f"{BOLD}Tiempo total de trabajo: {GREEN}{format_time_hh_mm(total_work_minutes_session)}{RESET}")
            print(f"{BOLD}Tiempo total de descanso: {ORANGE}{format_time_hh_mm(total_break_minutes_session)}{RESET}")
            print(f"{BOLD}----------------------------------{RESET}\n")

        try:
            # Nuevas opciones en el menú principal
            print(f"{BOLD}Selecciona una opción:{RESET}")
            print(f"  {GREEN}1. Iniciar nuevo conjunto de ciclos Pomodoro{RESET}")
            print(f"  {BLUE}2. Iniciar Temporizador Simple (cuenta hacia arriba){RESET}")
            print(f"  {RED}3. Salir del programa{RESET}")
            
            # Bucle para validar la entrada del menú principal
            while True:
                choice = input(f"{BOLD}Tu elección (1, 2 o 3): {RESET}").strip() # .strip() para quitar espacios
                if choice in ['1', '2', '3']:
                    break # Salir del bucle si la elección es válida
                else:
                    print(f"{RED}Opción no válida. Por favor, ingresa '1', '2' o '3'.{RESET}")
            
            if choice == '1': # Opción: Iniciar Pomodoro
                # Bucle para validar la entrada de personalización
                while True:
                    customize_choice = input(f"{BOLD}¿Quieres personalizar la configuración para este conjunto de ciclos? ({GREEN}s{RESET}/{RED}n{RESET}): {RESET}").lower().strip()
                    if customize_choice in ['s', 'n']:
                        break
                    else:
                        print(f"{RED}Opción no válida. Por favor, ingresa 's' o 'n'.{RESET}")
                
                work, short_break, long_break, cycles = 60, 10, 25, 4 # Valores por defecto ajustados

                if customize_choice == 's':
                    # Bucle para validar entrada numérica de duraciones y ciclos
                    while True:
                        try:
                            work = int(input(f"{YELLOW}Duración del período de TRABAJO (minutos): {RESET}"))
                            short_break = int(input(f"{YELLOW}Duración del DESCANSO CORTO (minutos): {RESET}"))
                            long_break = int(input(f"{YELLOW}Duración del DESCANSO LARGO (minutos): {RESET}"))
                            cycles = int(input(f"{YELLOW}Número de ciclos Pomodoro (ej. 4 para descanso largo): {RESET}"))
                            
                            if work <= 0 or short_break <= 0 or long_break <= 0 or cycles <= 0:
                                print(f"{RED}Las duraciones y el número de ciclos deben ser valores POSITIVOS. Intenta de nuevo.{RESET}")
                            else:
                                break # Salir del bucle si todas las entradas son válidas
                        except ValueError:
                            print(f"{RED}Entrada inválida. Por favor, ingresa SOLO NÚMEROS enteros.{RESET}")
                    
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
                
            elif choice == '2': # Opción: Iniciar Temporizador Simple
                elapsed_minutes_simple = run_simple_timer(total_pomodoros_session, total_short_breaks_session, total_long_breaks_session)
                total_work_minutes_session += elapsed_minutes_simple
                clear_screen()
                print(f"{BOLD}{BLUE}¡Temporizador Simple finalizado!{RESET}")
                print(f"{BOLD}Tiempo añadido al trabajo: {GREEN}{format_time_hh_mm(elapsed_minutes_simple)}{RESET}")
                input(f"\n{BOLD}{LIGHT_GRAY}Presiona Enter para volver al menú principal...{RESET}")

            elif choice == '3': # Opción: Salir del programa
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
                break # Sale del bucle infinito, terminando el script

        except Exception as e: # Captura excepciones generales que no sean ValueError de las entradas numéricas
            print(f"{RED}Ocurrió un error inesperado: {e}{RESET}")
            print(f"{RED}Volviendo al menú principal.{RESET}")
            time.sleep(1)

# ==============================================================================
# Punto de entrada del programa
# ==============================================================================
if __name__ == "__main__":
    main()
