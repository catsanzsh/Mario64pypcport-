from ursina import *
from math import sin, cos, radians

app = Ursina()
window.size = (600, 400)
window.borderless = False
window.title = "Super Mario 64 Inspired Game"

# Player setup
player = Entity(model='cube', color=color.red, scale=(1,1,1), position=(0,1,0))
player.y_speed = 0
player.on_ground = False

# Level setup
ground = Entity(model='cube', scale=(10,1,10), position=(0,0,0), color=color.green, collider='box')
platform1 = Entity(model='cube', scale=(2,1,2), position=(3,1,3), color=color.blue, collider='box')
platform2 = Entity(model='cube', scale=(2,1,2), position=(-3,2,-3), color=color.blue, collider='box')
moving_platform = Entity(model='cube', scale=(2,1,2), position=(3,1,0), color=color.orange, collider='box')
platform3 = Entity(model='cube', scale=(2,1,2), position=(0,3,0), color=color.blue, collider='box')

# Goal setup
goal = Entity(model='cube', scale=(1,1,1), position=(5,1,5), color=color.yellow)

# Lighting
light = DirectionalLight()
light.direction = (1, -1, -1)

# Camera setup
camera_angle = 0

def update():
    # Player movement
    player.x += held_keys['d'] * time.dt * 5
    player.x -= held_keys['a'] * time.dt * 5
    player.z += held_keys['w'] * time.dt * 5
    player.z -= held_keys['s'] * time.dt * 5

    # Jumping
    if held_keys['space'] and player.on_ground:
        player.y_speed = 5

    # Gravity
    player.y_speed -= time.dt * 10
    player.y += player.y_speed * time.dt

    # Collision detection
    hit_info = raycast(player.position + Vec3(0, -0.5, 0), direction=(0,-1,0), distance=1)
    if hit_info.hit:
        platform_top = hit_info.entity.position.y + hit_info.entity.scale_y / 2
        if player.y - 0.5 <= platform_top:
            player.y = platform_top + 0.5
            if player.y_speed < 0:
                player.y_speed = 0
            player.on_ground = True
        else:
            player.on_ground = False
    else:
        player.on_ground = False

    # Move moving platform
    moving_platform.x = 3 + sin(time.time()) * 2

    # Camera control
    if held_keys['q']:
        global camera_angle
        camera_angle += time.dt * 100
    if held_keys['e']:
        camera_angle -= time.dt * 100
    camera.position = player.position + Vec3(sin(radians(camera_angle)) * 10, 10, cos(radians(camera_angle)) * 10)
    camera.look_at(player)

    # Check for goal
    if distance(player, goal) < 1:
        print("You win!")

app.run()
