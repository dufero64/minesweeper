import pygame
import random

pygame.init()
WIDTH, HEIGHT = 600, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

GRID_SIZE = 10
MINE_COUNT = 20
remaining_mines = MINE_COUNT  
start_time = pygame.time.get_ticks()  
final_time = None 

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False 
        self.surrounding_mines = 0

def is_valid_pos(row, col):
    return 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE

def reveal_adjacent(grid, row, col):
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]
    grid[row][col].is_revealed = True
    
    if grid[row][col].surrounding_mines == 0:
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            if is_valid_pos(new_row, new_col) and not grid[new_row][new_col].is_revealed:
                reveal_adjacent(grid, new_row, new_col)

def count_surrounding_mines(grid, row, col):
    surrounding = [
        (-1, -1), (-1, 0), (-1, 1),
         (0, -1),          (0, 1),
         (1, -1), (1, 0), (1, 1),
    ]
    count = 0
    for r_offset, c_offset in surrounding:
        r, c = row + r_offset, col + c_offset
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and grid[r][c].is_mine:
            count += 1
    return count

def calculate_numbers(grid):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if not grid[row][col].is_mine:
                grid[row][col].surrounding_mines = count_surrounding_mines(grid, row, col)

def create_grid():
    grid = [[Cell(row, col) for col in range(GRID_SIZE)] for row in range(GRID_SIZE)]
    
    all_positions = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
    mine_positions = random.sample(all_positions, MINE_COUNT)
    
    for (r, c) in mine_positions:
        grid[r][c].is_mine = True
        
    calculate_numbers(grid)
    return grid

def draw_grid(window, grid):
    cell_width = WIDTH // GRID_SIZE
    cell_height = HEIGHT // GRID_SIZE
    font = pygame.font.Font(None, 36)
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            cell = grid[row][col]
            color = WHITE if cell.is_revealed else GRAY
            
            pygame.draw.rect(window, color, (col*cell_width, row*cell_height, cell_width, cell_height))
            if cell.is_revealed:
                if cell.is_mine:
                    pygame.draw.circle(window, BLACK, (col*cell_width + cell_width//2, row*cell_height + cell_height//2), cell_width//2 - 5)
                elif cell.surrounding_mines > 0:
                    text = font.render(str(cell.surrounding_mines), True, BLACK)
                    window.blit(text, (col*cell_width + cell_width//3, row*cell_height + cell_height//4))
            elif cell.is_flagged:  # New condition to draw a flag on flagged cells
                pygame.draw.polygon(window, (255, 0, 0), [(col*cell_width + cell_width//2, row*cell_height + cell_height//4),
                                                          (col*cell_width + cell_width//4, row*cell_height + 3*cell_height//4),
                                                          (col*cell_width + 3*cell_width//4, row*cell_height + 3*cell_height//4)])
                
            pygame.draw.rect(window, BLACK, (col*cell_width, row*cell_height, cell_width, cell_height), 1)

def handle_click(pos, grid, button):
    global remaining_mines
    cell_width = WIDTH // GRID_SIZE
    cell_height = HEIGHT // GRID_SIZE
    x, y = pos
    col = x // cell_width
    row = y // cell_height
    
    cell = grid[row][col]
    if button == 1 and not cell.is_flagged:  
        cell.is_revealed = True
        if cell.is_mine:
            for r in grid:
                for c in r:
                    c.is_revealed = True
            return True
        elif cell.surrounding_mines == 0:
            reveal_adjacent(grid, row, col)
    elif button == 3:  # Right mouse button
        cell.is_flagged = not cell.is_flagged
        remaining_mines = remaining_mines - 1 if cell.is_flagged else remaining_mines + 1
    return False

def draw_text(window, text, size, color, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    window.blit(text_surface, (x, y))

def check_win(grid):
    return all((cell.is_revealed and not cell.is_mine) or cell.is_mine for row in grid for cell in row)

def main():
    global remaining_mines, final_time 
    clock = pygame.time.Clock()
    grid = create_grid()
    run = True
    game_over = False
    player_wins = False  
    
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not (game_over or player_wins): 
                game_over = handle_click(event.pos, grid, event.button)  

        if not player_wins and not game_over and check_win(grid):
            player_wins = True  
            final_time = pygame.time.get_ticks()

        draw_grid(WINDOW, grid)
        
        draw_text(WINDOW, f"{remaining_mines}", 36, (255, 0, 0), 10, 10)
        
        if game_over or player_wins:
            if final_time is None:
                final_time = pygame.time.get_ticks()  
            elapsed_time = (final_time - start_time) // 1000
        else:
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        
        draw_text(WINDOW, f"Time: {elapsed_time}s", 36, (255, 0, 0), WIDTH - 150, 10)
        
        if game_over:
            draw_text(WINDOW, "Game Over", 72, (255, 0, 0), WIDTH // 2 - 100, HEIGHT // 2 - 36)
        elif player_wins:
            draw_text(WINDOW, "You Win!", 72, (0, 255, 0), WIDTH // 2 - 100, HEIGHT // 2 - 36)

        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()