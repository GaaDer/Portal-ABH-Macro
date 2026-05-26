import pygame
import threading
import ctypes
import time
from inputs import get_gamepad

# --- CONFIGURACIÓN ---
# He añadido BTN_TL (LB) a la lista
BOTONES = ["BTN_SOUTH", "BTN_EAST", "BTN_NORTH", "BTN_WEST", "BTN_TR", "BTN_TL"]
STICKS = ["ABS_X", "ABS_Y", "ABS_RX", "ABS_RY"]

estado = {k: 0 for k in BOTONES + STICKS}
activo = False


# --- LÓGICA DE MACRO ---
def fast_scroll_down():
    ctypes.windll.user32.mouse_event(0x0800, 0, 0, -120, 0)


def bucle_macro():
    global activo
    while True:
        if activo:
            fast_scroll_down()
        time.sleep(0.02)


# --- LÓGICA DE LECTURA ---
def monitor_mando():
    global activo
    while True:
        try:
            for event in get_gamepad():
                if event.code in estado:
                    estado[event.code] = event.state
                    # Toggle de ráfaga con RB
                    if event.code == "BTN_TR" and event.state == 1:
                        activo = not activo
        except:
            pass


# --- VISUALIZADOR PYGAME ---
def dibujar_mando(ventana):
    ventana.fill((30, 30, 30))

    # 1. Stick Izquierdo
    pygame.draw.circle(ventana, (50, 50, 50), (100, 150), 40, 2)
    lx = 100 + (estado.get("ABS_X", 0) / 32768) * 30
    ly = 150 - (estado.get("ABS_Y", 0) / 32768) * 30
    pygame.draw.circle(ventana, (0, 255, 255), (int(lx), int(ly)), 15)

    # 2. Botones A, B, X, Y
    pos_botones = [(300, 210), (330, 180), (300, 150), (270, 180)]
    for i, b in enumerate(BOTONES[:4]):
        color = (0, 255, 0) if estado.get(b, 0) > 0 else (100, 100, 100)
        pygame.draw.circle(ventana, color, pos_botones[i], 15)

    # 3. Bumpers: LB (izq) y RB (der)
    color_lb = (255, 255, 0) if estado.get("BTN_TL", 0) > 0 else (100, 100, 100)  # Amarillo para LB
    color_rb = (255, 0, 0) if estado.get("BTN_TR", 0) > 0 else (100, 100, 100)  # Rojo para RB
    pygame.draw.rect(ventana, color_lb, (50, 50, 100, 20))  # LB
    pygame.draw.rect(ventana, color_rb, (250, 50, 100, 20))  # RB

    # 4. Texto informativo
    font = pygame.font.SysFont("Arial", 16)
    status = f"RAFA RB (Salto): {'ON' if activo else 'OFF'}"
    ventana.blit(font.render(status, True, (255, 255, 255)), (20, 20))
    ventana.blit(font.render("LB (Crouch)", True, (255, 255, 255)), (50, 30))


# --- EJECUCIÓN ---
if __name__ == "__main__":
    threading.Thread(target=monitor_mando, daemon=True).start()
    threading.Thread(target=bucle_macro, daemon=True).start()

    pygame.init()
    ventana = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Visualizador ABH Pro")
    reloj = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: exit()

        dibujar_mando(ventana)
        pygame.display.flip()
        reloj.tick(60)
