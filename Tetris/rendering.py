import pygame

# I'll probably add more functions for pretty rendering
def draw_rect_border(surface, color, rect, width, border_color):
    pygame.draw.rect(surface, color, rect)
    offset = (-(width // 2), -(width // 2))
    pygame.draw.lines(
        surface, 
        border_color, 
        True, 
        (_add_tuples(rect.topleft, offset), 
        _add_tuples(rect.bottomleft, offset), 
        _add_tuples(rect.bottomright, offset), 
        _add_tuples(rect.topright, offset)),
        width
    )

def _add_tuples(t1, t2):
    return [t1[i] + t2[i] for i in range(min(len(t1), len(t2)))]
        
