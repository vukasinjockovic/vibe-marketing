"""Service chain executor with automatic fallback.

Usage:
    from lib.service_chain import execute_with_fallback

    result, service_used = execute_with_fallback(
        capability="image_generation",
        execute_fn=lambda svc: call_image_api(svc),
        agent_name="vibe-image-generator",
        campaign_id="abc123",
        task_id="xyz789",
    )
"""
import json
import os
import subprocess
import sys
import time
from typing import Any, Callable, Optional, Tuple


def _run_convex(fn: str, args: dict) -> str:
    env = os.environ.copy()
    url = env.get("CONVEX_SELF_HOSTED_URL", "http://localhost:3210")
    cmd = ["npx", "convex", "run", fn, json.dumps(args), "--url", url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Convex error: {result.stderr}")
    return result.stdout.strip()


def resolve_chain(
    capability: str,
    campaign_id: Optional[str] = None,
    batch_id: Optional[str] = None,
) -> list[dict]:
    """Resolve the full fallback chain for a capability."""
    args: dict = {"categoryName": capability}

    if campaign_id or batch_id:
        fn = "services:resolveChainWithOverrides"
        if campaign_id:
            args["campaignId"] = campaign_id
        if batch_id:
            args["contentBatchId"] = batch_id
    else:
        fn = "services:resolveChain"

    result = _run_convex(fn, args)
    if not result or result in ("null", "[]"):
        return []
    return json.loads(result)


def _log_execution(
    service_id: str,
    category_name: str,
    agent_name: str,
    status: str,
    retry_attempt: int,
    duration_ms: Optional[int] = None,
    error_message: Optional[str] = None,
    task_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    batch_id: Optional[str] = None,
    estimated_cost: Optional[float] = None,
) -> None:
    """Log a service execution attempt to Convex."""
    args: dict = {
        "serviceId": service_id,
        "categoryName": category_name,
        "agentName": agent_name,
        "status": status,
        "retryAttempt": retry_attempt,
    }
    if duration_ms is not None:
        args["durationMs"] = duration_ms
    if error_message:
        args["errorMessage"] = error_message[:500]
    if task_id:
        args["taskId"] = task_id
    if campaign_id:
        args["campaignId"] = campaign_id
    if batch_id:
        args["contentBatchId"] = batch_id
    if estimated_cost is not None:
        args["estimatedCost"] = estimated_cost

    try:
        _run_convex("services:logServiceExecution", args)
    except Exception as e:
        print(f"Warning: failed to log execution: {e}", file=sys.stderr)


def execute_with_fallback(
    capability: str,
    execute_fn: Callable[[dict], Any],
    agent_name: str,
    campaign_id: Optional[str] = None,
    batch_id: Optional[str] = None,
    task_id: Optional[str] = None,
) -> Tuple[Any, dict]:
    """Execute a capability using the fallback chain.

    Args:
        capability: The capability name (e.g. "image_generation")
        execute_fn: Function that takes a service dict and returns result.
                   Should raise on failure.
        agent_name: Name of the calling agent (for logging)
        campaign_id: Optional campaign ID for override resolution
        batch_id: Optional batch ID for override resolution
        task_id: Optional task ID for logging

    Returns:
        Tuple of (result, service_used_dict)

    Raises:
        RuntimeError: If all services in the chain fail
    """
    chain = resolve_chain(capability, campaign_id, batch_id)
    if not chain:
        raise RuntimeError(
            f"No active services for capability '{capability}'. "
            f"Configure at least one provider in the dashboard."
        )

    errors = []
    for i, service in enumerate(chain):
        service_id = service.get("_id", "")
        start = time.time()

        try:
            result = execute_fn(service)
            duration_ms = int((time.time() - start) * 1000)

            _log_execution(
                service_id=service_id,
                category_name=capability,
                agent_name=agent_name,
                status="success",
                retry_attempt=i,
                duration_ms=duration_ms,
                task_id=task_id,
                campaign_id=campaign_id,
                batch_id=batch_id,
            )

            return result, service

        except TimeoutError as e:
            duration_ms = int((time.time() - start) * 1000)
            error_msg = str(e)
            errors.append(f"{service.get('displayName', service.get('name'))}: timeout - {error_msg}")

            _log_execution(
                service_id=service_id,
                category_name=capability,
                agent_name=agent_name,
                status="timeout",
                retry_attempt=i,
                duration_ms=duration_ms,
                error_message=error_msg,
                task_id=task_id,
                campaign_id=campaign_id,
                batch_id=batch_id,
            )

        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            error_msg = str(e)

            status = "rate_limited" if "rate" in error_msg.lower() else "failed"
            errors.append(f"{service.get('displayName', service.get('name'))}: {error_msg}")

            _log_execution(
                service_id=service_id,
                category_name=capability,
                agent_name=agent_name,
                status=status,
                retry_attempt=i,
                duration_ms=duration_ms,
                error_message=error_msg,
                task_id=task_id,
                campaign_id=campaign_id,
                batch_id=batch_id,
            )

    raise RuntimeError(
        f"All {len(chain)} services failed for capability '{capability}':\n"
        + "\n".join(f"  [{i+1}] {e}" for i, e in enumerate(errors))
    )
