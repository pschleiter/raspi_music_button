import typing as t
from pathlib import Path

import click
from click import ClickException

from raspi_music_button.bootstrap import bootstrap
from raspi_music_button.domain import model

service = bootstrap()

card_option = click.option(
    "-c", "--card", "card", type=int, help="Card to be used for playback."
)
volume_option = click.option(
    "-v",
    "--volume",
    "volume",
    type=click.IntRange(0, 100),
    help="Setting the volume of the playback.",
)
shuffle_option = click.option(
    "-z",
    "--shuffle",
    "shuffle",
    default=False,
    is_flag=True,
    help="Shuffles all given songs before playing.",
)
loop_option = click.option(
    "-l",
    "--loop",
    "loop",
    default=False,
    is_flag=True,
    help="Starts an infinite loop. Can only be aborted by CTRL-C.",
)
single_option = click.option(
    "-s",
    "--single-song",
    "single_song",
    default=False,
    is_flag=True,
    help="On press only plays a single song of the given songs.",
)


@click.group()
def cli():
    pass


@cli.command(help="Lists all available playback cards.")
def list_cards():
    click.echo("The following playback cards where found:")
    click.echo(_card_listing(cards=service.get_list_of_devices()))


@cli.group(help="Plays the given song(s)")
def play():
    pass


@play.command("song", help="Plays the given song(s) on the selected playback device.")
@click.argument("song-path", nargs=-1, type=click.Path(exists=True))
@card_option
@volume_option
@shuffle_option
def play_song(song_path, card, volume, shuffle):
    _validate_song_path(song_path=song_path)

    cards = service.get_list_of_devices()
    while card is None or card not in [c.card for c in cards]:
        card = _select_card(cards=cards)

    if volume is not None:
        service.set_volume(card_id=card, volume_prct=volume)

    service.play_songs(card_id=card, songs=list(song_path), shuffle=shuffle)


@play.command(
    "folder",
    help="Plays all mp3 files in the given folder on the selected playback device.",
)
@click.argument("song-folder", nargs=1, type=click.Path(exists=True))
@card_option
@volume_option
@shuffle_option
def play_folder(song_folder, card, volume, shuffle):
    cards = service.get_list_of_devices()
    while card is None or card not in [c.card for c in cards]:
        card = _select_card(cards=cards)

    if volume is not None:
        service.set_volume(card_id=card, volume_prct=volume)

    service.play_folder(card_id=card, folder=Path(song_folder), shuffle=shuffle)


@cli.group(help="Plays the given song on pressed button")
@click.option(
    "-b",
    "--button",
    "gpio",
    type=click.IntRange(2, 27),
    prompt=True,
    help="GPIO number of the buttton. For more information see"
    " https://www.raspberrypi.com/documentation/computers/os.html#gpio-and-the-40-pin-header",
)
@click.pass_context
def button(ctx, gpio):
    ctx.ensure_object(dict)

    ctx.obj["gpio"] = gpio


@button.command("song", help="Plays the given song(s) on the selected playback device.")
@click.argument("song-path", nargs=-1, type=click.Path(exists=True))
@card_option
@volume_option
@shuffle_option
@loop_option
@single_option
@click.pass_context
def button_song(ctx, song_path, card, volume, shuffle, loop, single_song):
    _validate_song_path(song_path=song_path)

    cards = service.get_list_of_devices()
    while card is None or card not in [c.card for c in cards]:
        card = _select_card(cards=cards)

    if volume is not None:
        service.set_volume(card_id=card, volume_prct=volume)

    service.trigger_songs(
        gpio=ctx.obj["gpio"],
        card_id=card,
        songs=list(song_path),
        loop=loop,
        shuffle=shuffle,
        single_song=single_song,
    )


@play.command(
    "folder",
    help="Plays all mp3 files in the given folder on the selected playback device.",
)
@click.argument("song-folder", nargs=1, type=click.Path(exists=True))
@card_option
@volume_option
@shuffle_option
@loop_option
@single_option
@click.pass_context
def button_folder(ctx, song_folder, card, volume, shuffle, loop, single_song):
    cards = service.get_list_of_devices()
    while card is None or card not in [c.card for c in cards]:
        card = _select_card(cards=cards)

    if volume is not None:
        service.set_volume(card_id=card, volume_prct=volume)

    service.trigger_folder(
        gpio=ctx.obj["gpio"],
        card_id=card,
        folder=song_folder,
        loop=loop,
        shuffle=shuffle,
        single_song=single_song,
    )


def _select_card(cards) -> int:
    return click.prompt(
        "\n".join(
            ["Select one the following playback cards:"]
            + [_card_listing(cards=cards, indent=2)]
            + ["Your choice"]
        ),
        type=int,
    )


def _card_listing(cards: t.List[model.PlaybackCard], indent: int = 0) -> str:
    return "\n".join([f"{' '*indent}[{card.card}]: {card.name}" for card in cards])


def _validate_song_path(song_path):
    if len(song_path) == 0:
        raise ClickException(
            "No song path was provided. Please see --help for more details."
        )
