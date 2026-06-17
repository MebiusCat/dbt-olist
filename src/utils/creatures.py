import random

CREATURES_DATA = [
    {
        "kaomoji": "☂[o_o]",
        "name": "Aegis",
        "start": "Deploying the defense umbrella... Bring on the errors!",
        "success": "Storm has passed. Clean run, not a single drop of error reached us!"
    },
    {
        "kaomoji": "««(o_o)»»",
        "name": "Sonar",
        "start": "Scanning frequencies... System perimeter is clear.",
        "success": "Scan complete. All data sectors are peaceful and secure."
    },
    {
        "kaomoji": "(⌐■_■)",
        "name": "Matrix",
        "start": "Architect mode on. Time to execute this master plan.",
        "success": "Just as built. Beautiful execution, zero refactoring needed."
    },
    {
        "kaomoji": "ヘ( ^o^ )ノ",
        "name": "Spark",
        "start": "All engines green! We are officially live!",
        "success": "Touchdown! Operation successful, high fives all around!"
    },
    {
        "kaomoji": "└[o_o]┘",
        "name": "Cargo",
        "start": "Heavy payload detected. Loading operational modules...",
        "success": "All packages safely delivered. Unloading completed without leaks."
    },
    {
        "kaomoji": "⊂(▀¯▀_ )",
        "name": "Vanguard",
        "start": "Sentinel active. No unauthorized queries on my watch.",
        "success": "Mission accomplished. Perimeter secure, threatening bugs neutralized."
    },
    {
        "kaomoji": "＼| ￣–￣ |／",
        "name": "Titan",
        "start": "I awaken from a thousand-year slumber to guard this data.",
        "success": "My watch is temporarily over. The data remains untouched and eternal."
    },
    {
        "kaomoji": "ᕦ(ò_ó)ᕤ",
        "name": "Apex",
        "start": "Powering up to maximum capacity! Let's crush this task.",
        "success": "Task absolutely crushed! Systems cooling down now."
    },
    {
        "kaomoji": "ᕙ(^▿^-)ᕗ",
        "name": "Orion",
        "start": "Space pilot in the cockpit. Ready for liftoff!",
        "success": "Orbit reached successfully. Smooth landing, planet secured!"
    },
    {
        "kaomoji": "(⊙_☉)",
        "name": "Giga",
        "start": "Holy moly... Look at the size of this batch!",
        "success": "We actually processed all of that?! Unbelievable, but it's done!"
    },
    {
        "kaomoji": "(⚆_⚆)",
        "name": "Inspector",
        "start": "Terabytes scanned... Zero violations detected. Carry on.",
        "success": "Final audit complete. Perfect data integrity. You may proceed."
    },
    {
        "kaomoji": "╚(•⌂•)╝",
        "name": "Panic_Bot",
        "start": "Shields powering UP! Emergency power redirected to awesome!",
        "success": "We survived?! I mean—of course, calculated victory! Shields recharging."
    },
    {
        "kaomoji": "(o_o)7",
        "name": "Cadet",
        "start": "Aye-aye, captain! Execution sequence initiated.",
        "success": "Mission accomplished, captain! Awaiting your next orders!"
    },
    {
        "kaomoji": "(o_o)ﾉ",
        "name": "Rogue",
        "start": "Haha, bye losers! Let's see if you survive the debug.",
        "success": "Dropped the mic and leaving. It actually worked, see ya next time!"
    }
]

_CURRENT_CREATURE = random.choice(CREATURES_DATA)

def get_log_format(event_type: str, fun_mode: bool) -> str:
    plain_messages = {
        "start": "Pipeline initialized. Monitoring system state...",
        "success": "Pipeline finished successfully. Data transfer completed.",
    }
    if not fun_mode:
        return plain_messages.get(event_type, "")
    
    cc = _CURRENT_CREATURE
    return f"[{cc['name']}] {cc['kaomoji']} : {cc[event_type]}"

