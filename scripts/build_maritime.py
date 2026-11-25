"""Build the illustrated maritime scenes used by the GitHub profile README."""

from argparse import ArgumentParser
from base64 import b64encode
from pathlib import Path
from xml.sax.saxutils import escape

from .typo import text_path


ASSETS = Path(__file__).resolve().parents[1] / "assets" / "maritime"
PARCHMENT = "#eee9dc"
INK = "#232a2b"
NAVY = "#28374a"
BRASS = "#9b6d36"
MUTED = "#59564c"
DISPLAY = "Didot-Bold"
ITALIC = "Didot-Italic"
BODY = "IowanOldStyle-Roman"
LABEL = "AvenirNext-DemiBold"
WIDTH = 1200
X = 72


def text(value, y, size, *, x=X, font=BODY, fill=INK, anchor="start", tracking=0):
    return text_path(
        value, font, size, x, y, anchor=anchor, fill=fill, letter_spacing=tracking
    )


def label(value, y, size=24, *, x=X, anchor="start", fill=MUTED, tracking=1.5):
    return text(value, y, size, x=x, font=LABEL, fill=fill, anchor=anchor, tracking=tracking)


def image(name, x, y, width, height):
    return (f'<use x="{x}" y="{y}" width="{width}" height="{height}" xlink:href="#{name}"/>')


def layer(name):
    pixels = b64encode((ASSETS / f"{name}.webp").read_bytes()).decode("ascii")
    return (
        f'<symbol id="{name}" viewBox="0 0 1 1" preserveAspectRatio="none">'
        f'<image width="1" height="1" preserveAspectRatio="none" '
        f'xlink:href="data:image/webp;base64,{pixels}"/></symbol>'
    )


def page(title, description, height, scene, *art, width=WIDTH, definitions=""):
    assets = "\n    ".join(layer(name) for name in ("paper", *art))
    motion = (ASSETS / "motion.css").read_text()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
  width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">{escape(title)}</title>
  <desc id="description">{escape(description)}</desc>
  <style>{motion}</style>
  <defs>
    <clipPath id="frame"><rect width="{width}" height="{height}" rx="28"/></clipPath>
    <pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse">
      <path d="M0 36V0H36" fill="none" stroke="#70664f" stroke-width="1" opacity=".22"/>
    </pattern>
    {assets}
    {definitions}
  </defs>
  <g clip-path="url(#frame)">
    <rect width="{width}" height="{height}" fill="{PARCHMENT}"/>
    <g opacity=".79">{image("paper", 0, 0, width, height)}</g>
    {scene}
  </g>
  <rect x="2.25" y="2.25" width="{width - 4.5}" height="{height - 4.5}" rx="25.75"
    fill="none" stroke="{INK}" stroke-width="4.5"/>
</svg>
'''


def swell(y, height, fill, css, *, filled=True):
    # Each 520-unit segment starts and ends at the same height and tangent.
    path = f"M-1040 {y}" + f"c92 {-height} 163 {-height} 260 0s168 {height} 260 0" * 6
    if filled:
        path += "v230H-1040Z"
    return (f'<path class="{css}" d="{path}" fill="{fill}" '
            f'stroke="{INK}" stroke-width="2.9" stroke-linecap="round"/>')


def intro():
    vessel = image("vessel", 576, 62, 590, 457)
    return page(
        "Drishti Sharma",
        "Somewhere between art and algorithms. Data Science & Artificial Intelligence at "
        "Florida International University, Miami, FL. An illustrated survey ship sails across layered waves.",
        588,
        f'''
    <g fill="#7d8076" opacity=".14">
      <path class="cloud cloud-one" d="M-200 146c80-3 106-12 135-29 16-10 45-18 83-9
        32-34 73-20 79 0 31-9 54 3 63 17 27 4 68 9 100 21Z"/>
      <path class="cloud cloud-two" d="M845 137c55-4 61-19 88-21 29-39 78-27 89-4
        30-11 53-5 66 10 30 3 65 8 104 15Z"/>
    </g>
    {swell(455, 19, "#d7d7c9", "swell-far")}
    <g class="ship-entry">
      <g class="ship">
        <g clip-path="url(#rigging)">{vessel}</g>
        <g class="pennant pennant-main"><g clip-path="url(#main-flag)">{vessel}</g></g>
        <g class="pennant pennant-aft"><g clip-path="url(#aft-flag)">{vessel}</g></g>
        <g clip-path="url(#canvas-sail)">
          <ellipse class="sail-light" cx="835" cy="218" rx="102" ry="56" fill="url(#canvas-light)"/>
        </g>
      </g>
    </g>
    {swell(501, 21, "#c2c9c5", "swell-middle")}
    <g opacity=".52">{swell(524, 17, "none", "swell-middle", filled=False)}</g>
    {swell(555, 19, "#e0e0d2", "swell-near")}
    <g opacity=".50">{swell(580, 14, "none", "swell-near", filled=False)}</g>
    {label("DATA SCIENCE & ARTIFICIAL INTELLIGENCE", 103, 21, tracking=1.65)}
    {text("Drishti", 225, 119, font=DISPLAY)}
    {text("Sharma", 324, 114, font=DISPLAY)}
    {text("Somewhere between art and algorithms.", 377, 27, font=ITALIC, fill=NAVY)}
    {label("Florida International University · Miami, FL", 414, 21, tracking=.13)}
    ''',
        "vessel",
        definitions='''
    <clipPath id="rigging">
      <path clip-rule="evenodd" d="M0 0H1200V588H0Z M862.5 72H966V104H862.5Z M703.7 135H768V156H703.7Z"/>
    </clipPath>
    <clipPath id="main-flag"><rect x="862.5" y="72" width="103.5" height="32"/></clipPath>
    <clipPath id="aft-flag"><rect x="703.7" y="135" width="64.3" height="21"/></clipPath>
    <clipPath id="canvas-sail">
      <path d="M799 167Q842 178 913 180Q939 207 921 239Q892 244 857 256 804 258 777 280Q813 204 799 167Z"/>
    </clipPath>
    <radialGradient id="canvas-light">
      <stop stop-color="#fff5da" stop-opacity=".37"/>
      <stop offset="1" stop-color="#fff5da" stop-opacity="0"/>
    </radialGradient>''',
    )


def stage(x=64, y=159, width=1072, height=210):
    return f'''
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="13" fill="#d8d8cb"
      fill-opacity=".51" stroke="#736b57" stroke-opacity=".45" stroke-width="1.4"/>
    <rect x="{x + 1}" y="{y + 1}" width="{width - 2}" height="{height - 2}" rx="12"
      fill="url(#grid)" opacity=".65"/>'''


def pulse(path, duration, begin, *, radius=4.2, color=BRASS):
    return f'''
    <circle r="{radius}" fill="{color}" opacity="0">
      <animateMotion path="{path}" dur="{duration}s" begin="{begin}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.14;.82;1"
        dur="{duration}s" begin="{begin}s" repeatCount="indefinite"/>
    </circle>'''


def project(name, question, description, summary, focus, diagram, *, definitions=""):
    return page(
        name, f"{question} {description}", 532,
        f'''
    {text(name, 84, 55, font=DISPLAY)}
    {label("IN DEVELOPMENT", 77, 18, x=1128, anchor="end")}
    {text(question, 129, 28, font=ITALIC, fill=NAVY)}
    {stage()}
    {diagram}
    {text(summary[0], 424, 29)}
    {text(summary[1], 463, 29)}
    {label(focus, 505, 19, tracking=.45)}
    {label("Repository ↗", 505, 19, x=1128, anchor="end", fill=NAVY, tracking=.3)}
    ''', definitions=definitions,
    )


def memory_station(x, title, variant):
    sparks = (
        (-21, -15, 4), (7, -25, 3), (24, -7, 4.3), (19, 18, 3.6),
        (-14, 23, 4), (-26, 8, 3), (2, 5, 5),
    )
    color_marks = (1, 2, 4, 6) if variant == "recovered" else (2, 6)
    spacing = .57 if variant == "dormant" else 1
    strength = .58 if variant == "dormant" else 1
    motes = "".join(
        f'<circle cx="{px * spacing:g}" cy="{py * spacing:g}" r="{radius * strength:g}" '
        f'fill="{BRASS if index in color_marks else NAVY}"/>'
        for index, (px, py, radius) in enumerate(sparks)
    )
    return f'''
    <g transform="translate({x} 251)">
      <circle r="53" fill="#eeebdf" stroke="#7b7460" stroke-width="1.9"/>
      <circle r="43" fill="#b9c1bb" fill-opacity=".31" stroke="#8f795b" stroke-width="1.6"
        stroke-dasharray="48 11 15 10" transform="rotate(-22)"/>
      <g class="memory {variant}" opacity="{strength}">{motes}</g>
    </g>
    {label(title, 337, 23, x=x, anchor="middle", fill=NAVY, tracking=1.9)}
    '''


def mnemoai():
    route = "M224 251H976"
    tracers = "".join(pulse(route, 6.8, offset) for offset in (0, -2.25, -4.5))
    return project(
        "MnemoAI", "Can AI forget without losing what it once knew?",
        "An animated diagram of active, dormant, and recovered memory.",
        ("Open-source AI memory infrastructure exploring retention,", "forgetting, and memory recovery."),
        "Python · AI Infrastructure · Memory Systems · Information Retrieval",
        f'''
    <path d="{route}" fill="none" stroke="#777762" stroke-width="2.3" stroke-linecap="round" stroke-dasharray="2 9"/>
    <g class="tracers">{tracers}</g>
    {memory_station(225, "ACTIVE", "active")}
    {memory_station(600, "DORMANT", "dormant")}
    {memory_station(975, "RECOVERED", "recovered")}
    ''',
    )


def repolens():
    inputs = tuple(
        f"M285 {y}C400 {y} 474 250 586 251" for y in (202, 225, 248, 271, 294)
    )
    outputs = tuple(
        f"M617 251C691 251 728 {y} 823 {y}" for y in (205, 251, 297)
    )
    connections = "".join(f'<path d="{path}"/>' for path in (*inputs, *outputs))
    tracers = "".join(
        pulse(path, 2.65, -index * .39, color=NAVY) for index, path in enumerate(inputs)
    ) + "".join(
        pulse(path, 2.65, -index * .62 - .48, color=BRASS) for index, path in enumerate(outputs)
    )
    code = "".join(
        f'<path d="M116 {y}h{width}" stroke="#37475a" stroke-width="5" stroke-linecap="round"/>'
        for y, width in ((202, 108), (225, 76), (248, 118), (271, 94), (294, 107))
    )
    results = "".join(
        f'''<rect x="818" y="{y - 18}" width="260" height="36" rx="5"
          fill="#eae3d2" stroke="#8a795e" stroke-width="1.5"/>
        {label(result, y + 7, 21, x=948, anchor="middle", fill=NAVY, tracking=.2)}'''
        for y, result in zip((205, 251, 297), ("Architecture Map", "Plain Walkthrough", "Visual Flow"))
    )
    return project(
        "RepoLens", "Understanding software shouldn’t require reading every line of code.",
        "Signals from a GitHub repository flow through an AI lens to an architecture map, "
        "a plain walkthrough, and a visual flow.",
        ("Turns GitHub repositories into visual maps and", "plain-language walkthroughs."),
        "Python · React · LLMs · Generative AI",
        f'''
    <g fill="none" stroke="#66716e" stroke-width="2">{connections}</g>
    <g class="tracers">{tracers}</g>
    <rect x="96" y="184" width="191" height="128" rx="8" fill="#e5e2d6" stroke="#6b746c" stroke-width="1.5"/>
    {code}
    <path d="M248 202h21m-32 46h32m-21 46h21" fill="none" stroke="#a68150"
      stroke-width="3.8" stroke-linecap="round"/>
    <circle cx="600" cy="251" r="53" fill="#a07946" stroke="#544835" stroke-width="2"/>
    <circle cx="600" cy="251" r="46" fill="url(#lens-glass)" stroke="#e7d6ae" stroke-width="2.2"/>
    <path class="lens-light" d="M570 250a30 30 0 0 1 32-29" fill="none" stroke="#f6f0dc"
      stroke-width="3.4" stroke-linecap="round"/>
    <path d="M584 263l16-27 17 27zm16-27v27" fill="none" stroke="#37475a"
      stroke-width="1.8" stroke-linejoin="round"/>
    {results}
    {label("GITHUB REPO", 346, 21, x=190, anchor="middle", fill=NAVY)}
    {label("AI LENS", 346, 21, x=600, anchor="middle", fill=NAVY)}
    ''',
        definitions='''
    <radialGradient id="lens-glass" cx=".33" cy=".23" r=".90">
      <stop stop-color="#ece9d7"/><stop offset=".4" stop-color="#c9d1ca"/>
      <stop offset="1" stop-color="#758991"/>
    </radialGradient>''',
    )


INTERESTS = (
    ("Artificial", "Intelligence"),
    ("Machine Learning",),
    ("Data Science",),
    ("Generative AI",),
    ("AI Memory Systems",),
    ("Multi-Agent", "Orchestration"),
    ("Open-Source", "Development"),
)
TECHNICAL_DESCRIPTION = (
    "A vertical quest map linking three islands, with areas of interest alongside. "
    "Languages and data: Python, Java, R, and SQL. "
    "Web: JavaScript, HTML & CSS, and React. "
    "Version control: Git & GitHub. Interests include artificial intelligence, machine learning, "
    "data science, generative AI, AI memory systems, multi-agent orchestration, and open-source development."
)
GROUPS = (
    ("Languages & data", ("Python · Java · R · SQL",)),
    ("Web", ("JavaScript · HTML & CSS", "React")),
    ("Version control", ("Git & GitHub",)),
)
ISLANDS = (
    ("M-68 7Q-65-11-44-19T-14-30Q4-36 19-25T42-18Q64-17 69 0T54 19Q31 34 10 24T-19 27Q-36 32-53 20T-68 7Z",
     "M-18-9l-10 9 10 9m36-18 10 9-10 9M5-13L-5 13"),
    ("M-65 4Q-62-14-47-15T-24-27Q-9-36 11-28T39-26Q59-29 66-12T65 12Q56 30 36 25T15 24Q-4 35-24 24T-52 20Q-65 17-65 4Z",
     "M-22-13h44v27h-44zM-22-5h44m-36-4h2m5 0h2"),
    ("M-65-4Q-63-20-42-21T-19-28Q1-39 20-25T44-19Q63-18 67-1T52 20Q38 29 19 23T-5 26Q-23 35-41 24T-65-4Z",
     "M-12-8v17m0-8q25 0 25-12M-12-13a4 4 0 1 0 0 .01M-12 15a4 4 0 1 0 0 .01M13-16a4 4 0 1 0 0 .01"),
)


def island(x, y, artwork, scale=1):
    shore, icon = artwork
    return f'''
    <g transform="translate({x} {y}) scale({scale})">
      <path d="{shore}" fill="#ede2c8" stroke="#827455" stroke-width="2.1" stroke-linejoin="round"/>
      <path d="{shore}" transform="scale(.84 .73)" fill="none" stroke="#ac9970"
        stroke-width="1.3" stroke-dasharray="2 3.4" opacity=".74"/>
      <path d="{icon}" fill="none" stroke="{NAVY}" stroke-width="2.65" stroke-linecap="round" stroke-linejoin="round"/>
    </g>
    '''


def quest_sea(x, y, width, height):
    return f'''
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="13" fill="#b6bfbb"
      fill-opacity=".31" stroke="#81745b" stroke-opacity=".56" stroke-width="1.6"/>
    '''


def quest_route(path, waypoints):
    return f'''
    <path d="{path}" fill="none" stroke="#796e54" stroke-width="2.7" stroke-linecap="round" stroke-dasharray="3 9"/>
    {waypoints}
    <g class="tracers">{pulse(path, 8.6, -1.15, radius=6.2, color="#a06b27")}</g>
    '''


def interest_column(x, y, size, *, narrow=False):
    if narrow:
        heading = label("AREAS OF", y, 15, x=x) + label("INTEREST", y + 21, 15, x=x)
        y += 62
    else:
        heading = label("AREAS OF INTEREST", y, 19, x=x)
        y += 45
    lines = []
    for index, item in enumerate(INTERESTS):
        if index == 0 and not narrow:
            item = (" ".join(item),)
        for part in item:
            lines.append(text(part, y, size, x=x))
            y += size + 5
        y += 11
    return heading + "".join(lines)


def technical():
    path = (
        "M157 166C145 185 196 191 204 222S135 254 158 273 "
        "S271 293 264 333 129 379 149 411S217 420 200 455 139 485 155 516"
    )
    positions = ((204, 222), (264, 333), (200, 455))
    landmarks = "".join(island(x, y, shape, 1.1) for (x, y), shape in zip(positions, ISLANDS))
    stops = "".join(
        text(title, y + 1, 32, x=384, font=DISPLAY)
        + text(" · ".join(items), y + 39, 26, x=384, fill=NAVY)
        for (_, y), (title, items) in zip(positions, GROUPS)
    )
    return page(
        "Technical Universe", TECHNICAL_DESCRIPTION, 568,
        f'''
    {text("Technical Universe", 104, 59, font=DISPLAY)}
    {image("compass", 1058, 25, 71, 94)}
    {quest_sea(64, 137, 782, 397)}
    <path d="M99 310q8-6 16 0t16 0m184-106q8-6 16 0t16 0m-28 267q8-6 16 0t16 0m388-75q8-6 16 0t16 0"
      fill="none" stroke="#647a7c" stroke-width="1.8" stroke-linecap="round" opacity=".48"/>
    {quest_route(path, landmarks)}
    {stops}
    {interest_column(881, 169, 23)}
    ''',
        "compass",
    )


def technical_mobile():
    path = (
        "M80 165C69 185 110 194 100 220S65 261 82 284Q115 309 108 351 "
        "S68 411 80 440 114 456 101 485 73 526 88 558"
    )
    positions = ((100, 220), (108, 351), (101, 485))
    landmarks = "".join(island(x, y, shape, .66) for (x, y), shape in zip(positions, ISLANDS))
    stops = "".join(
        text(title, y + 1, 27, x=171, font=DISPLAY)
        + "".join(text(line, y + 34 + index * 27, 22, x=171, fill=NAVY)
                  for index, line in enumerate(items))
        for (_, y), (title, items) in zip(positions, GROUPS)
    )
    return page(
        "Technical Universe", TECHNICAL_DESCRIPTION, 630,
        f'''
    {text("Technical Universe", 100, 46, x=43, font=DISPLAY)}
    {image("compass", 604, 29, 66, 87)}
    {quest_sea(43, 133, 426, 455)}
    <path d="M61 318q7-5 14 0t14 0m45 102q7-5 14 0t14 0"
      fill="none" stroke="#647a7c" stroke-width="1.7" stroke-linecap="round" opacity=".48"/>
    {quest_route(path, landmarks)}
    {stops}
    {interest_column(494, 163, 20, narrow=True)}
    ''',
        "compass", width=720,
    )


def beyond():
    return page(
        "Beyond the Code",
        "I study data science and AI. I also write poetry and paint. "
        "I’m drawn to where logic and creativity meet.",
        326,
        f'''
    {text("Beyond the Code", 107, 54, font=DISPLAY)}
    {text("I study data science and AI. I also write", 179, 30)}
    {text("poetry and paint. I’m drawn to where", 225, 30)}
    {text("logic and creativity meet.", 271, 30)}
    <path class="logline" d="M801 279q39-10 70 0t70 0t70 0t70 0"
      fill="none" stroke="#807859" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="4 7"/>
    {image("logbook", 799, 49, 315, 239)}
    ''',
        "logbook",
    )


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    check = parser.parse_args().check
    for build in (intro, mnemoai, repolens, technical, technical_mobile, beyond):
        output = ASSETS / f"{build.__name__.replace('_', '-')}.svg"
        scene = build()
        if check:
            if output.read_text() != scene:
                raise SystemExit(f"{output} needs to be rebuilt")
        else:
            output.write_text(scene)


if __name__ == "__main__":
    main()
