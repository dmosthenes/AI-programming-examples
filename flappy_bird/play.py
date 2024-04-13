import pygame
import sys
from bird_and_pipe import Bird, Pipe

def run():

    pygame.init()

    width = 800
    height = 600

    black = (0,0,0)

    FPS = 60
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("flappy bird with neural net")

    # Set pipe generation interval
    INTERVAL = 45

    generation = 0

    sample_size = 50

    dead_birds = []

    max_pipes = 0

    font = pygame.font.Font(None, 36)

    while True:

        frame_counter = 0

        # Initialise game objects

        # If first generation, initialise random birds
        if generation == 0:

            birds = [Bird(screen) for _ in range(sample_size * 10)]

        # If later generation, mutate best birds
        else:

            # Sort birds by highest score
            best_birds = sorted(dead_birds, key=lambda x: x.score, reverse=True)

            print(f"Generation: {generation}, Max Distance: {best_birds[0].score}")

            birds = []

            for bird in best_birds[:10]:


                for _ in range(sample_size):

                    birds.extend([Bird(screen, bird, 0.1)])

                    assert birds[0].score == 0

            dead_birds = []

        assert birds != []

        pipes = []

        # Store reference to the pipe closest to
        # and moving towards player
        current_pipe = None
        bird_x_pos = birds[0].x
        max_pipe_dst = screen.get_width() - bird_x_pos

        generation += 1

        pipe_num = 0

        # Inner while loop runs a given generation
        while birds:

            frame_counter += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill(black)

            # Draw max pipes
            pipe_counter_surface = font.render(f"Max pipe: {str(max_pipes)}", True, (255,255,255))
            pipe_counter_rect = pipe_counter_surface.get_rect()
            pipe_counter_rect.topright = (screen.get_width() * 0.9, screen.get_height() * 0.1)
            screen.blit(pipe_counter_surface, pipe_counter_rect)

            # Draw current generation
            generation_surface = font.render(f"Generation: {str(generation)}", True, (255,255,255))
            generation_rect = generation_surface.get_rect()
            generation_rect.topleft = (screen.get_width() * 0.1, screen.get_height() * 0.1)
            screen.blit(generation_surface, generation_rect)

            # Draw current bird count
            bird_count_surface = font.render(f"Alive birds: {len(birds)}", True, (255,255,255))
            bird_count_rect = bird_count_surface.get_rect()
            bird_count_rect.bottomright = (screen.get_width() * 0.9, screen.get_height() * 0.9)
            screen.blit(bird_count_surface, bird_count_rect)

            clock.tick(FPS)       

            # Add a new pipe every second second
            if frame_counter % INTERVAL == 0 or len(pipes) == 0:
                pipes.append(Pipe(screen, pipe_num))
                pipe_num += 1

                if pipe_num > max_pipes:
                    max_pipes = pipe_num

            # Initialise current pipe
            if not current_pipe and len(pipes) > 0:
                current_pipe = pipes[0]

            # Update current pipe if it has passed the bird
            if current_pipe.toplft[0] + pipes[0].width < bird_x_pos:
                current_pipe = pipes[1]
                
                # Check if 0th pipe is offscreen
                if pipes[0].toplft[0] + pipes[0].width <= 0:
                    pipes = pipes[1:]
 
            # Draw all pipes
            for pipe in pipes:
                pipe.draw()
                pipe.update()

            removed_birds = []

            for bird in birds:

                if current_pipe:

                    # Decide whether to jump
                    bird.choice(current_pipe.toplft[0] - bird.x / max_pipe_dst,
                                current_pipe.gapy / height,
                                current_pipe.gapy + current_pipe.gapdst / height)

                    # Check boundary and collision
                    if bird.out_of_bounds() or bird.collides(current_pipe):
                        bird.set_score(pipe_num)
                        removed_birds.append(bird)
                        # birds.remove(bird)
                        
                bird.update()
                bird.draw()

            # Remove any dead birds
            for rm_bird in removed_birds:
                if rm_bird in birds:
                    birds.remove(rm_bird)
            
            dead_birds.extend(removed_birds)
                
            pygame.display.flip()


def main():

    run()

if __name__ == "__main__":
    main()