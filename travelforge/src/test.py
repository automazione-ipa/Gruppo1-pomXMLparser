# detect_langchain.py
import importlib
import sys
import pkgutil

def try_import(modname):
    try:
        mod = importlib.import_module(modname)
        return True, mod
    except Exception as e:
        return False, e

print("PYTHON:", sys.version)
print("Installed langchain-related packages (quick scan):")
for name in sorted({m.name for m in pkgutil.iter_modules()}):
    if name.startswith("langchain") or name.startswith("langchain_") or name == "langchain_core":
        print("  -", name)

# Check langchain version
ok, mod = try_import("langchain")
if ok:
    try:
        print("langchain.__version__ =", getattr(mod, "__version__", "unknown"))
    except Exception:
        print("langchain loaded but no __version__")

else:
    print("langchain import failed:", mod)

print("\n-- Trying common import locations for chat model factory and PydanticOutputParser --\n")

chat_candidates = [
    "langchain.chat_models",                 # maybe has init_chat_model
    "langchain.chat_models.openai",          # older/newer layouts
    "langchain.chat_models.openai_chat",     # guessing
    "langchain.chat_models._openai",         # guessing
]

parser_candidates = [
    "langchain.output_parsers.pydantic",
    "langchain.output_parsers",
    "langchain.output_parsers.pydantic_output",
    "langchain.schema",
    "langchain_core.output_parsers.pydantic",
    "langchain_core.schema",
]

print("Chat model import attempts:")
for c in chat_candidates:
    ok, res = try_import(c)
    print(f"  {c:<40} ->", "OK" if ok else f"FAIL ({type(res).__name__})")

print("\nParser import attempts:")
for p in parser_candidates:
    ok, res = try_import(p)
    print(f"  {p:<40} ->", "OK" if ok else f"FAIL ({type(res).__name__})")

# Try to locate PydanticOutputParser symbol
found = False
for p in parser_candidates:
    ok, mod = try_import(p)
    if ok:
        if hasattr(mod, "PydanticOutputParser"):
            print(f"\nPydanticOutputParser found in {p}")
            found = True
            break
        else:
            print(f"  {p} imported but PydanticOutputParser not present; attributes: {sorted([a for a in dir(mod) if not a.startswith('_')])[:20]}")
if not found:
    print("\nPydanticOutputParser not found in checked locations. You probably need to install the proper langchain version or the 'langchain-openai' provider.")

print("\nDONE. If imports fail, run:\n  pip install --pre -U langchain==1.0.0a10 langchain-openai openai python-dotenv pydantic\nor\n  pip install langchain==0.3.27 openai python-dotenv pydantic\ndepending whether you want the 1.0 alpha or stable 0.3.x.")
