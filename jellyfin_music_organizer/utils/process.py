from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
import subprocess
import threading
import queue
import logging
from pathlib import Path

@dataclass
class ProcessResult:
    """Type-safe process execution result."""
    returncode: int
    stdout: str
    stderr: str
    error: Optional[Exception] = None

class ProcessManager:
    """Manage external process execution."""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._active_processes: Dict[int, subprocess.Popen] = {}
        self._output_queues: Dict[int, queue.Queue] = {}

    def run_process(
        self,
        command: List[str],
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> ProcessResult:
        """Run a process and capture its output."""
        try:
            process = subprocess.Popen(
                command,
                cwd=str(cwd) if cwd else None,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Set up output queues
            stdout_queue: queue.Queue = queue.Queue()
            stderr_queue: queue.Queue = queue.Queue()
            
            # Start output reader threads
            def read_output(pipe: Any, q: queue.Queue) -> None:
                for line in pipe:
                    q.put(line)
                    if output_callback:
                        output_callback(line)
                q.put(None)  # Signal EOF

            threading.Thread(
                target=read_output,
                args=(process.stdout, stdout_queue),
                daemon=True
            ).start()
            
            threading.Thread(
                target=read_output,
                args=(process.stderr, stderr_queue),
                daemon=True
            ).start()

            # Collect output
            stdout_lines: List[str] = []
            stderr_lines: List[str] = []
            
            while True:
                if process.poll() is not None:
                    break
                
                try:
                    stdout_line = stdout_queue.get_nowait()
                    if stdout_line is not None:
                        stdout_lines.append(stdout_line)
                except queue.Empty:
                    pass

                try:
                    stderr_line = stderr_queue.get_nowait()
                    if stderr_line is not None:
                        stderr_lines.append(stderr_line)
                except queue.Empty:
                    pass

            return ProcessResult(
                returncode=process.returncode,
                stdout="".join(stdout_lines),
                stderr="".join(stderr_lines)
            )

        except Exception as e:
            self.logger.error(f"Process execution failed: {e}")
            return ProcessResult(
                returncode=-1,
                stdout="",
                stderr="",
                error=e
            ) 