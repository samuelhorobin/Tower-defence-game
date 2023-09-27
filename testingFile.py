import pygame
<<<<<<< HEAD
import cProfile
=======
>>>>>>> 86ed09644d3b544a50098dabc0ac0306d2f0cc97

# Initialize Pygame
pygame.init()

# Create a display window
screen = pygame.display.set_mode((800, 600))

# Create an animated surface (replace this with your own animation logic)
def create_animated_surface():
    animated_surface = pygame.Surface((200, 200))
    animated_surface.fill((255, 0, 0))  # Fill with red for visibility
    # Add your animation logic here
    return animated_surface

animated_surface = create_animated_surface()
original_size = animated_surface.get_size()
zoom_factor = 1.0  # Initial zoom factor

running = True
<<<<<<< HEAD
profiler = cProfile.Profile()
profiler.enable()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            profiler.print_stats(sort='tottime')
=======
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
>>>>>>> 86ed09644d3b544a50098dabc0ac0306d2f0cc97
            running = False

    # Clear the screen
    screen.fill((0, 0, 0))

    # Update the zoom factor (for zooming in, you can increase it)
<<<<<<< HEAD
    zoom_factor += 0.001  # Adjust this value as needed
=======
    zoom_factor += 0.01  # Adjust this value as needed
>>>>>>> 86ed09644d3b544a50098dabc0ac0306d2f0cc97

    # Calculate the new size based on the zoom factor
    current_size = (int(original_size[0] * zoom_factor), int(original_size[1] * zoom_factor))

    # Resize the animated surface
    zoomed_surface = pygame.transform.scale(animated_surface, current_size)

    # Blit the zoomed surface onto the screen
    screen.blit(zoomed_surface, (100, 100))  # Adjust position as needed

    # Update the display
    pygame.display.flip()

pygame.quit()
