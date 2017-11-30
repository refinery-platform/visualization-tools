import glob
import os
import unittest
import subprocess
import ntpath


class ToolLoadingTests(unittest.TestCase):

    def setUp(self):
        self.tool_annotation_names = [
            tool_annotation_name
            for tool_annotation_name in glob.glob("tool-annotations/*.json")
        ]

    def test_tool_definition_generation(self):
        for tool_annotation_name in self.tool_annotation_names:
            print "Tool Annotation: ", tool_annotation_name
            try:
                subprocess.check_call(
                    [
                        "python",
                        "refinery-platform/refinery/manage.py",
                        "load_tools",
                        "--visualizations",
                        "{}".format(tool_annotation_name)
                    ]
                )
            except subprocess.CalledProcessError as e:
                print e
                self.fail()

if __name__ == "__main__":
    unittest.main()
