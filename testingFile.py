import pygame
import cProfile

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
profiler = cProfile.Profile()
profiler.enable()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            profiler.print_stats(sort='tottime')
            running = False

    # Clear the screen
    screen.fill((0, 0, 0))

    # Update the zoom factor (for zooming in, you can increase it)
    zoom_factor += 0.001  # Adjust this value as needed

    # Calculate the new size based on the zoom factor
    current_size = (int(original_size[0] * zoom_factor), int(original_size[1] * zoom_factor))

    # Resize the animated surface
    zoomed_surface = pygame.transform.scale(animated_surface, current_size)

    # Blit the zoomed surface onto the screen
    screen.blit(zoomed_surface, (100, 100))  # Adjust position as needed

    # Update the display
    pygame.display.flip()

pygame.quit()
