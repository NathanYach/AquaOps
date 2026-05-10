class Zone:
    def __init__(
        self,
        zone_id,
        zone_display_name,
        zone_enabled,
        environment,
        soil,
        hardware,
        watering,
    ):
        self.zone_id = zone_id
        self.zone_display_name = zone_display_name
        self.zone_enabled = zone_enabled

        self.environment = environment
        self.soil = soil
        self.hardware = hardware
        self.watering = watering