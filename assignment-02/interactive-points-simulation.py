from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

width = 500
height = 500
diamond1 = random.randint(-200, 200)
diamond2 = 220
diamondSpeed = 2
catcher = 0
point = 0
gameOver = False
paused = False
cheat = False
diamondColor = [random.random(), random.random(), random.random()]
lastTime = time.time()
deltaTime = 0


# pixel drawing
def drawPixel(x, y):
    glPointSize(2)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()


# draw diamond
def drawDiamond(x, y):
    glColor3f(diamondColor[0], diamondColor[1], diamondColor[2])
    midpointLine(x, y + 10, x + 10, y)
    midpointLine(x + 10, y, x, y - 10)
    midpointLine(x, y - 10, x - 10, y)
    midpointLine(x - 10, y, x, y + 10)


# draw catcher
def drawCatcher():
    global catcher
    if gameOver:
        glColor3f(1, 0, 0)
    else:
        glColor3f(1, 1, 1)
    y = -220
    midpointLine(catcher - 50, y, catcher + 50, y)
    midpointLine(catcher - 50, y, catcher - 25, y - 20)
    midpointLine(catcher + 50, y, catcher + 25, y - 20)
    midpointLine(catcher - 25, y - 20, catcher + 25, y - 20)


# draw restart button
def drawRestartButton():
    glColor3f(0, 1, 1)
    midpointLine(-200, 210, -220, 190)
    midpointLine(-200, 170, -220, 190)
    midpointLine(-200, 190, -160, 190)


# draw pause button
def drawPauseButton():
    glColor3f(1, 0.7, 0)
    if paused == False:
        midpointLine(-10, 210, -10, 170)
        midpointLine(10, 210, 10, 170)
    else:
        midpointLine(-10, 210, -10, 170)
        midpointLine(-10, 210, 20, 190)
        midpointLine(-10, 170, 20, 190)


# draw exit button
def drawExitButton():
    glColor3f(1, 0, 0)
    midpointLine(200, 210, 240, 170)
    midpointLine(200, 170, 240, 210)


# find zone
def findZone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) > abs(dy):
        if dx >= 0 and dy >= 0:
            return 0
        if dx < 0 and dy >= 0:
            return 3
        if dx < 0 and dy < 0:
            return 4
        if dx >= 0 and dy < 0:
            return 7
    else:
        if dx >= 0 and dy >= 0:
            return 1
        if dx < 0 and dy >= 0:
            return 2
        if dx < 0 and dy < 0:
            return 5
        if dx >= 0 and dy < 0:
            return 6


# convert to zone
def toZone0(zone, x, y):
    if zone == 0:
        return x, y
    if zone == 1:
        return y, x
    if zone == 2:
        return y, -x
    if zone == 3:
        return -x, y
    if zone == 4:
        return -x, -y
    if zone == 5:
        return -y, -x
    if zone == 6:
        return -y, x
    if zone == 7:
        return x, -y


# convert from zone
def fromZone0(zone, x, y):
    if zone == 0:
        return x, y
    if zone == 1:
        return y, x
    if zone == 2:
        return -y, x
    if zone == 3:
        return -x, y
    if zone == 4:
        return -x, -y
    if zone == 5:
        return -y, -x
    if zone == 6:
        return y, -x
    if zone == 7:
        return x, -y


# midpoint line
def midpointLine(x1, y1, x2, y2):
    zone = findZone(x1, y1, x2, y2)
    x1, y1 = toZone0(zone, x1, y1)
    x2, y2 = toZone0(zone, x2, y2)
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    x = x1
    y = y1

    while x <= x2:
        px, py = fromZone0(zone, x, y)
        drawPixel(px, py)

        if d > 0:
            y += 1
            d += incNE
        else:
            d += incE
        x += 1


# collision detection
def collision():
    diamondBox = {'x': diamond1 - 10, 'y': diamond2 - 10, 'width': 20, 'height': 20}
    catcherBox = {'x': catcher - 50, 'y': -240, 'width': 100, 'height': 20}
    return (diamondBox['x'] < catcherBox['x'] + catcherBox['width'] and
            diamondBox['x'] + diamondBox['width'] > catcherBox['x'] and
            diamondBox['y'] < catcherBox['y'] + catcherBox['height'] and
            diamondBox['y'] + diamondBox['height'] > catcherBox['y'])


# display
def display():
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    drawRestartButton()
    drawPauseButton()
    drawExitButton()
    drawDiamond(diamond1, diamond2)
    drawCatcher()
    glutSwapBuffers()


# animate
def animate():
    global diamond2, point, gameOver, diamond1, diamondSpeed, diamondColor, lastTime, deltaTime
    currentTime = time.time()
    deltaTime = currentTime - lastTime
    lastTime = currentTime
    if paused or gameOver:
        glutPostRedisplay()
        return
    if cheat:
        if catcher < diamond1:
            moveRight()
        elif catcher > diamond1:
            moveLeft()
    diamond2 -= diamondSpeed * 100 * deltaTime
    if collision():
        point += 1
        print("Score:", point)
        diamond2 = 220
        diamond1 = random.randint(-200, 200)
        diamondColor = [random.random(), random.random(), random.random()]
        diamondSpeed += 0.2
    if diamond2 < -230:
        gameOver = True
        print("Game Over! Score:", point)
    glutPostRedisplay()


#Move right
def moveRight():
    global catcher
    if catcher < 200:
        catcher += 15
        
        
# move left
def moveLeft():
    global catcher
    if catcher > -200:
        catcher -= 15


#Keyboard input
def keyboard(key, x, y):
    global cheat
    if key == b'c':
        cheat = not cheat

#Mouse input
def mouse(button, state, x, y):
    global point, gameOver, paused, diamond2, diamond1, diamondSpeed
    if state == GLUT_DOWN:
        mx = x - 250
        my = 250 - y
        if -220 < mx < -160 and 170 < my < 210:
            point = 0
            gameOver = False
            diamondSpeed = 2
            diamond2 = 220
            diamond1 = random.randint(-200, 200)
        if -20 < mx < 20 and 170 < my < 210:
            paused = not paused
        if 200 < mx < 240 and 170 < my < 210:
            print("Goodbye. Score:", point)
            glutLeaveMainLoop()

#Special keys
def special(key, x, y):
    if key == GLUT_KEY_LEFT:
        moveLeft()
    if key == GLUT_KEY_RIGHT:
        moveRight()

#Setup
def setup():
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-250, 250, -250, 250, 0, 1)
    glMatrixMode(GL_MODELVIEW)

#Main
def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(500, 200)
    glutCreateWindow(b"Catch The Diamonds")
    setup()
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special)
    glutMouseFunc(mouse)
    glutMainLoop()


if __name__ == "__main__":
    main()