# base_mode.py
import urwid
import csv
import os

# Global registry for all modes
MODE_REGISTRY = {}

def register_mode(mode_id, display_name):
    """Decorator to register modes"""
    def decorator(cls):
        MODE_REGISTRY[mode_id] = (display_name, cls)
        return cls
    return decorator

class BaseMode:
    """Base class for all operation modes"""

    def __init__(self, app):
        """
        app: 這裡會是 ModeApp 的實例，裡面含有
             - loop (urwid.MainLoop)
             - 其他 Controller (car_controller, arm_controller, ...)
             - 也有一些輔助方法 (如 horizontal_select、main_menu 等)
        """
        self.app = app

    def enter(self):
        """Called when entering this mode"""
        raise NotImplementedError("Subclasses must implement enter()")

    def exit(self):
        """Called when exiting this mode"""
        pass

    def show_submode_screen(self, message, on_key):
        """Helper to show a submode screen with key handler"""
        text = urwid.Text(message)
        filler = urwid.Filler(text, valign="top")

        self.app.loop.widget = filler
        self.app.loop.unhandled_input = lambda key: self.handle_submode_key(key, on_key)

    def handle_submode_key(self, key, on_key):
        """Process keys for submode screens"""
        if key == "q":
            self.app.main_menu()
        else:
            on_key(key)

class GenericMode(BaseMode):
    """Template-based mode that loads configuration from CSV data"""

    def __init__(self, app, config):
        super().__init__(app)
        self.mode_id = config["mode_id"]
        self.display_name = config["display_name"]
        self.controller_name = config["controller_name"]
        self.method_name = config["method_name"]
        self.param_type = config["param_type"]
        self.description = config["description"]

        # Parse submodes
        if config["submodes"] == "none":
            self.submodes = []
        else:
            self.submodes = config["submodes"].split(";")

    def enter(self):
        """Handle mode entry based on configuration"""
        # If we have submodes, show submode selection
        if self.submodes:
            self.app.horizontal_select(self.submodes, self.handle_submode_select)
        else:
            # Direct input mode (like vehicle control)
            text = urwid.Text(f"{self.display_name}\n{self.description}\nPress 'q' to return to main menu.")
            filler = urwid.Filler(text, valign="top")
            self.app.loop.widget = filler
            self.app.loop.unhandled_input = self.handle_direct_input

    def handle_direct_input(self, key):
        """Handle keys for direct input modes"""
        if key == "q":
            # Get the controller from the app
            controller = getattr(self.app, self.controller_name)
            # Call the method
            getattr(controller, self.method_name)(key)
            self.app.main_menu()
        else:
            controller = getattr(self.app, self.controller_name)
            getattr(controller, self.method_name)(key)

    def handle_submode_select(self, submode):
        """Handle submode selection based on configuration"""
        def on_key(key):
            # Get the controller from the app
            controller = getattr(self.app, self.controller_name)

            # Convert parameter if needed
            param = submode
            if self.param_type == "int":
                param = int(submode)

            # Call the appropriate method with the converted parameter
            getattr(controller, self.method_name)(param, key)

            # Handle 'q' key special case for some modes
            if key == "q":
                if self.mode_id.startswith("mode_auto"):
                    getattr(controller, self.method_name)(param, key="q")

        # Show the submode screen
        self.show_submode_screen(
            message=f"{self.display_name}: Submode {submode}\n{self.description}\nPress 'q' to go back.",
            on_key=on_key,
        )

# Dummy placeholder for backward compatibility
def load_modes_from_csv(filepath):
    """Legacy function - implementation moved to mode_manager.py"""
    return {}
