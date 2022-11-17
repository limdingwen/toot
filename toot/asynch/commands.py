import asyncio
import click
import os
import sys
import random

from typing import List, Optional, Tuple
from toot.asynch import api
from toot.output import print_out
from toot.utils import EOF_KEY, editor_input, multiline_input

# Add shorthand -h for invoking help
CONTEXT = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT)
@click.option('--debug/--no-debug', default=False)
@click.option('--color/--no-color', default=sys.stdout.isatty())
def cli(debug: bool, color: bool):
    click.echo(f"Debug is {'on' if debug else 'off'}", err=True)
    click.echo(f"Color is {'on' if color else 'off'}", err=True)


@cli.command()
@click.argument("hostname")
def instance(hostname: str, debug: bool):
    instance = asyncio.run(api.instance(hostname))
    print(instance.json())


@cli.command()
@click.argument("text", required=False)
@click.option(
    "-e",
    "--editor",
    is_flag=True,
    flag_value=os.environ.get("EDITOR"),
    show_default=os.environ.get("EDITOR"),
    help="Use an editor to compose your toot, defaults to editor defined in "
         "$EDITOR environment variable."
)
@click.option(
    "-m",
    "--media",
    multiple=True,
    help="Path to a media file to attach (specify multiple times to attach "
         "up to 4 files)",
)
@click.option(
    "-d",
    "--description",
    multiple=True,
    help="Plain-text description of the media for accessibility purposes, one "
         "per attached media",
)
def post(
    text: str,
    editor: str,
    media: Tuple[str, ...],
    description: Tuple[str, ...],
):
    if editor and not sys.stdin.isatty():
        raise click.UsageError("Cannot run editor if not in tty.")

    if len(media) > 4:
        raise click.UsageError("Cannot attach more than 4 files.")

    # Read any text that might be piped to stdin
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read().rstrip()

    # Match media to corresponding description and upload
    uploaded_media = []

    for idx, file in enumerate(media):
        file_desc = description[idx].strip() if idx < len(description) else None
        print(idx, file, file_desc)
        result = _do_upload(file, file_desc)
        uploaded_media.append(result)

    media_ids = [m["id"] for m in uploaded_media]

    if uploaded_media and not text:
        text = "\n".join(m['text_url'] for m in uploaded_media)

    if editor:
        text = editor_input(editor, text)
    elif not text:
        print_out("Write or paste your toot. Press <yellow>{}</yellow> to post it.".format(EOF_KEY))
        text = multiline_input()

    if not text:
        raise click.UsageError("You must specify either text or media to post.")

    # response = api.post_status(
    #     app, user, text,
    #     visibility=visibility,
    #     media_ids=media_ids,
    #     sensitive=sensitive,
    #     spoiler_text=spoiler_text,
    #     in_reply_to_id=reply_to,
    #     language=language,
    #     scheduled_at=scheduled_at,
    #     content_type=content_type
    # )

    # if "scheduled_at" in response:
    #     print_out("Toot scheduled for: <green>{}</green>".format(response["scheduled_at"]))
    # else:
    #     print_out("Toot posted: <green>{}</green>".format(response.get('url')))

    # """Print FILENAME."""
    # click.echo(filename)


def _do_upload(file: str, description: Optional[str]):
    print("Faking upload:", file, description)
    id = random.randint(1, 99999)
    return {"id": id, "text_url": f"http://example.com/{id}"}


def main():
    # Allow overriding options using environment variables
    # https://click.palletsprojects.com/en/8.1.x/options/?highlight=auto_env#values-from-environment-variables
    cli(auto_envvar_prefix='TOOT')
