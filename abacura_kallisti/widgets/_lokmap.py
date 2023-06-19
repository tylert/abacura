"""Kallisti Map Widget"""
from __future__ import annotations

import random
from typing import TYPE_CHECKING, Optional

from textual import log
from textual.app import ComposeResult
from textual.events import Resize
from textual.containers import Container, Center, Middle
from textual.widget import Widget
from textual.widgets import Static

from abacura.widgets.resizehandle import ResizeHandle

if TYPE_CHECKING:
    from abacura.mud.session import Session
    from abacura_kallisti.atlas.world import World

class MapPoint():
    def __init__(self, room: str, x: int, y: int):
        self.room = room
        self.x = x
        self.y = y

class LOKMap(Container):

    world: Optional[World] = None

    def __init__(self, resizer: bool=True, id: str=""):
        super().__init__()
        self.id=id
        self.resizer: bool = resizer
        self.map = Static(id="minimap", classes="lokmap", expand=True)


    def compose(self) -> ComposeResult:
        yield self.map
        if self.resizer:
            yield ResizeHandle(self, "bottom")

    def on_mount(self) -> None:
        pass

    def generate_map(self) -> None:
        #START_ROOM='3001'
        START_ROOM='3001'
        BFS = []
       
        H = self.content_size.height - 1
        W = self.content_size.width
        cH = int(H/3)
        cW = int(W/5)
        cenH = int(cH/2)
        cenW = int(cW/2)

        # Y is first in the matrix!
        Matrix = [['' for x in range(cW)] for y in range(cH)]
        room = self.world.rooms[START_ROOM]
        visited = {}

        BFS.append(MapPoint(room.vnum, cenW-1, cenH))

        #while we've got rooms, iterate them
        while len(BFS) > 0:
            here = BFS.pop(0)
            if here.room == '' or not here.room in self.world.rooms:
                continue

            visited[here.room] = 1
            room = self.world.rooms[here.room]
            if Matrix[here.y][here.x] == '':
                Matrix[here.y][here.x] = here.room

                # Add exits to BFS
                if (here.y-1) >= 0 and "north" in room.exits:
                    if not room.exits["north"].to_vnum in visited:
                        log(f"appending {room.exits['north']}")
                        BFS.append(MapPoint(room.exits["north"].to_vnum, here.x, here.y -1))

                if (here.y +1) < len(Matrix) and "south" in room.exits:
                    if not room.exits["south"].to_vnum in visited:
                        log(f"appending {room.exits['south']}")
                        BFS.append(MapPoint(room.exits["south"].to_vnum, here.x, here.y+1))

                if (here.x +1) < len(Matrix[here.y]) and "east" in room.exits:
                    if not room.exits["east"].to_vnum in visited:
                        log(f"appending {room.exits['east']}")
                        BFS.append(MapPoint(room.exits["east"].to_vnum, here.x+1, here.y))

                if (here.x -1) >= 0 and "west" in room.exits:
                    if not room.exits["west"].to_vnum in visited:
                        log(f"appending {room.exits['west']}")
                        BFS.append(MapPoint(room.exits["west"].to_vnum, here.x-1, here.y))        

        # draw the map with Matrix of size Viewport
        buf =self.draw_map(Matrix, self.content_size.width, self.content_size.height-1, cur_room="3001")
        self.map.update(buf)
    
    def get_terrain_icon(self, terrain: str) -> str:
        if 'Inside' in terrain:
            return "[on rgb(55,59,65)] [/on rgb(55,59,65)]"
        if 'City' in terrain:
            return "[on rgb(40,42,46)] [/on rgb(40,42,46)]"
        if 'Path' in terrain:
            return "[on rgb(92,49,20)] [/on rgb(92,49,20)]"
        if 'Forest' in terrain:
            return "[on rgb(28,93,25)] [/on rgb(28,93,25)]"
        if 'Field' in terrain:
            return "[on rgb(91,163,88)] [/on rgb(91,163,88)]"
        if 'Water' in terrain:
            return "[on rgb(52,124,186)] [/on rgb(52,124,186)]"
        
        return " "
    def draw_map(self, Matrix, cW, cH, cur_room: str="") -> str:
        ytmp = len(Matrix) * 3
        xtmp = int((cW - len(Matrix[0])*5)/ 2)
        
        a_map = [[' ' for x in range(cW)] for y in range(cH)]
        # subtract one for the 0-index array
        y = 2 - 1
        #x = xtmp + 3 - 1
        # Let's just pad X for now

        for yp in Matrix:
            x = xtmp + 3 -1
            for xp in yp:
                if xp == '':
                    x += 5
                    continue
                    
                room = self.world.rooms[xp]
                t_icon = self.get_terrain_icon(room.terrain)
                if room.vnum == cur_room:
                    a_map[y][x] = "[bold red]@[/bold red]"
                
                a_map[y-1][x-1] = t_icon
                a_map[y-1][x-2] = t_icon
                a_map[y-1][x+2] = t_icon

                a_map[y][x-1] = "["
                a_map[y][x+1] = "]"

                a_map[y+1][x-1] = t_icon
                a_map[y+1][x-2] = t_icon
                a_map[y+1][x+2] = t_icon

                if "north" in room.exits:
                    a_map[y-1][x] = "|"
                else :
                    a_map[y-1][x] = t_icon
                if "south" in room.exits:
                    a_map[y+1][x] = "|"
                else :
                    a_map[y+1][x] = t_icon
                if "east" in room.exits:
                    a_map[y][x+2] = "—"
                else :
                    a_map[y][x+2] = t_icon
                if "west" in room.exits:
                    a_map[y][x-2] = "—"
                else :
                    a_map[y][x-2] = t_icon
                if "up" in room.exits:
                    a_map[y-1][x+1] = "+"
                else:
                    a_map[y-1][x+1] = t_icon
                if "down" in room.exits:
                    a_map[y+1][x+1] = "-"
                else :
                    a_map[y+1][x+1] = t_icon
                x += 5
            y += 3

        return "\n".join([''.join(yp) for yp in a_map])

    def on_resize(self, event: Resize):
        if getattr(self.screen.session, "world", None):
            if self.world is None:
                log("Load the world")
                self.world = self.screen.session.world
            self.generate_map()
