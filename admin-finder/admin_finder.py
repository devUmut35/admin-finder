from __future__ import annotations

import argparse
import atexit
import ctypes
import os
import shlex
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import local
from urllib.parse import urljoin

import requests


AUTHOR = "devUmut35"
TOOL_NAME = "devUmut35 Admin Finder"
DEFAULT_WORDLIST = Path("wordlists/admin_paths.txt")
THREAD_LOCAL = local()

FOUND_CODES = {200}
REDIRECT_CODES = {301, 302, 307, 308}
AUTH_CODES = {401}
FORBIDDEN_CODES = {403}
MAYBE_CODES = {405}
HIT_CODES = FOUND_CODES | REDIRECT_CODES | AUTH_CODES | FORBIDDEN_CODES | MAYBE_CODES

RED = "\033[91m"
BRIGHT_RED = "\033[38;2;255;0;0m"
BOLD = "\033[1m"
RESET = "\033[0m"


def enable_windows_ansi() -> None:
    if os.name != "nt":
        return
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 4)
    except Exception:
        pass


def set_title(title: str) -> None:
    if os.name == "nt":
        os.system(f"title {title}")
    else:
        sys.stdout.write(f"\033]0;{title}\007")


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def restore_console() -> None:
    sys.stdout.write(RESET)
    sys.stdout.flush()
    if os.name == "nt":
        os.system("color 07 >nul 2>&1")
        os.system("title Command Prompt")


def start_style() -> None:
    enable_windows_ansi()
    set_title(TOOL_NAME)
    clear_screen()
    if os.name == "nt":
        os.system("color 0C")
    sys.stdout.write(BRIGHT_RED + BOLD)
    sys.stdout.flush()


def boxed(lines: list[str]) -> str:
    width = max(len(line) for line in lines) + 4
    top = "+" + "-" * width + "+"
    body = [f"|  {line.ljust(width - 4)}  |" for line in lines]
    return "\n".join([top, *body, top])


def banner() -> None:
    lines = [
    "",
    r"      ___      ____    __  __   ___   _   _      _____  ___   _   _   ____   _____  ____    ",
    r"     /   \    |  _ \  |  \/  | |_ _| | \ | |    |  ___||_ _| | \ | | |  _ \ | ____||  _ \   ",
    r"    /  ^  \   | | | | | |\/| |  | |  |  \| |    | |_    | |  |  \| | | | | ||  _|  | |_) |  ",
    r"   /  /_\  \  | |_| | | |  | |  | |  | |\  |    |  _|   | |  | |\  | | |_| || |___ |  _ <   ",
    r"  /__/   \__\ |____/  |_|  |_| |___| |_| \_|    |_|    |___| |_| \_| |____/ |_____||_| \_\  ",
    "",
    "                              signature: devUmut35",
    "",
]
    print(boxed(lines))


def example_text() -> None:
    print("Example:")
    print("  scan https://example.com")
    print("  scan https://example.com -t 60 --timeout 2")
    print("  scan https://example.com --hide-404 -o results.txt")
    print()


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("URL cannot be empty.")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    if not url.endswith("/"):
        url += "/"
    return url


def load_wordlist(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Wordlist not found: {path}")
    seen = set()
    paths = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        item = line.strip()
        if not item:
            continue
        item = item.lstrip("/")
        if item not in seen:
            seen.add(item)
            paths.append(item)
    if not paths:
        raise ValueError("Wordlist is empty.")
    return paths


def get_session() -> requests.Session:
    active_session = getattr(THREAD_LOCAL, "session", None)
    if active_session is None:
        active_session = requests.Session()
        active_session.headers.update({"User-Agent": f"{AUTHOR}-admin-finder/7.0"})
        THREAD_LOCAL.session = active_session
    return active_session


def classify(status: int) -> tuple[str, str]:
    if status in FOUND_CODES:
        return "FOUND", "page exists"
    if status in REDIRECT_CODES:
        return "REDIRECT", "redirect detected"
    if status in FORBIDDEN_CODES:
        return "FORBIDDEN", "access denied"
    if status in AUTH_CODES:
        return "AUTH", "login required"
    if status in MAYBE_CODES:
        return "MAYBE", "endpoint may exist"
    if status == 404:
        return "NOT FOUND", "not found"
    return "CHECKED", "checked"


def check_path(index: int, total: int, base_url: str, path: str, timeout: float) -> dict:
    url = urljoin(base_url, path.lstrip("/"))
    try:
        response = get_session().get(url, timeout=timeout, allow_redirects=False)
        status = response.status_code
        location = response.headers.get("Location")
        label, message = classify(status)
        return {
            "index": index,
            "total": total,
            "url": url,
            "status": status,
            "location": location,
            "label": label,
            "message": message,
            "hit": status in HIT_CODES,
        }
    except requests.RequestException:
        return {
            "index": index,
            "total": total,
            "url": url,
            "status": None,
            "location": None,
            "label": "ERROR",
            "message": "request failed",
            "hit": False,
        }


def result_line(result: dict) -> str:
    status = "---" if result["status"] is None else str(result["status"])
    line = f"[{result['index']:03}/{result['total']:03}] {result['url']} -> {result['label']} ({status})"
    if result["location"]:
        line += f" | {result['location']}"
    return line


def ask(question: str, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    try:
        answer = input(f"{question} [{suffix}]: ").strip().lower()
    except KeyboardInterrupt:
        print()
        return default
    if not answer:
        return default
    return answer in {"y", "yes"}


def header(target: str, wordlist: str, total: int, threads: int, timeout: float) -> None:
    print(f"Target   : {target}")
    print(f"Wordlist : {wordlist}")
    print(f"Paths    : {total}")
    print(f"Threads  : {threads}")
    print(f"Timeout  : {timeout}s")
    print("-" * 90)


def summary(results: list[dict], stopped: bool) -> None:
    ordered = sorted(results, key=lambda item: item["index"])
    hits = [item for item in ordered if item["hit"]]
    counts = {
        "FOUND": 0,
        "REDIRECT": 0,
        "FORBIDDEN": 0,
        "AUTH": 0,
        "MAYBE": 0,
        "NOT FOUND": 0,
        "CHECKED": 0,
        "ERROR": 0,
    }
    for item in ordered:
        counts[item["label"]] = counts.get(item["label"], 0) + 1
    print("-" * 90)
    print("SUMMARY")
    print(f"FOUND     : {counts['FOUND']}")
    print(f"REDIRECT  : {counts['REDIRECT']}")
    print(f"FORBIDDEN : {counts['FORBIDDEN']}")
    print(f"AUTH      : {counts['AUTH']}")
    print(f"MAYBE     : {counts['MAYBE']}")
    print(f"NOT FOUND : {counts['NOT FOUND']}")
    print(f"ERROR     : {counts['ERROR']}")
    if stopped:
        print("STATUS    : STOPPED BY USER")
    print("-" * 90)
    print("FOUND RESULTS")
    if hits:
        for item in hits:
            print(result_line(item))
    else:
        print("No found results.")
    print("-" * 90)


def run_scan(target: str, wordlist: str, output: str | None, timeout: float, threads: int, hide_404: bool) -> int:
    target_url = normalize_url(target)
    paths = load_wordlist(Path(wordlist))
    total = len(paths)
    threads = max(1, min(threads, total))
    results = []
    stopped = False

    header(target_url, wordlist, total, threads, timeout)

    executor = ThreadPoolExecutor(max_workers=threads)
    futures = [
        executor.submit(check_path, index, total, target_url, path, timeout)
        for index, path in enumerate(paths, start=1)
    ]

    try:
        for future in futures:
            try:
                item = future.result()
            except KeyboardInterrupt:
                print()
                if ask("Stop scan and print results?", True):
                    stopped = True
                    for pending in futures:
                        pending.cancel()
                    break
                continue

            results.append(item)

            if not (hide_404 and item["label"] == "NOT FOUND"):
                print(result_line(item))

    finally:
        executor.shutdown(wait=not stopped, cancel_futures=stopped)

    summary(results, stopped)

    if output:
        hits = [item for item in sorted(results, key=lambda item: item["index"]) if item["hit"]]
        Path(output).write_text("\n".join(result_line(item) for item in hits) + "\n", encoding="utf-8")
        print(f"Saved: {output}")

    return 130 if stopped else 0

def parser() -> argparse.ArgumentParser:
    app = argparse.ArgumentParser(prog="admin_finder", description="devUmut35 Admin Finder")
    app.add_argument("target", nargs="?")
    app.add_argument("-u", "--url")
    app.add_argument("-w", "--wordlist", default=str(DEFAULT_WORDLIST))
    app.add_argument("-o", "--output")
    app.add_argument("-t", "--threads", type=int, default=50)
    app.add_argument("--timeout", type=float, default=2.0)
    app.add_argument("--hide-404", action="store_true")
    return app


def help_text() -> None:
    print("Commands:")
    print("  scan https://example.com")
    print("  scan https://example.com -t 80 --timeout 1.5")
    print("  scan https://example.com --hide-404")
    print("  scan https://example.com -o results.txt")
    print("  clear")
    print("  help")
    print("  exit")
    print()


def interactive() -> int:
    app = parser()
    example_text()
    while True:
        try:
            command = input("devUmut35> ").strip()
        except KeyboardInterrupt:
            print()
            if ask("Exit Admin Finder?", False):
                return 0
            continue
        except EOFError:
            print()
            return 0
        if not command:
            continue
        lowered = command.lower()
        if lowered in {"exit", "quit"}:
            print("bye.")
            time.sleep(0.7)
            clear_screen()
            return 0
        if lowered in {"help", "?"}:
            help_text()
            continue
        if lowered in {"clear", "cls"}:
            clear_screen()
            banner()
            example_text()
            continue
        if lowered.startswith("scan "):
            try:
                args = app.parse_args(shlex.split(command)[1:])
            except SystemExit:
                print("Invalid command. Type help.")
                continue
            target = args.target or args.url
            if not target:
                print("Example: scan https://example.com")
                continue
            run_scan(target, args.wordlist, args.output, args.timeout, args.threads, args.hide_404)
            continue
        print("Unknown command. Type help.")


def main() -> int:
    atexit.register(restore_console)
    start_style()
    banner()

    app = parser()
    args = app.parse_args()
    target = args.target or args.url

    if not target:
        return interactive()

    try:
        return run_scan(
            target,
            args.wordlist,
            args.output,
            args.timeout,
            args.threads,
            args.hide_404,
        )
    except KeyboardInterrupt:
        print()
        if ask("Exit Admin Finder?", True):
            print("bye.")
            time.sleep(0.7)
            clear_screen()
            return 130
        return 0
    except Exception as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())