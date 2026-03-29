# Sauna Controller Home Assistant Integration

This repository provides a Home Assistant integration for the VectorForge Controls Sauna Controller.

## Features
- Device discovery via mDNS/zeroconf (`_http._tcp.local.` + name `sauna-controller*`)
- Climate entity for temperature/setpoint
- Sensors for state, temperature, fault code, etc.
- Switches and buttons for controls

## Installation (HACS)
1. Install HACS (if not installed) in Home Assistant.
2. In HACS, choose "Integrations" → "Explore" → "Custom repositories".
3. Add this repository URL with type `integration`.
4. Install "Sauna Controller" and restart Home Assistant.

## Configuration
- If zeroconf discovery works, Home Assistant prompts automatically.
- Manual setup:
  - Settings -> Devices & Services -> Add Integration -> Sauna Controller
  - Enter `host`, `port`, optional `name`.

## Zeroconf requirements
Your sauna device must advertise an mDNS service using:
- `service type`: `_http._tcp.local.`
- `service name`: `sauna-controller*`

and respond to HTTP GET `/api/state` on that host/port.

## Developer notes
- `custom_components/sauna_controller/manifest.json` includes `config_flow` and `zeroconf`.
- `config_flow.py` includes `async_step_zeroconf`, `async_step_zeroconf_confirm`, and host-state validation.

## Support
- Issues: https://github.com/vectorforgecontrols/sauna-controller-ha/issues
