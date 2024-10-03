import pygame
import random
import sys
import json
import os

pygame.init()

ANCHO = 800
ALTO = 600
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
GRIS = (128, 128, 128)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Invasores Espaciales")
reloj = pygame.time.Clock()

controles_predeterminados = {
    "Mover Izquierda": pygame.K_LEFT,
    "Mover Derecha": pygame.K_RIGHT,
    "Disparar": pygame.K_SPACE,
    "Pausa": pygame.K_ESCAPE,
}


def cargar_controles():
    try:
        with open("Configuraciones/controles.txt", "r") as f:
            controles_guardados = {}
            for linea in f:
                accion, tecla = linea.strip().split(":")
                controles_guardados[accion] = int(tecla)
            return controles_guardados
    except FileNotFoundError:
        return controles_predeterminados


def guardar_controles(controles):
    with open("Configuraciones/controles.txt", "w") as f:
        for accion, tecla in controles.items():
            f.write(f"{accion}:{tecla}\n")


def cargar_puntuaciones():
    try:
        with open("Configuraciones/puntuaciones.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"mejor_puntuacion": 0}


def guardar_puntuaciones(puntuaciones):
    with open("Configuraciones/puntuaciones.json", "w") as f:
        json.dump(puntuaciones, f)


controles = cargar_controles()
puntuaciones = cargar_puntuaciones()
mejor_puntuacion = puntuaciones["mejor_puntuacion"]


class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, VERDE, [(0, 40), (25, 0), (50, 40)])
        self.rect = self.image.get_rect()
        self.rect.centerx = ANCHO // 2
        self.rect.bottom = ALTO - 10
        self.velocidad_x = 0

    def update(self):
        self.rect.x += self.velocidad_x
        if self.rect.right > ANCHO:
            self.rect.right = ANCHO
        if self.rect.left < 0:
            self.rect.left = 0

    def disparar(self):
        bala = Bala(self.rect.centerx, self.rect.top)
        todos_los_sprites.add(bala)
        balas.add(bala)


class Enemigo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, ROJO, [(20, 0), (0, 40), (40, 40)])
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(ANCHO - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.velocidad_y = random.randrange(1, 4)

    def update(self):
        self.rect.y += self.velocidad_y
        if self.rect.top > ALTO:
            self.rect.x = random.randrange(ANCHO - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.velocidad_y = random.randrange(1, 4)


class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(AZUL)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.velocidad_y = -10

    def update(self):
        self.rect.y += self.velocidad_y
        if self.rect.bottom < 0:
            self.kill()


def mostrar_texto(superficie, texto, tamaño, x, y, color=BLANCO):
    fuente = pygame.font.Font(None, tamaño)
    texto_superficie = fuente.render(texto, True, color)
    texto_rect = texto_superficie.get_rect()
    texto_rect.midtop = (x, y)
    superficie.blit(texto_superficie, texto_rect)


def personalizar_controles():
    global controles
    seleccion = 0
    opciones = list(controles.keys())
    esperando_tecla = False
    while True:
        pantalla.fill(NEGRO)
        mostrar_texto(pantalla, "Personalizar Controles", 48, ANCHO // 2, 50)
        for i, opcion in enumerate(opciones):
            color = AZUL if i == seleccion else BLANCO
            texto = f"{opcion}: {pygame.key.name(controles[opcion])}"
            if esperando_tecla and i == seleccion:
                texto = f"{opcion}: Presiona una tecla..."
            mostrar_texto(pantalla, texto, 36, ANCHO // 2, 150 + i * 50, color)
        mostrar_texto(
            pantalla, "Presiona ENTER para seleccionar", 24, ANCHO // 2, ALTO - 100
        )
        mostrar_texto(pantalla, "Presiona ESC para volver", 24, ANCHO // 2, ALTO - 60)
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                guardar_controles(controles)
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if esperando_tecla:
                    controles[opciones[seleccion]] = evento.key
                    esperando_tecla = False
                    guardar_controles(controles)
                else:
                    if evento.key == pygame.K_ESCAPE:
                        return
                    elif evento.key == pygame.K_UP:
                        seleccion = (seleccion - 1) % len(opciones)
                    elif evento.key == pygame.K_DOWN:
                        seleccion = (seleccion + 1) % len(opciones)
                    elif evento.key == pygame.K_RETURN:
                        esperando_tecla = True


def menu_principal():
    seleccion = 0
    opciones = ["Jugar", "Controles", "Salir"]
    while True:
        pantalla.fill(NEGRO)
        mostrar_texto(pantalla, "Invasores Espaciales", 65, ANCHO // 2, ALTO // 4)
        for i, opcion in enumerate(opciones):
            color = BLANCO if i == seleccion else (150, 150, 150)
            mostrar_texto(pantalla, opcion, 36, ANCHO // 2, ALTO // 2 + i * 50, color)
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                elif evento.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                elif evento.key == pygame.K_RETURN:
                    if seleccion == 0:
                        return True
                    elif seleccion == 1:
                        personalizar_controles()
                    elif seleccion == 2:
                        return False


def reiniciar_juego():
    global todos_los_sprites, enemigos, balas
    todos_los_sprites = pygame.sprite.Group()
    enemigos = pygame.sprite.Group()
    balas = pygame.sprite.Group()
    jugador = Jugador()
    todos_los_sprites.add(jugador)
    for i in range(8):
        enemigo = Enemigo()
        todos_los_sprites.add(enemigo)
        enemigos.add(enemigo)
    return jugador


def menu_pausa():
    seleccion = 0
    opciones = ["Reanudar", "Reiniciar", "Menu Principal"]
    pausado = True
    while pausado:
        pantalla.fill(NEGRO)
        mostrar_texto(pantalla, "PAUSA", 65, ANCHO // 2, ALTO // 4)
        for i, opcion in enumerate(opciones):
            color = BLANCO if i == seleccion else (150, 150, 150)
            mostrar_texto(pantalla, opcion, 36, ANCHO // 2, ALTO // 2 + i * 50, color)
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                elif evento.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                elif evento.key == pygame.K_RETURN:
                    return opciones[seleccion].lower()


def juego():
    global todos_los_sprites, enemigos, balas, mejor_puntuacion
    jugador = reiniciar_juego()
    puntuacion = 0
    while True:
        reloj.tick(60)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == controles["Mover Izquierda"]:
                    jugador.velocidad_x = -5
                elif evento.key == controles["Mover Derecha"]:
                    jugador.velocidad_x = 5
                elif evento.key == controles["Disparar"]:
                    jugador.disparar()
                elif evento.key == controles["Pausa"]:
                    opcion = menu_pausa()
                    if opcion == "reanudar":
                        pass
                    elif opcion == "reiniciar":
                        jugador = reiniciar_juego()
                        puntuacion = 0
                    elif opcion == "menu principal":
                        return None
            elif evento.type == pygame.KEYUP:
                if (
                    evento.key == controles["Mover Izquierda"]
                    and jugador.velocidad_x < 0
                ):
                    jugador.velocidad_x = 0
                elif (
                    evento.key == controles["Mover Derecha"] and jugador.velocidad_x > 0
                ):
                    jugador.velocidad_x = 0
        todos_los_sprites.update()
        hits = pygame.sprite.groupcollide(enemigos, balas, True, True)
        for hit in hits:
            puntuacion += 10
            enemigo = Enemigo()
            todos_los_sprites.add(enemigo)
            enemigos.add(enemigo)
        hits = pygame.sprite.spritecollide(jugador, enemigos, False)
        if hits:
            if puntuacion > mejor_puntuacion:
                mejor_puntuacion = puntuacion
                puntuaciones["mejor_puntuacion"] = mejor_puntuacion
                guardar_puntuaciones(puntuaciones)
            mostrar_game_over(puntuacion, mejor_puntuacion)
            jugador = reiniciar_juego()
            puntuacion = 0
        pantalla.fill(NEGRO)
        todos_los_sprites.draw(pantalla)
        mostrar_texto(pantalla, f"Puntuación: {puntuacion}", 25, ANCHO // 2, 10)
        mostrar_texto(pantalla, f"Mejor: {mejor_puntuacion}", 25, ANCHO - 70, 10)
        pygame.display.flip()


def mostrar_game_over(puntuacion, mejor_puntuacion):
    esperando = True
    while esperando:
        pantalla.fill(NEGRO)
        mostrar_texto(pantalla, "¡GAME OVER!", 65, ANCHO // 2, ALTO // 4)
        mostrar_texto(pantalla, f"Puntuación: {puntuacion}", 36, ANCHO // 2, ALTO // 2)
        mostrar_texto(
            pantalla,
            f"Mejor puntuación: {mejor_puntuacion}",
            36,
            ANCHO // 2,
            ALTO // 2 + 50,
        )
        mostrar_texto(
            pantalla, "Presiona una tecla para continuar", 36, ANCHO // 2, ALTO - 100
        )
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYUP:
                esperando = False


def main():
    while True:
        if menu_principal():
            resultado = juego()
            if resultado is False:
                break
        else:
            break
    pygame.quit()


if __name__ == "__main__":
    main()
