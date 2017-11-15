import glob
import os
import unittest
import subprocess
import ntpath


class ToolLoadingTests(unittest.TestCase):

    def setUp(self):
        self.tool_annotation_names = [
            ntpath.basename(tool_annotation_name).replace(".json", "")
            for tool_annotation_name in glob.glob("tool-annotations/*.json")
        ]

    def test_tool_definition_generation(self):
        for tool_annotation_name in self.tool_annotation_names:
            print "Tool Annotation: ", tool_annotation_name
            subprocess.check_call(
                "python refinery-platform/refinery/manage.py load_tools --visualizations {}".format(
                    tool_annotation_name
                )
            )


if __name__ == "__main__":
    unittest.main()
