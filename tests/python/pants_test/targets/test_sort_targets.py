# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from pants.base.build_graph import BuildGraph, CycleException, sort_targets
from pants.base.payload import EmptyPayload
from pants.base.target import Target
from pants.base.exceptions import TargetDefinitionException

from pants_test.base_test import BaseTest


class SortTargetsTest(BaseTest):
  def test_validation(self):
    valid = self.make_target(':valid')

  # TODO(pl): Fix up and move to Address tests
  #     self.assertRaises(TargetDefinitionException,
  #                       self.make_target,
  #                       name=1)

    self.make_target(':valid2', dependencies=[valid])

  # TODO(pl): What kind of exception should this actually be?
  #     self.assertRaises(TargetDefinitionException,
  #                       self.make_target,
  #                       ':invalid',
  #                       dependencies=1)

  def test_detect_cycle_direct(self):
    a = self.make_target(':a')

    # no cycles yet
    sort_targets([a])
    self.build_graph.inject_dependency(a.address, a.address)
    try:
      sort_targets([a])
      self.fail("Expected a cycle to be detected")
    except CycleException:
      # expected
      pass

  def test_detect_cycle_indirect(self):
    c = self.make_target(':c')
    b = self.make_target(':b', dependencies=[c])
    a = self.make_target(':a', dependencies=[c, b])

    # no cycles yet
    sort_targets([a])

    self.build_graph.inject_dependency(c.address, a.address)
    try:
      sort_targets([a])
      self.fail("Expected a cycle to be detected")
    except CycleException:
      # expected
      pass

  def test_sort(self):
    a = self.make_target(':a')
    b = self.make_target(':b', dependencies=[a])
    c = self.make_target(':c', dependencies=[b])
    d = self.make_target(':d', dependencies=[c, a])
    e = self.make_target(':e', dependencies=[d])

    self.assertEquals(sort_targets([a,b,c,d,e]), [e,d,c,b,a])
    self.assertEquals(sort_targets([b,d,a,e,c]), [e,d,c,b,a])
    self.assertEquals(sort_targets([e,d,c,b,a]), [e,d,c,b,a])
