from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import STATE_UNKNOWN, DEVICE_CLASS_MONETARY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity import Entity
from homeassistant import config_entries

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    lending_entities = []

    api_client = hass.data[DOMAIN][entry.entry_id]

    # Utilisez api_client pour créer des entités ou effectuer d'autres opérations.
    lendings_data = await api_client.lendings()

    for lending_data in lendings_data:
        lending_entity = MeriaLendingSensor(entry.entry_id, lending_data)
        lending_entities.append(lending_entity)

    async_add_entities(lending_entities, True)


class MeriaLendingSensor(Entity):
    def __init__(self, entry_id, lending_data) -> None:
        self._entry_id = entry_id
        self._lending_data = lending_data
        self._state = STATE_UNKNOWN

    @property
    def name(self):
        return f"Lending {self._lending_data['currencyCode']}"

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return f"lending_{self._lending_data['currencyCode']}"

    @property
    def device_class(self):
        return DEVICE_CLASS_MONETARY

    @property
    def unit_of_measurement(self):
        return self._lending_data["currencyCode"]

    async def async_update(self):
        api_client = self.hass.data[DOMAIN][self._entry_id]

        try:
            # Appelez la méthode pour obtenir les dernières données du prêt
            new_data = await api_client.lending(self._lending_data["currencyCode"])

            # Mettez à jour l'état de l'entité en fonction des nouvelles données
            self._state = new_data["amount"]

        except Exception as e:  # pylint: disable=broad-except
            # Gérer les erreurs de mise à jour ici (par exemple, journaliser l'erreur)
            self._state = STATE_UNKNOWN
