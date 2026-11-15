import asyncio
import os
import sys
import tempfile
from pathlib import Path
from pydantic import BaseModel
from golden_agent.config.settings import Settings, get_settings


class ExecutionResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False
    backend: str = "subprocess"


class SandboxRunner:
    """Executes untrusted Python or shell code inside Docker when available,
    with an isolated temporary-directory subprocess fallback.
    """

    def __init__(self, settings: Settings | None = None, prefer_docker: bool = True) -> None:
        self.settings = settings or get_settings()
        self.prefer_docker = prefer_docker

    def _docker_available(self) -> bool:
        if not self.prefer_docker:
            return False
        try:
            import docker  # type: ignore[import-untyped]

            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False

    async def run_python(self, code: str, timeout: int | None = None) -> ExecutionResult:
        effective_timeout = timeout or self.settings.sandbox_timeout_seconds
        if self._docker_available():
            return await asyncio.to_thread(self._run_in_docker, code, effective_timeout)
        return await self._run_in_subprocess(code, effective_timeout)

    def _run_in_docker(self, code: str, timeout: int) -> ExecutionResult:
        import docker  # type: ignore[import-untyped]

        client = docker.from_env()
        with tempfile.TemporaryDirectory(prefix="golden_sbx_") as tmpdir:
            script_path = Path(tmpdir) / "task.py"
            script_path.write_text(code, encoding="utf-8")

            container = None
            try:
                container = client.containers.run(
                    image=self.settings.docker_sandbox_image,
                    command=["python", "/workspace/task.py"],
                    volumes={tmpdir: {"bind": "/workspace", "mode": "ro"}},
                    working_dir="/workspace",
                    network_mode="none",
                    mem_limit=self.settings.sandbox_memory_limit,
                    read_only=True,
                    detach=True,
                )
                status = container.wait(timeout=timeout)
                logs_out = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
                logs_err = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")
                return ExecutionResult(
                    exit_code=int(status.get("StatusCode", 1)),
                    stdout=logs_out,
                    stderr=logs_err,
                    backend="docker",
                )
            except Exception as exc:
                return ExecutionResult(
                    exit_code=124,
                    stdout="",
                    stderr=f"Docker sandbox execution error: {exc}",
                    timed_out="timed out" in str(exc).lower(),
                    backend="docker",
                )
            finally:
                if container is not None:
                    try:
                        container.remove(force=True)
                    except Exception:
                        pass

    async def _run_in_subprocess(self, code: str, timeout: int) -> ExecutionResult:
        with tempfile.TemporaryDirectory(prefix="golden_sub_") as tmpdir:
            script_path = Path(tmpdir) / "task.py"
            script_path.write_text(code, encoding="utf-8")

            safe_env = {
                "PATH": os.environ.get("PATH", ""),
                "HOME": tmpdir,
                "TMPDIR": tmpdir,
                "PYTHONDONTWRITEBYTECODE": "1",
            }

            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                "-I",
                str(script_path),
                cwd=tmpdir,
                env=safe_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                return ExecutionResult(
                    exit_code=proc.returncode or 0,
                    stdout=stdout_b.decode("utf-8", errors="replace"),
                    stderr=stderr_b.decode("utf-8", errors="replace"),
                    backend="subprocess",
                )
            except TimeoutError:
                proc.kill()
                await proc.communicate()
                return ExecutionResult(
                    exit_code=124,
                    stdout="",
                    stderr=f"Execution timed out after {timeout}s.",
                    timed_out=True,
                    backend="subprocess",
                      )
              
