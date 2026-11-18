"""CLI entry points for the editor's film planning and review workflow."""
import film_plan
import film_review_server
import film_variants
import footage_selects
import studio_core as core
import style_feedback


def add_parsers(sub):
    p = sub.add_parser("plan", help="Resolve a film brief into one route, required inputs and next commands")
    p.add_argument("brief")
    p.add_argument("--job")
    p.add_argument("--kind", choices=core.routes())
    p.add_argument("--profile")
    p = sub.add_parser("selects", help="Rank quotes and source in/out points; optionally index a local transcript")
    p.add_argument("job")
    p.add_argument("--query", default="")
    p.add_argument("--asset")
    inputs = p.add_mutually_exclusive_group()
    inputs.add_argument("--transcript", help="Job-relative measured Whisper JSON for this registered asset")
    inputs.add_argument("--model", help="Local whisper.cpp model; requires whisper-cli on PATH")
    p = sub.add_parser("variants", help="Three playable styles and human review")
    actions = p.add_subparsers(dest="action", required=True)
    for name in ("openings", "build", "serve", "rate", "import", "prefer", "use"):
        action = actions.add_parser(name)
        action.add_argument("job")
        if name in ("serve", "rate", "import", "use"):
            action.add_argument("--collection", required=True)
        if name in ("rate", "use"):
            action.add_argument("--style", choices=style_feedback.STYLES, required=name == "use")
        if name == "rate":
            action.add_argument("--stars", type=int, choices=range(1, 6))
            action.add_argument("--note")
        if name == "import":
            action.add_argument("--source", required=True)
        if name == "serve":
            action.add_argument("--port", type=int, default=0)
        if name == "build":
            action.add_argument("--render")
        if name == "openings":
            action.add_argument("--query", default="")


def run(args, job_path, emit):
    if args.command == "plan":
        emit(film_plan.plan(args.brief, job_path(args.job) if args.job else None, kind=args.kind, profile=args.profile))
        return 0
    folder = job_path(args.job)
    if args.command == "selects":
        if args.asset:
            footage_selects.media(folder, args.asset)
        if args.transcript or args.model:
            if not args.asset:
                raise ValueError("Bind the transcript to a registered asset with --asset")
            footage_selects.index(folder, args.asset, transcript=args.transcript, model=args.model)
        emit(footage_selects.shortlist(folder, args.query, args.asset))
        return 0
    if args.action == "openings":
        emit(film_variants.render_set(folder, openings=True, query=args.query))
    elif args.action == "build":
        emit(film_variants.render_set(folder, args.render))
    elif args.action == "prefer":
        job = core.read(folder / "job.json")
        emit(style_feedback.summary(folder.parent, job.get("style_profile", "local")))
    elif args.action == "serve":
        film_review_server.run(folder, args.collection, args.port)
    elif args.action == "import":
        emit(style_feedback.import_file(folder, args.collection, args.source))
    elif args.action == "rate" and not args.style:
        if args.stars is not None or not args.note or not args.note.strip():
            raise ValueError("Provide --style to rate a version, or --note for a comment on all versions")
        emit(style_feedback.save(folder, args.collection, [], "chat", general_note=args.note))
    else:
        directory, manifest = style_feedback.collection(folder, args.collection)
        variant = next(v for v in manifest["variants"] if v["style"] == args.style)
        if args.action == "rate":
            entry = {"style": args.style, "sha256": variant["sha256"], "stars": args.stars, "note": args.note}
            emit(style_feedback.save(folder, args.collection, [entry], "chat"))
        elif args.action == "use":
            if manifest["kind"] != "films":
                raise ValueError("Select a full film as the master")
            path = core.local(directory, variant["file"]).relative_to(folder).as_posix()
            if core.sha(folder / path) != variant["sha256"]:
                raise ValueError("Film has changed")
            receipt = core.render_provenance(folder, path)
            if receipt.get("fingerprint") != core.fingerprint(folder):
                raise ValueError("Film sources have changed; render again")
            result = core.probe_job(folder, path)
            emit({"render": path, "probe_passed": result["passed"], "failures": result["failures"], "reviewed": False})
            return int(not result["passed"])
    return 0
