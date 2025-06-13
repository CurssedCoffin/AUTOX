from rich.console import Console
from loguru import logger

# define logger
console = Console()
logger.remove()

def _log_formatter(record: dict) -> str:
    """Log message formatter"""
    color_map = {
        'TRACE': 'dim blue',
        'DEBUG': 'cyan',
        'INFO': 'bold',
        'SUCCESS': 'bold green',
        'WARNING': 'yellow',
        'ERROR': 'bold red',
        'CRITICAL': 'bold white on red'
    }
    lvl_color = color_map.get(record['level'].name, 'cyan')
    return (
        '[not bold green]{time:YYYY/MM/DD HH:mm:ss}[/not bold green] | {level}'
        + f'  - [{lvl_color}]{{message}}[/{lvl_color}]'
    )

logger.add(
    console.print,
    level='TRACE',
    format=_log_formatter,
    colorize=False,
    # enqueue=True,
)