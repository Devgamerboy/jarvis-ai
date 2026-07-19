"""Test file path safety."""

from jarvis.tools.enhanced_file_tools import (
    CreateDirTool,
    CopyFileTool,
    MoveFileTool,
    DeleteFileTool,
    SearchFilesTool,
    SearchContentTool,
)


class TestFileSafety:
    def setup_method(self):
        self.create = CreateDirTool()
        self.copy = CopyFileTool()
        self.move = MoveFileTool()
        self.delete = DeleteFileTool()
        self.search = SearchFilesTool()
        self.search_content = SearchContentTool()

    def test_create_dir_missing_path(self):
        r = self.create.execute()
        assert "Path is required" in r.get("error", "")

    def test_copy_missing_source(self):
        r = self.copy.execute(source="", destination="/tmp/test")
        assert "required" in r.get("error", "")

    def test_move_missing_source(self):
        r = self.move.execute(source="", destination="/tmp/test")
        assert "required" in r.get("error", "")

    def test_delete_missing_path(self):
        r = self.delete.execute()
        assert "Path is required" in r.get("error", "")

    def test_search_missing_pattern(self):
        r = self.search.execute()
        assert "Search pattern" in r.get("error", "")

    def test_search_content_missing_text(self):
        r = self.search_content.execute()
        assert "Search text" in r.get("error", "")
