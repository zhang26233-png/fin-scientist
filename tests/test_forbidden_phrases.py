from pathlib import Path


FORBIDDEN_PHRASES = [
    "\u63a8\u8350\u4e70\u5165",
    "\u5f3a\u70c8\u770b\u591a",
    "\u5fc5\u6da8",
    "\u4e0a\u6da8\u6982\u7387",
    "\u4e70\u5165\u8bc4\u5206",
    "\u63a8\u8350\u8bc4\u5206",
    "\u4e70\u5165\u4fe1\u53f7",
    "\u5356\u51fa\u4fe1\u53f7",
    "\u4ea4\u6613\u4fe1\u53f7",
    "\u81ea\u52a8\u4ea4\u6613",
    "\u9ad8\u4ef7\u503c\u80a1\u7968",
    "\u9ad8\u4ef7\u503c\u677f\u5757",
]

SCAN_PATHS = [
    Path("app.py"),
    Path("legacy_app.py"),
    Path("ui"),
    Path("config"),
    Path("data"),
    Path("core"),
]


def iter_python_files():
    for path in SCAN_PATHS:
        if path.is_file():
            yield path
        else:
            yield from path.rglob("*.py")


def test_forbidden_phrases_not_used_in_runtime_code():
    hits = []
    for path in iter_python_files():
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN_PHRASES:
            if phrase in text:
                hits.append(f"{path}: {phrase}")

    assert hits == []
