def show_decision(decision):
    print("\n================ HUMAN VIEW: VIDEO PLAN ================")

    print(f"\n🎯 Hook:\n{decision.hook}")

    print(f"\n💡 Selling Points:")
    for p in decision.selling_points:
        print(f"- {p}")

    print(f"\n📝 Script:\n{decision.script}")

    print("\n🎬 Storyboard:")
    for s in decision.storyboard:
        print(f"- {s['scene_id']} | {s['duration']}s | {s['visual_desc']}")


def show_composition(plan):
    print("\n================ VIDEO EDIT PLAN ================")

    for clip in plan.clip_order:
        print(
            f"{clip['scene_id']} | {clip['duration']}s | "
            f"{clip['emphasis']} | {clip['transition_after']} | {clip['cta_slot']}"
        )
