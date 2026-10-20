import sys
import os
import argparse
import subprocess
import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from perchance_client import PerchanceImageClient, POPULAR_STYLES, SHAPE_MAPPINGS

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(force_terminal=True)


def open_image(path: str) -> None:
    """Opens the generated image using the default system viewer."""
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception as err:
        console.print(f"[yellow]Warning: Could not open image automatically: {err}[/yellow]")


def display_styles_table() -> None:
    """Displays a formatted table of popular and available art styles."""
    styles_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles.json")
    all_styles = []
    if os.path.exists(styles_file):
        try:
            with open(styles_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                all_styles = [item.get("text", "") for item in raw_data if item.get("text")]
        except Exception:
            pass

    display_list = all_styles if all_styles else POPULAR_STYLES

    table = Table(title="🎨 Available Perchance Art Styles", border_style="cyan", show_lines=True)
    table.add_column("#", justify="center", style="dim", width=4)
    table.add_column("Style Name", style="bold white")
    table.add_column("#", justify="center", style="dim", width=4)
    table.add_column("Style Name", style="bold white")

    # Split into 2 columns for compact display
    half = (len(display_list) + 1) // 2
    for i in range(half):
        col1_idx = i + 1
        col1_val = display_list[i]
        col2_idx = i + 1 + half
        col2_val = display_list[i + half] if (i + half) < len(display_list) else ""
        table.add_row(
            str(col1_idx),
            col1_val,
            str(col2_idx) if col2_val else "",
            col2_val
        )

    console.print(table)
    console.print("[dim]Tip: You can use any of these styles with '-s <style_name>'. Partial names also match![/dim]\n")


def generate_with_progress(
    client: PerchanceImageClient,
    prompt_text: str,
    style: str = None,
    shape: str = "square",
    negative_prompt: str = None,
    num_images: int = 1,
    disable_safety: bool = True,
    output_path: str = None,
    auto_open: bool = False,
):
    result = None
    style_label = f" | Style: {style}" if style else ""
    shape_label = f" | Shape: {shape}"

    try:
        with console.status(f"[cyan]Generating image{style_label}{shape_label}...[/cyan]", spinner="dots") as status:
            def update_status(message: str):
                status.update(f"[cyan]{message}[/cyan]")

            result = client.generate(
                prompt=prompt_text,
                style=style,
                shape=shape,
                negative_prompt=negative_prompt,
                num_images=num_images,
                disable_safety_settings=disable_safety,
                output_file=output_path,
                on_status=update_status,
            )
    except Exception as err:
        console.print(f"\n[bold red]Generation Error:[/bold red] {err}")
        return None

    if result and result.get("saved_paths"):
        console.print(f"[bold green]✓ Generation Succeeded![/bold green] [dim]({result['elapsed_time']}s)[/dim]")
        for path in result["saved_paths"]:
            console.print(f"File saved: [bold white]{path}[/bold white]")
            if auto_open:
                open_image(path)
        console.print()

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Perchance AI Text-to-Image Generator CLI (100% Free & Unlimited, Zero Login)"
    )
    parser.add_argument("prompt", nargs="?", default=None, help="Image prompt description.")
    parser.add_argument("-s", "--style", default=None, help="Art style (e.g., 'Cinematic', 'Painted Anime', 'Casual Photo').")
    parser.add_argument("-ar", "--aspect", "--shape", default="square", choices=["square", "portrait", "landscape", "1:1", "9:16", "16:9", "4:3", "3:4"], help="Image aspect ratio/shape (default: square).")
    parser.add_argument("-n", "--negative", default=None, help="Negative prompt (elements to avoid).")
    parser.add_argument("-c", "--count", type=int, default=1, help="Number of images to generate (default: 1).")
    parser.add_argument("-o", "--output", default=None, help="Custom output file or directory.")
    parser.add_argument("--open", action="store_true", help="Automatically open generated image after completion.")
    parser.add_argument("--list-styles", action="store_true", help="Display all available art styles and exit.")
    parser.add_argument("--safe", action="store_true", help="Enable safety filters (default: safety filters disabled for creative freedom).")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging.")
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold cyan]🎨 Perchance AI Text-to-Image Generator[/bold cyan]\n"
            "[dim]Free • Unlimited • Zero Login Required • Cloudflare Bypassed[/dim]",
            border_style="cyan",
            expand=False,
        )
    )

    if args.list_styles:
        display_styles_table()
        return

    disable_safety = not args.safe

    client = PerchanceImageClient(headless=True, debug=args.debug)

    try:
        if args.prompt:
            generate_with_progress(
                client=client,
                prompt_text=args.prompt,
                style=args.style,
                shape=args.aspect,
                negative_prompt=args.negative,
                num_images=args.count,
                disable_safety=disable_safety,
                output_path=args.output,
                auto_open=args.open,
            )
            return

        # Interactive Session Mode
        console.print("[dim]Commands: 'styles' (list art styles), 'exit' / 'q' (quit).[/dim]")
        console.print("[dim]Tip: You can prefix prompts with style: 'cinematic: a futuristic city'[/dim]\n")

        current_style = args.style
        current_shape = args.aspect

        while True:
            try:
                style_tag = f"[bold magenta][{current_style}][/bold magenta] " if current_style else ""
                shape_tag = f"[bold blue][{current_shape}][/bold blue] "
                user_input = Prompt.ask(f"{style_tag}{shape_tag}[bold]Prompt[/bold]")

                if not user_input or user_input.strip().lower() in ("q", "quit", "exit"):
                    console.print("[dim]Exiting.[/dim]")
                    break

                clean_input = user_input.strip()

                if clean_input.lower() in ("styles", "list", "help styles"):
                    display_styles_table()
                    continue

                if clean_input.lower().startswith("style:"):
                    parts = clean_input.split(":", 1)
                    current_style = parts[1].strip() or None
                    console.print(f"[cyan]Active style set to: {current_style}[/cyan]\n")
                    continue

                if clean_input.lower().startswith("shape:") or clean_input.lower().startswith("aspect:"):
                    parts = clean_input.split(":", 1)
                    current_shape = parts[1].strip() or "square"
                    console.print(f"[cyan]Active shape set to: {current_shape}[/cyan]\n")
                    continue

                # Check inline style prefix like "cinematic: prompt"
                req_style = current_style
                if ":" in clean_input and not clean_input.startswith("http"):
                    possible_style, rest = clean_input.split(":", 1)
                    if any(possible_style.strip().lower() in s.lower() for s in POPULAR_STYLES):
                        req_style = possible_style.strip()
                        clean_input = rest.strip()

                generate_with_progress(
                    client=client,
                    prompt_text=clean_input,
                    style=req_style,
                    shape=current_shape,
                    negative_prompt=args.negative,
                    num_images=args.count,
                    disable_safety=disable_safety,
                    auto_open=True,
                )
                console.print("─" * 45)

            except KeyboardInterrupt:
                console.print("\n[dim]Interrupted. Exiting.[/dim]")
                break
    finally:
        client.close()


if __name__ == "__main__":
    main()
