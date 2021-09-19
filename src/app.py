import click


@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name', help='The person to greet.') # pylint: disable=syntax-error
def hello(count, name):
  """Simple program that greets NAME for a total of COUNT times."""
  for _ in range(count):
    click.echo(   f"Hello {name}!")


if __name__ == '__main__':
  # pylint: disable=no-value-for-parameter
  hello()
