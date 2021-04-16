from qcengine.util import execute
from mmic.components.blueprints import SpecificComponent
from typing import Any, Dict, Tuple
from ..models import CmdOutput, CmdInput
import ntpath
import os

__all__ = ["CmdComponent"]


class CmdComponent(SpecificComponent):
    @classmethod
    def input(cls):
        return CmdInput

    @classmethod
    def output(cls):
        return CmdOutput

    def execute(
        self,
        inputs: Dict[str, Any],
    ) -> Tuple[bool, Dict[str, Any]]:

        if isinstance(inputs, dict):
            inputs = self.input()(**inputs)

        env = os.environ.copy()
        scratch_directory = inputs.scratch_directory

        if inputs.config:
            env["MKL_NUM_THREADS"] = str(config.ncores)
            env["OMP_NUM_THREADS"] = str(config.ncores)

            scratch_directory = config.scratch_directory

        infiles = {}
        if inputs.infiles:
            flag = inputs.as_binary or "r"
            for fpath in inputs.infiles:
                fname = ntpath.basename(fpath)
                with open(fpath, flag) as fp:
                    infiles[fname] = fp.read()

        exe_success, proc = execute(
            command=inputs.command,
            infiles=infiles,
            outfiles=inputs.outfiles,
            outfiles_load=inputs.outfiles_load,
            scratch_directory=scratch_directory,
            scratch_name=inputs.scratch_name,
            scratch_messy=inputs.scratch_messy,
            timeout=inputs.timeout,
            environment=env,
        )

        if exe_success:
            if proc.get("stderr"):
                if inputs.raise_err:
                    raise RuntimeError(proc.get("stderr"))
            return exe_success, self.output()(
                outfiles=proc.get("outfiles"),
                stdout=proc.get("stdout"),
                stderr=proc.get("stderr"),
                scratch_directory=proc.get("scratch_directory"),
            )
        else:
            raise RuntimeError(proc.get("stderr"))