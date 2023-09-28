from sys import argv, stdin, stdout, exit
from . import ansiprint, parse


if len(argv) == 1 and stdin.isatty():
    from textwrap import dedent

    usage = """
    Usage: python -m ansimarkup [<arg> [<arg> ...]]

    Example usage:
      python -m ansimarkup '<b>Bold</b>' '<r>Red</r>'
      python -m ansimarkup '<b><r>Bold Red</r></b>'
      python -m ansimarkup < input-with-markup.txt
      echo '<b>Bold</b>' | python -m ansimarkup
    """

    print(dedent(usage).strip())
    exit(0)

if not stdin.isatty():
    for line in stdin:
        stdout.write(parse(line))
else:
    ansiprint(*argv[1:])
