# supersemgrep

## Prerequisites

You need to [install Semgrep system-wide](https://github.com/returntocorp/semgrep#getting-started).

## Installation

Get started with

```sh
git clone https://github.com/returntocorp/supersemgrep
cd supersemgrep
conda env create -f supersemgrep.yml
conda activate supersemgrep
SEMGREP_SKIP_BIN=true pip install semgrep
conda run python -m src.supersemgrep --config=s/underyx:no-wiki-in-private-projects
```
