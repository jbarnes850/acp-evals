"""
Supervisor pattern: Centralized coordination.

A supervisor agent delegates tasks to worker agents and combines results.
Based on LangChain's research on supervisor patterns.
"""

import asyncio
from datetime import datetime
from typing import Any

from acp_evals.patterns.base import AgentInfo, AgentPattern


class SupervisorPattern(AgentPattern):
    """
    Supervisor multi-agent pattern.

    First agent acts as supervisor, delegating to and coordinating other agents.
    """

    def __init__(
        self,
        supervisor: AgentInfo,
        workers: list[AgentInfo],
        name: str | None = None,
    ):
        """
        Initialize supervisor pattern.

        Args:
            supervisor: The supervisor agent
            workers: List of worker agents
            name: Optional pattern name
        """
        # Supervisor is first, then workers
        all_agents = [supervisor] + workers
        super().__init__(all_agents, name)
        self.supervisor = supervisor
        self.workers = workers

    @property
    def pattern_type(self) -> str:
        return "supervisor"

    async def execute(
        self,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute supervisor pattern.

        Args:
            task: Task to execute
            context: Optional context

        Returns:
            Execution results with delegation tracking
        """
        start_time = datetime.now()

        # Phase 1: Supervisor creates delegation plan
        supervisor_start = datetime.now()
        supervisor_prompt = f"""You are a supervisor agent coordinating {len(self.workers)} worker agents.

Task: {task}

Available workers:
{self._format_workers()}

Create a delegation plan that assigns specific subtasks to each worker.
Format your response as:
1. Worker: [worker_name] - Task: [specific subtask]
2. Worker: [worker_name] - Task: [specific subtask]
...

After the delegation plan, provide instructions for combining the results."""

        client = self._get_client(self.supervisor)
        message = self._create_message(supervisor_prompt)

        try:
            run = await client.run_sync(
                agent=self.supervisor.name,
                input=[message]
            )

            delegation_plan = run.output[0].parts[0].content if run.output else ""
            supervisor_latency = (datetime.now() - supervisor_start).total_seconds()

        except Exception as e:
            return {
                "pattern": self.pattern_type,
                "error": f"Supervisor failed: {str(e)}",
                "success": False,
            }

        # Phase 2: Parse delegation and execute workers
        delegations = self._parse_delegation_plan(delegation_plan)
        worker_results = []

        # Execute workers concurrently
        worker_tasks = []
        for delegation in delegations:
            worker_name = delegation["worker"]
            subtask = delegation["task"]

            # Find worker agent
            worker = next((w for w in self.workers if w.name == worker_name), None)
            if not worker:
                continue

            # Create async task for worker
            worker_task = self._execute_worker(worker, subtask, task)
            worker_tasks.append(worker_task)

        # Wait for all workers
        if worker_tasks:
            worker_results = await asyncio.gather(*worker_tasks, return_exceptions=True)

        # Phase 3: Supervisor combines results
        combine_start = datetime.now()
        combine_prompt = f"""You are the supervisor agent. The workers have completed their tasks.

Original task: {task}

Your delegation plan:
{delegation_plan}

Worker results:
{self._format_worker_results(delegations, worker_results)}

Now combine these results into a final answer for the original task."""

        try:
            run = await client.run_sync(
                agent=self.supervisor.name,
                input=[self._create_message(combine_prompt)]
            )

            final_output = run.output[0].parts[0].content if run.output else ""
            combine_latency = (datetime.now() - combine_start).total_seconds()

        except Exception as e:
            final_output = f"Failed to combine results: {str(e)}"
            combine_latency = (datetime.now() - combine_start).total_seconds()

        end_time = datetime.now()

        # Calculate overhead
        total_worker_latency = sum(
            r["latency"] for r in worker_results
            if isinstance(r, dict) and "latency" in r
        )
        supervisor_overhead = supervisor_latency + combine_latency
        parallelization_efficiency = (
            total_worker_latency / max(
                r["latency"] for r in worker_results
                if isinstance(r, dict) and "latency" in r
            )
            if worker_results and any(isinstance(r, dict) for r in worker_results)
            else 0
        )

        return {
            "pattern": self.pattern_type,
            "final_output": final_output,
            "delegation_plan": delegation_plan,
            "worker_results": worker_results,
            "total_latency": (end_time - start_time).total_seconds(),
            "supervisor_overhead": supervisor_overhead,
            "parallelization_efficiency": parallelization_efficiency,
            "workers_used": len(worker_results),
            "success": bool(final_output and not final_output.startswith("Failed")),
        }

    def _format_workers(self) -> str:
        """Format worker information for supervisor."""
        lines = []
        for worker in self.workers:
            line = f"- {worker.name}"
            if worker.role:
                line += f": {worker.role}"
            if worker.capabilities:
                line += f" (capabilities: {', '.join(worker.capabilities)})"
            lines.append(line)
        return "\n".join(lines)

    def _parse_delegation_plan(self, plan: str) -> list[dict[str, str]]:
        """Parse delegation plan from supervisor."""
        delegations = []
        lines = plan.split("\n")

        for line in lines:
            # Look for pattern: "Worker: [name] - Task: [task]"
            if "Worker:" in line and "Task:" in line:
                try:
                    parts = line.split(" - ")
                    worker_part = parts[0].split("Worker:")[1].strip()
                    task_part = parts[1].split("Task:")[1].strip()

                    # Clean up formatting
                    worker_name = worker_part.strip(". ")
                    task_desc = task_part.strip(". ")

                    delegations.append({
                        "worker": worker_name,
                        "task": task_desc,
                    })
                except:
                    continue

        return delegations

    async def _execute_worker(
        self,
        worker: AgentInfo,
        subtask: str,
        original_task: str,
    ) -> dict[str, Any]:
        """Execute a single worker agent."""
        start_time = datetime.now()

        worker_prompt = f"""You are a worker agent with the following role: {worker.role or 'general assistant'}

Original task context: {original_task}

Your specific subtask: {subtask}

Complete your subtask and provide a clear, focused response."""

        try:
            client = self._get_client(worker)
            run = await client.run_sync(
                agent=worker.name,
                input=[self._create_message(worker_prompt)]
            )

            response = run.output[0].parts[0].content if run.output else ""

            return {
                "worker": worker.name,
                "subtask": subtask,
                "response": response,
                "latency": (datetime.now() - start_time).total_seconds(),
                "success": True,
            }

        except Exception as e:
            return {
                "worker": worker.name,
                "subtask": subtask,
                "error": str(e),
                "latency": (datetime.now() - start_time).total_seconds(),
                "success": False,
            }

    def _format_worker_results(
        self,
        delegations: list[dict[str, str]],
        results: list[Any],
    ) -> str:
        """Format worker results for supervisor."""
        formatted = []

        for i, result in enumerate(results):
            if isinstance(result, dict) and result.get("success"):
                formatted.append(
                    f"Worker: {result['worker']}\n"
                    f"Task: {result['subtask']}\n"
                    f"Result: {result['response']}\n"
                )
            elif isinstance(result, dict):
                formatted.append(
                    f"Worker: {result['worker']}\n"
                    f"Task: {result['subtask']}\n"
                    f"Error: {result.get('error', 'Unknown error')}\n"
                )

        return "\n---\n".join(formatted)
