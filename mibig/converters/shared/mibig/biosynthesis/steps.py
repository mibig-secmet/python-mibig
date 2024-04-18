# steps have the following format:
# A -> B (first enzyme A acts, then enzyme B acts)
# A/B (enzyme A and B act simultaneously, or in an unknown order)
# instead of enzymes, module names can be used as well
# 1 -> 2/A -> 3 (module 1 acts, then module 2 and A act simultaneously, then module 3 acts)
# TODO: how to deal with multiple ordered steps that themsselves are in unknown order?

def parse_step(step_description: str) -> list[tuple[str, ...]]:
    steps = step_description.split("->")
    parsed_steps = []
    for step in steps:
        parsed_steps.append(tuple(map(str.strip, step.split("/"))))
    return parsed_steps


def format_step(steps: list[tuple[str, ...]]) -> str:
    return " -> ".join("/".join(step) for step in steps)

