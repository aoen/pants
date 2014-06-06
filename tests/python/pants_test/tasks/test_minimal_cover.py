# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from textwrap import dedent

from pants.backend.core.tasks.minimal_cover import MinimalCover
from pants.backend.python.targets.python_library import PythonLibrary
from pants_test.tasks.test_base import ConsoleTaskTest


class BaseMinimalCovertTest(ConsoleTaskTest):
  @classmethod
  def task_type(cls):
    return MinimalCover


class MinimalCoverEmptyTest(BaseMinimalCovertTest):
  def test(self):
    self.assert_console_output(targets=[])


class MinimalCoverTest(BaseMinimalCovertTest):
  @property
  def alias_groups(self):
    return {
      'target_aliases': {
        'python_library': PythonLibrary,
      },
    }

  def setUp(self):
    super(MinimalCoverTest, self).setUp()

    def add_to_build_file(path, name, *deps):
      all_deps = ["'%s'" % dep for dep in list(deps)]
      self.add_to_build_file(path, dedent('''
          python_library(name='%s',
            dependencies=[%s]
          )
          ''' % (name, ','.join(all_deps))))

    add_to_build_file('common/a', 'a')
    add_to_build_file('common/b', 'b')
    add_to_build_file('common/c', 'c')
    add_to_build_file('overlaps', 'one', 'common/a', 'common/b')
    add_to_build_file('overlaps', 'two', 'common/a', 'common/c')
    add_to_build_file('overlaps', 'three', 'common/a', 'overlaps:one')

  def test_roots(self):
    self.assert_console_output(
      'common/a/BUILD:a',
      targets=[self.target('common/a')],
      extra_targets=[self.target('common/b')]
    )

  def test_nodups(self):
    targets = [self.target('common/a')] * 2
    self.assertEqual(2, len(targets))
    self.assert_console_output(
      'common/a/BUILD:a',
      targets=targets
    )

  def test_disjoint(self):
    self.assert_console_output(
      'common/a/BUILD:a',
      'common/b/BUILD:b',
      'common/c/BUILD:c',
      targets=[
        self.target('common/a'),
        self.target('common/b'),
        self.target('common/c'),
      ]
    )

  def test_identical(self):
    self.assert_console_output(
      'common/a/BUILD:a',
      targets=[
        self.target('common/a'),
        self.target('common/a'),
        self.target('common/a'),
      ]
    )

  def test_intersection(self):
    self.assert_console_output(
      'overlaps/BUILD:one',
      'overlaps/BUILD:two',
      targets=[
        self.target('overlaps:one'),
        self.target('overlaps:two')
      ]
    )

    self.assert_console_output(
      'overlaps/BUILD:one',
      'common/c/BUILD:c',
      targets=[
        self.target('common/a'),
        self.target('common/b'),
        self.target('common/c'),
        self.target('overlaps:one'),
      ]
    )

    self.assert_console_output(
      'overlaps/BUILD:two',
      'overlaps/BUILD:three',
      targets=[
        self.target('common/a'),
        self.target('common/b'),
        self.target('common/c'),
        self.target('overlaps:one'),
        self.target('overlaps:two'),
        self.target('overlaps:three'),
      ]
    )
