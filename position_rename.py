"""文件名按位置/定界符变换的纯逻辑模块。

20261022 110136 新增：为“按位置/定界符改名”功能提供与界面无关的纯逻辑实现，
包含字符计数换算、六类变换（覆盖九项功能）、新名称校验、批次重名检测与序号规划。
本模块不导入 tkinter，也不直接操作磁盘（磁盘存在性通过 exists_func 注入），便于单元测试。
"""

import os

# 计数模式：unit=汉字计 2、其余计 1；char=每个字符均计 1
COUNT_MODE_UNIT = "unit"
COUNT_MODE_CHAR = "char"

# 动作类型
ACTION_DELETE = "delete"
ACTION_REPLACE = "replace"
ACTION_INSERT = "insert"

# 规则类型（对应九项功能）
RULE_POS_BEFORE = "pos_before"      # 第 x 个字符前 y 个字符：删除/替换/添加
RULE_POS_AFTER = "pos_after"        # 第 x 个字符后 y 个字符：删除/替换/添加
RULE_DELIM_BEFORE = "delim_before"  # 某定界符前全部字符：删除/替换/添加
RULE_DELIM_AFTER = "delim_after"    # 某定界符后全部字符：删除/替换/添加
RULE_HEAD = "head"                  # 前 X 个字符：删除/替换
RULE_TAIL = "tail"                  # 后 X 个字符：删除/替换

# 序号位置
POSITION_PREFIX = "prefix"  # 前置：序号+连接符+名称
POSITION_SUFFIX = "suffix"  # 后置：名称+连接符+序号

INVALID_NAME_CHARS = '\\/:*?"<>|'
MAX_NAME_LENGTH = 255
RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


def is_cjk_char(ch):
    """判断字符是否属于 CJK 表意文字（汉字），用于“汉字计 2”的宽度换算。"""
    code = ord(ch)
    return (
        0x3400 <= code <= 0x4DBF
        or 0x4E00 <= code <= 0x9FFF
        or 0xF900 <= code <= 0xFAFF
        or 0x20000 <= code <= 0x2FA1F
    )


def char_width(ch, count_mode=COUNT_MODE_UNIT):
    """单个字符占用的计数权重。默认模式下汉字 2、其余（含全角标点【】）1。"""
    if count_mode == COUNT_MODE_CHAR:
        return 1
    return 2 if is_cjk_char(ch) else 1


def text_width(text, count_mode=COUNT_MODE_UNIT):
    """整段文本按计数方式折算后的总权重。"""
    return sum(char_width(ch, count_mode) for ch in text)


def split_name(name, protect_extension=True):
    """拆分主名称与扩展名。

    保护扩展名时以最后一个“.”为界，且该点不在首位、不在末位；
    目录名或未勾选保护时返回 (name, "")。
    """
    if not protect_extension or not name:
        return name, ""
    index = name.rfind(".")
    if 0 < index < len(name) - 1:
        return name[:index], name[index:]
    return name, ""


def char_index_before_unit(text, unit_pos, count_mode=COUNT_MODE_UNIT):
    """返回“第 unit_pos 个计数位置之前”的字符索引（落在汉字内部时向下取整）。"""
    if unit_pos <= 0:
        return 0
    accumulated = 0
    for index, ch in enumerate(text):
        width = char_width(ch, count_mode)
        if accumulated + width >= unit_pos:
            return index
        accumulated += width
    return len(text)


def char_index_after_unit(text, unit_pos, count_mode=COUNT_MODE_UNIT):
    """返回“第 unit_pos 个计数位置之后”的字符索引（落在汉字内部时向上取整）。"""
    if unit_pos <= 0:
        return 0
    accumulated = 0
    for index, ch in enumerate(text):
        accumulated += char_width(ch, count_mode)
        if accumulated >= unit_pos:
            return index + 1
    return len(text)


def _to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _find_delimiter_index(text, delimiter, occurrence):
    """查找定界符位置；occurrence 为正整数表示第 N 次，-1 或 0 表示最后一次。"""
    if not delimiter:
        return None, "定界符不能为空"
    if occurrence is None or occurrence == "":
        occurrence = 1
    occurrence = _to_int(occurrence, 1)
    if occurrence <= 0:
        index = text.rfind(delimiter)
        if index < 0:
            return None, f"未找到定界符 '{delimiter}'"
        return index, None
    start = 0
    for order in range(1, occurrence + 1):
        index = text.find(delimiter, start)
        if index < 0:
            return None, f"未找到第 {occurrence} 个定界符 '{delimiter}'"
        if order == occurrence:
            return index, None
        start = index + len(delimiter)
    return None, f"未找到第 {occurrence} 个定界符 '{delimiter}'"


def validate_new_name(name, is_directory=False):
    """校验新名称是否合法；合法返回 None，否则返回原因文本。"""
    if not name or not name.strip():
        return "新名称为空"
    if len(name) > MAX_NAME_LENGTH:
        return f"新名称过长（{len(name)} 字符，上限 {MAX_NAME_LENGTH}）"
    for ch in name:
        if ch in INVALID_NAME_CHARS:
            return f"新名称含非法字符 '{ch}'"
    if name[-1] in (" ", "."):
        return "新名称不能以空格或点结尾"
    base, _ = split_name(name, not is_directory)
    if base.strip().upper() in RESERVED_NAMES:
        return f"新名称 '{base.strip()}' 为系统保留名"
    return None


def apply_rule(name, rule, is_directory=False):
    """对单个名称应用一条变换规则。

    rule 支持的键：type、action、x、y、text、delimiter、occurrence、
    count_mode、protect_extension。
    返回 (新名称, None) 或 (None, 失败原因)。
    """
    if not name:
        return None, "名称为空"

    rule_type = rule.get("type")
    action = rule.get("action", ACTION_REPLACE)
    count_mode = rule.get("count_mode", COUNT_MODE_UNIT)
    text = rule.get("text") or ""
    protect_extension = rule.get("protect_extension", True)

    base, extension = split_name(name, protect_extension and not is_directory)
    total_units = text_width(base, count_mode)

    if rule_type == RULE_POS_BEFORE:
        x = _to_int(rule.get("x"))
        if x < 1 or x > total_units:
            return None, f"位置 {x} 超出范围（主名称共 {total_units} 个字符）"
        if action == ACTION_INSERT:
            index = char_index_before_unit(base, x, count_mode)
            new_base = base[:index] + text + base[index:]
        else:
            y = _to_int(rule.get("y"))
            if y < 1:
                return None, "要删除/替换的字符数必须大于 0"
            start = char_index_before_unit(base, x - y, count_mode)
            end = char_index_after_unit(base, x - 1, count_mode)
            middle = text if action == ACTION_REPLACE else ""
            new_base = base[:start] + middle + base[end:]
    elif rule_type == RULE_POS_AFTER:
        x = _to_int(rule.get("x"))
        if x < 1 or x > total_units:
            return None, f"位置 {x} 超出范围（主名称共 {total_units} 个字符）"
        start = char_index_after_unit(base, x, count_mode)
        if action == ACTION_INSERT:
            new_base = base[:start] + text + base[start:]
        else:
            raw_y = rule.get("y")
            if raw_y in (None, "", "all", -1, "-1"):
                end = len(base)
            else:
                y = _to_int(raw_y)
                if y < 1:
                    return None, "要删除/替换的字符数必须大于 0"
                end = char_index_after_unit(base, x + y, count_mode)
            middle = text if action == ACTION_REPLACE else ""
            new_base = base[:start] + middle + base[end:]
    elif rule_type == RULE_HEAD:
        x = _to_int(rule.get("x"))
        if x < 1 or x > total_units:
            return None, f"字符数 {x} 超出范围（主名称共 {total_units} 个字符）"
        end = char_index_after_unit(base, x, count_mode)
        new_base = (text if action == ACTION_REPLACE else "") + base[end:]
    elif rule_type == RULE_TAIL:
        x = _to_int(rule.get("x"))
        if x < 1 or x > total_units:
            return None, f"字符数 {x} 超出范围（主名称共 {total_units} 个字符）"
        keep_units = total_units - x + 1  # 20261022 110136 修正：后 X 个字符应从区间 [L-X+1, L] 起算，避免多删一个字符
        index = char_index_before_unit(base, keep_units, count_mode)
        new_base = base[:index] + (text if action == ACTION_REPLACE else "")
    elif rule_type in (RULE_DELIM_BEFORE, RULE_DELIM_AFTER):
        delimiter = rule.get("delimiter") or ""
        index, error = _find_delimiter_index(base, delimiter, rule.get("occurrence", 1))
        if error:
            return None, error
        if rule_type == RULE_DELIM_BEFORE:
            if action == ACTION_DELETE:
                new_base = base[index:]
            elif action == ACTION_REPLACE:
                new_base = text + base[index:]
            else:
                new_base = base[:index] + text + base[index:]
        else:
            end = index + len(delimiter)
            if action == ACTION_DELETE:
                new_base = base[:end]
            elif action == ACTION_REPLACE:
                new_base = base[:end] + text
            else:
                new_base = base[:end] + text + base[end:]
    else:
        return None, f"未知的规则类型：{rule_type}"

    if not new_base:
        return None, "运算结果的主名称为空"

    new_name = new_base + extension
    error = validate_new_name(new_name, is_directory)
    if error:
        return None, error
    return new_name, None


def format_sequence(index, num_type="1", pad_width=0):
    """把序号数字格式化为显示文本：数字（可补零）、A/a 字母序列、罗马数字。"""
    if index < 1:
        index = 1
    if num_type == "A":
        result = ""
        value = index
        while value > 0:
            value -= 1
            result = chr(65 + value % 26) + result
            value //= 26
        return result
    if num_type == "a":
        result = ""
        value = index
        while value > 0:
            value -= 1
            result = chr(97 + value % 26) + result
            value //= 26
        return result
    if num_type == "Ⅰ":
        numerals = [
            (1000, "Ⅿ"), (900, "ⅭⅯ"), (500, "Ⅾ"), (400, "ⅭⅮ"),
            (100, "Ⅽ"), (90, "ⅩⅭ"), (50, "Ⅼ"), (40, "ⅩⅬ"),
            (10, "Ⅹ"), (9, "Ⅸ"), (5, "Ⅴ"), (4, "Ⅳ"), (1, "Ⅰ"),
        ]
        result = ""
        value = index
        for number, numeral in numerals:
            count = value // number
            result += numeral * count
            value -= number * count
        return result
    pad_width = _to_int(pad_width)
    if pad_width > 0:
        return str(index).zfill(pad_width)
    return str(index)


def insert_sequence(name, token, position=POSITION_PREFIX, is_directory=False):
    """把已含连接符的序号文本插入到主名称前/后（扩展名之前）。"""
    base, extension = split_name(name, not is_directory)
    if position == POSITION_SUFFIX:
        return base + token + extension
    return token + base + extension


def find_conflicting_indices(entries, exists_func=None):
    """返回批次内可能重名的条目索引集合。

    entries 为 dict 列表，键：path（原完整路径）、new_name（候选新名）。
    重名包括：同一目录内候选新名重复；目标路径在磁盘上已被其他项占用。
    """
    conflicting = set()
    grouped = {}
    for index, entry in enumerate(entries):
        parent = os.path.dirname(entry.get("path", ""))
        key = (os.path.normcase(parent), os.path.normcase(entry.get("new_name", "")))
        grouped.setdefault(key, []).append(index)
    for indices in grouped.values():
        if len(indices) > 1:
            conflicting.update(indices)
    if exists_func is not None:
        for index, entry in enumerate(entries):
            path = entry.get("path", "")
            parent = os.path.dirname(path)
            target = os.path.join(parent, entry.get("new_name", ""))
            if os.path.normcase(target) != os.path.normcase(path) and exists_func(target):
                conflicting.add(index)
    return conflicting


def plan_batch_sequence(entries, options, exists_func=None):
    """为整批条目规划最终新名称。

    entries：dict 列表，键 path（原完整路径）、new_name（候选新名）、
             is_directory（可选）。
    options：enabled（是否启用）、position（prefix/suffix）、num_type、
             connector、start（起始序号）、pad_width（补零位数）、
             reset_per_dir（每个目录重新从 1 开始，默认 False）。
    返回与 entries 等长的新名称列表；未启用或不存在重名时原样返回候选新名。
    """
    candidate_names = [entry.get("new_name", "") for entry in entries]
    options = options or {}
    if not options.get("enabled"):
        return candidate_names
    if not entries:
        return candidate_names

    if not find_conflicting_indices(entries, exists_func):
        return candidate_names

    position = options.get("position", POSITION_PREFIX)
    num_type = options.get("num_type", "1")
    connector = options.get("connector", "-") or ""
    start = max(1, _to_int(options.get("start"), 1))
    pad_width = _to_int(options.get("pad_width"), 0)
    reset_per_dir = bool(options.get("reset_per_dir"))

    order = sorted(
        range(len(entries)),
        key=lambda i: (
            os.path.normcase(os.path.dirname(entries[i].get("path", ""))),
            os.path.basename(entries[i].get("path", "")).lower(),
            i,
        ),
    )

    used_keys = set()
    result = list(candidate_names)
    sequence = start
    current_parent = None
    max_attempts = 10000

    for index in order:
        entry = entries[index]
        path = entry.get("path", "")
        parent = os.path.dirname(path)
        is_directory = bool(entry.get("is_directory"))
        if reset_per_dir and parent != current_parent:
            sequence = start
            current_parent = parent

        assigned = None
        key = None
        for _ in range(max_attempts):
            sequence_text = format_sequence(sequence, num_type, pad_width)
            if position == POSITION_SUFFIX:
                token = connector + sequence_text
            else:
                token = sequence_text + connector
            name = insert_sequence(candidate_names[index], token, position, is_directory)
            key = (os.path.normcase(parent), os.path.normcase(name))
            target = os.path.join(parent, name)
            occupied = key in used_keys
            if not occupied and exists_func is not None:
                if os.path.normcase(target) != os.path.normcase(path) and exists_func(target):
                    occupied = True
            if not occupied:
                assigned = name
                break
            sequence += 1

        if assigned is None:
            assigned = candidate_names[index]
        else:
            used_keys.add(key)
        result[index] = assigned
        sequence += 1

    return result