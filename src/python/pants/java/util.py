# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import os

from pants.base.workunit import WorkUnit
from pants.java.executor import Executor, SubprocessExecutor
from pants.java.nailgun_executor import NailgunExecutor


def execute_java(classpath, main, jvm_options=None, args=None, executor=None,
                 workunit_factory=None, workunit_name=None, workunit_labels=None):
  """Executes the java program defined by the classpath and main.

  If `workunit_factory` is supplied, does so in the context of a workunit.

  :param list classpath: the classpath for the java program
  :param string main: the fully qualified class name of the java program's entry point
  :param list jvm_options: an optional sequence of options for the underlying jvm
  :param list args: an optional sequence of args to pass to the java program
  :param executor: an optional java executor to use to launch the program; defaults to a subprocess
    spawn of the default java distribution
  :param workunit_factory: an optional callable that can produce a workunit context
  :param string workunit_name: an optional name for the work unit; defaults to the main
  :param list workunit_labels: an optional sequence of labels for the work unit

  Returns the exit code of the java program.
  Raises `pants.java.Executor.Error` if there was a problem launching java itself.
  """
  executor = executor or SubprocessExecutor()
  if not isinstance(executor, Executor):
    raise ValueError('The executor argument must be a java Executor instance, give %s of type %s'
                     % (executor, type(executor)))

  # When running pants under mesos/aurora, the sandbox pathname can be very long.  Since it gets
  # prepended to most components in the classpath, in some runs the classpath gets too big and
  # interferes with the maximum length of args. We prevent this by using paths relative to the
  # cwd (which are most of the components of the classpath generated by pants).

  cwd_prefix = os.getcwd() + os.path.sep
  cwd_prefix_length = len(cwd_prefix)

  def relativize_path(path):
    path = os.path.realpath(path)
    if path.startswith(cwd_prefix):
      return path[cwd_prefix_length:]
    else:
      return path

  relativized_classpath = [relativize_path(p) for p in classpath]
  runner = executor.runner(relativized_classpath, main, args=args, jvm_options=jvm_options)
  workunit_name = workunit_name or main
  return execute_runner(runner,
                        workunit_factory=workunit_factory,
                        workunit_name=workunit_name,
                        workunit_labels=workunit_labels)


def execute_runner(runner, workunit_factory=None, workunit_name=None, workunit_labels=None):
  """Executes the given java runner.

  If `workunit_factory` is supplied, does so in the context of a workunit.

  :param runner: the java runner to run
  :param workunit_factory: an optional callable that can produce a workunit context
  :param string workunit_name: an optional name for the work unit; defaults to the main
  :param list workunit_labels: an optional sequence of labels for the work unit

  Returns the exit code of the java runner.
  Raises `pants.java.Executor.Error` if there was a problem launching java itself.
  """
  if not isinstance(runner, Executor.Runner):
    raise ValueError('The runner argument must be a java Executor.Runner instance, '
                     'given %s of type %s' % (runner, type(runner)))

  if workunit_factory is None:
    return runner.run()
  else:
    workunit_labels = [
        WorkUnit.TOOL,
        WorkUnit.NAILGUN if isinstance(runner.executor, NailgunExecutor) else WorkUnit.JVM
    ] + (workunit_labels or [])

    with workunit_factory(name=workunit_name, labels=workunit_labels, cmd=runner.cmd) as workunit:
      ret = runner.run(stdout=workunit.output('stdout'), stderr=workunit.output('stderr'))
      workunit.set_outcome(WorkUnit.FAILURE if ret else WorkUnit.SUCCESS)
      return ret
