"""Constants for the Sauna Controller integration."""

DOMAIN = "sauna_controller"
MANUFACTURER = "VectorForge Controls"
MODEL = "Sauna Controller"

DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 5  # seconds

# API endpoints
API_STATE = "/api/state"
API_SETPOINT = "/api/setpoint"
API_RESET_FAULT = "/api/reset_fault"

# WebSocket
WS_PATH = "/ws"

# State values
STATE_IDLE = "IDLE"
STATE_HEATING = "HEATING"
STATE_DOOR_OPEN = "DOOR_OPEN"
STATE_FAULT = "FAULT"
STATE_PROVISIONING = "PROVISIONING"

# Fault flags
FAULT_NO_RISE = 0x01
FAULT_MAX_RUNTIME = 0x02
FAULT_SENSOR_ERROR = 0x04

FAULT_DESCRIPTIONS = {
    FAULT_NO_RISE: "No temperature rise",
    FAULT_MAX_RUNTIME: "Max runtime exceeded",
    FAULT_SENSOR_ERROR: "Sensor error",
}

# Setpoint limits (°F)
SETPOINT_MIN = 60.0
SETPOINT_MAX = 200.0
SETPOINT_STEP = 1.0
SETPOINT_DEFAULT = 160.0

# Config entry keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_NAME = "name"
