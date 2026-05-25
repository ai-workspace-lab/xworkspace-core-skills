import importlib.util
import json
import shutil
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_it_infra_video.py"
FIXTURE = ROOT / "tests/fixtures/it-infra-chain"


spec = importlib.util.spec_from_file_location("build_it_infra_video", SCRIPT)
runner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)


def write_png(path: Path, rgb: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = height = 16
    raw = b"".join(b"\x00" + bytes(rgb) * width for _ in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def copy_fixture(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    shutil.copytree(FIXTURE, project)
    write_png(project / "assets/images/001-control-plane.png", (21, 91, 255))
    write_png(project / "assets/images/002-data-plane.png", (24, 191, 166))
    write_png(project / "assets/images/003-observability.png", (73, 217, 255))
    return project


class BuildItInfraVideoTest(unittest.TestCase):
    def test_manifest_drives_config_and_html_without_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = copy_fixture(Path(tmp))

            code = runner.main(
                [
                    "--project-dir",
                    str(project),
                    "--title",
                    "Service Mesh fixture",
                    "--audio-mode",
                    "none",
                ]
            )

            self.assertEqual(code, 1)
            self.assertFalse((project / "index.html").exists())

            code = runner.main(
                [
                    "--project-dir",
                    str(project),
                    "--title",
                    "Service Mesh fixture",
                    "--audio-mode",
                    "tone",
                    "--section-duration",
                    "1.2",
                ]
            )

            self.assertEqual(code, 0)
            config = json.loads((project / "video.config.json").read_text(encoding="utf-8"))
            html = (project / "index.html").read_text(encoding="utf-8")

            self.assertEqual(config["timelineColumns"], 3)
            self.assertEqual(len(config["sections"]), 3)
            self.assertEqual(config["sections"][0]["image"], "assets/images/001-control-plane.png")
            self.assertEqual(config["sections"][1]["start"], 1.2)
            self.assertEqual(html.count('id="bgm"'), 1)
            self.assertEqual(html.count('id="scene-service-mesh-control-plane"'), 1)
            self.assertEqual(html.count('data-track-index="1"'), 3)
            self.assertEqual(html.count('data-track-index="5"'), 3)
            self.assertIn(
                "Render not executed",
                (project / "DELIVERY.md").read_text(encoding="utf-8"),
            )

    def test_requires_prepared_task_scope_when_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            project = copy_fixture(tmp_path)

            code = runner.main(
                [
                    "--project-dir",
                    str(project),
                    "--title",
                    "Service Mesh fixture",
                    "--audio-mode",
                    "tone",
                    "--require-task-scope",
                    "--session-key",
                    "draft:1779524982823421-3",
                    "--run-id",
                    "turn-1779685283403237342",
                ]
            )

            self.assertEqual(code, 1)

            scoped_project = (
                tmp_path
                / "workspace"
                / "tasks"
                / "draft_1779524982823421-3"
                / "turn-1779685283403237342"
            )
            shutil.copytree(project, scoped_project)
            code = runner.main(
                [
                    "--project-dir",
                    str(scoped_project),
                    "--title",
                    "Service Mesh fixture",
                    "--audio-mode",
                    "tone",
                    "--require-task-scope",
                    "--session-key",
                    "draft:1779524982823421-3",
                    "--run-id",
                    "turn-1779685283403237342",
                ]
            )

            self.assertEqual(code, 0)
            delivery = (scoped_project / "DELIVERY.md").read_text(encoding="utf-8")
            self.assertIn("tasks/draft_1779524982823421-3/turn-1779685283403237342", delivery)

    def test_rejects_manifest_image_that_is_not_real_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = copy_fixture(Path(tmp))
            (project / "assets/images/002-data-plane.png").write_text("<svg></svg>", encoding="utf-8")

            rows = runner.parse_markdown_table(project / "assets/images/manifest.md")
            self.assertEqual(len(rows), 3)

            with self.assertRaisesRegex(runner.BuildError, "not a real PNG"):
                runner.read_manifest(project / "assets/images/manifest.md", project)


if __name__ == "__main__":
    unittest.main()
