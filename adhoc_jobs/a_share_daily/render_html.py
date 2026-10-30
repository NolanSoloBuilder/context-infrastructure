"""Compatibility entry point for the shared US/A-share HTML presentation."""
import argparse
from pathlib import Path
import subprocess

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    if source.name != 'report.md':
        parser.error('Expected a dated report.md')
    subprocess.run(['node', str(Path(__file__).with_suffix('.mjs')), '--out', str(source.parent),
                    '--report-date', source.parent.name], check=True)
