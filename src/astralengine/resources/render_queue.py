from __future__ import annotations

from dataclasses import dataclass, field

from astralengine.rendering.draw_packet import DrawPacket


@dataclass(slots=True)
class RenderQueue:
    '''
    Per-frame collection of extracted draw packets.
    '''
    packets: list[DrawPacket] = field(default_factory=list)

    def clear(self) -> None:
        self.packets.clear()

    def add(self, packet: DrawPacket) -> None:
        self.packets.append(packet)