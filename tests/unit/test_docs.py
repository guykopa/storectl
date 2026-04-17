from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent.parent / "docs"
CONF = DOCS_DIR / "conf.py"
INDEX = DOCS_DIR / "index.rst"


def content(path: Path) -> str:
    return path.read_text()


class TestDocsExist:
    def test_docs_directory_exists(self) -> None:
        assert DOCS_DIR.is_dir()

    def test_conf_exists(self) -> None:
        assert CONF.exists()

    def test_index_exists(self) -> None:
        assert INDEX.exists()


class TestConfPy:
    def test_has_project_name(self) -> None:
        assert "storectl" in content(CONF)

    def test_has_autodoc_extension(self) -> None:
        assert "sphinx.ext.autodoc" in content(CONF)

    def test_has_napoleon_extension(self) -> None:
        assert "sphinx.ext.napoleon" in content(CONF)

    def test_has_viewcode_extension(self) -> None:
        assert "sphinx.ext.viewcode" in content(CONF)

    def test_has_html_theme(self) -> None:
        assert "html_theme" in content(CONF)


class TestIndexRst:
    def test_has_title(self) -> None:
        assert "storectl" in content(INDEX)

    def test_has_toctree(self) -> None:
        assert "toctree" in content(INDEX)

    def test_has_modules_reference(self) -> None:
        assert "modules" in content(INDEX)
