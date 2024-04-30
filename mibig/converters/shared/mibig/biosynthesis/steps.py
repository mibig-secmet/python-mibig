# steps have the following format:

# Commas signify an unordered path: exA, exB, exC
# greater-than signs signify an ordered path: exA > exB > exC
# To indicate modules, use square brackets: [modA]
# To indicate cooperation, use a plus sign: exA + exB
# To indicate two enzymes being interchangeable, use a pipe symbol: exA | exB
# A trans-AT can be written like this [modA] + exB
# TODO: how to deal with multiple ordered steps that themsselves are in unknown order?

def parse_step(step_description: str) -> list[tuple[str, ...]]:
    steps = step_description.split(">")
    parsed_steps = []
    for step in steps:
        parsed_steps.append(tuple(map(str.strip, step.split(","))))
    return parsed_steps


def format_step(steps: list[tuple[str, ...]]) -> str:
    return " > ".join("/".join(step) for step in steps)

