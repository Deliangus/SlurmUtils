#############################################################
# @Time        :   2022/11/29 05:12:03
# @FileName    :   shutils.py
# @FileDir     :   ~/project/SlurmUtils
# @Author      :   Yuxiang Luo
# @Email       :   luo.929@osu.edu
# @Software    :   VSCode
# @Organization:   Center of Weldability, The Ohio State University
# @Usage       :   #TODO: Add Usage
#############################################################

import json
from pathlib import Path
from typing import Dict, List, Union


LICENSE_USAGE = {
    28: 70,
    14: 50,
    8: 40,
    7: 48,
    1: 12,
}
CONCURRENCY_CORE_USAGE = {
    28: 28,
    14: 28,
    8: 8,
    7: 28,
    1: 8,
}
TIME_CORE_USAGE = {28: 8, 14: 13, 8: 13, 7: 13, 1: 84}

def make_shell_script(
    script_path,
    content,
    hours=2,
    minutes=0,
    license: dict = {},
    cores=28,
    account='PAS2138',
    modules: List = [],
    python_env: str = "",
    gpus: int = 0,
    env_vars: Dict = {},
    set_flag: Union[str, None] = "x",
    sbatch_log: Union[Path, None] = None,
):
    cores = max(cores, 8)
    env_var_decls = []
    for vname, vval in env_vars.items():
        env_var_decls.extend([f"{vname}={vval}", f"export {vname}"])
    sbatch_log_file = "output/%j.log" if (sbatch_log is None) else sbatch_log
    shell_script_head = [
        "#!/bin/sh",
        f"#SBATCH --time={hours:02d}:{minutes:02d}:00",
        f"#SBATCH --account={account}",
        f"#SBATCH --output={sbatch_log_file}",
        "#SBATCH --mail-type=FAIL",
        f"#SBATCH --ntasks={cores}",
        *[f"#SBATCH -L {key}@osc:{val}" for key, val in license.items()],
        f"#SBATCH --gpus-per-node={gpus}" if gpus > 0 else "",
        # "source ./sh01_sbatch_head.sh",
        # "if test -z $FEA_MODEL; then",
        # "\tFEA_MODEL=2D_FEA",
        # "\texport FEA_MODEL",
        # "fi",
        *env_var_decls,
        # "if test -z $OBS_TYPE; then",
        # f"\tOBS_TYPE={obs_type}",
        # "\texport OBS_TYPE",
        # "fi",
        *[f"module load {key}" for key in modules],
        # "module load miniconda3",
        # "module load cuda/11.2.2",
        # "module load project/project/cres",
        # "module load abaqus/2021",
        f"source activate {python_env}" if python_env != "" else "",
        # "source activate urlfea",
        # "conda env list",
        # "source ./sh01_copy_code.sh",
        # f"cp $0 \"$OUTPUT_DIR/{script_path.name}\"",
        # "cd \"$OUTPUT_DIR\" || exit",
        "" if set_flag is None else f"set -{set_flag}",
    ]
    shell_script_tail = [
        "mv \"$SLURM_SUBMIT_DIR/output/$SLURM_JOB_ID.log\" \"$OUTPUT_DIR/sbatch.log\"",
    ]

    with open(script_path, 'w') as fout:
        fout.write("\n".join(shell_script_head + content + shell_script_tail))


def make_command(head, params_dict: Dict, stdout_redirect: str = ""):
    command = [
        head, *[f"--{key}={val}" for key, val in params_dict.items()],
        f">> {stdout_redirect}" if len(stdout_redirect) > 0 else ""
    ]
    return " ".join(command)
