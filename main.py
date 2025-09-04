import pygame
import sys
import os
import json
from collections import defaultdict

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("CYBER-AUTOPSY // TraumaScan v2.0.77")

# Cyberpunk 2077 color palette
NEON_PINK = (255, 0, 128)
NEON_BLUE = (0, 195, 255)
NEON_YELLOW = (255, 203, 0)
NEON_GREEN = (0, 255, 136)
NEON_PURPLE = (180, 0, 255)
DARK_PURPLE = (30, 5, 60)
DARK_BLUE = (10, 15, 40)
DARK_GRAY = (20, 20, 30)
LIGHT_CYBER = (170, 180, 190)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Colors for specific UI elements
BG_COLOR = DARK_BLUE
PANEL_COLOR = DARK_PURPLE
BUTTON_COLOR = DARK_GRAY
BUTTON_HOVER = (50, 40, 80)
TEXT_COLOR = LIGHT_CYBER
HIGHLIGHT_COLOR = NEON_BLUE
ACCENT_COLOR = NEON_PINK

# Fonts - trying to use a cyberpunk-style font, fallback to Arial
try:
    title_font = pygame.font.Font("assets/cyberpunk.ttf", 36)
    header_font = pygame.font.Font("assets/cyberpunk.ttf", 28)
    font = pygame.font.Font("assets/cyberpunk.ttf", 20)
    small_font = pygame.font.Font("assets/cyberpunk.ttf", 16)
except:
    print("Cyberpunk font not found, using system fonts")
    title_font = pygame.font.SysFont("Arial", 36, bold=True)
    header_font = pygame.font.SysFont("Arial", 28, bold=True)
    font = pygame.font.SysFont("Arial", 20)
    small_font = pygame.font.SysFont("Arial", 16)

# Diagram types with their file paths
DIAGRAMS = {
    "MALE FRONT": "assets/MFS.png",
    "FEMALE FRONT": "assets/FFS.png", 
    "SKELETON": "assets/S.png"
}

# Wound types with their asset paths
WOUND_TYPES = {
    "LACERATION": "assets/cut.png",
    "FISSURE": "assets/fissure.png",  # Changed from "Cut" to "Fissure"
    "GUNSHOT WOUND": "assets/gunshot.png",
    "FRACTURE": "assets/bruise.png",
    "EXPLOSION": "assets/explosion.png",
    "AMPUTATION": None  # No asset for amputation
}

# Wound colors for amputation and when images can't be loaded
WOUND_COLORS = {
    "LACERATION": NEON_PINK,
    "FISSURE": NEON_BLUE,
    "GUNSHOT WOUND": NEON_YELLOW,
    "FRACTURE": NEON_GREEN,
    "EXPLOSION": NEON_PURPLE,
    "AMPUTATION": (255, 100, 0)  # Orange for amputation
}

# JSON file for saving/loading data
DATA_FILE = "autopsy_data.json"

# Function to load images with error handling
def load_images():
    diagram_images = {}
    wound_images = {}
    
    # Load diagram images
    for name, path in DIAGRAMS.items():
        try:
            # Load and scale the image to fit the diagram area
            img = pygame.image.load(path)
            # Scale to fit the diagram area (keeping aspect ratio)
            img_width = 800
            img_height = 900
            img = pygame.transform.scale(img, (img_width, img_height))
            diagram_images[name] = img
        except:
            print(f"Error loading diagram image: {path}")
            # Create a placeholder if image can't be loaded
            placeholder = pygame.Surface((800, 900))
            placeholder.fill(DARK_GRAY)
            pygame.draw.rect(placeholder, NEON_BLUE, (0, 0, 800, 900), 2)
            text = font.render(f"IMAGE NOT FOUND: {path}", True, NEON_PINK)
            text_rect = text.get_rect(center=(400, 450))
            placeholder.blit(text, text_rect)
            diagram_images[name] = placeholder
    
    # Load wound images
    for name, path in WOUND_TYPES.items():
        if path:  # Skip amputation which has no asset
            try:
                img = pygame.image.load(path).convert_alpha()
                wound_images[name] = img
            except:
                print(f"Error loading wound image: {path}")
                wound_images[name] = None
    
    return diagram_images, wound_images

# Function to save data to JSON
def save_data(diagram, wounds):
    data = {
        "current_diagram": diagram,
        "wounds": []
    }
    
    for wound in wounds:
        wound_data = {
            "type": wound.wound_type,
            "position": wound.position,
            "size": wound.size
        }
        data["wounds"].append(wound_data)
    
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
    
    print(f"Data saved to {DATA_FILE}")

# Function to load data from JSON
def load_data():
    if not os.path.exists(DATA_FILE):
        return None, []
    
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        wounds = []
        for wound_data in data["wounds"]:
            wounds.append(Wound(
                wound_data["type"],
                wound_data["position"],
                wound_data["size"]
            ))
        
        return data["current_diagram"], wounds
    except:
        print(f"Error loading data from {DATA_FILE}")
        return None, []

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, icon=None, outline_color=NEON_BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.outline_color = outline_color
        self.is_hovered = False
        self.icon = icon
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=3)
        pygame.draw.rect(surface, self.outline_color, self.rect, 2, border_radius=3)
        
        # Draw cyberpunk-style corner accents
        corner_size = 8
        # Top-left
        pygame.draw.line(surface, self.outline_color, 
                        (self.rect.left, self.rect.top + corner_size),
                        (self.rect.left, self.rect.top), 2)
        pygame.draw.line(surface, self.outline_color, 
                        (self.rect.left + corner_size, self.rect.top),
                        (self.rect.left, self.rect.top), 2)
        # Top-right
        pygame.draw.line(surface, self.outline_color, 
                        (self.rect.right, self.rect.top + corner_size),
                        (self.rect.right, self.rect.top), 2)
        pygame.draw.line(surface, self.outline_color, 
                        (self.rect.right - corner_size, self.rect.top),
                        (self.rect.right, self.rect.top), 2)
        # Bottom-left
        pygame.draw.line(surface, self.outline_color, 
                        (self.rect.left, self.rect.bottom - corner_size),
                        (self.rect.left, self.rect.bottom), 2)
        pygame.draw.line(surface, self.outline_color, 
                        (self.rect.left + corner_size, self.rect.bottom),
                        (self.rect.left, self.rect.bottom), 2)
        # Bottom-right
        pygame.draw.line(surface, self.outline_color, 
                        (self.rect.right, self.rect.bottom - corner_size),
                        (self.rect.right, self.rect.bottom), 2)
        pygame.draw.line(surface, self.outline_color, 
                        (self.rect.right - corner_size, self.rect.bottom),
                        (self.rect.right, self.rect.bottom), 2)
        
        if self.icon:
            # Scale icon to fit button
            scaled_icon = pygame.transform.scale(self.icon, (self.rect.height - 10, self.rect.height - 10))
            icon_rect = scaled_icon.get_rect(center=self.rect.center)
            surface.blit(scaled_icon, icon_rect)
        else:
            text_surface = font.render(self.text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Wound:
    def __init__(self, wound_type, position, size=40):
        self.wound_type = wound_type
        self.position = position
        self.size = size
        
    def draw(self, surface, wound_images):
        if self.wound_type == "AMPUTATION":
            # Draw a circle with an X for amputation
            pygame.draw.circle(surface, WOUND_COLORS["AMPUTATION"], self.position, self.size)
            pygame.draw.line(surface, BLACK, 
                            (self.position[0] - self.size//2, self.position[1] - self.size//2),
                            (self.position[0] + self.size//2, self.position[1] + self.size//2), 3)
            pygame.draw.line(surface, BLACK, 
                            (self.position[0] + self.size//2, self.position[1] - self.size//2),
                            (self.position[0] - self.size//2, self.position[1] + self.size//2), 3)
        elif self.wound_type in wound_images and wound_images[self.wound_type]:
            # Draw the wound image at the correct size
            img = wound_images[self.wound_type]
            scaled_img = pygame.transform.scale(img, (self.size * 2, self.size * 2))
            img_rect = scaled_img.get_rect(center=self.position)
            surface.blit(scaled_img, img_rect)
        else:
            # Fallback to colored circle if image not available
            pygame.draw.circle(surface, WOUND_COLORS.get(self.wound_type, NEON_PINK), self.position, self.size)

class App:
    def __init__(self):
        self.current_diagram = "MALE FRONT"
        self.wounds = []
        self.selected_wound_type = "LACERATION"
        self.wound_size = 40
        self.fullscreen = False
        
        # Load diagram and wound images
        self.diagram_images, self.wound_images = load_images()
        
        # Load saved data
        saved_diagram, saved_wounds = load_data()
        if saved_diagram:
            self.current_diagram = saved_diagram
            self.wounds = saved_wounds
        
        # Calculate layout dimensions
        self.diagram_width = 800
        self.ui_panel_width = SCREEN_WIDTH - self.diagram_width
        self.button_width = 200
        self.button_height = 50
        self.button_margin = 15
        
        # Create UI elements
        self.create_ui_elements()
        
    def create_ui_elements(self):
        # Calculate positions based on current layout
        start_x = self.diagram_width + 20
        y_pos = 80
        
        # Create diagram selection buttons
        self.diagram_buttons = []
        for diagram_name in DIAGRAMS.keys():
            self.diagram_buttons.append(Button(
                start_x, y_pos, self.button_width, self.button_height, 
                diagram_name, BUTTON_COLOR, BUTTON_HOVER, outline_color=NEON_GREEN
            ))
            y_pos += self.button_height + self.button_margin
            
        # Create wound type selection buttons
        self.wound_buttons = []
        wound_start_x = start_x + self.button_width + 20
        y_pos = 80
        for wound_type in WOUND_TYPES.keys():
            icon = self.wound_images.get(wound_type) if wound_type != "AMPUTATION" else None
            self.wound_buttons.append(Button(
                wound_start_x, y_pos, self.button_width, self.button_height, 
                wound_type, BUTTON_COLOR, BUTTON_HOVER, icon, outline_color=NEON_PURPLE
            ))
            y_pos += self.button_height + self.button_margin
            
        # Create control buttons
        control_start_x = wound_start_x + self.button_width + 20
        y_pos = 80
        self.clear_button = Button(control_start_x, y_pos, self.button_width, self.button_height, 
                                  "CLEAR ALL", BUTTON_COLOR, BUTTON_HOVER, outline_color=NEON_PINK)
        y_pos += self.button_height + self.button_margin
        
        self.save_button = Button(control_start_x, y_pos, self.button_width, self.button_height, 
                                 "SAVE", BUTTON_COLOR, BUTTON_HOVER, outline_color=NEON_YELLOW)
        y_pos += self.button_height + self.button_margin
        
        self.load_button = Button(control_start_x, y_pos, self.button_width, self.button_height, 
                                 "LOAD", BUTTON_COLOR, BUTTON_HOVER, outline_color=NEON_BLUE)
        y_pos += self.button_height + self.button_margin
        
        # Create erase mode toggle
        self.erase_button = Button(control_start_x, y_pos, self.button_width, self.button_height, 
                                  "ERASE: OFF", BUTTON_COLOR, BUTTON_HOVER, outline_color=NEON_PINK)
        self.erase_mode = False
        y_pos += self.button_height + self.button_margin
        
        # Create wound size controls
        self.size_up_button = Button(control_start_x, y_pos, self.button_width//2 - 5, self.button_height, 
                                    "SIZE +", BUTTON_COLOR, BUTTON_HOVER, outline_color=NEON_GREEN)
        self.size_down_button = Button(control_start_x + self.button_width//2 + 5, y_pos, 
                                      self.button_width//2 - 5, self.button_height, 
                                      "SIZE -", BUTTON_COLOR, BUTTON_HOVER, outline_color=NEON_GREEN)
        y_pos += self.button_height + self.button_margin
        
        # Create fullscreen toggle
        self.fullscreen_button = Button(control_start_x, y_pos, self.button_width, self.button_height, 
                                       "FULLSCREEN", BUTTON_COLOR, BUTTON_HOVER, outline_color=NEON_BLUE)
        
    def draw_cyberpunk_ui(self):
        # Draw background
        screen.fill(BG_COLOR)
        
        # Draw diagram area with cyberpunk border
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, self.diagram_width, SCREEN_HEIGHT))
        pygame.draw.rect(screen, NEON_BLUE, (0, 0, self.diagram_width, SCREEN_HEIGHT), 3)
        
        # Draw UI panel with cyberpunk style
        pygame.draw.rect(screen, PANEL_COLOR, (self.diagram_width, 0, self.ui_panel_width, SCREEN_HEIGHT))
        pygame.draw.line(screen, NEON_PURPLE, (self.diagram_width, 0), (self.diagram_width, SCREEN_HEIGHT), 3)
        
        # Draw cyberpunk grid lines in the background
        for i in range(0, SCREEN_WIDTH, 20):
            alpha = 20 if i % 100 != 0 else 40
            grid_surf = pygame.Surface((1, SCREEN_HEIGHT), pygame.SRCALPHA)
            grid_surf.fill((NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], alpha))
            screen.blit(grid_surf, (i, 0))
            
        for i in range(0, SCREEN_HEIGHT, 20):
            alpha = 20 if i % 100 != 0 else 40
            grid_surf = pygame.Surface((SCREEN_WIDTH, 1), pygame.SRCALPHA)
            grid_surf.fill((NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], alpha))
            screen.blit(grid_surf, (0, i))
        
        # Draw title with cyberpunk style
        title = title_font.render("CYBER-AUTOPSY // TraumaScan v2.0.77", True, NEON_BLUE)
        screen.blit(title, (self.diagram_width + 20, 20))
        
        # Draw section headers with cyberpunk style
        headers = [
            ("BODY MODEL SELECT", self.diagram_width + 20, 50, NEON_GREEN),
            ("TRAUMA TYPE", self.diagram_width + 20 + self.button_width + 20, 50, NEON_PURPLE),
            ("CONTROL SYSTEMS", self.diagram_width + 20 + 2*(self.button_width + 20), 50, NEON_YELLOW)
        ]
        
        for text, x, y, color in headers:
            header = header_font.render(text, True, color)
            screen.blit(header, (x, y))
        
        # Draw the current diagram
        screen.blit(self.diagram_images[self.current_diagram], (0, 0))
        
        # Draw wounds
        for wound in self.wounds:
            wound.draw(screen, self.wound_images)
            
        # Draw buttons
        for button in self.diagram_buttons:
            button.draw(screen)
            
        for button in self.wound_buttons:
            button.draw(screen)
            
        self.clear_button.draw(screen)
        self.save_button.draw(screen)
        self.load_button.draw(screen)
        self.erase_button.draw(screen)
        self.size_up_button.draw(screen)
        self.size_down_button.draw(screen)
        self.fullscreen_button.draw(screen)
        
        # Draw wound size
        size_text = font.render(f"TRAUMA SIZE: {self.wound_size}", True, NEON_GREEN)
        size_text_x = self.diagram_width + 20 + 2*(self.button_width + 20)
        size_text_y = self.fullscreen_button.rect.bottom + 20
        screen.blit(size_text, (size_text_x, size_text_y))
        
        # Draw wound statistics in a cyberpunk style panel
        stats_panel_y = max(
            self.diagram_buttons[-1].rect.bottom if self.diagram_buttons else 0,
            self.wound_buttons[-1].rect.bottom if self.wound_buttons else 0,
            size_text_y + 40
        ) + 30
        
        # Draw stats panel
        stats_panel_height = 200
        pygame.draw.rect(screen, DARK_GRAY, (self.diagram_width + 20, stats_panel_y, 
                                           self.ui_panel_width - 40, stats_panel_height), border_radius=5)
        pygame.draw.rect(screen, NEON_BLUE, (self.diagram_width + 20, stats_panel_y, 
                                           self.ui_panel_width - 40, stats_panel_height), 2, border_radius=5)
        
        stats_title = header_font.render("TRAUMA ANALYSIS", True, NEON_PINK)
        screen.blit(stats_title, (self.diagram_width + 30, stats_panel_y + 10))
        
        # Count wounds by type
        wound_counts = defaultdict(int)
        for wound in self.wounds:
            wound_counts[wound.wound_type] += 1
        
        # Draw stats in columns
        col1_x = self.diagram_width + 30
        col2_x = col1_x + 200
        col3_x = col2_x + 200
        
        stats_y = stats_panel_y + 50
        col = 1
        for i, wound_type in enumerate(WOUND_TYPES):
            count = wound_counts[wound_type]
            if count > 0:
                text = f"{wound_type}: {count}"
                color = WOUND_COLORS.get(wound_type, TEXT_COLOR)
                text_surface = font.render(text, True, color)
                
                if col == 1:
                    screen.blit(text_surface, (col1_x, stats_y))
                    col = 2
                elif col == 2:
                    screen.blit(text_surface, (col2_x, stats_y))
                    col = 3
                else:
                    screen.blit(text_surface, (col3_x, stats_y))
                    col = 1
                    stats_y += 30
                
                # If we're still in the same column, move down
                if col != 1:
                    stats_y += 30
        
        # Draw total wounds
        total_text = font.render(f"TOTAL TRAUMAS: {len(self.wounds)}", True, NEON_YELLOW)
        screen.blit(total_text, (self.diagram_width + 30, stats_panel_y + stats_panel_height - 30))
        
        # Draw instructions in a cyberpunk terminal style
        instructions = [
            "> SYSTEM READY",
            "> SELECT BODY MODEL AND TRAUMA TYPE",
            "> CLICK ON DIAGRAM TO MARK TRAUMA",
            "> TOGGLE ERASE MODE TO REMOVE MARKS",
            "> ADJUST TRAUMA SIZE AS NEEDED",
            "> SAVE/LOAD ANALYSIS DATA"
        ]
        
        instructions_y = stats_panel_y + stats_panel_height + 20
        for i, instruction in enumerate(instructions):
            color = NEON_GREEN if i == 0 else TEXT_COLOR
            text_surface = small_font.render(instruction, True, color)
            screen.blit(text_surface, (self.diagram_width + 30, instructions_y))
            instructions_y += 25
            
        # Draw cyberpunk-style scan lines
        scan_line = pygame.Surface((SCREEN_WIDTH, 1), pygame.SRCALPHA)
        scan_line.fill((NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], 30))
        scan_y = pygame.time.get_ticks() // 10 % SCREEN_HEIGHT
        screen.blit(scan_line, (0, scan_y))
        
    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Save data before quitting
                    save_data(self.current_diagram, self.wounds)
                    running = False
                    
                # Check diagram selection buttons
                for i, button in enumerate(self.diagram_buttons):
                    if button.is_clicked(mouse_pos, event):
                        self.current_diagram = list(DIAGRAMS.keys())[i]
                
                # Check wound type selection buttons
                for i, button in enumerate(self.wound_buttons):
                    if button.is_clicked(mouse_pos, event):
                        self.selected_wound_type = list(WOUND_TYPES.keys())[i]
                
                # Check control buttons
                if self.clear_button.is_clicked(mouse_pos, event):
                    self.wounds = []
                
                if self.save_button.is_clicked(mouse_pos, event):
                    save_data(self.current_diagram, self.wounds)
                
                if self.load_button.is_clicked(mouse_pos, event):
                    saved_diagram, saved_wounds = load_data()
                    if saved_diagram:
                        self.current_diagram = saved_diagram
                        self.wounds = saved_wounds
                
                # Check erase button
                if self.erase_button.is_clicked(mouse_pos, event):
                    self.erase_mode = not self.erase_mode
                    self.erase_button.text = f"ERASE: {'ON' if self.erase_mode else 'OFF'}"
                
                # Check size buttons
                if self.size_up_button.is_clicked(mouse_pos, event):
                    self.wound_size = min(80, self.wound_size + 5)
                if self.size_down_button.is_clicked(mouse_pos, event):
                    self.wound_size = max(20, self.wound_size - 5)
                
                # Check fullscreen button
                if self.fullscreen_button.is_clicked(mouse_pos, event):
                    self.toggle_fullscreen()
                
                # Add or remove wounds
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if click is on the diagram area
                    if mouse_pos[0] < self.diagram_width:
                        if self.erase_mode:
                            # Remove wounds that are clicked on
                            self.wounds = [wound for wound in self.wounds 
                                         if not (abs(wound.position[0] - mouse_pos[0]) < wound.size + 5 and
                                                 abs(wound.position[1] - mouse_pos[1]) < wound.size + 5)]
                        else:
                            # Add a new wound
                            self.wounds.append(Wound(self.selected_wound_type, mouse_pos, self.wound_size))
            
            # Update button hover states
            all_buttons = (self.diagram_buttons + self.wound_buttons + 
                          [self.clear_button, self.save_button, self.load_button,
                           self.erase_button, self.size_up_button, self.size_down_button,
                           self.fullscreen_button])
            
            for button in all_buttons:
                button.check_hover(mouse_pos)
            
            # Draw the cyberpunk UI
            self.draw_cyberpunk_ui()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        global screen, SCREEN_WIDTH, SCREEN_HEIGHT
        
        if self.fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
        else:
            screen = pygame.display.set_mode((1600, 900))
            SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 900
        
        # Recreate UI elements with new dimensions
        self.diagram_width = 800 if not self.fullscreen else int(SCREEN_WIDTH * 0.6)
        self.ui_panel_width = SCREEN_WIDTH - self.diagram_width
        self.create_ui_elements()
        
        # Scale diagram images to new size
        for name, img in self.diagram_images.items():
            self.diagram_images[name] = pygame.transform.scale(img, (self.diagram_width, SCREEN_HEIGHT))

if __name__ == "__main__":
    app = App()
    app.run()