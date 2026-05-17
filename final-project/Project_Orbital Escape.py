from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

WINDOW_WIDTH  = 1000
WINDOW_HEIGHT = 800
GRID_LENGTH   = 4300
fovY          = 110

MAX_LEVEL     = 5
current_level = 1

rocket_pos    = [0.0, -1600.0, 80.0]
rocket_vel    = [0.0,  0.0,     0.0]
rocket_angle  = 90.0
rocket_radius = 40
ROCKET_SCALE  = 1.28

ROCKET_MAIN_THRUST     = 1.20
ROCKET_REVERSE_THRUST  = 0.72
ROCKET_SIDE_THRUST     = 0.84
ROCKET_BOOST_THRUST    = 2.05
ROCKET_DRAG_ACTIVE     = 0.34
ROCKET_DRAG_IDLE       = 0.82
ROCKET_REVERSE_BRAKE   = 1.35
ROCKET_TURN_RESPONSE   = 7.5
ROCKET_MAX_TURN_RATE   = 185.0

BLACK_HOLE_INFLUENCE   = 1450.0
BLACK_HOLE_EVENT_HORIZON = 92.0
CHEAT_FIRE_COOLDOWN    = 0.55

score        = 0
life         = 3
energy       = 0
boost_energy = 100.0

game_over      = False
game_completed = False
cheat_mode     = False

camera_mode   = 0
smooth_cam_x  = 0.0
smooth_cam_y  = 0.0
smooth_cam_z  = 0.0

key_states = {"w": False, "a": False, "s": False, "d": False, "b": False}

bullets    = []
obstacles  = []
explosions = []
meteors    = []
star_cache = []
nebula_cache = []
black_hole = None

auto_fire_timer = 0.0
meteor_timer    = 0.0
warning_timer   = 0.0
level_time_left = 0.0
game_time       = 0.0
last_time       = 0

_quadric = None

planets = [
    {"name": "Solar Core",    "orbit":    0, "radius": 140, "color": (1.0,  0.45, 0.0),  "speed": 0.000, "angle":   0},
    {"name": "Blue Planet",   "orbit":  900, "radius":  70, "color": (0.1,  0.45, 1.0),  "speed": 0.080, "angle":  30},
    {"name": "Green Planet",  "orbit": 1650, "radius":  82, "color": (0.2,  1.0,  0.35), "speed": 0.065, "angle": 120},
    {"name": "Purple Planet", "orbit": 2400, "radius":  94, "color": (0.65, 0.2,  1.0),  "speed": 0.050, "angle": 210},
    {"name": "Red Planet",    "orbit": 3150, "radius": 106, "color": (1.0,  0.15, 0.1),  "speed": 0.040, "angle": 300},
    {"name": "Golden Planet", "orbit": 3900, "radius": 120, "color": (1.0,  0.85, 0.1),  "speed": 0.030, "angle":  70},
]

level_settings = {
    1: {"difficulty": "EASY",      "obstacles": 12, "gravity": 0.62, "obstacle_speed": 0.90, "obstacle_chase_speed":  22, "move_range_min": 100, "move_range_max": 180, "meteor_interval": 6.5, "meteor_speed": 320, "meteor_burst": 1, "max_meteors":  3, "meteor_radius_min": 24, "meteor_radius_max": 34, "time_limit": 150},
    2: {"difficulty": "NORMAL",    "obstacles": 16, "gravity": 0.78, "obstacle_speed": 1.35, "obstacle_chase_speed":  36, "move_range_min": 140, "move_range_max": 230, "meteor_interval": 5.2, "meteor_speed": 420, "meteor_burst": 1, "max_meteors":  4, "meteor_radius_min": 28, "meteor_radius_max": 40, "time_limit": 170},
    3: {"difficulty": "HARD",      "obstacles": 20, "gravity": 0.94, "obstacle_speed": 1.90, "obstacle_chase_speed":  55, "move_range_min": 190, "move_range_max": 300, "meteor_interval": 4.0, "meteor_speed": 540, "meteor_burst": 2, "max_meteors":  6, "meteor_radius_min": 32, "meteor_radius_max": 46, "time_limit": 190},
    4: {"difficulty": "VERY HARD", "obstacles": 24, "gravity": 1.10, "obstacle_speed": 2.55, "obstacle_chase_speed":  78, "move_range_min": 250, "move_range_max": 380, "meteor_interval": 3.0, "meteor_speed": 680, "meteor_burst": 2, "max_meteors":  8, "meteor_radius_min": 36, "meteor_radius_max": 52, "time_limit": 210},
    5: {"difficulty": "EXTREME",   "obstacles": 28, "gravity": 1.28, "obstacle_speed": 3.30, "obstacle_chase_speed": 105, "move_range_min": 320, "move_range_max": 500, "meteor_interval": 2.2, "meteor_speed": 860, "meteor_burst": 3, "max_meteors": 10, "meteor_radius_min": 42, "meteor_radius_max": 60, "time_limit": 240},
}


# ── Utilities ──────────────────────────────────────────────────────────────────

def q():
    return _quadric


def generate_star_cache():
    global star_cache, nebula_cache
    rng = random.Random(99)
    star_cache = []
    nebula_cache = []
    for size, count, r, g, b in [(5, 70, 1.0, 1.0, 1.0), (3, 180, 0.85, 0.85, 0.95), (2, 310, 0.6, 0.6, 0.75)]:
        for _ in range(count):
            star_cache.append((
                rng.randint(-4800, 4800),
                rng.randint(-4800, 4800),
                rng.randint(350, 2400),
                size, r, g, b,
                rng.uniform(0, math.pi * 2),
            ))
    for _ in range(26):
        nebula_cache.append((
            rng.randint(-4400, 4400),
            rng.randint(-4400, 4400),
            rng.randint(280, 1150),
            rng.randint(220, 520),
            rng.choice([(0.16, 0.42, 0.95), (0.55, 0.16, 0.85), (0.08, 0.72, 0.85), (0.95, 0.28, 0.16)]),
            rng.uniform(0, math.pi * 2),
        ))


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1.0, 1.0, 1.0)):
    glColor3f(*color)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def get_planet_position(planet):
    if planet["orbit"] == 0:
        return [0.0, 0.0, float(planet["radius"])]
    a = math.radians(planet["angle"])
    return [planet["orbit"] * math.cos(a), planet["orbit"] * math.sin(a), float(planet["radius"])]


def get_target_planet():
    return planets[current_level]


def get_target_position():
    return get_planet_position(get_target_planet())


def get_distance_to_target():
    tx, ty, tz = get_target_position()
    return math.sqrt((tx - rocket_pos[0])**2 + (ty - rocket_pos[1])**2 + (tz - rocket_pos[2])**2)


def find_nearest_planet():
    best, best_d = None, 1e9
    for planet in planets:
        px, py, pz = get_planet_position(planet)
        d = math.sqrt((px - rocket_pos[0])**2 + (py - rocket_pos[1])**2 + (pz - rocket_pos[2])**2)
        if d < best_d:
            best_d = d
            best = planet
    return best, best_d


def clamp(value, low, high):
    return max(low, min(high, value))


def smooth_rotate_angle(current, target, dt):
    diff = (target - current + 540) % 360 - 180
    eased = diff * (1.0 - math.exp(-ROCKET_TURN_RESPONSE * dt))
    eased = clamp(eased, -ROCKET_MAX_TURN_RATE * dt, ROCKET_MAX_TURN_RATE * dt)
    return (current + eased) % 360


def distance2_xy(ax, ay, bx, by):
    dx = ax - bx
    dy = ay - by
    return dx*dx + dy*dy


def alive_obstacles():
    return [obs for obs in obstacles if obs["alive"]]


# ── Level management ───────────────────────────────────────────────────────────

def reset_rocket_for_level():
    global rocket_pos, rocket_vel, rocket_angle
    tx, ty, _ = get_target_position()
    length = math.sqrt(tx*tx + ty*ty)
    if length == 0:
        sx, sy = 0.0, -1600.0
    else:
        dist = min(GRID_LENGTH - 250, planets[current_level]["orbit"] + 500)
        sx = -tx / length * dist
        sy = -ty / length * dist
    rocket_pos[:] = [sx, sy, 80.0]
    rocket_vel[:] = [0.0, 0.0, 0.0]
    rocket_angle  = math.degrees(math.atan2(ty - sy, tx - sx))


def create_obstacles_for_level():
    settings  = level_settings[current_level]
    rng       = random.Random(current_level * 200)
    sx, sy    = rocket_pos[0], rocket_pos[1]
    tx, ty, _ = get_target_position()
    path_len  = math.sqrt((tx-sx)**2 + (ty-sy)**2) or 1
    nx, ny    = -(ty-sy)/path_len, (tx-sx)/path_len
    result    = []

    for i in range(settings["obstacles"]):
        t = (i + 1) / (settings["obstacles"] + 1)
        px = sx + (tx-sx)*t
        py = sy + (ty-sy)*t
        x, y = px, py
        for _ in range(30):
            off = rng.randint(-480, 480)
            cx  = px + nx*off + (rng.random()-0.5)*200
            cy  = py + ny*off + (rng.random()-0.5)*200
            if math.sqrt((cx-sx)**2 + (cy-sy)**2) < 300:
                continue
            if all(math.sqrt((cx-e["base"][0])**2 + (cy-e["base"][1])**2) >= 180 for e in result):
                x, y = cx, cy
                break
        else:
            off = rng.randint(-400, 400)
            x   = px + nx*off
            y   = py + ny*off

        size = rng.randint(35 + current_level*3, 55 + current_level*5)
        result.append({
            "base":         [float(x), float(y), 80.0],
            "pos":          [float(x), float(y), 80.0],
            "size":         size,
            "alive":        True,
            "rot":          float(rng.randint(0, 360)),
            "rot_speed":    rng.uniform(-2.4, 2.4) * settings["obstacle_speed"],
            "move_axis":    rng.choice(["x", "y"]),
            "move_range":   rng.randint(settings["move_range_min"], settings["move_range_max"]),
            "move_speed":   rng.uniform(0.9, 1.8) * settings["obstacle_speed"],
            "chase_factor": rng.uniform(0.80, 1.25),
            "phase":        rng.uniform(0, math.pi*2),
            "cr":           rng.uniform(0.45, 0.72),
            "cg":           rng.uniform(0.10, 0.28),
            "cb":           rng.uniform(0.08, 0.20),
        })
    return result


def create_black_hole_for_level():
    rng = random.Random(current_level * 733 + int(game_time * 1000) + score * 3)
    tx, ty, _ = get_target_position()
    sx, sy = rocket_pos[0], rocket_pos[1]

    for _ in range(80):
        x = rng.randint(-GRID_LENGTH + 700, GRID_LENGTH - 700)
        y = rng.randint(-GRID_LENGTH + 700, GRID_LENGTH - 700)
        if distance2_xy(x, y, sx, sy) < 850*850:
            continue
        if distance2_xy(x, y, tx, ty) < 850*850:
            continue
        too_close = False
        for planet in planets:
            px, py, _ = get_planet_position(planet)
            if distance2_xy(x, y, px, py) < 520*520:
                too_close = True
                break
        if not too_close:
            return {
                "pos":     [float(x), float(y), 95.0],
                "radius":  BLACK_HOLE_EVENT_HORIZON + current_level * 7,
                "gravity": 210000.0 + current_level * 42000.0,
                "spin":    rng.uniform(0, 360),
            }

    return {
        "pos":     [float(-ty * 0.42), float(tx * 0.42), 95.0],
        "radius":  BLACK_HOLE_EVENT_HORIZON + current_level * 7,
        "gravity": 210000.0 + current_level * 42000.0,
        "spin":    0.0,
    }


def setup_level():
    global bullets, obstacles, explosions, meteors, black_hole
    global level_time_left, meteor_timer, warning_timer
    global smooth_cam_x, smooth_cam_y, smooth_cam_z
    bullets         = []
    explosions      = []
    meteors         = []
    level_time_left = float(level_settings[current_level]["time_limit"])
    meteor_timer    = 0.0
    warning_timer   = 0.0
    reset_rocket_for_level()
    obstacles     = create_obstacles_for_level()
    black_hole    = create_black_hole_for_level()
    smooth_cam_x  = rocket_pos[0]
    smooth_cam_y  = rocket_pos[1]
    smooth_cam_z  = rocket_pos[2]


def complete_level():
    global current_level, game_completed, game_over, score, energy, boost_energy
    create_explosion(rocket_pos[0], rocket_pos[1], rocket_pos[2], power=1.25)
    score        += 100 * current_level
    energy       += 2
    boost_energy  = min(100.0, boost_energy + 35)
    if current_level < MAX_LEVEL:
        current_level += 1
        setup_level()
    else:
        game_completed = True
        game_over      = True


def reset_game():
    global current_level, score, life, energy, boost_energy
    global game_over, game_completed, cheat_mode
    current_level  = 1
    score          = 0
    life           = 3
    energy         = 0
    boost_energy   = 100.0
    game_over      = False
    game_completed = False
    cheat_mode     = False
    setup_level()


# ── Drawing ────────────────────────────────────────────────────────────────────

def draw_space_floor():
    GL = GRID_LENGTH
    glBegin(GL_QUADS)
    glColor3f(0.01, 0.01, 0.04)
    glVertex3f(-GL, -GL, 0); glVertex3f(GL, -GL, 0)
    glVertex3f( GL,  GL, 0); glVertex3f(-GL,  GL, 0)
    glEnd()
    glColor3f(0.05, 0.05, 0.11)
    step = 600
    half = 3
    glBegin(GL_QUADS)
    i = -GL
    while i <= GL:
        glVertex3f(i-half, -GL, 1); glVertex3f(i+half, -GL, 1)
        glVertex3f(i+half,  GL, 1); glVertex3f(i-half,  GL, 1)
        glVertex3f(-GL, i-half, 1); glVertex3f(GL, i-half, 1)
        glVertex3f( GL, i+half, 1); glVertex3f(-GL, i+half, 1)
        i += step
    glEnd()


def draw_stars():
    glDisable(GL_DEPTH_TEST)
    for (x, y, z, size, r, g, b, phase) in star_cache:
        bright = 0.82 + 0.18 * math.sin(game_time * 1.3 + phase)
        glPointSize(size)
        glBegin(GL_POINTS)
        glColor3f(r * bright, g * bright, b * bright)
        glVertex3f(x, y, z)
        glEnd()
    glEnable(GL_DEPTH_TEST)


def draw_nebula():
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    for x, y, z, radius, color, phase in nebula_cache:
        pulse = 0.72 + 0.18 * math.sin(game_time * 0.45 + phase)
        r, g, b = color
        glBegin(GL_TRIANGLE_FAN)
        glColor4f(r * 0.26, g * 0.26, b * 0.26, 0.20 * pulse)
        glVertex3f(x, y, z)
        for i in range(25):
            a = 2 * math.pi * i / 24
            wobble = 0.82 + 0.18 * math.sin(a * 3 + phase)
            glColor4f(r * 0.04, g * 0.04, b * 0.04, 0.0)
            glVertex3f(x + math.cos(a) * radius * wobble, y + math.sin(a) * radius * wobble, z)
        glEnd()
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)


def draw_orbit_ring(radius):
    glColor3f(0.13, 0.13, 0.23)
    glLineWidth(1.0)
    glBegin(GL_LINE_LOOP)
    steps = 128
    for i in range(steps):
        a = 2 * math.pi * i / steps
        glVertex3f(radius * math.cos(a), radius * math.sin(a), 2)
    glEnd()


def draw_black_hole():
    if black_hole is None:
        return
    quad = q()
    x, y, z = black_hole["pos"]
    radius = black_hole["radius"]
    spin = black_hole["spin"] + game_time * 95

    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(spin, 0, 0, 1)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    for i in range(4):
        ring_r = radius * (1.45 + i * 0.36)
        glColor4f(0.08 + i*0.05, 0.48 + i*0.10, 1.0, 0.34 - i*0.055)
        glLineWidth(4.0 - i * 0.6)
        glBegin(GL_LINE_LOOP)
        for step in range(140):
            a = 2 * math.pi * step / 140
            stretch = 1.0 + 0.11 * math.sin(a * 3 + game_time * 3.0 + i)
            glVertex3f(math.cos(a) * ring_r * stretch, math.sin(a) * ring_r * 0.62, 0)
        glEnd()

    glDisable(GL_BLEND)
    glColor3f(0.0, 0.0, 0.0)
    gluSphere(quad, radius, 32, 18)
    glColor3f(0.55, 0.92, 1.0)
    glLineWidth(2.5)
    glBegin(GL_LINE_LOOP)
    for step in range(120):
        a = 2 * math.pi * step / 120
        glVertex3f(math.cos(a) * radius * 1.05, math.sin(a) * radius * 1.05, 2)
    glEnd()
    glPopMatrix()


def draw_planets():
    quad = q()
    target = get_target_planet()

    for planet in planets:
        if planet["orbit"] > 0:
            draw_orbit_ring(planet["orbit"])

    for planet in planets:
        if planet["orbit"] == 0:
            continue
        x, y, z = get_planet_position(planet)
        r, g, b  = planet["color"]
        rad      = planet["radius"]
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(r*0.28, g*0.28, b*0.28)
        gluSphere(quad, rad*1.12, 24, 24)
        glColor3f(r, g, b)
        gluSphere(quad, rad, 32, 32)
        glPushMatrix()
        glTranslatef(-rad*0.28, -rad*0.28, rad*0.32)
        glColor3f(min(1.0, r+0.38), min(1.0, g+0.38), min(1.0, b+0.38))
        gluSphere(quad, rad*0.30, 12, 12)
        glPopMatrix()
        if planet is target:
            glColor3f(0.0, 1.0, 0.85)
            glLineWidth(2.5)
            ring_r = rad * 1.68
        else:
            glColor3f(0.6, 0.6, 0.75)
            glLineWidth(1.0)
            ring_r = rad * 1.30
        glBegin(GL_LINE_LOOP)
        for ri in range(120):
            ra = 2 * math.pi * ri / 120
            glVertex3f(math.cos(ra)*ring_r, math.sin(ra)*ring_r, 0)
        glEnd()
        glPopMatrix()

    # Sun
    sun  = planets[0]
    x, y, z = get_planet_position(sun)
    rs   = sun["radius"]
    pulse = 1.0 + 0.045 * math.sin(game_time * 2.6)
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.45, 0.18, 0.04)
    gluSphere(quad, rs*1.42*pulse, 24, 24)
    glColor3f(0.88, 0.38, 0.07)
    gluSphere(quad, rs*1.20*pulse, 28, 28)
    glColor3f(1.0, 0.65, 0.14)
    gluSphere(quad, rs*pulse, 36, 36)
    glColor3f(1.0, 0.95, 0.55)
    gluSphere(quad, rs*0.50, 22, 22)
    glPopMatrix()


def draw_rocket():
    if camera_mode == 2:
        return
    quad     = q()
    thrusting = any(key_states[k] for k in ("w", "a", "s", "d", "b")) or cheat_mode
    flicker   = 0.88 + 0.12 * math.sin(game_time * 28.0)

    glPushMatrix()
    glTranslatef(rocket_pos[0], rocket_pos[1], rocket_pos[2])
    glRotatef(rocket_angle, 0, 0, 1)
    glScalef(ROCKET_SCALE, ROCKET_SCALE, ROCKET_SCALE)

    # Body cylinder
    glPushMatrix()
    glColor3f(0.80, 0.80, 0.90)
    glTranslatef(-40, 0, 0)
    glRotatef(90, 0, 1, 0)
    gluCylinder(quad, 16, 16, 80, 20, 6)
    glPopMatrix()

    # Nose cone
    glPushMatrix()
    glColor3f(0.92, 0.12, 0.12)
    glTranslatef(40, 0, 0)
    glRotatef(90, 0, 1, 0)
    gluCylinder(quad, 16, 0, 36, 20, 6)
    glPopMatrix()

    # Cockpit window
    glPushMatrix()
    glColor3f(0.15, 0.78, 1.0)
    glTranslatef(8, 0, 15)
    gluSphere(quad, 9, 14, 14)
    glPopMatrix()

    # Wings
    for side in (16, -16):
        glPushMatrix()
        glColor3f(0.92, 0.30, 0.0)
        glTranslatef(-35, side, -6)
        glScalef(1.1, 0.35, 0.35)
        glutSolidCube(30)
        glPopMatrix()

    # Engine nozzle
    glPushMatrix()
    glColor3f(0.50, 0.50, 0.55)
    glTranslatef(-40, 0, 0)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(quad, 14, 18, 12, 16, 4)
    glPopMatrix()

    # Thruster flame
    if thrusting:
        glPushMatrix()
        glColor3f(1.0, 0.62 * flicker, 0.0)
        glTranslatef(-65, 0, 0)
        glRotatef(-90, 0, 1, 0)
        gluCylinder(quad, 12, 0, 46 * flicker, 14, 5)
        glPopMatrix()
        glPushMatrix()
        glColor3f(1.0, 0.14 * flicker, 0.0)
        glTranslatef(-78, 0, 0)
        glRotatef(-90, 0, 1, 0)
        gluCylinder(quad, 8, 0, 30 * flicker, 12, 4)
        glPopMatrix()

    glPopMatrix()


def draw_obstacles():
    quad = q()
    for obs in obstacles:
        if not obs["alive"]:
            continue
        x, y, z = obs["pos"]
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(obs["rot"], 1, 1, 0.4)
        glColor3f(obs["cr"], obs["cg"], obs["cb"])
        gluSphere(quad, obs["size"]*0.55, 12, 12)
        glColor3f(obs["cr"]*0.48, obs["cg"]*0.48, obs["cb"]*0.48)
        glScalef(0.6, 0.6, 0.6)
        glutSolidCube(obs["size"]*0.70)
        glPopMatrix()


def draw_meteors():
    quad = q()
    for meteor in meteors:
        x, y, z = meteor["pos"]
        r        = meteor["radius"]
        vx, vy   = meteor["vel"][0], meteor["vel"][1]
        spd      = math.sqrt(vx*vx + vy*vy) or 1
        dx, dy   = vx/spd, vy/spd
        sx, sy   = -dy, dx

        # Tail segments
        for i in range(5):
            back  = r*(0.85 + i*0.52)
            side  = ((i % 2)*2 - 1) * r * (0.14 + 0.06*i)
            ex    = x - dx*back + sx*side
            ey    = y - dy*back + sy*side
            er    = r * max(0.08, 0.56 - i*0.10)
            glPushMatrix()
            glTranslatef(ex, ey, z)
            glColor3f(1.0, max(0.05, 0.50 - i*0.10), 0.0)
            gluSphere(quad, er, 10, 10)
            glPopMatrix()

        # Glow halo
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(1.0, 0.38, 0.04)
        gluSphere(quad, r*1.22, 16, 16)
        glPopMatrix()

        # Rock body
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(meteor["rot"], *meteor["spin_axis"])
        glColor3f(0.38, 0.22, 0.15)
        gluSphere(quad, r*0.92, 16, 16)
        glColor3f(0.24, 0.13, 0.09)
        glScalef(1.18, 0.82, 1.0)
        glutSolidCube(r*1.12)
        glPopMatrix()


def draw_bullets():
    quad = q()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    for bullet in bullets:
        x, y, z = bullet["pos"]
        vx, vy = bullet["vel"][0], bullet["vel"][1]
        spd = math.sqrt(vx*vx + vy*vy) or 1
        dx, dy = vx/spd, vy/spd
        glLineWidth(3.0 if bullet.get("auto") else 2.0)
        glBegin(GL_LINES)
        if bullet.get("auto"):
            glColor4f(0.2, 1.0, 0.95, 0.95)
        else:
            glColor4f(1.0, 0.92, 0.25, 0.85)
        glVertex3f(x, y, z)
        glColor4f(1.0, 0.25, 0.04, 0.0)
        glVertex3f(x - dx*85, y - dy*85, z)
        glEnd()
        glPushMatrix()
        glTranslatef(x, y, z)
        if bullet.get("auto"):
            glColor4f(0.25, 1.0, 0.95, 0.95)
        else:
            glColor4f(1.0, 0.92, 0.25, 0.95)
        gluSphere(quad, 7, 10, 10)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        gluSphere(quad, 3, 8, 8)
        glPopMatrix()
    glDisable(GL_BLEND)


def draw_explosions():
    quad = q()
    for exp in explosions:
        x, y, z   = exp["pos"]
        radius     = exp["radius"]
        life_frac  = max(0.0, exp["life"])
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor4f(1.0, 0.22 + life_frac*0.15, 0.0, 0.55 * life_frac)
        gluSphere(quad, radius*1.35, 16, 12)
        glColor4f(1.0, 0.58 + life_frac*0.12, 0.02, 0.72 * life_frac)
        gluSphere(quad, radius, 18, 18)
        glColor4f(1.0, 0.82 + life_frac*0.12, 0.0, 0.90 * life_frac)
        gluSphere(quad, radius*0.55, 16, 16)
        glColor4f(1.0, 1.0, 1.0, life_frac)
        gluSphere(quad, radius*0.22, 12, 12)
        glPopMatrix()

        glLineWidth(2.0)
        for p in exp["particles"]:
            px, py, pz = p["pos"]
            vx, vy, vz = p["vel"]
            glow = max(0.0, p["life"] / p["max_life"])
            glColor4f(p["color"][0], p["color"][1], p["color"][2], glow)
            glBegin(GL_LINES)
            glVertex3f(px, py, pz)
            glVertex3f(px - vx * 0.035, py - vy * 0.035, pz - vz * 0.035)
            glEnd()
            glPushMatrix()
            glTranslatef(px, py, pz)
            gluSphere(quad, p["size"] * (0.6 + glow), 8, 8)
            glPopMatrix()
        glDisable(GL_BLEND)


def draw_hud():
    target   = get_target_planet()
    dist     = int(get_distance_to_target())
    alive_n  = sum(1 for o in obstacles if o["alive"])
    diff     = level_settings[current_level]["difficulty"]
    cam_name = ["Follow", "Cinematic", "FPV"][camera_mode]
    time_col = (1.0, 0.3, 0.1) if level_time_left < 20 else (1.0, 1.0, 0.55)

    lh = 23
    y  = WINDOW_HEIGHT - 24
    draw_text(10, y, f"ORBITAL ESCAPE  |  Level {current_level}/5  [{diff}]",      color=(0.35, 0.90, 1.0))
    y -= lh
    draw_text(10, y, f"Target: {target['name']}   Dist: {dist}   Time: {int(level_time_left)}s",  color=time_col)
    y -= lh
    draw_text(10, y, f"Life: {life}   Score: {score}   Energy: {energy}/10   Boost: {int(boost_energy)}%", color=(0.55, 1.0, 0.55))
    y -= lh
    draw_text(10, y, f"Obstacles: {alive_n}   Meteors: {len(meteors)}   Camera: {cam_name}", color=(0.78, 0.78, 0.92))
    y -= lh
    if black_hole is not None:
        bhx, bhy, _ = black_hole["pos"]
        bh_dist = int(math.sqrt((rocket_pos[0]-bhx)**2 + (rocket_pos[1]-bhy)**2))
        danger = (1.0, 0.38, 0.16) if bh_dist < BLACK_HOLE_INFLUENCE else (0.48, 0.82, 1.0)
        draw_text(10, y, f"Black Hole: {bh_dist} away   Gravity: {level_settings[current_level]['gravity']:.2f}x", color=danger)

    if warning_timer > 0 and int(game_time * 5) % 2 == 0:
        draw_text(WINDOW_WIDTH//2 - 140, WINDOW_HEIGHT//2 + 70,
                  "!  METEOR INCOMING  !", color=(1.0, 0.18, 0.08))

    if cheat_mode:
        draw_text(10, 38, "CHEAT MODE ACTIVE", color=(1.0, 0.80, 0.0))

    if camera_mode == 2:
        draw_text(WINDOW_WIDTH//2 - 5, WINDOW_HEIGHT//2 - 6, "+", color=(0.0, 1.0, 0.45))

    if game_over and not game_completed:
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        draw_text(cx - 80,  cy + 30, "GAME  OVER",        color=(1.0, 0.18, 0.10))
        draw_text(cx - 65,  cy - 5,  f"Score: {score}",   color=(1.0, 1.0, 0.45))
        draw_text(cx - 100, cy - 40, "Press R to Restart", color=(0.80, 0.80, 0.80))

    if game_completed:
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        draw_text(cx - 120, cy + 35, "MISSION  COMPLETE!",   color=(0.25, 1.0, 0.50))
        draw_text(cx - 80,  cy,      f"Final Score: {score}", color=(1.0, 0.90, 0.28))
        draw_text(cx - 105, cy - 38, "Press R to Play Again", color=(0.80, 0.80, 0.80))


def draw_shapes():
    draw_stars()
    draw_nebula()
    draw_planets()
    draw_black_hole()
    draw_obstacles()
    draw_meteors()
    draw_bullets()
    draw_rocket()
    draw_explosions()


# ── Game logic ─────────────────────────────────────────────────────────────────

def create_explosion(x, y, z, power=1.0):
    particles = []
    count = int(18 + 12 * power)
    for _ in range(count):
        a = random.uniform(0, math.pi * 2)
        lift = random.uniform(-0.18, 0.55)
        speed = random.uniform(85, 245) * power
        life_span = random.uniform(0.45, 0.95) * power
        particles.append({
            "pos":      [x, y, z],
            "vel":      [math.cos(a) * speed, math.sin(a) * speed, lift * speed],
            "life":     life_span,
            "max_life": life_span,
            "size":     random.uniform(3.0, 8.0) * power,
            "color":    random.choice([(1.0, 0.72, 0.12), (1.0, 0.22, 0.04), (0.95, 0.92, 0.58), (0.55, 0.72, 1.0)]),
        })
    explosions.append({
        "pos":      [x, y, z],
        "radius":   8.0 * power,
        "life":     1.15 * power,
        "grow":     105.0 * power,
        "particles": particles,
    })


def fire_bullet(target=None, auto=False):
    if game_over:
        return
    if target is None:
        a   = math.radians(rocket_angle)
        dx  = math.cos(a)
        dy  = math.sin(a)
        life = 3.2
        speed = 950.0
    else:
        dx = target[0] - rocket_pos[0]
        dy = target[1] - rocket_pos[1]
        d  = math.sqrt(dx*dx + dy*dy) or 1
        dx /= d
        dy /= d
        life = clamp(d / 1350.0 + 0.45, 0.75, 3.4)
        speed = 1350.0
    bullets.append({
        "pos":  [rocket_pos[0] + dx*90, rocket_pos[1] + dy*90, rocket_pos[2]],
        "vel":  [dx*speed, dy*speed, 0.0],
        "life": life,
        "auto": auto,
    })


def update_cheat_mode(dt):
    global auto_fire_timer, rocket_angle
    if not cheat_mode or game_over:
        return

    auto_fire_timer = max(0.0, auto_fire_timer - dt)
    if any(b.get("auto") for b in bullets):
        return

    targets = alive_obstacles()
    if not targets:
        return

    target = min(targets, key=lambda o: distance2_xy(o["pos"][0], o["pos"][1], rocket_pos[0], rocket_pos[1]))
    tx, ty, tz = target["pos"]
    desired_angle = math.degrees(math.atan2(ty - rocket_pos[1], tx - rocket_pos[0]))
    rocket_angle = smooth_rotate_angle(rocket_angle, desired_angle, dt * 1.8)

    if auto_fire_timer <= 0:
        fire_bullet([tx, ty, tz], auto=True)
        auto_fire_timer = CHEAT_FIRE_COOLDOWN


def push_rocket_away_from(x, y):
    dx  = rocket_pos[0] - x
    dy  = rocket_pos[1] - y
    d   = math.sqrt(dx*dx + dy*dy) or 1
    dx /= d; dy /= d
    rocket_pos[0] += dx * 80
    rocket_pos[1] += dy * 80
    rocket_vel[0]  = dx * 180
    rocket_vel[1]  = dy * 180


def lose_life():
    global life, game_over
    if cheat_mode:
        return
    life -= 1
    if life <= 0:
        game_over = True
    else:
        setup_level()


def spawn_meteor():
    global warning_timer
    settings = level_settings[current_level]
    if len(meteors) >= settings["max_meteors"]:
        return
    side = random.randint(0, 3)
    M    = GRID_LENGTH + 350
    if   side == 0: x, y = -M, random.randint(-GRID_LENGTH, GRID_LENGTH)
    elif side == 1: x, y =  M, random.randint(-GRID_LENGTH, GRID_LENGTH)
    elif side == 2: x, y = random.randint(-GRID_LENGTH, GRID_LENGTH), -M
    else:           x, y = random.randint(-GRID_LENGTH, GRID_LENGTH),  M
    spread   = max(70, 280 - current_level*35)
    tx = rocket_pos[0] + random.randint(-spread, spread)
    ty = rocket_pos[1] + random.randint(-spread, spread)
    dx, dy = tx - x, ty - y
    d  = math.sqrt(dx*dx + dy*dy) or 1
    sp = settings["meteor_speed"]
    meteors.append({
        "pos":       [float(x), float(y), 80.0],
        "vel":       [dx/d*sp, dy/d*sp, 0.0],
        "radius":    random.randint(settings["meteor_radius_min"], settings["meteor_radius_max"]),
        "life":      12.0,
        "rot":       random.uniform(0, 360),
        "rot_speed": random.uniform(90, 220),
        "spin_axis": [random.uniform(0.3, 1.0), random.uniform(0.3, 1.0), random.uniform(0.3, 1.0)],
    })
    warning_timer = 1.5


def spawn_meteor_burst():
    for _ in range(level_settings[current_level]["meteor_burst"]):
        spawn_meteor()


def update_bullets(dt):
    global score, energy, boost_energy, life
    for bullet in bullets[:]:
        if bullet.get("auto"):
            targets = alive_obstacles()
            if targets:
                target = min(targets, key=lambda o: distance2_xy(o["pos"][0], o["pos"][1], bullet["pos"][0], bullet["pos"][1]))
                dx = target["pos"][0] - bullet["pos"][0]
                dy = target["pos"][1] - bullet["pos"][1]
                d  = math.sqrt(dx*dx + dy*dy) or 1
                speed = math.sqrt(bullet["vel"][0]**2 + bullet["vel"][1]**2) or 1350.0
                bullet["vel"][0] += (dx/d * speed - bullet["vel"][0]) * min(1.0, 5.5 * dt)
                bullet["vel"][1] += (dy/d * speed - bullet["vel"][1]) * min(1.0, 5.5 * dt)
        bullet["pos"][0] += bullet["vel"][0] * dt
        bullet["pos"][1] += bullet["vel"][1] * dt
        bullet["life"]   -= dt
        if bullet["life"] <= 0:
            bullets.remove(bullet)
            continue
        hit = False
        for obs in obstacles:
            if not obs["alive"]:
                continue
            dx = bullet["pos"][0] - obs["pos"][0]
            dy = bullet["pos"][1] - obs["pos"][1]
            if math.sqrt(dx*dx + dy*dy) < obs["size"]:
                obs["alive"] = False
                create_explosion(*obs["pos"], power=1.0 + obs["size"] / 90.0)
                score       += 15
                energy      += 1
                boost_energy = min(100.0, boost_energy + 8)
                if energy >= 10:
                    life  += 1
                    energy = 0
                if bullet in bullets:
                    bullets.remove(bullet)
                hit = True
                break
        if hit:
            continue
        for meteor in meteors[:]:
            dx = bullet["pos"][0] - meteor["pos"][0]
            dy = bullet["pos"][1] - meteor["pos"][1]
            if math.sqrt(dx*dx + dy*dy) < meteor["radius"] + 8:
                create_explosion(*meteor["pos"], power=1.20)
                score       += 25
                energy      += 1
                boost_energy = min(100.0, boost_energy + 12)
                if meteor in meteors: meteors.remove(meteor)
                if bullet in bullets: bullets.remove(bullet)
                break


def update_explosions(dt):
    for exp in explosions[:]:
        exp["radius"] += exp["grow"] * dt
        exp["life"]   -= dt * 1.9
        for p in exp["particles"][:]:
            p["pos"][0] += p["vel"][0] * dt
            p["pos"][1] += p["vel"][1] * dt
            p["pos"][2] += p["vel"][2] * dt
            p["vel"][0] *= math.exp(-1.6 * dt)
            p["vel"][1] *= math.exp(-1.6 * dt)
            p["vel"][2] = p["vel"][2] * math.exp(-1.8 * dt) - 60.0 * dt
            p["life"]   -= dt
            if p["life"] <= 0:
                exp["particles"].remove(p)
        if exp["life"] <= 0 and not exp["particles"]:
            explosions.remove(exp)


def update_meteors(dt):
    for meteor in meteors[:]:
        meteor["pos"][0] += meteor["vel"][0] * dt
        meteor["pos"][1] += meteor["vel"][1] * dt
        meteor["rot"]    += meteor["rot_speed"] * dt
        meteor["life"]   -= dt
        if meteor["life"] <= 0:
            meteors.remove(meteor)
            continue
        dx = rocket_pos[0] - meteor["pos"][0]
        dy = rocket_pos[1] - meteor["pos"][1]
        if math.sqrt(dx*dx + dy*dy) < rocket_radius + meteor["radius"]:
            if cheat_mode:
                create_explosion(*meteor["pos"], power=1.15)
                if meteor in meteors:
                    meteors.remove(meteor)
            else:
                create_explosion(*rocket_pos, power=1.55)
                lose_life()
            return


def update_planets():
    for planet in planets:
        planet["angle"] = (planet["angle"] + planet["speed"]) % 360


def update_obstacles(dt):
    settings    = level_settings[current_level]
    chase_speed = settings["obstacle_chase_speed"]
    for obs in obstacles:
        if not obs["alive"]:
            continue
        obs["rot"] += obs["rot_speed"] * dt * 60
        wave      = math.sin(game_time * obs["move_speed"] + obs["phase"])
        side_wave = math.cos(game_time * obs["move_speed"] * 0.70 + obs["phase"])
        drift     = obs["move_range"] * 0.10 * current_level
        if obs["move_axis"] == "x":
            obs["pos"][0] = obs["base"][0] + wave * obs["move_range"]
            obs["pos"][1] = obs["base"][1] + side_wave * drift
        else:
            obs["pos"][0] = obs["base"][0] + side_wave * drift
            obs["pos"][1] = obs["base"][1] + wave * obs["move_range"]
        dx = rocket_pos[0] - obs["base"][0]
        dy = rocket_pos[1] - obs["base"][1]
        d  = math.sqrt(dx*dx + dy*dy) or 1
        obs["base"][0] += (dx/d) * chase_speed * obs["chase_factor"] * dt
        obs["base"][1] += (dy/d) * chase_speed * obs["chase_factor"] * dt


def update_rocket(dt):
    global rocket_angle, boost_energy, life
    if game_over:
        return

    thrust   = 410 + current_level * 26
    acc_x    = 0.0
    acc_y    = 0.0
    local_forward = 0.0
    local_side    = 0.0
    boost_active  = False
    tx, ty, _ = get_target_position()
    a        = math.radians(rocket_angle)
    fwd_x, fwd_y  = math.cos(a), math.sin(a)
    left_x, left_y = -math.sin(a), math.cos(a)

    if not cheat_mode:
        if key_states["w"]:
            local_forward += ROCKET_MAIN_THRUST
        if key_states["s"]:
            local_forward -= ROCKET_REVERSE_THRUST
        if key_states["a"]:
            local_side += ROCKET_SIDE_THRUST
        if key_states["d"]:
            local_side -= ROCKET_SIDE_THRUST

        input_power = math.sqrt(local_forward*local_forward + local_side*local_side)
        if input_power > ROCKET_MAIN_THRUST:
            scale = ROCKET_MAIN_THRUST / input_power
            local_forward *= scale
            local_side    *= scale

        acc_x += (fwd_x * local_forward + left_x * local_side) * thrust
        acc_y += (fwd_y * local_forward + left_y * local_side) * thrust

        boost_active = key_states["b"] and boost_energy > 0
        if boost_active:
            acc_x       += fwd_x * thrust * ROCKET_BOOST_THRUST
            acc_y       += fwd_y * thrust * ROCKET_BOOST_THRUST
            boost_energy = max(0.0, boost_energy - 45 * dt)
        else:
            boost_energy = min(100.0, boost_energy + 12 * dt)

        forward_speed = rocket_vel[0] * fwd_x + rocket_vel[1] * fwd_y
        if key_states["s"] and forward_speed > 0:
            brake = min(forward_speed, thrust * ROCKET_REVERSE_BRAKE * dt)
            rocket_vel[0] -= fwd_x * brake
            rocket_vel[1] -= fwd_y * brake
    else:
        alive_obs = [o for o in obstacles if o["alive"]]
        if alive_obs:
            nearest = min(alive_obs, key=lambda o: (o["pos"][0]-rocket_pos[0])**2 + (o["pos"][1]-rocket_pos[1])**2)
            adx = nearest["pos"][0] - rocket_pos[0]
            ady = nearest["pos"][1] - rocket_pos[1]
            ad  = math.sqrt(adx*adx + ady*ady) or 1
            rocket_angle = math.degrees(math.atan2(ady, adx))
            if ad > 350:
                acc_x += adx/ad * thrust
                acc_y += ady/ad * thrust
            elif ad < 200:
                acc_x -= adx/ad * thrust * 0.4
                acc_y -= ady/ad * thrust * 0.4
        else:
            gdx, gdy = tx - rocket_pos[0], ty - rocket_pos[1]
            gd = math.sqrt(gdx*gdx + gdy*gdy) or 1
            rocket_angle = math.degrees(math.atan2(gdy, gdx))
            acc_x += gdx/gd * thrust * 1.5
            acc_y += gdy/gd * thrust * 1.5
        boost_energy = 100.0
        for meteor in meteors:
            awx = rocket_pos[0] - meteor["pos"][0]
            awy = rocket_pos[1] - meteor["pos"][1]
            md  = math.sqrt(awx*awx + awy*awy) or 1
            if md < 280:
                acc_x += awx/md * thrust * 2.5
                acc_y += awy/md * thrust * 2.5

    # Sun gravity
    sdx, sdy = -rocket_pos[0], -rocket_pos[1]
    sd  = math.sqrt(sdx*sdx + sdy*sdy) or 1
    sg  = min(125.0, 21000.0 / sd) * (0.35 if cheat_mode else 1.0)
    acc_x += sdx/sd * sg
    acc_y += sdy/sd * sg

    # Nearest-planet gravity
    nearest_planet, _ = find_nearest_planet()
    px, py, _  = get_planet_position(nearest_planet)
    pgx, pgy   = px - rocket_pos[0], py - rocket_pos[1]
    pgd        = math.sqrt(pgx*pgx + pgy*pgy) or 1
    gm         = level_settings[current_level]["gravity"] * (0.45 if cheat_mode else 1.0)
    gs         = min(72.0, gm * 15500.0 / pgd)
    acc_x += pgx/pgd * gs
    acc_y += pgy/pgd * gs

    # Black-hole gravity
    if black_hole is not None:
        bhx, bhy, _ = black_hole["pos"]
        bdx = bhx - rocket_pos[0]
        bdy = bhy - rocket_pos[1]
        bd  = math.sqrt(bdx*bdx + bdy*bdy) or 1
        if bd < BLACK_HOLE_INFLUENCE:
            pull = 1.0 - bd / BLACK_HOLE_INFLUENCE
            bg = (90.0 + current_level * 26.0) * pull * pull
            bg += min(95.0, black_hole["gravity"] / (bd + 950.0) * 0.34)
            if cheat_mode:
                bg *= 0.62
            acc_x += bdx / bd * bg
            acc_y += bdy / bd * bg

    # Clamp acceleration
    al = math.sqrt(acc_x*acc_x + acc_y*acc_y)
    if al > thrust * 2.4:
        acc_x = acc_x/al * thrust * 2.4
        acc_y = acc_y/al * thrust * 2.4

    rocket_vel[0] += acc_x * dt
    rocket_vel[1] += acc_y * dt

    if cheat_mode:
        drag_rate = ROCKET_DRAG_ACTIVE * 0.45
    else:
        thrusting = any(key_states[k] for k in ("w", "a", "s", "d", "b"))
        drag_rate = ROCKET_DRAG_ACTIVE if thrusting else ROCKET_DRAG_IDLE
        if key_states["s"] and not key_states["w"]:
            drag_rate += 0.28
    drag = math.exp(-drag_rate * dt)
    rocket_vel[0] *= drag
    rocket_vel[1] *= drag

    if not cheat_mode and key_states["s"] and not key_states["w"]:
        forward_speed = rocket_vel[0] * fwd_x + rocket_vel[1] * fwd_y
        reverse_limit = 285.0 + current_level * 24
        if forward_speed < -reverse_limit:
            side_vx = rocket_vel[0] - fwd_x * forward_speed
            side_vy = rocket_vel[1] - fwd_y * forward_speed
            rocket_vel[0] = side_vx - fwd_x * reverse_limit
            rocket_vel[1] = side_vy - fwd_y * reverse_limit

    speed = math.sqrt(rocket_vel[0]**2 + rocket_vel[1]**2)
    max_speed = 560.0 + current_level * 45
    if key_states["w"]: max_speed += 170
    if boost_active:     max_speed += 250
    if cheat_mode:      max_speed += 220
    if speed > max_speed:
        rocket_vel[0] = rocket_vel[0] / speed * max_speed
        rocket_vel[1] = rocket_vel[1] / speed * max_speed

    rocket_pos[0] += rocket_vel[0] * dt
    rocket_pos[1] += rocket_vel[1] * dt

    # Rotate toward intentional thrust, but do not flip around during reverse drift.
    speed = math.sqrt(rocket_vel[0]**2 + rocket_vel[1]**2)
    if not cheat_mode:
        steer_x = fwd_x * max(local_forward, 0.0) + left_x * local_side
        steer_y = fwd_y * max(local_forward, 0.0) + left_y * local_side
        if boost_active:
            steer_x += fwd_x * 0.8
            steer_y += fwd_y * 0.8
        steer_len = math.sqrt(steer_x*steer_x + steer_y*steer_y)
        if steer_len > 0.05:
            target_a = math.degrees(math.atan2(steer_y, steer_x))
            rocket_angle = smooth_rotate_angle(rocket_angle, target_a, dt)
        else:
            forward_speed = rocket_vel[0] * fwd_x + rocket_vel[1] * fwd_y
            if speed > 70 and forward_speed > 25:
                target_a = math.degrees(math.atan2(rocket_vel[1], rocket_vel[0]))
                rocket_angle = smooth_rotate_angle(rocket_angle, target_a, dt * 0.65)
    elif speed > 40:
        target_a = math.degrees(math.atan2(rocket_vel[1], rocket_vel[0]))
        rocket_angle = smooth_rotate_angle(rocket_angle, target_a, dt)

    # Boundary wall
    if abs(rocket_pos[0]) > GRID_LENGTH or abs(rocket_pos[1]) > GRID_LENGTH:
        if cheat_mode:
            rocket_pos[0] = max(-GRID_LENGTH+80, min(GRID_LENGTH-80, rocket_pos[0]))
            rocket_pos[1] = max(-GRID_LENGTH+80, min(GRID_LENGTH-80, rocket_pos[1]))
            rocket_vel[0] *= -0.4
            rocket_vel[1] *= -0.4
        else:
            create_explosion(*rocket_pos, power=1.55)
            lose_life()
            return

    if black_hole is not None:
        bhx, bhy, bhz = black_hole["pos"]
        bd = math.sqrt((rocket_pos[0]-bhx)**2 + (rocket_pos[1]-bhy)**2 + (rocket_pos[2]-bhz)**2)
        if bd < black_hole["radius"] + rocket_radius * 0.55:
            create_explosion(*rocket_pos, power=1.65)
            if cheat_mode:
                push_rocket_away_from(bhx, bhy)
                rocket_vel[0] *= 1.4
                rocket_vel[1] *= 1.4
            else:
                lose_life()
            return

    # Planet collisions
    for i, planet in enumerate(planets):
        ppx, ppy, ppz = get_planet_position(planet)
        d = math.sqrt((rocket_pos[0]-ppx)**2 + (rocket_pos[1]-ppy)**2 + (rocket_pos[2]-ppz)**2)
        if i == current_level and d < planet["radius"] + rocket_radius + 20:
            complete_level()
            return
        if i != current_level and d < planet["radius"] + rocket_radius + 10:
            if cheat_mode:
                push_rocket_away_from(ppx, ppy)
            else:
                create_explosion(*rocket_pos, power=1.45)
                lose_life()
            return

    # Obstacle collisions
    for obs in obstacles:
        if not obs["alive"]:
            continue
        dx = rocket_pos[0] - obs["pos"][0]
        dy = rocket_pos[1] - obs["pos"][1]
        if math.sqrt(dx*dx + dy*dy) < obs["size"] + rocket_radius:
            if cheat_mode:
                obs["alive"] = False
                create_explosion(*obs["pos"], power=1.0 + obs["size"] / 90.0)
                push_rocket_away_from(obs["pos"][0], obs["pos"][1])
            else:
                create_explosion(*rocket_pos, power=1.45)
                lose_life()
            return


# ── Camera ─────────────────────────────────────────────────────────────────────

def update_smooth_camera(dt):
    global smooth_cam_x, smooth_cam_y, smooth_cam_z
    alpha = min(1.0, 9.0 * dt)
    smooth_cam_x += (rocket_pos[0] - smooth_cam_x) * alpha
    smooth_cam_y += (rocket_pos[1] - smooth_cam_y) * alpha
    smooth_cam_z += (rocket_pos[2] - smooth_cam_z) * alpha


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_WIDTH / WINDOW_HEIGHT, 1.0, 12000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == 0:
        a   = math.radians(rocket_angle)
        cx  = smooth_cam_x - math.cos(a) * 300
        cy  = smooth_cam_y - math.sin(a) * 300
        cz  = smooth_cam_z + 155
        gluLookAt(cx, cy, cz, smooth_cam_x, smooth_cam_y, smooth_cam_z, 0, 0, 1)

    elif camera_mode == 1:
        cx = smooth_cam_x - 1120
        cy = smooth_cam_y - 1120
        cz = smooth_cam_z + 880
        gluLookAt(cx, cy, cz, smooth_cam_x, smooth_cam_y, smooth_cam_z, 0, 0, 1)

    else:
        a    = math.radians(rocket_angle)
        dx   = math.cos(a)
        dy   = math.sin(a)
        ex   = rocket_pos[0] + dx * 55
        ey   = rocket_pos[1] + dy * 55
        ez   = rocket_pos[2] + 28
        gluLookAt(ex, ey, ez, ex + dx*400, ey + dy*400, ez, 0, 0, 1)


# ── Input ──────────────────────────────────────────────────────────────────────

def keyboardListener(key, x, y):
    global cheat_mode, camera_mode, auto_fire_timer
    try:
        key = key.decode("utf-8").lower()
    except Exception:
        return
    if key in key_states:
        key_states[key] = True
    if key == "c":
        cheat_mode = not cheat_mode
        auto_fire_timer = 0.0
    elif key == "v":
        camera_mode = (camera_mode + 1) % 3
    elif key == "r":
        reset_game()
    elif key == "1":
        camera_mode = 2
    elif key == "2":
        camera_mode = 0
    elif key == "3":
        camera_mode = 1


def keyboardUpListener(key, x, y):
    try:
        key = key.decode("utf-8").lower()
    except Exception:
        return
    if key in key_states:
        key_states[key] = False


def specialKeyListener(*_):
    pass


def mouseListener(button, state, x, y):
    global camera_mode
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        fire_bullet()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = (camera_mode + 1) % 3


# ── Main loop ──────────────────────────────────────────────────────────────────

def idle():
    global auto_fire_timer, meteor_timer, warning_timer, game_time, last_time, level_time_left

    now      = glutGet(GLUT_ELAPSED_TIME)
    dt       = min((now - last_time) / 1000.0, 0.05)
    last_time = now
    if dt <= 0:
        return

    game_time += dt

    update_smooth_camera(dt)
    update_planets()
    update_obstacles(dt)
    update_explosions(dt)

    if not game_over:
        update_rocket(dt)
        update_bullets(dt)
        update_meteors(dt)
        update_cheat_mode(dt)

        if not cheat_mode:
            level_time_left -= dt
            if level_time_left <= 0:
                create_explosion(*rocket_pos, power=1.55)
                lose_life()

        meteor_timer += dt
        if meteor_timer >= level_settings[current_level]["meteor_interval"]:
            spawn_meteor_burst()
            meteor_timer = 0.0

        if warning_timer > 0:
            warning_timer -= dt

    glutPostRedisplay()


def showScreen():
    glClearColor(0.0, 0.0, 0.018, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    setupCamera()
    draw_space_floor()
    draw_shapes()
    draw_hud()
    glutSwapBuffers()


def main():
    global last_time, _quadric
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"Orbital Escape")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.018, 1.0)
    _quadric = gluNewQuadric()
    generate_star_cache()
    reset_game()
    last_time = glutGet(GLUT_ELAPSED_TIME)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()
