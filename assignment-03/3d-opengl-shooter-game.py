from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

camera_pos = (0,400,400)
fovY = 120
playerAngle = 0
playerU = 0
playerV = 0
bullet = []
enemy = []
LifeRem = 5
Score = 0
BulletMissed = 0
gameOver = False
cameraAngle = 0 
cameraHeight = 400 
cameraRad = 400
cheatMode = False
autoFollow = False

def drawPlayer():
    glPushMatrix()
    glTranslatef(playerU, playerV, 0)
    glRotatef(playerAngle, 0, 0, 1)

    glPushMatrix()
    glColor3f(0.3, 0.6, 0.3)
    glScalef(1, 0.5, 1.5)
    glutSolidCube(40)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, 50)
    glColor3f(1, 0.8, 0.6)
    glutSolidSphere(15, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-10, 0, -40)
    glColor3f(0, 0, 1)
    gluCylinder(gluNewQuadric(), 10, 10, 40, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(10, 0, -40)    
    glColor3f(0, 0, 1)
    gluCylinder(gluNewQuadric(), 10, 10, 40, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(25, 0, 20)
    glRotatef(90, 0, 1, 0)
    glColor3f(1, 0.8, 0.6)
    gluCylinder(gluNewQuadric(), 8, 8, 40, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(40, 0, 20)
    glColor3f(0.8, 0.8, 0.8)
    glScalef(0.3, 1.5, 0.3)
    glutSolidCube(30)
    glPopMatrix()

    glPopMatrix()

def drawEnemy():
    for i in enemy:
        glPushMatrix()
        glTranslatef(i[0], i[1], 0)
        glColor3f(1, 0, 0)
        gluSphere(gluNewQuadric(), 30, 15, 15)
        glTranslatef(0, 0, 25)
        glColor3f(0, 0, 0)
        gluSphere(gluNewQuadric(), 10, 10, 10)
        glPopMatrix()

def spawnEnemy():
    global enemy
    enemy = []
    for i in range(5):
        X = random.randint(-450,450)
        Y = random.randint(-450,450)
        enemy.append([X,Y])

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setupCamera()
    drawGrid()
    drawBoundary()
    drawPlayer()
    drawEnemy()
    drawBullet()
    drawUI()
    glutSwapBuffers()

def setupCamera():
    global cameraAngle, cameraHeight, cameraRad, cheatMode, autoFollow, playerU, playerV, playerAngle

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if cheatMode and autoFollow:
        camX = playerU - 100 * math.cos(math.radians(playerAngle))
        camY = playerV - 100 * math.sin(math.radians(playerAngle))
        camZ = 80

        lookX = playerU + 100 * math.cos(math.radians(playerAngle))
        lookY = playerV + 100 * math.sin(math.radians(playerAngle))

        gluLookAt(camX, camY, camZ,
                  lookX, lookY, 0,
                  0, 0, 1)
    else:
        x = cameraRad * math.cos(math.radians(cameraAngle))
        y = cameraRad * math.sin(math.radians(cameraAngle))
        z = cameraHeight

        gluLookAt(x, y, z,
                  0, 0, 0,
                  0, 0, 1)

def drawBullet():
    for i in bullet:
        glPushMatrix()
        glTranslatef(i[0], i[1], 0)
        glColor3f(1, 0, 0)
        glutSolidCube(10)
        glPopMatrix()

def drawGrid():
    size = 600
    step = 60

    for i in range(-size,size,step):
        for j in range(-size,size,step):
            if (i//step + j//step) % 2 == 0:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0.7, 0.5, 1)
            glBegin(GL_QUADS)
            glVertex3f(i, j, 0)
            glVertex3f(i+step, j, 0)
            glVertex3f(i+step, j+step, 0)
            glVertex3f(i, j+step, 0)
            glEnd()

def drawBoundary():
    size = 600

    glColor3f(0, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(-size, -size, 0)
    glVertex3f(-size+10, -size, 0)
    glVertex3f(-size+10, size, 0)
    glVertex3f(-size, size, 0)
    glEnd()

    glColor3f(0, 1, 1)
    glBegin(GL_QUADS)
    glVertex3f(size-10, -size, 0)
    glVertex3f(size, -size, 0)
    glVertex3f(size, size, 0)
    glVertex3f(size-10, size, 0)
    glEnd()

    glColor3f(0, 0, 1)
    glBegin(GL_QUADS)
    glVertex3f(-size, size-10, 0)
    glVertex3f(size, size-10, 0)
    glVertex3f(size, size, 0)
    glVertex3f(-size, size, 0)
    glEnd()

    glColor3f(0, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(-size, -size, 0)
    glVertex3f(size, -size, 0)
    glVertex3f(size, -size+10, 0)
    glVertex3f(-size, -size+10, 0)
    glEnd()

def keyboardListener(key, x, y):
    global LifeRem, Score, BulletMissed, gameOver, playerU, playerV, playerAngle, bullet, cheatMode, autoFollow
    speed = 10

    if key == b'a':
        playerAngle +=10
    if key == b'd':
        playerAngle -=10
    if key == b'w':
        playerU += speed * math.cos(math.radians(playerAngle))
        playerV += speed * math.sin(math.radians(playerAngle))
    if key == b's':
        playerU -= speed * math.cos(math.radians(playerAngle))
        playerV -= speed * math.sin(math.radians(playerAngle))

    limit = 480
    playerU = max(-limit, min(limit, playerU))
    playerV = max(-limit, min(limit, playerV))

    if key == b'r' or key == b'R':
        if gameOver:
            LifeRem = 5
            Score = 0
            BulletMissed = 0
            gameOver = False
            playerU = 0
            playerV = 0
            playerAngle = 0
            bullet.clear()
            spawnEnemy()

    if key == b'c' or key == b'C':
        cheatMode = not cheatMode

    if key == b'v' or key == b'V':
        autoFollow = not autoFollow

def specialKeyListener(key, x, y):
    global cameraAngle, cameraHeight
    if key == GLUT_KEY_LEFT:
        cameraAngle += 15
    elif key == GLUT_KEY_RIGHT:
        cameraAngle -= 15
    elif key == GLUT_KEY_UP:
        cameraHeight += 45
    elif key == GLUT_KEY_DOWN:
        cameraHeight -= 45

def mouseListener(button, state, x, y):
    global bullet, playerU, playerV, playerAngle
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        bullet.append([playerU, playerV, playerAngle])

def idle():
    global bullet, enemy, Score, LifeRem, BulletMissed, gameOver, cheatMode, playerAngle

    if gameOver:
        glutPostRedisplay()
        return

    speed = 5

    for i in bullet:
        i[0] += speed * math.cos(math.radians(i[2]))
        i[1] += speed * math.sin(math.radians(i[2]))

    new_bullet = []
    for i in bullet:
        if cheatMode:
            new_bullet.append(i)
        else:
            if -600 < i[0] < 600 and -600 < i[1] < 600:
                new_bullet.append(i)
            else:
                BulletMissed += 1
    bullet[:] = new_bullet

    if cheatMode and len(enemy) > 0:

        target = enemy[0]
        minDist = 999999

        for e in enemy:
            dx = e[0] - playerU
            dy = e[1] - playerV
            d = math.sqrt(dx*dx + dy*dy)

            if d < minDist:
                minDist = d
                target = e

        dx = target[0] - playerU
        dy = target[1] - playerV

        playerAngle = math.degrees(math.atan2(dy, dx))

        bullet.append([playerU, playerV, playerAngle])

    for i in enemy:
        dX = playerU - i[0]
        dY = playerV - i[1]

        dist = math.sqrt(dX*dX + dY*dY)

        if dist != 0:
            i[0] += (dX / dist) * 0.5
            i[1] += (dY / dist) * 0.5

        if not cheatMode:
            if dist < 30:
                LifeRem -= 1
                i[0] = random.randint(-400, 400)
                i[1] = random.randint(-400, 400)

        i[0] = max(-480, min(480, i[0]))
        i[1] = max(-480, min(480, i[1]))

    new_enemy = []

    for i in enemy:
        hit = False

        for j in bullet:
            dx = i[0] - j[0]
            dy = i[1] - j[1]

            dist = math.sqrt(dx*dx + dy*dy)

            if cheatMode:
                hit = True
            else:
                if dist < 30:
                    hit = True

            if hit:
                Score += 1
                X = random.randint(-400, 400)
                Y = random.randint(-400, 400)
                new_enemy.append([X, Y])
                break

        if not hit:
            new_enemy.append(i)

    enemy[:] = new_enemy

    if LifeRem <= 0 or BulletMissed >= 10:
        gameOver = True

    glutPostRedisplay()

def drawText(x, y, text):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

def drawUI():
    global LifeRem, Score, BulletMissed, gameOver

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)

    drawText(10, 770, "Player Life Remaining: " + str(LifeRem))
    drawText(10, 740, "Game Score: " + str(Score))
    drawText(10, 710, "Player Bullet Missed: " + str(BulletMissed))

    if gameOver:
        drawText(600, 600, "GAME OVER")
        drawText(580, 580, "Press R to Restart")

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D OpenGL Intro")
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    spawnEnemy()
    glutMainLoop()

if __name__ == "__main__":
    main()