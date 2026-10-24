#!/usr/bin/env python3
"""Social Motion Studio: local jobs, skill routing, assembly and evidence checks."""
import argparse
import json
import shlex
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
import studio_core as core
from assembly import assemble
from edit_bridge import OPS as EDIT_OPS, edit as run_edit
import backgrounds_catalog
import bg_video
import motion_catalog
import sfx_catalog
import environment


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def job_path(value):
    root = (core.ROOT / "output/jobs").resolve()
    candidate = Path(value)
    path = candidate.resolve() if candidate.is_absolute() else (core.ROOT / value).resolve()
    if not path.is_relative_to(root) or not (path / "job.json").is_file():
        raise ValueError("Wskaż istniejącą produkcję wewnątrz output/jobs/")
    return path


def doctor():
    report = environment.inspect()
    core.write(core.ROOT / "output/system/doctor.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("demo", help="Create the bundled synthetic HyperFrames launch film")
    p.add_argument("--format", choices=core.FORMATS, default="16:9")
    p.add_argument("--render", action="store_true")
    p = sub.add_parser("render-html", help="Lint and render a job's source/index.html with pinned HyperFrames")
    p.add_argument("job")
    p.add_argument("--name", default="hyperframes")
    p.add_argument("--quality", choices=("draft", "standard", "high"), default="standard")
    sub.add_parser("map", help="Krótka mapa dostępnych ścieżek")
    sub.add_parser("doctor", help="Sprawdź lokalne narzędzia i ścieżki, bez sekretów i sieci")
    p = sub.add_parser("setup", help="Sprawdź środowisko i zainstaluj przypięte zależności lokalnie")
    p.add_argument("--with-library", action="store_true", help="Pobierz także pełną bibliotekę przypiętych źródeł i sprawdź jej integralność")
    p = sub.add_parser("route", help="Pokaż wybrane skille i oczekiwane wyniki")
    p.add_argument("kind", choices=core.routes())
    p = sub.add_parser("find", help="Szukaj w katalogu bez czytania wszystkich SKILL.md")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=12)
    p.add_argument("--source")
    p = sub.add_parser("motion", help="Katalog 637 efektów ruchu: find, show, recipe (tools/repos/awesome-ai-motion)")
    p.add_argument("action", choices=("find", "show", "recipe"))
    p.add_argument("query", nargs="?", default="", help="find: fraza; show: slug efektu; recipe: slug receptury")
    p.add_argument("--purpose")
    p.add_argument("--medium")
    p.add_argument("--family")
    p.add_argument("--level")
    p.add_argument("--rendered", action="store_true", help="tylko efekty z gotowym klipem i szablonem HTML")
    p.add_argument("--limit", type=int, default=12)
    p = sub.add_parser("sfx", help="Biblioteka SOUND EFFECTS: find, check, build (efekty nigdy powyżej 0.5 głośności)")
    p.add_argument("action", choices=("find", "check", "build"))
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--category")
    p.add_argument("--max-duration", type=float)
    p.add_argument("--limit", type=int, default=15)
    p = sub.add_parser("background", help="Tło z obrazu jako klip wideo (najazd, dryf albo statyczne)")
    p.add_argument("image", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--duration", type=float, required=True)
    p.add_argument("--format", choices=core.FORMATS, default="9:16")
    p.add_argument("--motion", choices=("push", "drift", "none"), default="push")
    p.add_argument("--amount", type=float, default=0.12)
    p = sub.add_parser("polish", help="Kontrola dopracowania ramki HTML: pomiary tekstu, bezpieczne pole, bramki UX")
    p.add_argument("html", type=Path)
    p.add_argument("--format", choices=core.FORMATS, default="16:9")
    p.add_argument("--seek", type=float, help="sekunda sceny; domyślnie koniec animacji")
    p.add_argument("--shot", type=Path, help="zapisz zrzut PNG")
    p.add_argument("--no-upstream", action="store_true")
    p = sub.add_parser("new", help="Załóż produkcję; nie uruchamia usług ani generacji")
    p.add_argument("title")
    p.add_argument("--kind", choices=core.routes(), required=True)
    p.add_argument("--format", choices=core.FORMATS, default="16:9")
    p.add_argument("--duration", type=float, required=True)
    p.add_argument("--language", default="pl")
    for name in ("resume", "pack"):
        p = sub.add_parser(name)
        p.add_argument("job")
    p = sub.add_parser("check", help="Sprawdź dowody wymagane dla etapu")
    p.add_argument("job")
    p.add_argument("--stage", choices=core.STAGES, required=True)
    p = sub.add_parser("asset-add", help="Skopiuj asset i zapisz pochodzenie")
    p.add_argument("job")
    p.add_argument("--file", type=Path, required=True)
    for option in ("source", "rights", "purpose"):
        p.add_argument("--" + option, required=True)
    p.add_argument("--provider")
    p.add_argument("--endpoint")
    p.add_argument("--request-id")
    p.add_argument("--prompt-file", type=Path)
    p = sub.add_parser("render-assembly", help="Zmontuj timeline przez lokalny FFmpeg")
    p.add_argument("job")
    p = sub.add_parser("edit", help="Edytuj zarejestrowany asset: efekty (fx) lub vstudio; sam robi probe i sheet")
    p.add_argument("job")
    p.add_argument("op", choices=EDIT_OPS)
    p.add_argument("--asset", action="append", required=True, help="ID z asset-add; concat przyjmuje kilka")
    p.add_argument("--name", required=True, help="Nowa nazwa renderu (bez rozszerzenia)")
    p.add_argument("--spec", help="fx: JSON z efektami względem katalogu produkcji, np. source/effects.json")
    p.add_argument("--effect", action="append", default=[], help="fx: np. punch_in:start=1,end=2.2,zoom=1.3")
    p.add_argument("--vstudio-args", default="", help="Dodatkowe argumenty vstudio edit, np. \"--start 1.5 --end 9\"")
    for name in ("probe", "sheet"):
        p = sub.add_parser(name)
        p.add_argument("job")
        p.add_argument("--render", required=True, help="Ścieżka względem katalogu produkcji")
    args = parser.parse_args()
    try:
        if args.command == "demo":
            from demo import create_demo
            folder = create_demo(args.format)
            result = {"job": str(folder), "synthetic_demo": True, "reviewed": False}
            if args.render:
                from hyperframes_adapter import render
                result.update(render(folder, "demo", "draft"))
            emit(result)
            return int(args.render and not result["probe_passed"])
        elif args.command == "map":
            emit({key: value["purpose"] for key, value in core.routes().items()})
        elif args.command == "doctor":
            report = doctor()
            emit(report)
            return int(not report["ready"])
        elif args.command == "setup":
            report = environment.setup(with_library=args.with_library)
            emit(report)
            return int(not report["setup"]["passed"])
        elif args.command == "route":
            route = dict(core.routes()[args.kind])
            route["read_first"] = core.read(core.ROOT / "config/routes.json")["always_read"]
            route["resolved_skills"] = [{"path": str(core.resolve_ref(p)), "exists": core.resolve_ref(p).is_file()} for p in route["skills"]]
            route["resolved_optional_skills"] = [{"path": str(core.resolve_ref(p)), "exists": core.resolve_ref(p).is_file()}
                                                for p in route.get("optional_skills", [])]
            emit(route)
        elif args.command == "find":
            tokens = args.query.casefold().split()
            entries = core.read(core.ROOT / "skills/catalog.json")["entries"]
            found = [item for item in entries if item["kind"] != "fixture" and (not args.source or item["source"] == args.source) and
                     all(token in " ".join(str(item.get(key, "")) for key in ("name", "description", "source", "path")).casefold() for token in tokens)]
            emit({"total_matches": len(found), "entries": found[:max(1, min(args.limit, 100))]})
        elif args.command == "motion":
            if args.action == "find":
                emit(motion_catalog.find(args.query, args.purpose, args.medium, args.family, args.level, args.rendered, args.limit))
            elif args.action == "show":
                emit(motion_catalog.show(args.query))
            else:
                emit(motion_catalog.recipe(args.query or None))
        elif args.command == "sfx":
            if args.action == "find":
                emit(sfx_catalog.find(args.query, args.category, args.max_duration, args.limit))
            elif args.action == "build":
                data = sfx_catalog.build()
                emit({"indexed": data["count"], "index": str(sfx_catalog.INDEX)})
            else:
                problems = sfx_catalog.check()
                emit({"passed": not problems, "problems": problems})
                return int(bool(problems))
        elif args.command == "background":
            emit(bg_video.render(args.image, args.output, args.duration, args.format, args.motion, args.amount))
        elif args.command == "polish":
            command = [sys.executable, "-I", str(core.ROOT / "scripts/polish_check.py"), str(args.html), "--format", args.format]
            command += ["--seek", str(args.seek)] if args.seek is not None else []
            command += ["--shot", str(args.shot)] if args.shot else []
            command += ["--no-upstream"] if args.no_upstream else []
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
            print(result.stdout, end="")
            if result.returncode and result.stderr:
                print(result.stderr[-1500:], file=sys.stderr)
            return result.returncode
        elif args.command == "new":
            folder = core.create_job(args.title, args.kind, args.format, args.duration, args.language)
            emit({"job": str(folder), "next": "Przeczytaj 5-pytan; dostosuj 5 pytań i zbierz odpowiedzi. Potem research."})
        else:
            folder = job_path(args.job)
            if args.command == "check":
                errors = core.check_job(folder, args.stage)
                emit({"stage": args.stage, "passed": not errors, "errors": errors})
                return int(bool(errors))
            if args.command == "resume":
                job = core.read(folder / "job.json")
                for stage in core.STAGES:
                    errors = core.check_job(folder, stage)
                    if errors:
                        emit({"job": job, "next_stage": stage, "missing": errors, "route": core.routes()[job["kind"]], "handoff": str(folder / "HANDOFF.md")})
                        break
                else:
                    emit({"job": job, "next": "Gotowe do pack; publikacja wymaga zgody"})
            elif args.command == "asset-add":
                metadata = {key: value for key, value in {"provider": args.provider, "endpoint": args.endpoint,
                            "request_id": args.request_id,
                            "prompt": args.prompt_file.read_text(encoding="utf-8-sig") if args.prompt_file else None}.items() if value}
                emit(core.register_asset(folder, args.file, args.source, args.rights, args.purpose, **metadata))
            elif args.command == "render-html":
                from hyperframes_adapter import render
                result = render(folder, args.name, args.quality)
                emit(result)
                return int(not result["probe_passed"])
            elif args.command == "render-assembly":
                errors = core.check_job(folder, "assets")
                if errors:
                    raise ValueError("\n".join(errors))
                emit({"render": str(assemble(folder)), "reviewed": False})
            elif args.command == "edit":
                result = run_edit(folder, args.op, args.asset, args.name, args.spec, args.effect,
                                  shlex.split(args.vstudio_args))
                emit(result)
                return int(not result["probe_passed"])
            elif args.command == "probe":
                result = core.probe_job(folder, args.render)
                emit({key: value for key, value in result.items() if key != "ffprobe"})
                return int(not result["passed"])
            elif args.command == "sheet":
                emit({"contact_sheet": str(core.contact_sheet(folder, args.render))})
            elif args.command == "pack":
                emit({"package": str(core.package_job(folder)), "published": False})
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
