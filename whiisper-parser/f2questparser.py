import argparse
from collections import defaultdict
from pathlib import Path
import struct
import json


def decode_quest(data: bytearray) -> dict:
    offset = 0

    def get_offset() -> int:
        return offset

    def seek(pos: int) -> None:
        nonlocal offset
        offset = pos

    def skip(n: int) -> None:
        nonlocal offset
        offset += n

    def valid_ptr(ptr) -> bool:
        return 0 < ptr <= len(data)

    def read_u32() -> int:
        """Read 4-bytes (alter nonlocal offset)"""
        nonlocal offset
        (val,) = struct.unpack_from("<I", data, offset)
        offset += 4
        return val

    def u32_to_hex(val: int) -> str:
        return struct.pack("<I", val).hex().upper()

    def read_u16() -> int:
        """Read 2-bytes (alter nonlocal offset)"""
        nonlocal offset
        (val,) = struct.unpack_from("<H", data, offset)
        offset += 2
        return val

    def u16_to_hex(val: int) -> str:
        return struct.pack("<H", val).hex().upper()

    def read_u8() -> int:
        """Read 1-byte (alter nonlocal offset)"""
        nonlocal offset
        val = data[offset]
        offset += 1
        return val

    def u8_to_hex(val: int) -> str:
        return struct.pack("<B", val).hex().upper()

    def read_f32() -> float:
        """Read 4-bytes (alter nonlocal offset)"""
        nonlocal offset
        (val,) = struct.unpack_from("<f", data, offset)
        offset += 4
        return val

    def f32_to_hex(val: float) -> str:
        return struct.pack("<f", val).hex().upper()

    def read_raw(n: int) -> bytearray:
        """Read n bytes from nonlocal offset, advance offset, return raw bytes."""
        nonlocal offset
        start = offset
        offset += n
        return data[start : start + n]

    def raw_to_hex(chunk: bytearray) -> str:
        """Convert bytes to uppercase hex string."""
        return chunk.hex().upper()

    def read_str() -> str:
        nonlocal offset
        start = offset
        end = data.find(b"\x00", offset)
        if end == -1:
            end = len(data)
        val = data[start:end].decode("utf-8")
        offset = end + 1  # skip the null terminator
        return val

    def auto_dict():
        return defaultdict(auto_dict)

    out_dict = auto_dict()

    out_dict["headerSection"]["identifier"] = u32_to_hex(read_u32())
    questInfoPtr = read_u32()
    supplyItemsPtr = read_u32()
    questRewardsPtr = read_u32()
    fixedInformationPtr = read_u32()
    smallMonInfoPtr = read_u32()
    bossInformationPtr = read_u32()
    gatherInfoPtr = read_u32()
    unknownInformationPtr = read_u32()
    gatherPointDataPtr = read_u32()
    out_dict["headerSection"]["bossSize"] = u16_to_hex(read_u16())
    out_dict["headerSection"]["largeMonsterSize%"] = u8_to_hex(read_u8())
    out_dict["headerSection"]["fixedValue"] = u8_to_hex(read_u8())
    out_dict["headerSection"]["guildPointsReward"] = u32_to_hex(read_u32())
    # is apparently 00000000 for gathering - X quests otherwise 0F000000
    out_dict["headerSection"]["unknown0"] = u32_to_hex(read_u32())
    out_dict["headerSection"]["carvingDifficulty"] = u8_to_hex(read_u8())
    out_dict["headerSection"]["arrivalPosition"] = u8_to_hex(read_u8())
    out_dict["headerSection"]["supplyState"]["supplyMode"] = u8_to_hex(read_u8())
    out_dict["headerSection"]["supplyState"]["supplyConditions"] = u8_to_hex(read_u8())
    out_dict["headerSection"]["supplyState"]["conditionQuantity"] = u8_to_hex(read_u8())
    out_dict["headerSection"]["difficulty"] = u8_to_hex(read_u8())
    skip(2)
    out_dict["headerSection"]["smallMonsterChange0"]["changeCondition"] = u32_to_hex(read_u32())
    out_dict["headerSection"]["smallMonsterChange0"]["targetCode"] = u16_to_hex(read_u16())
    out_dict["headerSection"]["smallMonsterChange0"]["quantity"] = u8_to_hex(read_u8())
    out_dict["headerSection"]["smallMonsterChange0"]["sequenceNumber"] = u8_to_hex(read_u8())
    out_dict["headerSection"]["smallMonsterChange1"]["changeCondition"] = u32_to_hex(read_u32())
    out_dict["headerSection"]["smallMonsterChange1"]["targetCode"] = u16_to_hex(read_u16())
    out_dict["headerSection"]["smallMonsterChange1"]["quantity"] = u8_to_hex(read_u8())
    out_dict["headerSection"]["smallMonsterChange1"]["sequenceNumber"] = u8_to_hex(read_u8())

    seek(questInfoPtr)
    out_dict["questInformation"]["questType"] = u8_to_hex(read_u8())
    out_dict["questInformation"]["additional"] = u8_to_hex(read_u8())
    out_dict["questInformation"]["unknown0"] = u16_to_hex(read_u16())  # 0000 or 0800 afaiik
    out_dict["questInformation"]["contractFee"] = u32_to_hex(read_u32())
    out_dict["questInformation"]["rewardMoney"] = u32_to_hex(read_u32())
    out_dict["questInformation"]["felyneCartLoss"] = u32_to_hex(read_u32())
    out_dict["questInformation"]["questTime"] = u32_to_hex(read_u32())
    questContentPtr = read_u32()
    out_dict["questInformation"]["questNumber"] = u16_to_hex(read_u16())
    out_dict["questInformation"]["questStarLevel"] = u8_to_hex(read_u8())
    out_dict["questInformation"]["unknown1"] = u8_to_hex(read_u8())
    out_dict["questInformation"]["questMap"] = u8_to_hex(read_u8())
    out_dict["questInformation"]["specialConditions"] = u8_to_hex(read_u8())
    out_dict["questInformation"]["targetCount"] = u8_to_hex(read_u8())
    out_dict["questInformation"]["unknown2"] = u8_to_hex(read_u8())
    out_dict["questInformation"]["questTarget0"]["questCondition"] = u8_to_hex(read_u8())
    out_dict["questInformation"]["questTarget0"]["additionalCondition"] = u16_to_hex(read_u16())
    skip(1)
    out_dict["questInformation"]["questTarget0"]["targetCode"] = u16_to_hex(read_u16())
    out_dict["questInformation"]["questTarget0"]["quantity"] = u16_to_hex(read_u16())
    out_dict["questInformation"]["questTarget1"]["questCondition"] = u8_to_hex(read_u8())
    out_dict["questInformation"]["questTarget1"]["additionalCondition"] = u16_to_hex(read_u16())
    skip(1)
    out_dict["questInformation"]["questTarget1"]["targetCode"] = u16_to_hex(read_u16())
    out_dict["questInformation"]["questTarget1"]["quantity"] = u16_to_hex(read_u16())
    trainingdataPtr = read_u32()

    seek(questContentPtr)
    commisionContentPtr = read_u32()

    seek(commisionContentPtr)
    questNamePtr = read_u32()
    successDescPtr = read_u32()
    failureDescPtr = read_u32()
    questDescPtr = read_u32()
    mainMonsterPtr = read_u32()
    clientPtr = read_u32()

    seek(questNamePtr)
    out_dict["textCommissionContent"]["questName"] = read_str()
    seek(successDescPtr)
    out_dict["textCommissionContent"]["successDesc"] = read_str()
    seek(failureDescPtr)
    out_dict["textCommissionContent"]["failureDesc"] = read_str()
    seek(questDescPtr)
    out_dict["textCommissionContent"]["questDesc"] = read_str()
    seek(mainMonsterPtr)
    out_dict["textCommissionContent"]["mainMonster"] = read_str()
    seek(clientPtr)
    out_dict["textCommissionContent"]["client"] = read_str()

    # TODO: training data extraction

    seek(supplyItemsPtr)
    supplyItemsArr = []
    while True:
        item = read_u16()
        if item == 0x0000:
            break
        qty = read_u16()
        supplyItemsArr.append({"itemCode": u16_to_hex(item), "quantity": u16_to_hex(qty)})

    out_dict["supplyItems"] = supplyItemsArr

    seek(questRewardsPtr)
    questRewardsArr = []
    saved = get_offset()
    while True:
        seek(saved)
        rewardAcquisitionCode = read_u32()
        rewardBlockPtr = read_u32()

        saved = get_offset()
        seek(rewardBlockPtr)  # WARN: this is dangerous and can fail
        items = []
        while True:
            temp = read_u16()
            if temp == 0xFFFF:  # or temp == 0x0000: seems like probability being 0x0000 does not break it?
                break
            probability = temp
            rewardCode = read_u16()
            quantity = read_u16()
            items.append(
                {
                    "probability": u16_to_hex(probability),
                    "rewardCode": u16_to_hex(rewardCode),
                    "quantity": u16_to_hex(quantity),
                }
            )

        questRewardsArr.append(
            {
                "rewardAcquisitionConditionCode": u32_to_hex(rewardAcquisitionCode),
                "rewards": items
            }
        )
        seek(saved)
        saved2 = get_offset()
        temp = read_u16()
        if temp == 0xFFFF or temp == 0x0000:
            break
        saved = saved2

    out_dict["questRewards"] = questRewardsArr

    seek(fixedInformationPtr)
    out_dict["fixedInformation"]["initialInfoState"] = u32_to_hex(read_u32())
    out_dict["fixedInformation"]["unknown0"] = u32_to_hex(read_u32())
    out_dict["fixedInformation"]["unknownValue"] = u16_to_hex(read_u16())
    out_dict["fixedInformation"]["unknown1"] = raw_to_hex(read_raw(6))
    out_dict["fixedInformation"]["endMarker"] = raw_to_hex(read_raw(8))
    gap_size = supplyItemsPtr - get_offset()
    out_dict["fixedInformation"]["unknown2"] = raw_to_hex(read_raw(gap_size))

    def parse_monster_setting(ptr: int) -> tuple:
        seek(ptr)
        areas = []
        saved = get_offset()
        while True:
            seek(saved)
            temp = read_u32()
            if temp == 0x00000000:
                break

            areaCode = temp
            skip(4)
            spawnPtr = read_u32()
            detailsPtr = read_u32()
            saved = get_offset()

            seek(spawnPtr)
            smallMonSpawn0 = read_u32()
            smallMonSpawn1 = read_u32()
            smallMonSpawn2 = read_u32()
            smallMonSpawn3 = read_u32()

            seek(detailsPtr)
            detailsArr = []
            while True:
                temp = read_u16()
                if temp == 0xFFFF:
                    break

                code = temp
                state = read_u16()
                quantity = read_u16()
                unknownValue = read_u16()
                unknown0 = read_raw(20)
                orientation = read_u32()
                x = read_f32()
                z = read_f32()
                y = read_f32()
                inQuestSequenceNumber = read_u16()
                skip(2)
                inQuestSize = read_u16()
                inQuestHP = read_u16()
                skip(8)

                detailsArr.append(
                    {
                        "code": u16_to_hex(code),
                        "state": u16_to_hex(state),
                        "quantity": u16_to_hex(quantity),
                        "unknownValue": u16_to_hex(unknownValue),
                        "unknown0": raw_to_hex(unknown0),
                        "orientation": u32_to_hex(orientation),
                        "X": f32_to_hex(x),
                        "Z": f32_to_hex(z),
                        "Y": f32_to_hex(y),
                        "inQuestSequenceNumber": u16_to_hex(inQuestSequenceNumber),
                        "inQuestSize": u16_to_hex(inQuestSize),
                        "inQuestHP": u16_to_hex(inQuestHP),
                    }
                )

            areas.append(
                {
                    "areaCode": u32_to_hex(areaCode),
                    "smallMonSpawn0": u32_to_hex(smallMonSpawn0),
                    "smallMonSpawn1": u32_to_hex(smallMonSpawn1),
                    "smallMonSpawn2": u32_to_hex(smallMonSpawn2),
                    "smallMonSpawn3": u32_to_hex(smallMonSpawn3),
                    "spawnDetails": detailsArr,
                }
            )

        seek(saved)
        skip(4)
        unknownPostAreas = read_raw(12)
        return areas, raw_to_hex(unknownPostAreas)

    seek(smallMonInfoPtr)
    initSmallMonPtr = read_u32()
    smallMonChange1Ptr = read_u32()
    smallMonChange2Ptr = read_u32()
    if valid_ptr(initSmallMonPtr):
        out_dict["initSmallMon"], out_dict["unknownPostinitSmallMon"] = parse_monster_setting(initSmallMonPtr)
    else:
        out_dict["initSmallMon"] = []
        out_dict["unknownPostinitSmallMon"] = "DDDDDDDDDDDDDDD"
    if smallMonChange1Ptr != initSmallMonPtr:
        out_dict["changeSmallMon1"], out_dict["unknownPostChangeSmallMon1"] = parse_monster_setting(smallMonChange1Ptr)
    else:
        out_dict["changeSmallMon1"] = []
        out_dict["unknownPostChangeSmallMon1"] = "DDDDDDDDDDDDDDD"
    if smallMonChange2Ptr != initSmallMonPtr:
        out_dict["changeSmallMon2"], out_dict["unknownPostChangeSmallMon2"] = parse_monster_setting(smallMonChange2Ptr)
    else:
        out_dict["changeSmallMon2"] = []
        out_dict["unknownPostChangeSmallMon2"] = "DDDDDDDDDDDDDDD"

    seek(bossInformationPtr)
    skip(8)
    bossSpawnPtr = read_u32()
    bossDetailPtr = read_u32()

    seek(bossSpawnPtr)
    out_dict["bossInfo"]["bossSpawn0"] = u32_to_hex(read_u32())
    out_dict["bossInfo"]["bossSpawn1"] = u32_to_hex(read_u32())
    out_dict["bossInfo"]["bossSpawn2"] = u32_to_hex(read_u32())
    out_dict["bossInfo"]["bossSpawn3"] = u32_to_hex(read_u32())

    seek(bossDetailPtr)
    bossDetailArr = []
    while True:
        temp = read_u16()
        if temp == 0xFFFF:
            break
        code = temp
        state = read_u16()
        quantity = read_u8()
        skip(2)
        spawnArea = read_u8()
        unknown0 = read_raw(20)
        orientation = read_u32()
        x = read_f32()
        z = read_f32()
        y = read_f32()
        inQuestSequenceNumber = read_u16()
        skip(2)
        inQuestSize = read_u16()
        inQuestHP = read_u16()
        skip(8)
        bossDetailArr.append(
            {
                "code": u16_to_hex(code),
                "state": u16_to_hex(state),
                "quantity": u8_to_hex(quantity),
                "spawnArea": u8_to_hex(spawnArea),
                "unknown0": raw_to_hex(unknown0),
                "orientation": u32_to_hex(orientation),
                "X": f32_to_hex(x),
                "Z": f32_to_hex(z),
                "Y": f32_to_hex(y),
                "inQuestSequenceNumber": u16_to_hex(inQuestSequenceNumber),
                "inQuestSize": u16_to_hex(inQuestSize),
                "inQuestHP": u16_to_hex(inQuestHP),
            }
        )

    out_dict["bossInfo"]["spawnDetails"] = bossDetailArr

    seek(gatherInfoPtr)
    gatherInfoArr = []
    saved = get_offset()
    while True:
        seek(saved)
        temp = read_u32()
        if temp == 0x00000000:
            saved = get_offset()
            gatherInfoArr.append([]) # empty arr if area pointer is null
            continue
        elif not valid_ptr(temp):
            break
        areaSettingPtr = temp
        saved = get_offset()

        seek(areaSettingPtr)
        areaSettingArr = []
        while True:
            temp = read_f32()
            if temp == -1.0:  # 0xBF800000 (BE)
                break
            x = temp
            z = read_f32()
            y = read_f32()
            effectiveRange = read_f32()
            gatherCode = read_u16()
            gatherFreqUpperLimit = read_u16()
            gatherType = read_u16()
            gatherFreqLowerLimit = read_u16()

            areaSettingArr.append(
                {
                    "X": f32_to_hex(x),
                    "Z": f32_to_hex(z),
                    "Y": f32_to_hex(y),
                    "effectiveRange": f32_to_hex(effectiveRange),
                    "gatherCode": u16_to_hex(gatherCode),
                    "gatherFreqUpperLimit": u16_to_hex(gatherFreqUpperLimit),
                    "gatherType": u16_to_hex(gatherType),
                    "gatherFreqLowerLimit": u16_to_hex(gatherFreqLowerLimit),
                }
            )

        gatherInfoArr.append(areaSettingArr)

    out_dict["gatherInfo"] = gatherInfoArr

    seek(unknownInformationPtr)
    skip(4)  # FFFF "end marker"
    # NOTE: i really dont know what to do with this, its variable, unknown information block, with unknown end
    #       what a pain in the ass...
    #       the quest dosent seem to care, so ill place the 6 zeros that are usually in most quests, some have a long one:
    #       (this one: "000000000000FFFF00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000999900000000000000000000" )
    out_dict["unknownPostUnknownInformationBlock"] = "00000000"

    seek(gatherPointDataPtr)
    gatherPointDataArr = []
    saved = get_offset()
    while True:
        seek(saved)
        temp = read_u32()
        if not valid_ptr(temp):
            break

        gatherMaterialPtr = temp

        saved = get_offset()
        seek(gatherMaterialPtr)
        codes = []
        while True:
            temp = read_u16()
            if temp == 0xFFFF:
                break
            probability = temp
            itemCode = read_u16()

            codes.append(
                {
                    "probability": u16_to_hex(probability),
                    "itemCode": u16_to_hex(itemCode)
                }
            )
        gatherPointDataArr.append(codes)

    out_dict["gatherPointData"] = gatherPointDataArr

    return out_dict


def encode_quest(data: dict) -> bytearray:
    buf = bytearray()
    symbols = {}  # name -> offset
    patches = []  # (target_name, placeholder_offset)

    def mark(name: str) -> None:
        """Remember the current offset as 'name'."""
        symbols[name] = len(buf)

    def w_ptr(target: str) -> None:
        """Write a 4-byte placeholder and record where to patch later."""
        patches.append((target, len(buf)))
        buf.extend(b"\xdd\xdd\xdd\xdd")  # placeholder

    def align4() -> None:
        """Align to 4-bytes"""
        while len(buf) % 4 != 0:
            buf.extend(b"\x00")

    def w_str(data: str) -> None:
        """Write 4-byte aligned null terminated utf-8 encoded string"""
        align4()
        raw = data.encode("utf-8") + b"\x00"
        buf.extend(raw)
        align4()

    def w_hex(data: str) -> None:
        """Writes a string of hex characters as bytes"""
        buf.extend(bytes.fromhex(data))

    def w_pad(n: int) -> None:
        """Writes 0's repeated n times"""
        buf.extend(b"\x00" * n)

    w_hex(data["headerSection"]["identifier"])
    w_ptr("questInfo")
    w_ptr("supplyItems")
    w_ptr("questRewards")
    w_ptr("fixedInformation")
    w_ptr("smallMonInfo")
    w_ptr("bossInformation")
    w_ptr("gatherInfo")
    w_ptr("unknownInformation")
    w_ptr("gatherPointData")
    w_hex(data["headerSection"]["bossSize"])
    w_hex(data["headerSection"]["largeMonsterSize%"])
    w_hex(data["headerSection"]["fixedValue"])
    w_hex(data["headerSection"]["guildPointsReward"])
    w_hex(data["headerSection"]["unknown0"])
    # w_hex("0F000000")
    w_hex(data["headerSection"]["carvingDifficulty"])
    w_hex(data["headerSection"]["arrivalPosition"])
    w_hex(data["headerSection"]["supplyState"]["supplyMode"])
    w_hex(data["headerSection"]["supplyState"]["supplyConditions"])
    w_hex(data["headerSection"]["supplyState"]["conditionQuantity"])
    w_hex(data["headerSection"]["difficulty"])
    w_pad(2)
    w_hex(data["headerSection"]["smallMonsterChange0"]["changeCondition"])
    w_hex(data["headerSection"]["smallMonsterChange0"]["targetCode"])
    w_hex(data["headerSection"]["smallMonsterChange0"]["quantity"])
    w_hex(data["headerSection"]["smallMonsterChange0"]["sequenceNumber"])
    w_hex(data["headerSection"]["smallMonsterChange1"]["changeCondition"])
    w_hex(data["headerSection"]["smallMonsterChange1"]["targetCode"])
    w_hex(data["headerSection"]["smallMonsterChange1"]["quantity"])
    w_hex(data["headerSection"]["smallMonsterChange1"]["sequenceNumber"])

    mark("questInfo")
    w_hex(data["questInformation"]["questType"])
    w_hex(data["questInformation"]["additional"])
    w_hex(data["questInformation"]["unknown0"])
    w_hex(data["questInformation"]["contractFee"])
    w_hex(data["questInformation"]["rewardMoney"])
    w_hex(data["questInformation"]["felyneCartLoss"])
    w_hex(data["questInformation"]["questTime"])
    w_ptr("questContent")
    w_hex(data["questInformation"]["questNumber"])
    w_hex(data["questInformation"]["questStarLevel"])
    w_hex(data["questInformation"]["unknown1"])
    w_hex(data["questInformation"]["questMap"])
    w_hex(data["questInformation"]["specialConditions"])
    w_hex(data["questInformation"]["targetCount"])
    w_hex(data["questInformation"]["unknown2"])
    w_hex(data["questInformation"]["questTarget0"]["questCondition"])
    w_hex(data["questInformation"]["questTarget0"]["additionalCondition"])
    w_pad(1)
    w_hex(data["questInformation"]["questTarget0"]["targetCode"])
    w_hex(data["questInformation"]["questTarget0"]["quantity"])
    w_hex(data["questInformation"]["questTarget1"]["questCondition"])
    w_hex(data["questInformation"]["questTarget1"]["additionalCondition"])
    w_pad(1)
    w_hex(data["questInformation"]["questTarget1"]["targetCode"])
    w_hex(data["questInformation"]["questTarget1"]["quantity"])
    # w_ptr("trainingData")
    w_hex("00000000")  # TODO: implement training data

    mark("questName")
    w_str(data["textCommissionContent"]["questName"])
    mark("successDesc")
    w_str(data["textCommissionContent"]["successDesc"])
    mark("failureDesc")
    w_str(data["textCommissionContent"]["failureDesc"])
    mark("questDesc")
    w_str(data["textCommissionContent"]["questDesc"])
    mark("mainMonster")
    w_str(data["textCommissionContent"]["mainMonster"])
    mark("client")
    w_str(data["textCommissionContent"]["client"])

    mark("commissionContent")
    w_ptr("questName")
    w_ptr("successDesc")
    w_ptr("failureDesc")
    w_ptr("questDesc")
    w_ptr("mainMonster")
    w_ptr("client")

    mark("questContent")
    w_ptr("commissionContent")
    w_ptr("commissionContent")
    w_ptr("commissionContent")
    w_ptr("commissionContent")
    w_ptr("commissionContent")
    w_ptr("commissionContent")
    w_ptr("commissionContent")

    mark("fixedInformation")
    w_hex(data["fixedInformation"]["initialInfoState"])
    w_hex(data["fixedInformation"]["unknown0"])
    w_hex(data["fixedInformation"]["unknownValue"])
    w_hex(data["fixedInformation"]["unknown1"])
    w_hex(data["fixedInformation"]["endMarker"])
    w_hex(data["fixedInformation"]["unknown2"])

    mark("supplyItems")
    for item in data["supplyItems"]:
        w_hex(item["itemCode"])
        w_hex(item["quantity"])
    w_hex("0000")

    w_hex(data["questInformation"]["questNumber"])  # postSupplyQuestNumber

    for i, code in enumerate(data["gatherPointData"]):
        mark(f"gatherCode{i}")
        for material in code:
            w_hex(material["probability"])
            w_hex(material["itemCode"])
        w_hex("FFFF")  # end marker
        align4()

    mark("gatherPointData")
    for i, code in enumerate(data["gatherPointData"]):
        w_ptr(f"gatherCode{i}")
    w_hex("FFFFFFFF")  # custom end marker

    for i, area in enumerate(data["gatherInfo"]):
        if area:
            mark(f"areaInfo{i}")
            for point in area:
                w_hex(point["X"])
                w_hex(point["Z"])
                w_hex(point["Y"])
                w_hex(point["effectiveRange"])
                w_hex(point["gatherCode"])
                w_hex(point["gatherFreqUpperLimit"])
                w_hex(point["gatherType"])
                w_hex(point["gatherFreqLowerLimit"])
            w_hex("000080BF")
            w_pad(20)

    mark("gatherInfo")
    for i, area in enumerate(data["gatherInfo"]):
        if area:
            w_ptr(f"areaInfo{i}")
        else:
            w_hex("00000000")  # null ptr
    w_hex("FFFFFFFF")  # custom end marker

    for i, rewardType in enumerate(data["questRewards"]):
        mark(f"rewardBlock{i}")
        for reward in rewardType["rewards"]:
            w_hex(reward["probability"])
            w_hex(reward["rewardCode"])
            w_hex(reward["quantity"])
        w_hex("FFFF")
        align4()

    mark("questRewards")
    for i, rewardType in enumerate(data["questRewards"]):
        w_hex(rewardType["rewardAcquisitionConditionCode"])
        w_ptr(f"rewardBlock{i}")
    w_hex("FFFF")
    align4()
    w_pad(4)

    mark("unknownInformation")
    w_hex("FFFF")
    w_hex(data["unknownPostUnknownInformationBlock"])

    # ------------------------- ugh small monster bs

    def w_template_small_mon_detail_and_spawn_block(
        jsonMonDataArr: str,
        markSpawnBlock: str,
        markSpawnDetail: str,
    ):
        """Write details (if any) and then spawn block after it for small monsters"""
        for i, area in enumerate(data[jsonMonDataArr]):
            mark(f"{markSpawnDetail}{i}")
            for detail in area["spawnDetails"]:
                w_hex(detail["code"])
                w_hex(detail["state"])
                w_hex(detail["quantity"])
                w_hex(detail["unknownValue"])
                w_hex(detail["unknown0"])
                w_hex(detail["orientation"])
                w_hex(detail["X"])
                w_hex(detail["Z"])
                w_hex(detail["Y"])
                w_hex(detail["inQuestSequenceNumber"])
                w_pad(2)
                w_hex(detail["inQuestSize"])
                w_hex(detail["inQuestHP"])
                w_pad(8)
            w_hex("FFFF")
            align4()
            w_pad(56)

            # idk if this shouldve been another loop, but i think fixed is fine for now
            mark(f"{markSpawnBlock}{i}")
            w_hex(area["smallMonSpawn0"])
            w_hex(area["smallMonSpawn1"])
            w_hex(area["smallMonSpawn2"])
            w_hex(area["smallMonSpawn3"])

    def w_template_small_mon_area_block(
        markMonDataArr: str,
        jsonMonDataArr: str,
        ptrSpawnBlock: str,
        ptrSpawnDetail: str,
        jsonUnknownPostData: str,
    ):
        """Write the area array for small monster pointer"""
        mark(markMonDataArr)
        for i, area in enumerate(data[jsonMonDataArr]):  # print array of area infos
            w_hex(area["areaCode"])
            w_pad(4)
            w_ptr(f"{ptrSpawnBlock}{i}")
            w_ptr(f"{ptrSpawnDetail}{i}")
        w_hex("00000000")  # custom end marker
        w_hex(data[jsonUnknownPostData])

    if data["initSmallMon"]:
        w_template_small_mon_detail_and_spawn_block(
            "initSmallMon", "initSmallMonSpawnBlock", "initSmallMonSpawnDetail"
        )

    if data["changeSmallMon1"]:
        w_template_small_mon_detail_and_spawn_block(
            "changeSmallMon1", "changeSmallMon1SpawnBlock", "changeSmallMon1SpawnDetail"
        )

    if data["changeSmallMon2"]:
        w_template_small_mon_detail_and_spawn_block(
            "changeSmallMon2", "changeSmallMon2SpawnBlock", "changeSmallMon2SpawnDetail"
        )

    # -----------------------------------------------------

    if data["initSmallMon"]:
        w_template_small_mon_area_block(
            "initSmallMon",
            "initSmallMon",
            "initSmallMonSpawnBlock",
            "initSmallMonSpawnDetail",
            "unknownPostinitSmallMon",
        )
    if data["changeSmallMon1"]:
        w_template_small_mon_area_block(
            "changeSmallMon1",
            "changeSmallMon1",
            "changeSmallMon1SpawnBlock",
            "changeSmallMon1SpawnDetail",
            "unknownPostChangeSmallMon1",
        )
    if data["changeSmallMon2"]:
        w_template_small_mon_area_block(
            "changeSmallMon2",
            "changeSmallMon2",
            "changeSmallMon2SpawnBlock",
            "changeSmallMon2SpawnDetail",
            "unknownPostChangeSmallMon2",
        )

    # ---------------------------------------------------

    # mark("smallMonNULL")
    # w_hex("00000000") # placing it here crashes the game, its placed at the bottom now

    mark("smallMonInfo")
    if data["initSmallMon"]:
        w_ptr("initSmallMon")
    else:
        w_ptr("smallMonNULL")

    if data["changeSmallMon1"]:
        w_ptr("changeSmallMon1")
    else:
        if data["initSmallMon"]:
            w_ptr("initSmallMon")
        else:
            w_ptr("smallMonNULL")

    if data["changeSmallMon2"]:
        w_ptr("changeSmallMon2")
    else:
        if data["initSmallMon"]:
            w_ptr("initSmallMon")
        else:
            w_ptr("smallMonNULL")
    w_pad(4)

    # boss monster

    mark("bossDetails")
    for detail in data["bossInfo"]["spawnDetails"]:
        w_hex(detail["code"])
        w_hex(detail["state"])
        w_hex(detail["quantity"])
        w_pad(2)
        w_hex(detail["spawnArea"])
        w_hex(detail["unknown0"])
        w_hex(detail["orientation"])
        w_hex(detail["X"])
        w_hex(detail["Z"])
        w_hex(detail["Y"])
        w_hex(detail["inQuestSequenceNumber"])
        w_pad(2)
        w_hex(detail["inQuestSize"])
        w_hex(detail["inQuestHP"])
        w_pad(8)
    w_hex("FFFF")
    align4()
    w_pad(56)

    mark("bossSpawn")
    w_hex(data["bossInfo"]["bossSpawn0"])
    w_hex(data["bossInfo"]["bossSpawn1"])
    w_hex(data["bossInfo"]["bossSpawn2"])
    w_hex(data["bossInfo"]["bossSpawn3"])

    mark("bossInformation")
    w_hex("0100000000000000")
    w_ptr("bossSpawn")
    w_ptr("bossDetails")
    w_hex("00000000")
    w_pad(4)

    mark("smallMonNULL")
    w_pad(10)

    # PATCHING POINTERS
    for target, pos in patches:
        if target not in symbols:
            raise KeyError(f"Pointer target '{target}' not found")
        struct.pack_into("<I", buf, pos, symbols[target])

    return buf


parser = argparse.ArgumentParser(
    prog="f2questparser.py",
    description="Convert a MHF2 quest file binary into JSON (for easier editing), and back to binary (for playing)",
    epilog="""Examples:
f2questparser -d quest.mib           # decodes to quest.json
f2questparser -d quest.mib out.json  # decodes to out.json
f2questparser -e quest.json          # encodes to quest.bin
f2questparser -e quest.json out.bin  # encodes to out.bin
    """,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-e", "--encode", action="store_true", help="Convert JSON to BIN")
group.add_argument("-d", "--decode", action="store_true", help="Convert BIN to JSON")

parser.add_argument("input_file", type=Path, help="Input file path (binary or JSON)")
parser.add_argument(
    "output_file",
    nargs="?",
    type=Path,
    default=None,
    help="Output file path (default: input name with .bin/.json suffix",
)

args = parser.parse_args()

if args.encode:
    default_output_path: Path = args.input_file.with_suffix(".bin")
else:
    default_output_path: Path = args.input_file.with_suffix(".json")

input_path: Path = args.input_file
output_path: Path = args.output_file or default_output_path

output_path.parent.mkdir(parents=True, exist_ok=True)

if not input_path.exists():
    raise FileNotFoundError(f"Input does not exist: {input_path}")
if not input_path.is_file():
    raise ValueError(f"Input is not a file: {input_path}")
if output_path.exists() and output_path.is_dir():
    raise ValueError(f"Output path is a directory: {output_path}")

print("Input:", input_path)
print("Output:", output_path)


if args.encode:
    with input_path.open("rt") as f:
        in_dict = json.load(f)

    out_data = encode_quest(in_dict)

    with output_path.open("wb") as f:
        f.write(out_data)

else:  # args.decode
    with input_path.open("rb") as f:
        in_data = bytearray(f.read())

    out_dict = decode_quest(in_data)

    with output_path.open("wt") as f:
        json.dump(out_dict, f, indent=2, ensure_ascii=False)
