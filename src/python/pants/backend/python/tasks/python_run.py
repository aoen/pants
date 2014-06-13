# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import signal
import tempfile

from twitter.common.python.pex import PEX
from twitter.common.python.pex_builder import PEXBuilder

from pants.backend.python.python_chroot import PythonChroot
from pants.backend.python.targets.python_binary import PythonBinary
from pants.backend.python.tasks.python_task import PythonTask
from pants.base.exceptions import TaskError
from pants.base.workunit import WorkUnit


class PythonRun(PythonTask):
  @staticmethod
  def is_binary(target):
    return isinstance(target, PythonBinary)

  def __init__(self, context, workdir):
    super(PythonRun, self).__init__(context, workdir)

  def execute(self):
    binaries = self.context.targets(self.is_binary)

    if len(binaries) == 0:
      raise TaskError('No python_binary target specified.')
    # Run the first binary only.
    binary = binaries[0]

    if binary.compatibility:
      interpreter = self.select_interpreter(binary.compatibility)
    else:
      interpreter = self.interpreter

    builder = PEXBuilder(tempfile.mkdtemp(), interpreter=interpreter, pex_info=binary.pexinfo)

    chroot = PythonChroot(
      targets=[binary],
      builder=builder,
      platforms=binary.platforms,
      interpreter=interpreter,
      conn_timeout=self.conn_timeout)

    builder = chroot.dump()
    builder.freeze()
    pex = PEX(builder.path(), interpreter=interpreter)
    with self.context.new_workunit(name='run', labels=[WorkUnit.RUN]):
      po = pex.run(blocking=False)
      try:
        return po.wait()
      except KeyboardInterrupt:
        po.send_signal(signal.SIGINT)
        raise
