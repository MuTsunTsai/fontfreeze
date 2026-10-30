# syntax=docker/dockerfile:1
#
# Build a uharfbuzz wheel for Pyodide 0.25.1 (Python 3.11.3, Emscripten 3.1.46).
# Upstream only ships `pyemscripten_2025_0` / `2026_0` wheels, which are ABI-incompatible with Pyodide 0.25.
#
# Usage (needs BuildKit, the default in recent Docker):
#
#   docker build -o dist .
#
# The wheel is written to ./dist/. Nothing is installed on the host; the build runs a smoke test
# in Node.js + Pyodide 0.25.1 before exporting, so a successful build means the wheel actually loads.

ARG PYODIDE_VERSION=0.25.1
# Not named EMSDK_VERSION: emsdk_env.sh unsets that variable.
ARG EMSCRIPTEN_VERSION=3.1.46
ARG UHARFBUZZ_VERSION=0.57.0
ARG FONTTOOLS_WHEEL=https://files.pythonhosted.org/packages/35/74/4ea331ecc65ba05a58b1e4e8ccd604c8a15565f876dfbf93fc2a2ea2e22b/fonttools-4.68.0-py3-none-any.whl

#####################################################################################################
# Build
#####################################################################################################

# pyodide-build requires the host Python minor version to match Pyodide's (3.11).
FROM python:3.11-bookworm AS build
ARG PYODIDE_VERSION
ARG EMSCRIPTEN_VERSION
ARG UHARFBUZZ_VERSION
SHELL ["/bin/bash", "-c"]

RUN git clone --depth 1 https://github.com/emscripten-core/emsdk.git /emsdk \
	&& /emsdk/emsdk install ${EMSCRIPTEN_VERSION} \
	&& /emsdk/emsdk activate ${EMSCRIPTEN_VERSION}

# Resolve pyodide-build's (loosely pinned) dependencies as of its release date,
# so that newer releases of typer, pydantic, etc. cannot break it.
# A fresh venv is required: the base image ships a recent `wheel` (without `wheel.cli`, which
# auditwheel-emscripten 0.0.9 needs), and uv would keep it since it already satisfies the requirement.
RUN pip install --no-cache-dir uv \
	&& uv venv /venv --python /usr/local/bin/python3.11 \
	&& uv pip install --python /venv --exclude-newer 2024-04-01 pyodide-build==${PYODIDE_VERSION} pip
ENV PATH=/venv/bin:$PATH

# The sdist bundles the HarfBuzz sources (the git repo uses a submodule).
WORKDIR /work
RUN python - <<'EOF'
import json, os, tarfile, urllib.request

version = os.environ["UHARFBUZZ_VERSION"]
with urllib.request.urlopen(f"https://pypi.org/pypi/uharfbuzz/{version}/json") as res:
	info = json.load(res)
url = next(u["url"] for u in info["urls"] if u["filename"].endswith(".tar.gz"))
path, _ = urllib.request.urlretrieve(url)
with tarfile.open(path) as tar:
	tar.extractall("/work")
EOF

WORKDIR /work/uharfbuzz-${UHARFBUZZ_VERSION}
# The first `pyodide` call downloads the cross-build environment into ./.pyodide-xbuildenv and prints
# progress to stdout, so only the last line is the actual value.
RUN EMSDK_QUIET=1 source /emsdk/emsdk_env.sh \
	&& EXPECTED="$(pyodide config get emscripten_version | tail -n 1)" \
	&& echo "Pyodide ${PYODIDE_VERSION} expects Emscripten ${EXPECTED}" \
	&& if [ "${EXPECTED}" != "${EMSCRIPTEN_VERSION}" ]; then echo "EMSCRIPTEN_VERSION mismatch: ${EMSCRIPTEN_VERSION}" >&2; exit 1; fi

# The limited API buys nothing here since the Python version is fixed; a plain cp311 wheel is the safer choice.
# `--exports pyinit`: the CLI default ("requested") puts every public symbol of the objects into a single
# -sEXPORTED_FUNCTIONS argument, and with all of HarfBuzz in one object that exceeds Linux's 128 KiB
# per-argument limit. An extension module only needs its PyInit_* entry point anyway.
RUN source /emsdk/emsdk_env.sh \
	&& USE_PY_LIMITED_API=0 pyodide build --exports pyinit -o /dist \
	&& mkdir -p /fonts && cp tests/data/*.ttf tests/data/*.otf /fonts/ \
	&& ls -l /dist

#####################################################################################################
# Smoke test: load the wheel in Pyodide 0.25.1 and pack GSUB/GPOS through fontTools + hb.repack
#####################################################################################################

FROM node:20-bookworm-slim AS test
ARG PYODIDE_VERSION
ARG FONTTOOLS_WHEEL
ENV FONTTOOLS_WHEEL=${FONTTOOLS_WHEEL}
WORKDIR /test
RUN npm init -y >/dev/null && npm install --no-audit --no-fund pyodide@${PYODIDE_VERSION}
COPY --from=build /dist /dist
COPY --from=build /fonts /fonts

COPY <<'EOF' test.mjs
import { loadPyodide } from "pyodide";
import { readdirSync, readFileSync } from "node:fs";

const py = await loadPyodide();
const wheel = readdirSync("/dist").find(f => f.endsWith(".whl"));
console.log("Testing", wheel);
await py.loadPackage("/dist/" + wheel);
await py.loadPackage(process.env.FONTTOOLS_WHEEL);

py.FS.mkdir("/fonts");
for(const f of readdirSync("/fonts")) py.FS.writeFile("/fonts/" + f, readFileSync("/fonts/" + f));

py.runPython(`
import os, uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otBase

print("uharfbuzz", hb.__version__, "/ HarfBuzz", hb.version_string())
assert otBase.have_uharfbuzz

# Plain shaping, to make sure the core library works.
blob = hb.Blob.from_file_path("/fonts/OpenSans.subset.ttf")
buf = hb.Buffer()
buf.add_str("Hello")
buf.guess_segment_properties()
hb.shape(hb.Font(hb.Face(blob)), buf)
assert len(buf.glyph_infos) == 5

# Force fontTools to go through hb.repack (raises instead of falling back to the Python packer).
packed = 0
for name in sorted(os.listdir("/fonts")):
	font = TTFont("/fonts/" + name)
	font.cfg[otBase.USE_HARFBUZZ_REPACKER] = True
	for tag in ("GSUB", "GPOS"):
		if tag in font and getattr(font[tag].table, "Version", 0) < 0x00010002:
			data = font[tag].compile(font)
			print(f"  {name} {tag}: {len(data)} bytes")
			packed += 1
assert packed > 0, "no GSUB/GPOS table was packed"
print("OK")
`);
EOF

RUN node test.mjs

#####################################################################################################
# Export (only reached if the test passes)
#####################################################################################################

FROM scratch AS export
COPY --from=test /dist/ /
