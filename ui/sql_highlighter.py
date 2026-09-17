"""Resaltador de sintaxis SQL basado en QSyntaxHighlighter."""
from __future__ import annotations

from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat

KEYWORDS = {
    "SELECT", "FROM", "WHERE", "GROUP", "BY", "ORDER", "HAVING", "LIMIT",
    "OFFSET", "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE", "CREATE",
    "TABLE", "DROP", "ALTER", "ADD", "COLUMN", "JOIN", "INNER", "LEFT",
    "RIGHT", "FULL", "OUTER", "ON", "AS", "AND", "OR", "NOT", "NULL", "IS",
    "IN", "LIKE", "BETWEEN", "EXISTS", "CASE", "WHEN", "THEN", "ELSE", "END",
    "DISTINCT", "UNION", "ALL", "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
    "UNIQUE", "CHECK", "DEFAULT", "INDEX", "WITH", "RECURSIVE", "CAST",
}

KEYWORD_COLOR = QColor("#00ffaa")
FUNCTION_COLOR = QColor("#00e5ff")
STRING_COLOR = QColor("#ffb300")
COMMENT_COLOR = QColor("#4d7c6d")
NUMBER_COLOR = QColor("#ffb300")
OPERATOR_COLOR = QColor("#00aa70")

FUNCTIONS = {
    "COUNT", "SUM", "AVG", "MIN", "MAX", "ROUND", "LENGTH", "UPPER",
    "LOWER", "SUBSTR", "TRIM", "COALESCE", "IFNULL", "NULLIF", "ABS",
    "DATE", "DATETIME", "STRFTIME", "TYPEOF", "GROUP_CONCAT",
}


class SQLHighlighter(QSyntaxHighlighter):
    def __init__(self, document) -> None:
        super().__init__(document)
        self._rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self._setup_rules()

    def _fmt(self, color: QColor, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        f = QTextCharFormat()
        f.setForeground(color)
        if bold:
            f.setFontWeight(QFont.Weight.Bold)
        if italic:
            f.setFontItalic(True)
        return f

    def _setup_rules(self) -> None:
        keyword_fmt = self._fmt(KEYWORD_COLOR, bold=True)
        for kw in KEYWORDS:
            self._rules.append(
                (
                    QRegularExpression(rf"\b{kw}\b", QRegularExpression.PatternOption.CaseInsensitiveOption),
                    keyword_fmt,
                )
            )
        func_fmt = self._fmt(FUNCTION_COLOR)
        for fn in FUNCTIONS:
            self._rules.append(
                (
                    QRegularExpression(rf"\b{fn}\b(?=\s*\()", QRegularExpression.PatternOption.CaseInsensitiveOption),
                    func_fmt,
                )
            )
        string_fmt = self._fmt(STRING_COLOR)
        for pat in (r"'.*?'", r'".*?"', r"`.*?`"):
            self._rules.append((QRegularExpression(pat), string_fmt))
        comment_fmt = self._fmt(COMMENT_COLOR, italic=True)
        self._rules.append((QRegularExpression(r"--[^\n]*"), comment_fmt))
        self._rules.append((QRegularExpression(r"/\*[\s\S]*?\*/"), comment_fmt))
        number_fmt = self._fmt(NUMBER_COLOR)
        self._rules.append((QRegularExpression(r"\b\d+(\.\d+)?\b"), number_fmt))
        op_fmt = self._fmt(OPERATOR_COLOR)
        self._rules.append((QRegularExpression(r"[=<>!+\-*/%()]"), op_fmt))

    def highlightBlock(self, text: str) -> None:
        self.setCurrentBlockState(0)
        for pattern, fmt in self._rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)