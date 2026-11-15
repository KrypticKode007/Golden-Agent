from pydantic import BaseModel
from golden_agent.runtime.sandbox import SandboxRunner


class VerificationReport(BaseModel):
    passed: bool
    feedback: str


class VerifierWorker:
    """Runs syntax/assertion checks inside the isolated sandbox before accepting code outputs."""

    def __init__(self, sandbox: SandboxRunner | None = None) -> None:
        self.sandbox = sandbox or SandboxRunner(prefer_docker=False)

    async def verify_python_snippet(self, code: str) -> VerificationReport:
        try:
            compile(code, "<golden_verify>", "exec")
        except SyntaxError as exc:
            return VerificationReport(passed=False, feedback=f"SyntaxError at line {exc.lineno}: {exc.msg}")

        res = await self.sandbox.run_python(code)
        if res.exit_code != 0:
            return VerificationReport(passed=False, feedback=f"Runtime error (exit {res.exit_code}): {res.stderr.strip()}")
        return VerificationReport(passed=True, feedback=res.stdout.strip() or "Verified clean.")
