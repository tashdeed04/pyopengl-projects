############TASK 1###########
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

#Variables
width = 500
height = 500
background = 0
counter = 0
rains = 0

drops = []
for i in range(60):
    x = random.randint(-250, 250)
    y = random.randint(-250, 250)
    drops.append([x, y])


#House
def drawBody():
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(-60, -120)
    glVertex2f(60, -120)
    glVertex2f(60, -20)
    glVertex2f(-60, -120)
    glVertex2f(60, -20)
    glVertex2f(-60, -20)
    glEnd()

#Roof
def drawRoof():
    glColor3f(0.0, 0.3, 0.8)
    glBegin(GL_TRIANGLES)
    glVertex2f(-80, -20)
    glVertex2f(80, -20)
    glVertex2f(0, 80)
    glEnd()

#Door
def drawDoor():
    glColor3f(0.4, 0.2, 0.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(-15, -120)
    glVertex2f(15, -120)
    glVertex2f(15, -70)
    glVertex2f(-15, -120)
    glVertex2f(15, -70)
    glVertex2f(-15, -70)
    glEnd()

#Windows
def drawWindows():
    glColor3f(0.3, 0.6, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(-45, -60)
    glVertex2f(-25, -60)
    glVertex2f(-25, -40)
    glVertex2f(-45, -60)
    glVertex2f(-25, -40)
    glVertex2f(-45, -40)
    glEnd()
    glBegin(GL_TRIANGLES)
    glVertex2f(25, -60)
    glVertex2f(45, -60)
    glVertex2f(45, -40)
    glVertex2f(25, -60)
    glVertex2f(45, -40)
    glVertex2f(25, -40)
    glEnd()

#Ground
def drawGround():
    glColor3f(0.5, 0.3, 0.1)
    glBegin(GL_TRIANGLES)
    glVertex2f(-250, -250)
    glVertex2f(250, -250)
    glVertex2f(250, -20)
    glVertex2f(-250, -250)
    glVertex2f(250, -20)
    glVertex2f(-250, -20)
    glEnd()

#Grass
def drawGrass():
    glColor3f(0.0, 0.6, 0.0)
    glBegin(GL_TRIANGLES)
    x = -250
    while x < 250:
        glVertex2f(x, -20)
        glVertex2f(x + 10, 25)
        glVertex2f(x + 20, -20)
        x += 20
    glEnd()

#Rain
def drawRain():
    glColor3f(0.3, 0.6, 1.0)
    glBegin(GL_LINES)
    for d in drops:
        glVertex2f(d[0], d[1])
        glVertex2f(d[0], d[1] - 15)
    glEnd()

#Setup
def setup():
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-250, 250, -250, 250, 0, 1)
    glMatrixMode(GL_MODELVIEW)

#Display
def display():
    if background == 0:
        glClearColor(0.0, 0.0, 0.0, 1.0)
    else:
        glClearColor(1.0, 1.0, 1.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    setup()
    drawGround()
    drawGrass()
    drawBody()
    drawRoof()
    drawDoor()
    drawWindows()
    drawRain()
    glutSwapBuffers()

#Animate
def animate():
    global background, counter

    for d in drops:
        d[1] -= 3
        if d[1] < -250:
            d[1] = 250
            d[0] = random.randint(-250, 250)
    counter += 1
    if counter > 240:
        background = 1 - background
        counter = 0
    glutPostRedisplay()

#Main
def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(500, 300)
    glutCreateWindow(b"Assignment 1")
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutMainLoop()


if __name__ == "__main__":
    main()




##########TASK 2############
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random


#Variables
width = 500
height = 500
background = 0
counter = 0
speed = 2
blink = 0
freeze = 0
points = []

#Draw Points
def drawPoints():
    for p in points:
        if blink == 1 and counter % 40 < 20:
            glColor3f(0, 0, 0)
        else:
            glColor3f(p[4], p[5], p[6])
        glPointSize(10)
        glBegin(GL_POINTS)
        glVertex2f(p[0], p[1])
        glEnd()

#Setup
def setup():
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-250, 250, -250, 250, 0, 1)
    glMatrixMode(GL_MODELVIEW)

#Display
def display():
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    setup()
    drawPoints()
    glutSwapBuffers()

#Animate
def animate():
    global counter

    if freeze == 0:
        for p in points:
            p[0] += p[2] * speed
            p[1] += p[3] * speed
            if p[0] > 250 or p[0] < -250:
                p[2] = -p[2]
            if p[1] > 250 or p[1] < -250:
                p[3] = -p[3]
    counter += 1
    glutPostRedisplay()

#Mouse
def mouse(button, state, x, y):
    global blink
    if state == GLUT_DOWN:
        px = x - 250
        py = 250 - y
        if button == GLUT_RIGHT_BUTTON:
            dx = random.choice([-1, 1])
            dy = random.choice([-1, 1])
            r = random.random()
            g = random.random()
            b = random.random()
            points.append([px, py, dx, dy, r, g, b])
        if button == GLUT_LEFT_BUTTON:
            if blink == 0:
                blink = 1
            else:
                blink = 0

#Special Keys
def special(key, x, y):
    global speed
    if key == GLUT_KEY_UP:
        speed += 1
    if key == GLUT_KEY_DOWN:
        if speed > 1:
            speed -= 1

#Keyboard
def keyboard(key, x, y):
    global freeze
    if key == b' ':
        if freeze == 0:
            freeze = 1
        else:
            freeze = 0

#Main
def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(500, 300)
    glutCreateWindow(b"Assignment 2")
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutMouseFunc(mouse)
    glutSpecialFunc(special)
    glutKeyboardFunc(keyboard)
    glutMainLoop()


if __name__ == "__main__":
    main()