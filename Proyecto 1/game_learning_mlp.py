import os
import csv
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pygame
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

import matplotlib
try:
    matplotlib.use("TkAgg")
except Exception:
    try:
        matplotlib.use("Qt5Agg")
    except Exception:
        pass
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

try:
    from PIL import Image, ImageSequence
except ImportError:
    Image = None
    ImageSequence = None

plt.ion()

BASE_W, BASE_H = 1080, 720
WINDOW_FRACTION = 0.97
EXTRA_SCALE = 1.1

# Carriles de la bala:
#   BAJO  → al nivel del suelo        → acción correcta: SALTAR  (1)
#   MEDIO → a media altura del jugador → acción correcta: AGACHARSE (2)
#   ALTO  → por encima de la cabeza   → acción correcta: NADA (0)
CARRIL_BAJO  = 0
CARRIL_MEDIO = 1
CARRIL_ALTO  = 2

# Tamaño del bucket de distancia para timelines (píxeles)
BUCKET_SIZE = 20


@dataclass
class Sample:
    velocidad_bala: float
    distancia: float
    bala_y: float
    accion: int   # 0=nada, 1=salto, 2=agacharse


@dataclass
class TimelineAgregado:
    carril: int
    buckets: Dict[int, int]  # distance_bucket → moda de acciones (0/1/2)


class Juego:
    def __init__(self) -> None:
        pygame.init()

        self._flags = 0
        self._fullscreen = False

        start_w = BASE_W
        start_h = BASE_H
        self.pantalla = pygame.display.set_mode((start_w, start_h), self._flags)
        pygame.display.set_caption("Juego: Bala + salto + agacharse + MLP")

        self.BLANCO   = (255, 255, 255)
        self.NEGRO    = (0,   0,   0)
        self.GRIS     = (200, 200, 200)
        self.AMARILLO = (255, 220, 120)
        self.ROJO     = (255,  80,  80)
        self.VERDE    = ( 80, 255, 120)
        self.CIAN     = (100, 220, 255)

        self.corriendo = True
        self.modo_auto = False

        self.datos_modelo: List[Sample] = []

        # Datos crudos para timeline agregado: carril → {bucket: [acciones]}
        self._carril_bucket_acciones: Dict[int, Dict[int, List[int]]] = {}

        # Timeline agregado listo para reproducción (moda por bucket)
        self._timeline_replay: Optional[TimelineAgregado] = None

        self.modelo: Optional[MLPClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.modelo_entrenado = False
        self.clase_unica: Optional[int] = None

        self.ultima_proba_salto: Optional[float] = None
        self.ultima_accion_auto: int = 0

        self.decision_window       = 500
        self.decision_record_every = 3
        self._decision_frame_counter = 0

        self.w, self.h   = start_w, start_h
        self.scale       = 1.0
        self.margin      = 50
        self.ground_y    = self.h - 100
        self.player_size        = (64, 96)
        self.player_crouch_size = (64, 48)
        self.bullet_size        = (20, 20)
        self.ship_size          = (80, 80)
        self.fondo_speed = 3

        self.salto             = False
        self.en_suelo          = True
        self.salto_vel_inicial = 20.0
        self.gravedad          = 1.0
        self.salto_vel         = self.salto_vel_inicial

        self.agachado           = False
        self.player_size_normal = self.player_size

        self.current_frame = 0
        self.frame_speed   = 10
        self.frame_count   = 0

        self.velocidad_bala = -12
        self.bala_disparada = False
        self.bala_carril    = CARRIL_BAJO
        self.COLOR_CARRIL   = {
            CARRIL_BAJO:  (255, 100, 100),
            CARRIL_MEDIO: (100, 220, 255),
            CARRIL_ALTO:  (180, 255, 150),
        }
        self.fondo_x1 = 0
        self.fondo_x2 = start_w

        self._apply_resolution(start_w, start_h, reset_positions=True)
        self.player_size_normal = self.player_size
        self._reset_estado_juego()

    # ═══════════════════════════════════════════════════════════════════
    # Resolución / assets
    # ═══════════════════════════════════════════════════════════════════
    def _apply_resolution(self, w: int, h: int, reset_positions: bool) -> None:
        self.w, self.h = int(w), int(h)
        self.scale     = max(1.0, min(self.w / BASE_W, self.h / BASE_H) * EXTRA_SCALE)
        self.margin    = int(50  * self.scale)
        self.ground_y  = self.h - int(100 * self.scale)

        self.player_size        = (int(64 * self.scale), int(96 * self.scale))
        self.player_crouch_size = (int(64 * self.scale), int(48 * self.scale))
        self.bullet_size        = (int(80 * self.scale), int(50 * self.scale))
        self.ship_size          = (int(80 * self.scale), int(80 * self.scale))
        self.fondo_speed        = max(1, int(2 * self.scale))

        self.salto_vel_inicial = 20 * self.scale
        self.gravedad          =  1 * self.scale
        self.salto_vel         = self.salto_vel_inicial
        self.decision_window   = int(500 * self.scale)
        self.fuente       = pygame.font.SysFont("Arial", int(24 * self.scale))
        self.fuente_chica = pygame.font.SysFont("Arial", int(18 * self.scale))
        self._cargar_assets()
        if reset_positions or not hasattr(self, "jugador"):
            self.jugador = pygame.Rect(self.margin, self.ground_y,
                                       self.player_size[0], self.player_size[1])
            self.bala = pygame.Rect(self.w - self.margin,
                                    self.ground_y + int(10 * self.scale),
                                    self.bullet_size[0], self.bullet_size[1])
            self.nave = pygame.Rect(self.w - int(100 * self.scale), self.ground_y,
                                    self.ship_size[0], self.ship_size[1])
        self.player_size_normal = self.player_size

    def _cargar_assets(self) -> None:
        def safe_load(path, size, fallback=(200, 200, 200, 255)):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(img, size)
            except Exception:
                surf = pygame.Surface(size, pygame.SRCALPHA)
                surf.fill(fallback)
                return surf

        base = os.path.dirname(__file__)

        self.jugador_frames = [
            safe_load(os.path.join(base, f"assets/sprites/mono_frame_{i}.png"),
                      self.player_size)
            for i in range(1, 5)
        ]
        self.jugador_frames_crouch = [
            safe_load(os.path.join(base, f"assets/sprites/crouch_frame_{i}.png"),
                      self.player_crouch_size)
            for i in range(1, 5)
        ]
        self.bala_img = safe_load(
            os.path.join(base, "assets/sprites/misil.png"),
            self.bullet_size, (160, 120, 255, 255)
        )
        self.fondo_frames, self.fondo_durations = self._cargar_gif_fondo(
            os.path.join(base, "assets/game/fondo3.gif")
        )
        self.fondo_frame_index = 0
        self.fondo_last_update = pygame.time.get_ticks()
        self.fondo_img = self.fondo_frames[0]
        self.fondo_w   = self.fondo_img.get_width()
        self.fondo_h   = self.fondo_img.get_height()

        self.nave_frames, self.nave_durations = self._cargar_gif_robot(
            os.path.join(base, "assets/game/robot.gif")
        )
        self.nave_frame_index = 0
        self.nave_last_update = pygame.time.get_ticks()
        self.nave_img = self.nave_frames[0]

    def _toggle_fullscreen(self) -> None:
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            info = pygame.display.Info()
            w = info.current_w or self.w
            h = info.current_h or self.h
            self.pantalla = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
            self._apply_resolution(w, h, reset_positions=True)
        else:
            self.pantalla = pygame.display.set_mode((BASE_W, BASE_H), self._flags)
            self._apply_resolution(BASE_W, BASE_H, reset_positions=True)
        self._reset_estado_juego()

    # ═══════════════════════════════════════════════════════════════════
    # Estado juego / modelo
    # ═══════════════════════════════════════════════════════════════════
    def _reset_estado_juego(self) -> None:
        self.jugador.x, self.jugador.y = self.margin, self.ground_y
        self.jugador.width, self.jugador.height = self.player_size

        self.nave.x,    self.nave.y    = self.w - int(100 * self.scale), self.ground_y
        self.bala.x    = self.w - self.margin
        self.bala_carril = CARRIL_BAJO
        self.bala.y    = (self._y_para_carril(CARRIL_BAJO)
                          if hasattr(self, "player_size_normal")
                          else self.ground_y + int(10 * self.scale))
        self.bala_disparada = False
        self.velocidad_bala = int(-10 * self.scale)
        self.salto     = False
        self.en_suelo  = True
        self.salto_vel = self.salto_vel_inicial
        self.agachado  = False
        if hasattr(self, "player_size_normal"):
            self.jugador.width  = self.player_size_normal[0]
            self.jugador.height = self.player_size_normal[1]
            self.jugador.y      = self.ground_y
        self._decision_frame_counter = 0
        self.fondo_x1 = 0
        self.fondo_x2 = self.fondo_w if hasattr(self, "fondo_w") else self.w
        self._timeline_replay = None

    def _reset_modelo(self) -> None:
        self.modelo           = None
        self.scaler           = None
        self.modelo_entrenado = False
        self.clase_unica      = None

    def entrenar_modelo_vacio(self) -> Tuple[bool, str]:
        self._reset_modelo()
        self.clase_unica = 0
        self.modelo_entrenado = True
        return True, "Modelo vacío (caso 0): el personaje no esquivará ninguna bala."

    # ═══════════════════════════════════════════════════════════════════
    # Export / gráficas
    # ═══════════════════════════════════════════════════════════════════
    def exportar_datos_csv(self) -> str:
        if not self.datos_modelo:
            return "No hay datos para exportar."
        base = os.path.dirname(__file__)
        ruta = os.path.join(base, "datos_mlp.csv")
        try:
            with open(ruta, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["velocidad_bala", "distancia", "bala_y", "accion"])
                for s in self.datos_modelo:
                    writer.writerow([s.velocidad_bala, s.distancia, s.bala_y, s.accion])
        except Exception as e:
            return f"Error al guardar CSV: {e}"
        return f"CSV guardado en datos_mlp.csv ({len(self.datos_modelo)} filas)."

    def graficar_datos_2d(self) -> str:
        if not self.datos_modelo:
            return "No hay datos para graficar."
        xs = [s.distancia      for s in self.datos_modelo]
        ys = [s.velocidad_bala for s in self.datos_modelo]
        color_map = {0: "blue", 1: "red", 2: "green"}
        cs = [color_map.get(s.accion, "gray") for s in self.datos_modelo]
        fig_num = plt.figure("Datos MLP - 2D", figsize=(8, 6)).number
        plt.figure(fig_num); plt.clf()
        ax = plt.gca()
        ax.scatter(xs, ys, c=cs, alpha=0.6, edgecolors="k", s=30)
        ax.set_xlabel("Distancia jugador-bala")
        ax.set_ylabel("Velocidad bala")
        ax.set_title("Datos MLP (azul=nada, rojo=salto, verde=agacharse)")
        ax.grid(True, alpha=0.3)
        plt.tight_layout(); plt.show(block=False); plt.draw()
        return "Mostrando gráfica 2D interactiva."

    def graficar_datos_3d(self) -> str:
        if not self.datos_modelo:
            return "No hay datos para graficar."
        xs = [s.distancia      for s in self.datos_modelo]
        ys = [s.velocidad_bala for s in self.datos_modelo]
        zs = list(range(len(self.datos_modelo)))
        color_map = {0: "blue", 1: "red", 2: "green"}
        cs = [color_map.get(s.accion, "gray") for s in self.datos_modelo]
        fig = plt.figure("Datos MLP - 3D", figsize=(8, 6)); plt.clf()
        ax  = fig.add_subplot(111, projection="3d")
        ax.scatter(xs, ys, zs, c=cs, alpha=0.6, edgecolors="k", s=30)
        ax.set_xlabel("Distancia"); ax.set_ylabel("Velocidad bala")
        ax.set_zlabel("Índice (tiempo aprox.)")
        ax.set_title("Datos MLP 3D (azul=nada, rojo=salto, verde=agacharse)")
        plt.tight_layout(); plt.show(block=False); plt.draw()
        return "Mostrando gráfica 3D interactiva."

    # ═══════════════════════════════════════════════════════════════════
    # Física / bala
    # ═══════════════════════════════════════════════════════════════════
    def _y_para_carril(self, carril: int) -> int:
        h_jugador  = self.player_size_normal[1]
        h_agachado = h_jugador // 2
        if carril == CARRIL_BAJO:
            return int(self.ground_y + h_jugador - self.bullet_size[1])
        elif carril == CARRIL_MEDIO:
            return int(self.ground_y + h_agachado - self.bullet_size[1])
        else:
            return int(self.ground_y - h_jugador - self.bullet_size[1] - int(8 * self.scale))

    def disparar_bala(self) -> None:
        if not self.bala_disparada:
            self.velocidad_bala = int(random.randint(-12, -6) * self.scale)
            self.bala_carril    = random.choice([CARRIL_BAJO, CARRIL_MEDIO, CARRIL_ALTO])
            self.bala.x = self.w - self.margin
            self.bala.y = self._y_para_carril(self.bala_carril)
            self.bala_disparada = True

            if self.modo_auto:
                self._seleccionar_timeline_replay()

    def reset_bala(self) -> None:
        self._timeline_replay = None
        self.bala.x     = self.w - self.margin
        self.bala_disparada = False

    def iniciar_salto(self) -> None:
        if self.en_suelo and not self.agachado:
            self.salto    = True
            self.en_suelo = False

    def iniciar_agacharse(self) -> None:
        if self.en_suelo and not self.salto and not self.agachado:
            self.jugador.width = self.player_crouch_size[0]
            self.jugador.height = self.player_crouch_size[1]
            self.jugador.y = self.ground_y + (self.player_size[1] - self.player_crouch_size[1])
            self.agachado = True

    def terminar_agacharse(self) -> None:
        if self.agachado:
            self.jugador.width = self.player_size[0]
            self.jugador.height = self.player_size[1]
            self.jugador.y = self.ground_y
            self.agachado = False

    def manejar_salto(self) -> None:
        if self.salto:
            self.jugador.y -= int(self.salto_vel)
            self.salto_vel  -= self.gravedad
            if self.jugador.y >= self.ground_y:
                self.jugador.y = self.ground_y
                self.salto     = False
                self.salto_vel = self.salto_vel_inicial
                self.en_suelo  = True

    # ═══════════════════════════════════════════════════════════════════
    # Registro de datos en modo MANUAL
    # ═══════════════════════════════════════════════════════════════════
    def registrar_decision_manual(self) -> None:
        if not self.bala_disparada:
            return

        distancia  = abs(self.jugador.x - self.bala.x)
        bala_y_rel = float(self.ground_y - self.bala.y)

        accion = (1 if not self.en_suelo
                  else 2 if self.agachado
                  else 0)

        # ── 1. Sample para el MLP ────────────────────────────────────────
        self.datos_modelo.append(
            Sample(float(self.velocidad_bala), float(distancia), bala_y_rel, accion)
        )

        # ── 2. Acumular bucket en timeline agregado ──────────────────────
        bucket = int(distancia // BUCKET_SIZE)
        if self.bala_carril not in self._carril_bucket_acciones:
            self._carril_bucket_acciones[self.bala_carril] = {}
        if bucket not in self._carril_bucket_acciones[self.bala_carril]:
            self._carril_bucket_acciones[self.bala_carril][bucket] = []
        self._carril_bucket_acciones[self.bala_carril][bucket].append(accion)

    # ═══════════════════════════════════════════════════════════════════
    # Entrenamiento MLP
    # ═══════════════════════════════════════════════════════════════════
    def entrenar_modelo(self) -> Tuple[bool, str]:
        samples = list(self.datos_modelo)
        if len(samples) < 80:
            return False, "Necesitas más datos (>= 80). Juega en MANUAL."

        X = [[s.velocidad_bala, s.distancia, s.bala_y] for s in samples]
        y = [s.accion for s in samples]
        clases = sorted(set(y))

        if len(clases) < 2:
            self._reset_modelo()
            self.clase_unica      = int(clases[0])
            self.modelo_entrenado = True
            nombres = {0: "NUNCA HACE NADA", 1: "SIEMPRE SALTA",
                       2: "SIEMPRE SE AGACHA"}
            n_tl = sum(len(b) for c in self._carril_bucket_acciones.values()
                       for b in c.values())
            return True, (f"Modelo trivial: {nombres.get(self.clase_unica,'?')}. "
                          f"Datos timeline: {n_tl}.")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        scaler  = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test  = scaler.transform(X_test)

        clf = MLPClassifier(
            hidden_layer_sizes=(32, 16),
            activation="relu",
            solver="adam",
            max_iter=500000,
            learning_rate_init=0.001,
            random_state=42,
        )
        clf.fit(X_train, y_train)
        acc = clf.score(X_test, y_test)

        self._reset_modelo()
        self.scaler           = scaler
        self.modelo           = clf
        self.modelo_entrenado = True

        conteo = {0: y.count(0), 1: y.count(1), 2: y.count(2)}
        n_tl   = sum(len(b) for c in self._carril_bucket_acciones.values()
                     for b in c.values())
        return True, (
            f"MLP entrenado. Accuracy≈{acc:.3f} | "
            f"nada={conteo[0]} salto={conteo[1]} agach={conteo[2]} | "
            f"datos_timeline={n_tl}"
        )

    # ═══════════════════════════════════════════════════════════════════
    # Decisión automática
    # ═══════════════════════════════════════════════════════════════════
    def decision_auto_accion(self) -> int:
        """MLP como fallback cuando no hay timeline. 0=nada, 1=salto, 2=agachar."""
        if not self.modelo_entrenado or not self.bala_disparada:
            return 0

        distancia  = abs(self.jugador.x - self.bala.x)
        bala_y_rel = float(self.ground_y - self.bala.y)

        # Modelo trivial (clase única)
        if self.clase_unica is not None and self.modelo is None:
            self.ultima_proba_salto = 1.0 if self.clase_unica == 1 else 0.0
            self.ultima_accion_auto = self.clase_unica
            return self.clase_unica

        if self.modelo is None or self.scaler is None:
            return 0

        X  = [[float(self.velocidad_bala), float(distancia), bala_y_rel]]
        Xs = self.scaler.transform(X)

        # Igual que el salto: predict() decide, predict_proba() solo es para HUD
        pred = int(self.modelo.predict(Xs)[0])

        if hasattr(self.modelo, "predict_proba"):
            probas = self.modelo.predict_proba(Xs)[0]
            clases = list(self.modelo.classes_)
            self.ultima_proba_salto = (float(probas[clases.index(1)])
                                       if 1 in clases else 0.0)
        else:
            self.ultima_proba_salto = 1.0 if pred == 1 else 0.0

        self.ultima_accion_auto = pred
        return pred

    # ═══════════════════════════════════════════════════════════════════
    # Timeline agregado (moda por bucket) — selección para AUTO
    # ═══════════════════════════════════════════════════════════════════
    def _seleccionar_timeline_replay(self) -> None:
        """
        Calcula la moda por bucket para el carril actual
        y la guarda en _timeline_replay para reproducirla.
        """
        from collections import Counter

        if self.bala_carril not in self._carril_bucket_acciones:
            self._timeline_replay = None
            return

        raw = self._carril_bucket_acciones[self.bala_carril]
        buckets_moda: Dict[int, int] = {}
        for bucket, acciones in raw.items():
            counter = Counter(acciones)
            buckets_moda[bucket] = counter.most_common(1)[0][0]

        self._timeline_replay = TimelineAgregado(
            carril=self.bala_carril, buckets=buckets_moda
        )

    # ═══════════════════════════════════════════════════════════════════
    # Menú
    # ═══════════════════════════════════════════════════════════════════
    def _dibujar_menu(self, msg: str = "") -> None:
        self.pantalla.fill(self.NEGRO)
        titulo = self.fuente.render("MENÚ", True, self.BLANCO)
        self.pantalla.blit(titulo, (self.w // 2 - titulo.get_width() // 2, int(60 * self.scale)))

        opciones = [
            "M  - Manual (reinicia dataset y modelo)",
            "A  - Auto (usa MLP; sin modelo NO reacciona)",
            "T  - Entrenar MLP con datos manuales",
            "E  - Entrenar vacío / caso 0 (personaje no hace nada)",
            "C  - Exportar datos a CSV",
            "G  - Gráfica 2D   |   H - Gráfica 3D",
            "F  - Fullscreen (toggle)",
            "Q  - Salir",
            "",
            "En MANUAL:  ESPACIO = saltar   |   S / ↓ = agacharse",
        ]
        x0     = int(80 * self.scale)
        y      = int(130 * self.scale)
        line_h = self.fuente.get_linesize()
        pad    = max(4, int(5 * self.scale))
        for op in opciones:
            color = self.AMARILLO if op.startswith("E  -") else self.BLANCO
            t = self.fuente.render(op, True, color)
            self.pantalla.blit(t, (x0, y))
            y += line_h + pad

        y += int(8 * self.scale)
        estado = [
            f"Memoria: {len(self.datos_modelo)} frames | Modelo: {'sí' if self.modelo_entrenado else 'no'}",
            f"Datos timeline: {sum(len(v) for d in self._carril_bucket_acciones.values() for v in d.values())} entradas",
            f"Resolución: {self.w}x{self.h}  scale≈{self.scale:.2f}",
        ]
        for line in estado:
            t = self.fuente_chica.render(line, True, self.GRIS)
            self.pantalla.blit(t, (x0, y))
            y += self.fuente_chica.get_linesize()

        if msg:
            mm = self.fuente_chica.render(msg, True, self.AMARILLO)
            self.pantalla.blit(mm, (x0, y + int(12 * self.scale)))

        pygame.display.flip()

    def mostrar_menu(self) -> None:
        msg = ""
        esperando = True
        self._decision_frame_counter = 0
        while esperando and self.corriendo:
            self._dibujar_menu(msg)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.corriendo = False
                    esperando = False
                    break
                if e.type == pygame.KEYDOWN:
                    k = e.key
                    if k == pygame.K_m:
                        self.modo_auto = False
                        self.datos_modelo.clear()
                        self._carril_bucket_acciones.clear()
                        self._reset_modelo()
                        self._reset_estado_juego()
                        esperando = False
                        break
                    if k == pygame.K_a:
                        if not self.modelo_entrenado:
                            msg = "Primero entrena el MLP (T) o entrena vacío (E)."
                        else:
                            self.modo_auto = True
                            self._reset_estado_juego()
                            esperando = False
                            break
                    if k == pygame.K_t:
                        ok, info = self.entrenar_modelo()
                        msg = info if ok else f"Error: {info}"
                    if k == pygame.K_e:
                        ok, info = self.entrenar_modelo_vacio()
                        msg = info if ok else f"Error: {info}"
                    if k == pygame.K_c:
                        msg = self.exportar_datos_csv()
                    if k == pygame.K_g:
                        msg = self.graficar_datos_2d()
                    if k == pygame.K_h:
                        msg = self.graficar_datos_3d()
                    if k == pygame.K_f:
                        self._toggle_fullscreen()
                    if k == pygame.K_q:
                        self.corriendo = False
                        esperando = False
                        return

    # ═══════════════════════════════════════════════════════════════════
    # Render
    # ═══════════════════════════════════════════════════════════════════
    def _update_frame(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.fondo_last_update >= self.fondo_durations[self.fondo_frame_index]:
            self.fondo_frame_index = (self.fondo_frame_index + 1) % len(self.fondo_frames)
            self.fondo_last_update = now
            self.fondo_img = self.fondo_frames[self.fondo_frame_index]

        self.fondo_x1 -= self.fondo_speed
        self.fondo_x2 -= self.fondo_speed

        if self.fondo_x1 <= -self.fondo_w:
            self.fondo_x1 = self.fondo_x2 + self.fondo_w
        if self.fondo_x2 <= -self.fondo_w:
            self.fondo_x2 = self.fondo_x1 + self.fondo_w

        self.pantalla.blit(self.fondo_img, (self.fondo_x1, 0))
        self.pantalla.blit(self.fondo_img, (self.fondo_x2, 0))

        # Se eliminó la línea guía del carril del proyectil.

        self.frame_count += 1
        if self.frame_count >= self.frame_speed:
            self.current_frame = (self.current_frame + 1) % len(self.jugador_frames)
            self.frame_count   = 0

        sprite = (self.jugador_frames_crouch if self.agachado
                  else self.jugador_frames)[self.current_frame]
        self.pantalla.blit(sprite, (self.jugador.x, self.jugador.y))

        now = pygame.time.get_ticks()
        if now - self.nave_last_update >= self.nave_durations[self.nave_frame_index]:
            self.nave_frame_index = (self.nave_frame_index + 1) % len(self.nave_frames)
            self.nave_last_update = now
            self.nave_img = self.nave_frames[self.nave_frame_index]
        self.pantalla.blit(self.nave_img, (self.nave.x, self.nave.y))

        if self.bala_disparada:
            self.bala.x += self.velocidad_bala
        if self.bala.x < -self.bullet_size[0]:
            self.reset_bala()
        self.pantalla.blit(self.bala_img, (self.bala.x, self.bala.y))

        if self.jugador.colliderect(self.bala):
            self._reset_estado_juego()

        # HUD
        nombres_carril = {
            CARRIL_BAJO:  "CARRIL BAJO  → SALTA",
            CARRIL_MEDIO: "CARRIL MEDIO → AGÁCHATE",
            CARRIL_ALTO:  "CARRIL ALTO  → NADA",
        }
        hud_y = 10
        if self.modelo_entrenado and self.modo_auto:
            nombres_accion = {0: "nada", 1: "salto", 2: "agachar"}
            modo = "TIMELINE" if self._timeline_replay is not None else "MLP"
            proba = (f"{self.ultima_proba_salto:.2f}"
                     if self.ultima_proba_salto is not None else "—")
            txt = self.fuente_chica.render(
                f"{modo}→{nombres_accion.get(self.ultima_accion_auto,'?')} "
                f"proba_salto≈{proba}",
                True, self.AMARILLO,
            )
            self.pantalla.blit(txt, (10, hud_y))
            hud_y += self.fuente_chica.get_linesize() + 4

        if self.agachado:
            txt2 = self.fuente_chica.render("AGACHADO", True, (100, 220, 255))
            self.pantalla.blit(txt2, (10, hud_y))
            hud_y += self.fuente_chica.get_linesize() + 4

        if self.bala_disparada:
            label = nombres_carril.get(self.bala_carril, "")
            color = self.COLOR_CARRIL.get(self.bala_carril, self.GRIS)
            if label:
                self.pantalla.blit(
                    self.fuente_chica.render(label, True, color), (10, hud_y)
                )

    # ═══════════════════════════════════════════════════════════════════
    # Loop principal
    # ═══════════════════════════════════════════════════════════════════
    def loop(self) -> None:
        reloj = pygame.time.Clock()
        self.mostrar_menu()

        while self.corriendo:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.corriendo = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_q:
                        self.corriendo = False
                    elif e.key in (pygame.K_ESCAPE, pygame.K_p):
                        self._reset_estado_juego()
                        self.mostrar_menu()
                    elif e.key == pygame.K_f:
                        self._toggle_fullscreen()
                    elif (e.key == pygame.K_SPACE
                          and not self.modo_auto
                          and self.en_suelo
                          and not self.agachado):
                        self.terminar_agacharse()
                        self.iniciar_salto()
                elif e.type == pygame.KEYUP:
                    if e.key in (pygame.K_s, pygame.K_DOWN) and not self.modo_auto:
                        self.terminar_agacharse()

            if not self.corriendo:
                break

            # ── Modo MANUAL ──────────────────────────────────────────────
            if not self.modo_auto:
                keys = pygame.key.get_pressed()
                if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.en_suelo and not self.salto:
                    self.iniciar_agacharse()
                elif not (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.agachado:
                    self.terminar_agacharse()
                self.registrar_decision_manual()

            # ── Modo AUTO: timeline agregado (moda) o MLP como fallback ──
            else:
                if self._timeline_replay is not None:
                    distancia = abs(self.jugador.x - self.bala.x)
                    bucket = int(distancia // BUCKET_SIZE)
                    accion = self._timeline_replay.buckets.get(bucket, 0)
                    self.ultima_accion_auto = accion
                else:
                    accion = self.decision_auto_accion()

                if accion == 1:
                    if self.agachado:
                        self.terminar_agacharse()
                    if self.en_suelo:
                        self.iniciar_salto()

                elif accion == 2:
                    if self.en_suelo and not self.salto:
                        self.iniciar_agacharse()

                else:  # accion == 0
                    if self.agachado:
                        self.terminar_agacharse()

            if self.salto:
                self.manejar_salto()

            if not self.bala_disparada:
                self.disparar_bala()

            self._update_frame()
            pygame.display.flip()
            reloj.tick(45)

        pygame.quit()



    # ═══════════════════════════════════════════════════════════════════
    # GIFs: escenario y nave animados
    # ═══════════════════════════════════════════════════════════════════
    def _cargar_gif_fondo(self, path: str):
        frames = []
        durations = []

        if Image is None or ImageSequence is None:
            print("[ERROR] Pillow no está instalado. Instala con: pip install pillow")
            fallback = pygame.Surface((self.w, self.h))
            fallback.fill((40, 40, 40))
            return [fallback], [100]

        try:
            gif = Image.open(path)

            for frame in ImageSequence.Iterator(gif):
                duration = frame.info.get("duration", 100)
                frame_rgba = frame.convert("RGBA")

                scale = max(self.w / frame_rgba.width, self.h / frame_rgba.height)
                new_w = int(frame_rgba.width * scale)
                new_h = int(frame_rgba.height * scale)

                frame_rgba = frame_rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)

                left = (new_w - self.w) // 2
                top = (new_h - self.h) // 2
                frame_rgba = frame_rgba.crop((left, top, left + self.w, top + self.h))

                surface = pygame.image.fromstring(
                    frame_rgba.tobytes(),
                    frame_rgba.size,
                    frame_rgba.mode,
                ).convert()

                frames.append(surface)
                durations.append(max(duration, 1))

            return frames, durations

        except Exception as e:
            print(f"[ERROR] No se pudo cargar el GIF de fondo: {e}")
            fallback = pygame.Surface((self.w, self.h))
            fallback.fill((40, 40, 40))
            return [fallback], [100]

    def _cargar_gif_robot(self, path: str):
        frames = []
        durations = []

        if Image is None or ImageSequence is None:
            print("[ERROR] Pillow no está instalado. Instala con: pip install pillow")
            fallback = pygame.Surface(self.ship_size, pygame.SRCALPHA)
            fallback.fill((140, 255, 200, 255))
            return [fallback], [100]

        try:
            gif = Image.open(path)

            for frame in ImageSequence.Iterator(gif):
                duration = frame.info.get("duration", 100)
                frame_rgba = frame.convert("RGBA")
                frame_rgba = frame_rgba.resize(
                    (self.ship_size[0], self.ship_size[1]),
                    Image.Resampling.LANCZOS,
                )

                surface = pygame.image.fromstring(
                    frame_rgba.tobytes(),
                    frame_rgba.size,
                    frame_rgba.mode,
                ).convert_alpha()

                frames.append(surface)
                durations.append(max(duration, 1))

            return frames, durations

        except Exception as e:
            print(f"[ERROR] No se pudo cargar GIF robot: {e}")
            fallback = pygame.Surface(self.ship_size, pygame.SRCALPHA)
            fallback.fill((140, 255, 200, 255))
            return [fallback], [100]


def main() -> None:
    Juego().loop()


if __name__ == "__main__":
    main()