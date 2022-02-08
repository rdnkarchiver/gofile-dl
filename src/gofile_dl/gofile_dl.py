import asyncio
import argparse
import logging as log
import os
from typing import Union
from urllib.parse import unquote

import aiohttp
from gofile import Gofile
from tqdm import tqdm

from gofile_dl import __version__ as VERSION


CHUNK_SIZE = 8192  # in bytes
MAX_CONCURRENT_DOWNLOADS = 5
MAX_DESCRIPTION_LENGTH = 20

TIMEOUT_CONN = 10
TIMEOUT_READ = 12 * 60 * 60  # 12 hrs * 60 mins * 60 secs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-file", "-i", metavar="<file>", help="file containing Gofile links"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        metavar="<directory>",
        help="directory in which to save downloaded files",
    )
    parser.add_argument(
        "--flatten",
        action="store_true",
        help="save all files in the same directory",
    )
    parser.add_argument(
        "--password",
        "-p",
        metavar="<password>",
        help="password of password-protected files",
    )
    parser.add_argument(
        "--token",
        "-t",
        metavar="<token>",
        help="Gofile account token (guest account will be used if omitted)",
    )
    parser.add_argument(
        "--dry-run",
        "--simulate",
        action="store_true",
        help="build the download target list but do not download anything",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="increase output verbosity",
    )
    parser.add_argument("--version", action="version", version="%(prog)s " + VERSION)
    parser.add_argument(
        "gofile_links",
        metavar="link",
        nargs="*",
        help="link to content to download (passing multiple links is supported)",
    )
    return parser.parse_args()


def setup_logging(verbose: bool) -> None:
    log.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=log.DEBUG if verbose else log.INFO,
    )


async def download(sess: aiohttp.ClientSession, url: str, dest: str) -> None:
    file_name: str = dest.split("/")[-1]
    description = f"{file_name[:MAX_DESCRIPTION_LENGTH]: <{MAX_DESCRIPTION_LENGTH}}"

    log.debug(f"downloading {url}")
    async with sess.get(url) as res:
        res: aiohttp.ClientResponse
        res.raise_for_status()

        remote_file_size = int(res.headers.get("content-length", 0))
        if os.path.isfile(dest):
            if os.path.getsize(dest) == remote_file_size:
                return
        with open(f"{dest}.temp", "wb") as f:
            progress_bar = tqdm(
                total=remote_file_size,
                desc=description,
                unit="B",
                unit_scale=True,
                leave=False,
            )
            while True:
                chunk = await res.content.read(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                progress_bar.update(len(chunk))
        os.rename(f"{dest}.temp", dest)


async def download_all(token: str, targets: list[dict[str, str]]) -> None:
    connector = aiohttp.TCPConnector(limit_per_host=MAX_CONCURRENT_DOWNLOADS)
    timeout = aiohttp.ClientTimeout(sock_connect=TIMEOUT_CONN, sock_read=TIMEOUT_READ)
    cookies = {
        "accountToken": token,
    }
    async with aiohttp.ClientSession(
        connector=connector, timeout=timeout, cookies=cookies
    ) as sess:
        tasks = [
            asyncio.create_task(download(sess, target["url"], target["dest"]))
            for target in targets
        ]
        responses = [  # noqa F841
            await f
            for f in tqdm(
                asyncio.as_completed(tasks),
                total=len(tasks),
                desc="Overall progress",
            )
        ]


def build_targets(
    client: Gofile, targets: list[dict[str, str]] = [], **kwargs
) -> list[dict[str, str]]:
    gofile_links: list[str] = kwargs["gofile_links"]
    input_file: str = kwargs["input_file"]
    password: str = kwargs["password"]
    flatten: bool = kwargs["flatten"]
    output_dir: str = kwargs["output_dir"]

    if input_file:
        with open(input_file, "r") as f:
            gofile_links += f.read().splitlines()

    for link in gofile_links:
        log.debug(f"link: {link}")
        content_id = link.split("/")[-1] if link.startswith("https://gofile.io/") else link
        content = client.get_content(content_id, password)
        if not content:
            log.error(f"could not get content for {content_id}.")
            continue

        log.debug(f"content: {content}")
        dest_dir: str = content["name"] if content["type"] == "file" else content_id
        if output_dir:
            if flatten:
                dest_dir = output_dir
            else:
                dest_dir = os.path.join(output_dir, content["name"])
        else:
            if flatten:
                dest_dir = os.getcwd()

        if not kwargs["dry_run"]:
            try:
                os.makedirs(dest_dir)
            except FileExistsError:
                pass

        contents: dict[str, dict[str, Union[str, int]]] = content["contents"]
        for val in contents.values():
            log.debug(f"val: {val}")
            if "link" in val:
                file_url: str = val["link"] if val["link"] != "overloaded" else val["directLink"]
                file_path = os.path.join(dest_dir, unquote(file_url.split("/")[-1]))
                targets.append(
                    {
                        "url": file_url,
                        "dest": file_path,
                    }
                )
                log.debug(f"targets: {targets}")
            if "code" in val:
                build_targets(
                    client,
                    targets,
                    gofile_links=[val["code"]],
                    password=password,
                    flatten=flatten,
                    output_dir=dest_dir,
                    dry_run=kwargs["dry_run"],
                )
    return targets


def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)

    client = Gofile(args.token)

    targets = build_targets(client, **vars(args))

    if args.dry_run:
        log.info("Dry run. No files will be downloaded.")
        log.info(f"targets: {targets}")
        return

    asyncio.get_event_loop().run_until_complete(download_all(client.token, targets))


if __name__ == "__main__":
    main()
