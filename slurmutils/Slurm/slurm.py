import subprocess
from collections import defaultdict
from typing import Dict


def get_job_dict():
    """
    Return {job_name: (state, cluster, job_id)} for *all* visible jobs.
    Falls back gracefully if federation/cluster info is absent.
    """
    # Ask every cluster we can see (requires Slurm ≥20.02 with Federation or dbd)

    fields = ["Name", "StateCompact", "Cluster"]
    cmd = ["squeue", "--noheader", f"-O{','.join(fields)}"]

    fmt = "%.8j|%i|%T|%B"  # id | state | cluster (M == cluster in squeue ≥22.05)
    user_name = subprocess.getoutput("whoami")
    try:
        cmd = [
            "squeue",
            f"--user={user_name}",
            "--noheader",
            "--clusters=all",
            "-o",
            fmt,
        ]
        out = subprocess.check_output(cmd, text=True).strip().splitlines()
    except subprocess.CalledProcessError:
        # Fallback: ask only the local cluster
        cmd = ["squeue", f"--user={user_name}", "--noheader", "-o", fmt]
        out = subprocess.check_output(cmd, text=True).strip().splitlines()

    jobs: Dict[str, Dict] = {}
    for line in out:
        # If the user is on a single cluster, the third field will be empty;
        # use $SLURM_CLUSTER_NAME or 'local' instead.
        fields = line.split("|")
        job_name, job_id, state, cluster = fields
        jobs[job_name] = {
            "state": state,
            "cluster": cluster,
            "job_id": int(job_id),
        }

    return jobs


if __name__ == "__main__":
    print(get_job_dict())
