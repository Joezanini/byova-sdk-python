"""Hatch build hook: generate gRPC stubs from vendored BYOVA proto files."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Generate Python gRPC stubs before packaging."""

    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: dict) -> None:
        root = Path(self.root)
        proto_dir = root / "src/webex_byova/media/_internal/proto"
        out_dir = root / "src/webex_byova/media/_internal/generated"
        out_dir.mkdir(parents=True, exist_ok=True)

        proto_files = sorted(proto_dir.glob("*.proto"))
        if not proto_files:
            return

        cmd = [
            sys.executable,
            "-m",
            "grpc_tools.protoc",
            f"-I{proto_dir}",
            f"--python_out={out_dir}",
            f"--grpc_python_out={out_dir}",
            f"--pyi_out={out_dir}",
            *[str(p) for p in proto_files],
        ]
        subprocess.run(cmd, check=True)

        # Fix relative imports in generated grpc modules.
        for grpc_file in out_dir.glob("*_grpc.py"):
            text = grpc_file.read_text(encoding="utf-8")
            text = text.replace(
                "import byova_common_pb2 as byova__common__pb2",
                "from webex_byova.media._internal.generated import byova_common_pb2 as byova__common__pb2",
            )
            text = text.replace(
                "import voicevirtualagent_pb2 as voicevirtualagent__pb2",
                "from webex_byova.media._internal.generated import voicevirtualagent_pb2 as voicevirtualagent__pb2",
            )
            text = text.replace(
                "import byova_common_pb2 as byova__common__pb2",
                "from webex_byova.media._internal.generated import byova_common_pb2 as byova__common__pb2",
            )
            grpc_file.write_text(text, encoding="utf-8")

        for pb2_file in out_dir.glob("*_pb2.py"):
            text = pb2_file.read_text(encoding="utf-8")
            if "import byova_common_pb2" in text:
                text = text.replace(
                    "import byova_common_pb2 as byova__common__pb2",
                    "from webex_byova.media._internal.generated import byova_common_pb2 as byova__common__pb2",
                )
                pb2_file.write_text(text, encoding="utf-8")

        init_file = out_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Generated gRPC/protobuf stubs (do not edit)."""\n', encoding="utf-8")
