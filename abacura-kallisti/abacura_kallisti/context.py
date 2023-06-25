import os

from abacura.plugins import ContextProvider
from abacura_kallisti.atlas.world import World
from abacura_kallisti.plugins.msdp import TypedMSDP
from abacura_kallisti.plugins.queue import QueueManager
from abacura.config import Config
from abacura_kallisti.mud.player import PlayerCharacter
from abacura_kallisti.atlas.location import LocationList


class LOKContextProvider(ContextProvider):
    def __init__(self, config: Config, session_name: str):
        data_dir = config.data_directory(session_name)
        super().__init__(config, session_name)
        self.world: World = World(os.path.join(data_dir, "world.db"))
        self.msdp: TypedMSDP = TypedMSDP()
        self.cq: QueueManager = QueueManager()
        self.pc: PlayerCharacter = PlayerCharacter()
        self.locations: LocationList = LocationList(os.path.join(data_dir, "locations.toml"))

    def get_injections(self) -> dict:
        lok_context = {"world": self.world, "msdp": self.msdp, "cq": self.cq, "pc": self.pc, 
                       "locations": self.locations}
        return lok_context
