from planespotting.identifiers import *
from planespotting.utils import *


long_msg_bits = 112
short_msg_bits = 56


def getMsgLength(df):
    if df > 16:
        return long_msg_bits
    else:
        return short_msg_bits

def getDF(frame):
    bin_frame = hexToDec(frame)
    df = int(bin_frame[0:5], 2)
    return df

def getTC(frame):
    data = frame[8:22]
    bin = hexToDec(data)
    if getMsgLength(getDF(frame)) == 112:
        return int(bin[0:5],2)
    else:
        return None

def getICAO(frame):
    return frame[2:8]

def getAirbornePosition(frame):
    print(frame)
    data = frame[8:22]
    bin = hexToDec(data)

    SS = int(bin[5:7],2)
    NICsb = int(bin[7],2)
    ALT = int(bin[8:20],2)
    T = int(bin[20],2)
    F = int(bin[21],2)
    LAT_CPR = int(bin[22:39],2)
    LON_CPR = int(bin[39:],2)

    return SS, NICsb, ALT, T, F, LAT_CPR, LON_CPR

def getVelocityData(frame, subtype):
    msg_bin = hexToDec(frame[8:22])
    if subtype == 1:
        IC = int(msg_bin[8], 2)
        RESV_A = int(msg_bin[9], 2)
        NAC =  int(msg_bin[10:13], 2)
        S_ew =  int(msg_bin[13], 2)
        V_ew =  int(msg_bin[14:24], 2)
        S_ns =  int(msg_bin[24], 2)
        V_ns =  int(msg_bin[25:35], 2)
        VrSrc =  int(msg_bin[35], 2)
        S_vr =  int(msg_bin[36], 2)
        Vr =  int(msg_bin[37:46], 2)
        RESV_B = int(msg_bin[46:48], 2)
        S_Dif = int(msg_bin[48], 2)
        Dif = int(msg_bin[49:56], 2)
        return IC, RESV_A, NAC, S_ew, V_ew, S_ns, V_ns, VrSrc, S_vr, Vr, RESV_B, S_Dif, S_Dif, Dif

    elif subtype == 3:
        IC = int(msg_bin[8], 2)
        RESV_A = int(msg_bin[9], 2)
        NAC =  int(msg_bin[10:13], 2)
        S_hdg =  int(msg_bin[13], 2)
        Hdg =  int(msg_bin[14:24], 2)
        AS_t =  int(msg_bin[24], 2)
        AS =  int(msg_bin[25:35], 2)
        VrSrc =  int(msg_bin[35], 2)
        S_vr =  int(msg_bin[36], 2)
        Vr =  int(msg_bin[37:46], 2)
        RESV_B = int(msg_bin[46:48], 2)
        S_Dif = int(msg_bin[48], 2)
        Dif = int(msg_bin[49:56], 2)
        return IC, RESV_A, NAC, S_hdg, Hdg, As_t, AS, VrSrc, S_vr, Vr, RESV_B, S_Dif, Dif



def decode(data):
    #for id in range(len(data["data"])):
    for frames in data['data']:
        #frames = data["data"]
        df = getDF(frames['adsb_msg'])
        tc = getTC(frames['adsb_msg'])
        frames['df'] = df
        frames['tc'] = tc
        decode_id = 0
        print(frames['adsb_msg'])
        # grouping messages by df and tc, that can be decoded the same or share similar parts
        if identifier1(df, tc):
            decode_id = 1
            frames['callsign_bin']=hexToDec(frames['adsb_msg'])[40:96]
            print(frames)
            continue
        if identifier2(df, tc):
            decode_id = 2
            continue
        if identifier3(df, tc):
            decode_id = 3

            SS, NICsb, ALT, T, F, LAT_CPR, LON_CPR = getAirbornePosition(frames['adsb_msg'])

            # filling in the now known values
            frames["ICAO"] = getICAO(frames['adsb_msg'])
            frames["SS"] = SS
            frames["NICsb"] = NICsb
            frames["ALT"] = ALT
            frames["T"] = T
            frames["F"] = F
            frames["LAT_CPR"] = LAT_CPR
            frames["LON_CPR"] = LON_CPR

            print(frames)
            continue
        if identifier4(df, tc):
            decode_id = 4
            subtype = int(hexToDec(frames['adsb_msg'][8:22])[5:8], 2)
            if subtype == 1:
                IC, RESV_A, NAC, S_ew, V_ew, S_ns, V_ns, VrSrc, S_vr, Vr, RESV_B, S_Dif, S_Dif, Dif = getVelocityData(frames['adsb_msg'], subtype)
                frames['Subtype'] = subtype
                frames["IC"] = IC
                frames["RESV_A"] = RESV_A
                frames["NAC"] =  NAC
                frames["S_ew"] =  S_ew
                frames["V_ew"] =  V_ew
                frames["S_ns"] =  S_ns
                frames["V_ns"] =  V_ns
                frames["VrSrc"] =  VrSrc
                frames["S_vr"] =  S_vr
                frames["Vr"] =  Vr
                frames["RESV_B"] = RESV_B
                frames["S_Dif"] = S_Dif
                frames["Dif"] = Dif

            elif subtype == 3:
                IC, RESV_A, NAC, S_hdg, Hdg, As_t, AS, VrSrc, S_vr, Vr, RESV_B, S_Dif, Dif = getVelocityData(frames['adsb_msg'], subtype)
                frames['Subtype'] = subtype
                frames["IC"] = IC
                frames["RESV_A"] = RESV_A
                frames["NAC"] =  NAC
                frames["S_hdg"] =  S_hdg
                frames["Hdg"] = Hdg
                frames["AS_t"] =  AS_t
                frames["AS"] =  AS
                frames["VrSrc"] =  VrSrc
                frames["S_vr"] =  S_vr
                frames["Vr"] =  Vr
                frames["RESV_B"] = RESV_B
                frames["S_Dif"] = S_Dif
                frames["Dif"] = Dif
            print(frames)
            continue
        if identifier5(df, tc):
            decode_id = 5
            continue
        if identifier6(df, tc):
            decode_id = 6
            continue
        if identifier7(df, tc):
            decode_id = 7

        # todo more decoders needed, because many messages escape them!

        #print(frames["id"], frames["timestamp"], df, tc, frames['adsb_msg'], decode_id)