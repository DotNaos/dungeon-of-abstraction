import sys
from pathlib import Path
from neurodungeon import run


def test_report_written(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["neurodungeon", "--goal", "hi", "--persist-dir", str(tmp_path)])
    run.cli()
    report_path = tmp_path / "cli_run" / "report.md"
    assert report_path.exists()
