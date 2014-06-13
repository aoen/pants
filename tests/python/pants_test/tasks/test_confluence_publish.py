# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from pants.backend.core.tasks.check_exclusives import ExclusivesMapping
from pants.backend.core.tasks.group_task import GroupMember, GroupIterator, GroupTask
from pants.backend.jvm.targets.java_library import JavaLibrary
from pants.backend.jvm.targets.scala_library import ScalaLibrary
from pants.backend.python.targets.python_library import PythonLibrary

from pants_test.base_test import BaseTest

class ConfluencePublishTest(BaseTest):
  def setUp(self):
    super(ConfluencePublishTest, self).setUp()

    self.add_to_build_file('root', dedent("""
        source_root('src/python/pants', page)
      """))

    self.add_to_build_file('src/python/pants', dedent("""
        import urllib

        from pants.backend.core.tasks.confluence_publish import ConfluencePublish


        def confluence_url_builder(page, config):
          title = config['title']
          return title, 'https://confluence.twitter.biz/display/%s/%s' % (
            config['space'],
            urllib.quote_plus(title)
          )
        confluence = wiki(name='confluence_wiki',
                          url_builder=confluence_url_builder,
                          )

        class TwitterConfluence(ConfluencePublish):
          def wiki(self):
            return confluence
          def api(self):
            return 'confluence2'

        goal(
          name='confluence',
          action=TwitterConfluence,
          dependencies=['markdown']
        ).install().with_description('Publish one or more confluence pages.')


        page(name='readme',
          source='README.md',
          provides=[
            wiki_artifact(
              # FIXME(areitz): investigate why '/src/python/pants/BUILD:confluence_wiki' doesn't work
              wiki=pants('src/python/pants:confluence_wiki'),
              space='~areitz',
              title='test_page',
            ),
          ],
        )

        page(name='readme2',
          source='README2.md',
          provides=[
            wiki_artifact(
              # FIXME(areitz): investigate why '/src/python/pants/BUILD:confluence_wiki' doesn't work
              wiki=pants('src/python/pants:confluence_wiki'),
              space='~areitz',
              title='test_page2',
            ),
          ],
        )


    """))

    def test_wiki_artifact(self):
      print("hi")