import pygame
import pymunk
from pymunk import pygame_util

pygame.init()

# Set up the screen
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pymunk Physics Simulation")

# Create a pymunk space
space = pymunk.Space()
space.gravity = (0, 1000)  # Set the gravity in the y-direction

# Create a static ground segment
ground_segment = pymunk.Segment(space.static_body, (0, height - 50), (width, height - 50), 5)
ground_segment.friction = 1.0
space.add(ground_segment)

# Create a dynamic rectangle
width_rect, height_rect = 50, 25
mass = 1
moment = pymunk.moment_for_box(mass, (width_rect, height_rect))
rectangle_body = pymunk.Body(mass, moment)
rectangle_body.position = (400, 300)
rectangle_shape = pymunk.Poly.create_box(rectangle_body, (width_rect, height_rect))
space.add(rectangle_body, rectangle_shape)

# Apply torque to make the rectangle spin
torque = 1000
rectangle_body.apply_impulse_at_local_point((torque, 0), (0, 0))

# Set up Pygame display for drawing
draw_options = pygame_util.DrawOptions(screen)

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Step the pymunk simulation
    dt = 1.0 / 60.0
    space.step(dt)

    # Clear the screen
    screen.fill((255, 255, 255))

    # Draw the objects
    space.debug_draw(draw_options)

    # Update the Pygame display
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
