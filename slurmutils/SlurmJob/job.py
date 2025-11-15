from typing import Dict, List, Union, Tuple
from pathlib import Path
from slurmutils.Slurm.shellUtils import make_shell_script


class SlurmJob:

    account: str
    content: List[str]

    licenses: Dict[str, int]

    modules: List[str]
    module_profile: Union[str, None]

    env_vars: Dict[str, str]
    notify_email: List[str]
    alias: Dict[str, str]
    paths: List[str]

    days: int
    hours: int
    minutes: int
    seconds: int

    cpus_per_task: int
    gpus: int
    memory: int

    python_home: Union[Path, None]
    set_flag: str

    pre_content: List[str]

    partition: Union[str, None]
    job_name: Union[str, None]

    interactive: bool

    working_dir: Union[Path, None]

    sbatch_args: Dict[str, Union[str, int, bool]]

    output_storage: List[str]

    def __init__(
        self,
        account: str,
        content: List[str],
        licenses: Dict[str, int],
        modules: List[str],
        env_vars: Dict[str, str],
        notify_email: List[str],
        aliases: Dict[str, str],
        paths: List[str],
        sbatch_args: Dict[str, Union[str, int, bool]],
        output_storage: List[str],
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        cpus_per_task: int = 1,
        gpus: int = 0,
        memory: int = 0,
        module_profile: Union[str, None] = None,
        python_home: Union[Path, None] = None,
        set_flag: str = "x",
        job_name: str = "",
        partition: str = "",
        interactive: bool = False,
        working_dir: Union[Path, None] = None,
    ):
        self.job_name = job_name
        self.partition = partition
        self.gpus = gpus
        self.cpus_per_task = cpus_per_task
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

        self.memory = memory
        self.notify_email = notify_email
        self.set_flag = set_flag
        self.interactive = interactive
        self.aliases = aliases
        self.paths = paths
        self.account = account
        self.python_home = python_home
        self.modules = modules
        self.content = content
        self.licenses = licenses
        self.working_dir = working_dir

        self.module_profile = module_profile
        self.env_vars = env_vars
        self.sbatch_args = sbatch_args
        self.output_storage = output_storage

    def prepend(self, content: List[str]):
        """Append content to the job script."""
        self.content = [*content, *self.content]

    def append(self, content: List[str]):
        """Append content to the job script."""
        self.content = [*self.content, *content]

    def write(
        self,
        job_name: str,
        script_path: Path,
        log_file: Union[Path, None] = None,
        delete_log_on_completion: bool = False,
        delete_script_on_completion: bool = False,
    ):
        job_name = "" if (self.job_name is None) else self.job_name
        python_env = str(self.python_home / "bin" /
                         "activate") if self.python_home else ""
        log_file = log_file if log_file is not None else script_path.with_suffix(
            '.log')
        set_flags = set(list(self.set_flag))

        if (delete_log_on_completion):
            self.append([f"rm -f {log_file}"])
            set_flags.add('e')
        if (delete_script_on_completion):
            self.append([f"rm -f {script_path}"])
            set_flags.add('e')

        preset_content = []
        if (self.working_dir is not None):
            preset_content.append(f"cd {self.working_dir}")

        make_shell_script(
            account=self.account,
            script_path=script_path,
            jobname=job_name,
            gpus=self.gpus,
            cores=self.cpus_per_task,
            hours=self.hours + self.days * 24,
            minutes=self.minutes,
            seconds=self.seconds,
            memory=self.memory,
            notifies=self.notify_email,
            sbatch_log=log_file,
            set_flag=''.join(set_flags),
            interactive=self.interactive,
            aliases=self.aliases,
            paths=self.paths,
            python_env=python_env,
            modules=self.modules,
            content=self.content,
            license=self.licenses,
            pre_set_content=preset_content,
            module_profie=self.module_profile,
            env_vars=self.env_vars,
            sbatch_args=self.sbatch_args,
        )
