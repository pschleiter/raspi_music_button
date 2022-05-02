import typing as t
from pathlib import Path

from raspi_music_button.adapters.amixer import AbstractAMixerAdapter
from raspi_music_button.adapters.aplay import AbstractAPlayAdapter
from raspi_music_button.adapters.mpg321 import AbstractMPG321Adapter


class FakeAPlayAdapter(AbstractAPlayAdapter):

    VERSION_STRING: str = "aplay: version 1.2.4 by Jaroslav Kysela <perex@perex.cz>"
    DEVICES_STRING: str = """**** List of PLAYBACK Hardware Devices ****
card 0: Headphones [bcm2835 Headphones], device 0: bcm2835 Headphones [bcm2835 Headphones]
  Subdevices: 8/8
  Subdevice #0: subdevice #0
  Subdevice #1: subdevice #1
  Subdevice #2: subdevice #2
  Subdevice #3: subdevice #3
  Subdevice #4: subdevice #4
  Subdevice #5: subdevice #5
  Subdevice #6: subdevice #6
  Subdevice #7: subdevice #7
card 1: USB [Jabra SPEAK 510 USB], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 2: vc4hdmi [vc4-hdmi], device 0: MAI PCM i2s-hifi-0 [MAI PCM i2s-hifi-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
"""

    @classmethod
    def _version(cls):
        return cls.VERSION_STRING

    @classmethod
    def _list_hardware_devices(cls):
        return cls.DEVICES_STRING


class FakeAMixerAdapter(AbstractAMixerAdapter):

    CONTENTS: t.Dict[int, str] = {
        0: """Simple mixer control 'Headphone',0
  Capabilities: pvolume pvolume-joined pswitch pswitch-joined
  Playback channels: Mono
  Limits: Playback -10239 - 400
  Mono: Playback 0 [96%] [0.00dB] [on]
""",
        1: """Simple mixer control 'PCM',0
  Capabilities: pvolume pvolume-joined pswitch pswitch-joined
  Playback channels: Mono
  Limits: Playback 0 - 11
  Mono: Playback 2 [18%] [-28.00dB] [on]
Simple mixer control 'Mic',0
  Capabilities: cvolume cvolume-joined cswitch cswitch-joined
  Capture channels: Mono
  Limits: Capture 0 - 7
  Mono: Capture 5 [71%] [3.00dB] [on]
""",
        2: "",
    }
    COMMANDS = []

    @classmethod
    def _version(cls) -> str:
        return "amixer version 1.2.4"

    @classmethod
    def _show_contents(cls, card_id: int) -> str:
        return cls.CONTENTS.get(
            card_id,
            """Invalid card number.
Usage: amixer <options> [command]

Available options:
  -h,--help       this help
  -c,--card N     select the card
  -D,--device N   select the device, default 'default'
  -d,--debug      debug mode
  -n,--nocheck    do not perform range checking
  -v,--version    print version of this program
  -q,--quiet      be quiet
  -i,--inactive   show also inactive controls
  -a,--abstract L select abstraction level (none or basic)
  -s,--stdin      Read and execute commands from stdin sequentially
  -R,--raw-volume Use the raw value (default)
  -M,--mapped-volume Use the mapped volume

Available commands:
  scontrols       show all mixer simple controls
  scontents       show contents of all mixer simple controls (default command)
  sset sID P      set contents for one mixer simple control
  sget sID        get contents for one mixer simple control
  controls        show all controls for given card
  contents        show contents of all controls for given card
  cset cID P      set control contents for one control
  cget cID        get control contents for one control
""",
        )

    @classmethod
    def _set_contents(cls, card_id: int, simple_control: str, value: str):
        cls.COMMANDS.append(("set_content", card_id, simple_control, value))


class FakeMPG321Adapter(AbstractMPG321Adapter):

    COMMANDS = []

    @classmethod
    def _version(cls) -> str:
        return """mpg321 version 0.3.2. Copyright (C) 2001, 2002 Joe Drew,
now maintained by Nanakos Chrysostomos and others.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

    @classmethod
    def play_songs(
        cls, card_id: int, songs: t.List[t.Union[Path, str]], shuffle: bool = False
    ):
        cls.COMMANDS.append(
            ("play_song", card_id, " ".join([str(song) for song in songs]))
        )
