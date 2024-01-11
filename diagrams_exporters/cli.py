import os
import subprocess
import click

from diagrams_exporters import printd, enable_debug
from diagrams_exporters import parse_dot
from diagrams_exporters import convert_to_diagrams

__VERSION__ = "0.1.0"


def get_filename_without_extension(file_path):
    base_name = os.path.basename(file_path)
    file_name, _ = os.path.splitext(base_name)
    return file_name


def get_current_directory_name():
    current_directory = os.getcwd()
    directory_name = os.path.basename(current_directory)
    return directory_name


@click.command()
@click.option("-v", "--version", is_flag=True, help="Print version")
@click.option("-f", "--file", help="Specify file or directory")
@click.option("-o", "--output", help="Specify output filename")
@click.option("-d", "--debug", is_flag=True, help="Enable debug mode")
@click.argument("provider", type=click.Choice(["terraform", "dot"]), required=False)
def cli(version, file, output, debug, provider):
    if version:
        click.echo(f"Diagrams Exporter: {__VERSION__}")
        return

    if debug:
        enable_debug()

    if provider == "dot":
        if file is None:
            click.echo("Error: -f/--file is required for dot provider.")
            return
        if output is None:
            output = f"{get_filename_without_extension(file)}-exported.dot"
        elif os.path.isdir(output):
            output = os.path.join(
                output, f"{get_filename_without_extension(file)}-exported.dot"
            )
        else:
            filename, _ = os.path.splitext(output)
            output = f"{filename}"

        run(file, output)
        return

    if provider == "terraform":
        if output is None:
            output = f"{get_current_directory_name()}-exported"
        elif os.path.isdir(output):
            output = os.path.join(output, f"{get_current_directory_name()}-exported")
        else:
            filename, _ = os.path.splitext(output)
            output = f"{filename}"

        # TODO input from another folder
        folder_name = get_current_directory_name()
        temp_dot_file = f"{folder_name}.dot"
        generate_terraform_graph(temp_dot_file)

        run(temp_dot_file, output)

        os.remove(temp_dot_file)
        return

    click.echo("Error: provider is required.")


def generate_terraform_graph(filename):
    try:
        with open(filename, "w") as dot_file:
            subprocess.run(
                ["terraform", "graph"],
                check=True,
                stdout=dot_file,
                stderr=subprocess.PIPE,
            )

        printd("Terraform graph generated successfully.")

    except subprocess.CalledProcessError as e:
        printd(f"Error generating Terraform graph:\n{e.stderr.decode('utf-8')}")
        raise e


def run(input, output):
    printd(f"Input: {input}")
    printd(f"Output: {output}")

    graph = parse_dot(input)
    convert_to_diagrams(graph, output)
