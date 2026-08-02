import os
import shutil
import subprocess
from tools.cwcheatio import CwCheatIO

QUESTS_LANG = "Custom" # JPN, USA, EUR, Full
asm_src_dir = "source"
build_dir = "build"
quests_dir = "quests"
armips = os.path.join("tools", "armips.exe")

def combineQuests():
    MHF2QST = os.path.join(build_dir, "MHF2QST")
    if os.path.exists(MHF2QST):
        shutil.rmtree(MHF2QST)
    os.makedirs(MHF2QST, exist_ok=True)
    print("Building quests file...")
    quests = os.path.join(quests_dir, QUESTS_LANG)
    mib_files = sorted([f for f in os.listdir(quests) if f.lower().endswith(".mib")])
    quest_size = 0x6800
    
    id = 60001;
    output = os.path.join(build_dir, "MHF2QST", "EVENT.BIN")
    with open(output, 'wb') as fp:
        for f in mib_files:
            quest = os.path.join(quests, f)
            with open(quest, "rb") as q:
                data = bytearray(q.read())
                size = len(data)
                
                if(size < quest_size):
                    data += b"\x00" * (quest_size - size)
                elif(size > quest_size):
                    data = data[:quest_size]
                data[0x64:0x66] = id.to_bytes(2, byteorder="little")
                fp.write(data)
            id += 1

def writefp(fp, offset, value):
    fp.seek(offset)
    fp.write(value.to_bytes(4, byteorder="little"))
 
def buildASM(asm):
    print("Compiling ASM...")
    
    subprocess.run(
        [armips, os.path.join(asm_src_dir, asm+".asm")],
        check=True
    )
        
def generateCheat(name, v):
    print("Generating cheat file...")
    asm = os.path.join(v)
    path = os.path.join(build_dir, v+".bin")
    if v == "EventLoaderJPN":
        file = CwCheatIO(os.path.join(build_dir, "ULJM05156.ini"))
        file.write(f"Event Quest Loader v1.2 [JPN]")
        file.write(f"_L 0x21147B58 0x0a200800\n") # lw v0,0x0(a1) -> j 0x08802000
        file.write(f"_L 0x21147B5C 0x00000000\n") # bnel v0,zero,0x09947B6C -> nop 
        
        file.seek(0x08802000)
        with open(path, "rb") as bin:
            file.write(bin.read())
        file.close()
    elif v == "EventLoaderUSA":
        file = CwCheatIO(os.path.join(build_dir, "ULUS10266.ini"))
        file.write(f"Event Quest Loader v1.2 [USA]")
        file.write(f"_L 0x21148570 0x0a200800\n") # lw v0,0x0(a1) -> j 0x08802000
        file.write(f"_L 0x21148574 0x00000000\n") # bnel v0,zero,0x09948584 -> nop 
        
        file.seek(0x08802000)
        with open(path, "rb") as bin:
            file.write(bin.read())
        file.close()
    elif v == "EventLoaderEUR":
        file = CwCheatIO(os.path.join(build_dir, "ULES00851.ini"))
        file.write(f"Event Quest Loader v1.2 [EUR]")
        file.write(f"_L 0x21149820 0x0a200800\n") # lw v0,0x0(a1) -> j 0x08802000
        file.write(f"_L 0x21149824 0x00000000\n") # bnel v0,zero,0x09949834 -> nop 
        
        file.seek(0x08802000)
        with open(path, "rb") as bin:
            file.write(bin.read())
        file.close()
    os.remove(path)
    
def generate(name, v, db, eb):
    buildASM(v)
    generateCheat(name, v)
    print("\nDone!")
        
if __name__ == "__main__":
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)
    combineQuests()
    generate("EventLoaderJPN", "EventLoaderJPN", "DATA_JPN.BIN", "EBOOT_JPN.BIN")
    generate("EventLoaderUSA", "EventLoaderUSA", "DATA_USA.BIN", "EBOOT_USA.BIN")
    generate("EventLoaderEUR", "EventLoaderEUR", "DATA_EUR.BIN", "EBOOT_EUR.BIN")

