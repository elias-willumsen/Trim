# #!/usr/bin/env python3
#
# Script for å kjøre yt-dlp med cookies fra Chrome, etterfulgt av auto-editor.
# Forutsetter at yt-dlp, auto-editor og FFMPEG er installert.

# Authored by Elias André Willumsen :D

import argparse
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


REQUIRED_PROGRAMS = ("yt-dlp", "ffmpeg", "auto-editor")
COOKIE_BROWSER = "chrome"
DOWNLOAD_FORMAT = "bv*+ba/b"
FORMAT_SORT = "res:720"


def run_command(cmd: list[str | Path]) -> None:
    normalized_cmd = [str(part) for part in cmd]
    print("Kjører:", shlex.join(normalized_cmd))
    result = subprocess.run(normalized_cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def safe_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:120] if name else "video"


def get_video_title(url: str) -> str:
    command = ["yt-dlp", "--cookies-from-browser", COOKIE_BROWSER, "--print", "%(title)s", url]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return "video"
    return safe_filename(result.stdout.strip())


def ensure_dependencies() -> None:
    missing_programs = [program for program in REQUIRED_PROGRAMS if shutil.which(program) is None]
    if not missing_programs:
        return

    for program in missing_programs:
        print(f"Fant ikke programmet: {program}")
    sys.exit(1)


def ensure_output_files_do_not_exist(files: list[Path]) -> None:
    existing_files = [file for file in files if file.exists()]
    if not existing_files:
        return

    print("Disse filene finnes allerede. Flytt eller slett dem før du kjører trim:")
    for file in existing_files:
        print(f" - {file}")
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="trim",
        description="Last ned en video, gjør den klar for auto-editor og skriv ut en trimmet fil."
    )
    parser.add_argument("url", help="Video-URL")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dependencies()

    url = args.url
    title = get_video_title(url)

    downloaded_file = Path(f"{title}.mp4")
    fixed_file = Path(f"{title}_fixed.mp4")
    trimmed_file = Path(f"{title}_trimmed.mp4")

    ensure_output_files_do_not_exist([downloaded_file, fixed_file, trimmed_file])

    # 1. Last ned
    run_command([
        "yt-dlp",
        "--cookies-from-browser", COOKIE_BROWSER,
        "-f", DOWNLOAD_FORMAT,
        "-S", FORMAT_SORT,
        "--merge-output-format", "mp4",
        "-o", str(downloaded_file),
        url
    ])

    # # 2. Konverter
    # run_command([
    #     "ffmpeg",
    #     "-i", downloaded_file,
    #     "-c:v", "h264_videotoolbox",
    #     "-c:a", "aac",
    #     str(fixed_file)
    # ])

    # 3. Trim
    run_command([
        "auto-editor",
        str(downloaded_file),
        "-o", str(trimmed_file)
    ])

    # 4. Slette mellomfiler
    for file in [downloaded_file]:
        try:
            file.unlink()
            print(f"Slettet: {file}")
        except FileNotFoundError:
            pass

    print(f"Ferdig: {trimmed_file}")


if __name__ == "__main__":
    main()