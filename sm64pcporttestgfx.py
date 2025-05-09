from ursina import *
from ursina.prefabs.platformer_controller_2d import PlatformerController2d # Just for print_on_screen if not globally available
from math import sin, cos, radians

app = Ursina()
window.size = (600, 400)
window.borderless = False
window.title = "Super Mario 64 Inspired Game - Fixed"

# Player setup
player = Entity(model='cube', color=color.red, scale=(1,1,1), position=(0,1,0), collider='box')
player.y_speed = 0
player.on_ground = False # Represents ground state from the *previous* frame for input logic

# Level setup
ground = Entity(model='cube', scale=(10,1,10), position=(0,0,0), color=color.green, collider='box')
platform1 = Entity(model='cube', scale=(2,1,2), position=(3,1,3), color=color.blue, collider='box')
platform2 = Entity(model='cube', scale=(2,1,2), position=(-3,2,-3), color=color.blue, collider='box')
moving_platform = Entity(model='cube', scale=(2,1,2), position=(3,1,0), color=color.orange, collider='box')
platform3 = Entity(model='cube', scale=(2,1,2), position=(0,3,0), color=color.blue, collider='box')

# Goal setup
goal = Entity(model='cube', scale=(1,1,1), position=(5,1,5), color=color.yellow, collider='box')

# Lighting
light = DirectionalLight()
light.direction = (1, -1, -1)

# Camera setup
camera_angle = 0

def update():
    global camera_angle

    # --- 1. Store previous state for deltas ---
    prev_moving_platform_x = moving_platform.x
    # prev_moving_platform_y = moving_platform.y # If it moved in Y
    # prev_moving_platform_z = moving_platform.z # If it moved in Z

    # --- 2. Handle player input for movement & jump ---
    player_dx = (held_keys['d'] - held_keys['a']) * time.dt * 5
    player_dz = (held_keys['w'] - held_keys['s']) * time.dt * 5
    
    player.x += player_dx
    player.z += player_dz

    # Jump intent (uses player.on_ground from *previous* frame's physics update)
    if held_keys['space'] and player.on_ground:
        player.y_speed = 5
        # player.on_ground = False # Optional: Mark as not on ground immediately.
                                 # The physics check will robustly determine this anyway.

    # --- 3. Apply physics (gravity) to player ---
    player.y_speed -= time.dt * 10  # Gravity
    player.y += player.y_speed * time.dt # Apply vertical speed

    # --- 4. Update moving platforms ---
    moving_platform.x = 3 + sin(time.time()) * 2
    platform_delta_x = moving_platform.x - prev_moving_platform_x
    # platform_delta_y = moving_platform.y - prev_moving_platform_y (if applicable)
    # platform_delta_z = moving_platform.z - prev_moving_platform_z (if applicable)

    # --- 5. Collision Detection and Resolution (Ground Check) ---
    # This determines player.on_ground for the *current* frame,
    # which will be used in the *next* frame's jump logic and sticking logic.
    is_grounded_this_frame = False
    hit_ground_entity = None

    # Raycast downwards from player's bottom center.
    # player.scale_y / 2 is player's half-height (0.5 for scale 1).
    ray_origin = player.world_position + Vec3(0, -player.scale_y / 2, 0)
    
    # Distance to check below feet. Allows slight penetration before snapping.
    ground_check_distance = 0.1 
    
    hit_info = raycast(origin=ray_origin,
                       direction=(0, -1, 0),
                       distance=ground_check_distance,
                       ignore=(player,),
                       debug=False) # Set True to visualize the ray

    if hit_info.hit:
        # A surface was hit. Only process if player is falling or very close to stopping vertically.
        if player.y_speed <= 0.01: # Small tolerance for nearly stopped upward motion
            # Snap player's bottom to the exact collision point on the surface.
            player.y = hit_info.world_point.y + (player.scale_y / 2)
            player.y_speed = 0  # Stop vertical movement as player is now grounded.
            is_grounded_this_frame = True
            hit_ground_entity = hit_info.entity
    
    player.on_ground = is_grounded_this_frame # Update player's ground status for the next frame.

    # --- 6. Handle sticking to moving platform ---
    if player.on_ground and hit_ground_entity == moving_platform:
        # Apply the platform's horizontal movement delta to the player.
        player.x += platform_delta_x
        # If platform also moved vertically (platform_delta_y), you might add:
        # player.y += platform_delta_y 
        # However, vertical sticking needs care as it can interfere with gravity/snapping logic.
        # For this fix, horizontal sticking is the primary concern.

    # --- 7. Camera Update ---
    if held_keys['q']:
        camera_angle += time.dt * 100
    if held_keys['e']:
        camera_angle -= time.dt * 100
    
    camera_offset_distance = 10
    camera_height_offset = 10 
    
    cam_x_offset = sin(radians(camera_angle)) * camera_offset_distance
    cam_z_offset = cos(radians(camera_angle)) * camera_offset_distance
    
    # Camera position is relative to player, orbits with Q/E
    camera.position = (player.x + cam_x_offset, player.y + camera_height_offset, player.z + cam_z_offset)
    camera.look_at(player.world_position) # Look at player's center

    # --- 8. Goal Check ---
    # Check distance between player's center and goal's center
    if distance(player.world_position, goal.world_position) < (player.scale_x / 2 + goal.scale_x / 2): # More accurate collision
        print_on_screen("You win!", position=(-0.1, 0.1), scale=2, duration=3)
        # To make the win more impactful, you could freeze player, or transition state:
        # player.disable() 
        # invoke(application.quit, delay=3) # Example: Quit after 3 seconds

app.run()
