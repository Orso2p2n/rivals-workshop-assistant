import abc
import textwrap
import typing as t


class GmlInjection(abc.ABC):
    def __init__(self, name: str, gml: str, use_pattern: str, give_pattern: str):
        self.name = name
        self.gml = gml
        self.use_pattern = use_pattern
        self.give_pattern = give_pattern

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.gml == other.gml
            and self.use_pattern == other.use_pattern
            and self.give_pattern == other.give_pattern
        )

    def __hash__(self):
        return hash(self.name)


class GmlDeclaration(GmlInjection, abc.ABC):
    IDENTIFIER_STRING = NotImplemented

    def __init__(self, name: str, gml: str, use_pattern: str):
        """Serialize the gml elements into the final gml structure."""
        super().__init__(
            name=name,
            gml=gml,
            give_pattern=fr"#{self.IDENTIFIER_STRING}(\s)*{name}(\W|$)",
            use_pattern=use_pattern,
        )

    @classmethod
    @abc.abstractmethod
    def from_gml(cls, name: str, content: str):
        raise NotImplementedError


class Define(GmlDeclaration):
    IDENTIFIER_STRING = "define"

    def __init__(
        self,
        name: str,
        content: str,
        version: int = 0,
        docs: str = "",
        params: t.List[str] = None,
    ):
        if params is None:
            params = []
        if params:
            param_string = f"({', '.join(params)})"
        else:
            param_string = ""

        self.docs = docs  # I think this might only apply to defines?

        head = f"#{self.IDENTIFIER_STRING} {name}{param_string}"
        if docs.strip():
            docs = textwrap.indent(textwrap.dedent(docs), "    // ") + "\n"

        content = textwrap.indent(textwrap.dedent(content), "    ")

        final = f"{head} // Version {version}\n{docs}{content}"
        gml = textwrap.dedent(final).strip()
        use_pattern = fr"(?<!#define)(^|\W){name}\("
        super().__init__(
            name,
            gml,
            use_pattern=use_pattern,
        )

    @classmethod
    def from_gml(cls, name: str, content: str):
        content = _remove_brackets(content)
        content = textwrap.dedent(content).strip("\n")
        docs, content = _split_docs_and_gml(content)
        name, params = _split_name_and_params(name)
        return cls(name=name, params=params, docs=docs, content=content)


def _normalize_comments(content: str) -> str:
    """Add // to the beginning of all lines inside a /* */ block"""

    split_by_enter = content.split("/*")
    normalized_splits = []
    for split in split_by_enter:
        inner_splits = split.split("*/")
        if len(inner_splits) == 1:
            normalized_splits.append(inner_splits[0])
        else:
            split_content, after = inner_splits

            normalized_content_lines = []
            split_content_lines = split_content.splitlines(keepends=True)
            normalized_content_lines.append(split_content_lines[0])
            for line in split_content_lines[1:]:
                # line_starts_with_comment_sign = any(
                #     line.lstrip().startswith(comment_sign) for comment_sign in ("//",)
                # )
                if line.lstrip().startswith("//"):
                    normalized_line = line
                else:
                    normalized_line = f"// {line}"
                normalized_content_lines.append(normalized_line)
            normalized_content = "".join(normalized_content_lines)

            content_and_after = f"{normalized_content}*/{after}"
            normalized_splits.append(content_and_after)
    full_normalized_content = "/*".join(normalized_splits)

    return full_normalized_content


def _is_content_line(line: str, remove_comments=False) -> bool:
    stripped = line.strip()
    is_empty = len(stripped) == 0

    if remove_comments:
        # This assumes that lines in /* blocks also have //
        is_comment = any(
            stripped.startswith(comment_str) for comment_str in ("//", "/*", "*/")
        )
        return not (is_empty or is_comment)
    else:
        return not is_empty


def _strip_content_in_direction(
    content: str, remove_comments: bool = False, reverse: bool = False
) -> str:
    stripped_lines = []

    lines = content.splitlines()
    if reverse:
        lines = reversed(lines)

    content_found = False
    for line in lines:
        if content_found:
            stripped_lines.append(line)
        else:
            if _is_content_line(line, remove_comments):
                content_found = True
                stripped_lines.append(line)

    if reverse:
        stripped_lines = reversed(stripped_lines)

    stripped_content = "\n".join(stripped_lines)
    return stripped_content


def _strip_non_content_lines(content: str) -> str:
    """Remove surrounding whitespace, empty lines, and comment lines"""
    content = _strip_content_in_direction(content)
    content = _strip_content_in_direction(content, remove_comments=True, reverse=True)
    return content


def _remove_brackets(content):
    has_start_bracket = content.strip().startswith("{")
    has_end_bracket = content.strip().endswith("}")
    if (has_start_bracket and not has_end_bracket) or (
        content.count("{") != content.count("}")
    ):
        raise ValueError(f"Mismatched curly braces at:\n{content}\n\n---\n")
    if has_start_bracket and has_end_bracket:
        content = content.strip().lstrip("{").rstrip("}").strip("\n")
    return content


def _split_docs_and_gml(content: str) -> t.Tuple[str, str]:
    lines = content.split("\n")
    non_docs_found = False

    doc_lines = []
    gml_lines = []
    for line in lines:
        if not non_docs_found:
            if line.lstrip().startswith("//"):
                line = line.split("//")[1].rstrip()
                if line[0] == " ":  # Remove padding from '// ' format
                    line = line[1:]
                doc_lines.append(line)
                continue
            else:
                non_docs_found = True
        gml_lines.append(line.rstrip())

    return "\n".join(doc_lines), "\n".join(gml_lines)


def _split_name_and_params(name: str) -> t.Tuple[str, t.List[str]]:
    name = name.strip()
    if "(" not in name:
        return name, []
    else:
        if not name.endswith(")"):
            raise ValueError(f"Missing ) for parameter line: {name}")
        name, param_string = name.rstrip(")").split("(")
        params = [param.strip() for param in param_string.split(",") if param]
        return name, params


class Macro(GmlDeclaration):
    IDENTIFIER_STRING = "macro"

    def __init__(self, name: str, value: str):
        gml = f"#macro {name} {value}"
        super().__init__(
            name,
            gml,
            use_pattern=fr"(^|\W){name}($|\W)",
        )

    @classmethod
    def from_gml(cls, name: str, content: str):
        if content[0] == " ":
            content = content[1:]  # remove leading space

        content = textwrap.dedent(content).strip("\n")
        content = "\n".join(line.rstrip() for line in content.split("\n"))

        return cls(name=name, value=content)


INJECT_TYPES = (Define, Macro)


if __name__ == "__main__":
    test = """\

1

/*

in first

  */    

2

/*

in second

hmm */

3
    
    """

    exp = """\

1

/*
// 
// in first
// 
//   */    

2

/*
// 
// in second
// 
// hmm */

3
    
    """

    out = _normalize_comments(test)
    assert out == exp
    print(out)
