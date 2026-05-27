from simpleeval import simple_eval

# 只保留安全的函数白名单，禁止 __import__、open、exec 等危险操作
SAFE_FUNCTIONS = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "len": len,
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
}


def safe_eval_expression(expression: str):
    """安全地求值数学/逻辑表达式。

    使用 simpleeval 替代原生 eval()，仅允许白名单内的函数调用，
    禁止属性访问、import、内置危险函数等。
    """
    return simple_eval(expression, functions=SAFE_FUNCTIONS)
