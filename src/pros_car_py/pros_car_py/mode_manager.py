import urwid
import os
import csv
from pros_car_py.base_mode import BaseMode, register_mode

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Path to the CSV configuration file
csv_path = os.path.join(current_dir, "config", "modes.csv")

class ModeTemplate(BaseMode):
    """Universal mode template that handles all mode types based on CSV configuration"""

    def __init__(self, app, config):
        super().__init__(app)
        # Load configuration
        self.mode_id = config['mode_id']
        self.display_name = config['display_name']
        self.controller = config['controller']
        self.method = config['method']
        self.has_quit_handler = config['has_quit_handler'].lower() == 'true'
        self.description = config['description']

        # Parse submodes
        if config['submodes'].lower() == 'none':
            self.submodes = []
        else:
            self.submodes = config['submodes'].split(';')

        # Parameter type conversion
        self.param_type = config['param_type']

    def enter(self):
        """Entry point for the mode"""
        # If we have submodes, show selection screen
        if self.submodes:
            self.app.horizontal_select(self.submodes, self.handle_submode_select)
        else:
            # Direct mode without submodes (like vehicle control)
            text = urwid.Text(f"{self.display_name}\n{self.description}\nPress 'q' to return to main menu.")
            filler = urwid.Filler(text, valign="top")
            self.app.loop.widget = filler
            self.app.loop.unhandled_input = self.handle_direct_input

    def handle_direct_input(self, key):
        """Handle input for modes without submodes"""
        # Get the controller object from app
        controller = getattr(self.app, self.controller)

        if key == "q":
            # Call method with quit key
            getattr(controller, self.method)(key)
            self.app.main_menu()
        else:
            # Call method with the key
            getattr(controller, self.method)(key)

    def handle_submode_select(self, submode):
        """Handle submode selection"""
        def on_key(key):
            # Get controller
            controller = getattr(self.app, self.controller)

            # Convert parameter if needed
            param = submode
            if self.param_type == 'int':
                param = int(submode)

            # Call the appropriate method
            getattr(controller, self.method)(param, key)

            # Special handling for quit in certain modes
            if key == "q" and self.has_quit_handler:
                getattr(controller, self.method)(param, key=key)

        self.show_submode_screen(
            message=f"{self.display_name}: Submode {submode}\n{self.description}\nPress 'q' to go back.",
            on_key=on_key
        )

# Function to load modes from CSV and register them
def load_and_register_modes():
    """Load modes from CSV and register them"""
    from pros_car_py.base_mode import MODE_REGISTRY

    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip comment lines
                if row['mode_id'].startswith('#'):
                    continue

                # Create factory function that captures the config
                def create_mode(app, config=row):
                    return ModeTemplate(app, config)

                # Register the mode
                MODE_REGISTRY[row['mode_id']] = (row['display_name'], create_mode)

        return len(MODE_REGISTRY)

    except Exception as e:
        print(f"Error loading modes from CSV: {e}")
        return 0
