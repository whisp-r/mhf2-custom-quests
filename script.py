import subprocess
import shutil
from pathlib import Path

CONFIG = {
    "loader-path": "loader",
    "f2questparser-path": "whiisper-parser",
    "ppsspp-path": "C:\\Users\\whiisper\\Desktop\\custom_psp\\",
    "ppsspp-savedata-name": "ULUS10266",
    "clean-to-append-cheat-ini-file": "base_cheats.ini",
    "input-json-path": "input",
    "input-json-quests": [
        "m60050.json",
        "m60051.json",
        "m60052.json",
        "m60053.json",
        "m60054.json",
        "m60055.json",
        "m60056.json",
        "m60057.json",
        "m60058.json",
        "m60059.json",
        "m60060.json",
        "m60061.json",
        "m60062.json",
        "m60063.json",
        "m60064.json",
    ],
}

out_quest_path = Path(CONFIG["loader-path"]) / "quests" / "Full"
in_quest_path = Path(CONFIG["input-json-path"])
script_path = Path(CONFIG["loader-path"]) / "generate.py"
f2questparser_script = Path(CONFIG["f2questparser-path"]) / "f2questparser.py"


# prepare Full folder in loader
print("removing " + str(out_quest_path))
if out_quest_path.exists():
    shutil.rmtree(out_quest_path)
print("creating " + str(out_quest_path))
out_quest_path.mkdir(parents=True)


# for quests in folder (input)
# run f2questparser.py <quest> <output_mib_folder (existing)>
for item in in_quest_path.iterdir():
    if item.is_file() and item.name in CONFIG["input-json-quests"]:
        print(f"f2questparser {item} {out_quest_path}")
        subprocess.run(["python", str(f2questparser_script), "-e", str(item), str(out_quest_path)])


# run generate.py
subprocess.run(
    ["python", script_path.name],
    cwd=script_path.parent,
    check=True
)

cheat_ini_name: str = CONFIG["ppsspp-savedata-name"] + ".ini"
cheat_file = Path(CONFIG["ppsspp-path"]) / "memstick" / "PSP" / "Cheats" / cheat_ini_name
build_mhf2qst_path = Path(CONFIG["loader-path"]) / "build" / "MHF2QST"
ppsspp_mhf2qst_path = Path(CONFIG["ppsspp-path"]) / "memstick" / "PSP" / "SAVEDATA" / "MHF2QST"
base_cheat_path = Path(CONFIG["clean-to-append-cheat-ini-file"])
built_cheat_path = Path(CONFIG["loader-path"]) / "build" / cheat_ini_name

# clean up the cheat and event.bin from before
print("removing " + str(ppsspp_mhf2qst_path))
if ppsspp_mhf2qst_path.exists():
    shutil.rmtree(ppsspp_mhf2qst_path)

print("removing " + str(cheat_file))
if cheat_file.exists():
    cheat_file.unlink()


# copy over mhf2qst/event.bin
print("copy " + str(build_mhf2qst_path) + str(ppsspp_mhf2qst_path))
shutil.copytree(str(build_mhf2qst_path), str(ppsspp_mhf2qst_path), dirs_exist_ok=True)

# combine into single cheat file
print("writing a: " + str(built_cheat_path) + "\tb: " + str(base_cheat_path))
cheat_file.write_text(
    built_cheat_path.read_text()
    + "\n\n" +
    base_cheat_path.read_text()
)
