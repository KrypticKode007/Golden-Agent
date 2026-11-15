import asyncio, os, sys, tempfile
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
    def __init__(self, settings: Settings | None = None, prefer_docker: bool = True) -> None:
        self.settings = settings or get_settings()
        self.prefer_docker = prefer_docker

    def _docker_available(self) -> bool:
        if not self.prefer_docker:
            return False
        try:
            import docker  # type: ignore[import-untyped]
            docker.from_env().ping()
            return True
        except Exception:
            return False

    async def run_python(self, code: str, timeout: int | None = None) -> ExecutionResult:
        t = timeout or self.settings.sandbox_timeout_seconds
        return await (asyncio.to_thread(self._run_docker, code, t) if self._docker_available() else self._run_subprocess(code, t))

    def _run_docker(self, code: str, timeout: int) -> ExecutionResult:
        import docker  # type: ignore[import-untyped]
        client = docker.from_env()
        with tempfile.TemporaryDirectory(prefix="golden_sbx_") as tmpdir:
            (Path(tmpdir) / "task.py").write_text(code, encoding="utf-8")
            container = None
            try:
                container = client.containers.run(
                    image=self.settings.docker_sandbox_image, command=["python", "/workspace/task.py"],
                    volumes={tmpdir: {"bind": "/workspace", "mode": "ro"}}, working_dir="/workspace",
                    network_mode="none", mem_limit=self.settings.sandbox_memory_limit, read_only=True, detach=True,
                )
                status = container.wait(timeout=timeout)
                return ExecutionResult(
                    exit_code=int(status.get("StatusCode", 1)),
                    stdout=container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace"),
                    stderr=container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace"), backend="docker",
                )
            except Exception as exc:
                return ExecutionResult(exit_code=124, stdout="", stderr=str(exc), timed_out="timed out" in str(exc).lower(), backend="docker")
            finally:
                if container:
                    try:
                        container.remove(force=True)
                    except Exception:
                        pass

    async def _run_subprocess(self, code: str, timeout: int) -> ExecutionResult:
        with tempfile.TemporaryDirectory(prefix="golden_sub_") as tmpdir:
            script = Path(tmpdir) / "task.py"
            script.write_text(code, encoding="utf-8")
            env = {"PATH": os.environ.get("PATH", ""), "HOME": tmpdir, "TMPDIR": tmpdir, "PYTHONDONTWRITEBYTECODE": "1"}
            proc = await asyncio.create_subprocess_exec(sys.executable, "-I", str(script), cwd=tmpdir, env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            try:
                out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                return ExecutionResult(exit_code=proc.returncode or 0, stdout=out.decode("utf-8", errors="replace"), stderr=err.decode("utf-8", errors="replace"))
            except TimeoutError:
                proc.kill()
                await proc.communicate()
                return ExecutionResult(exit_code=124, stdout="", stderr=f"Timed out after {timeout}s.", timed_out=True)
