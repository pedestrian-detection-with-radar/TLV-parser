import struct
import sys
import math

#
# TODO 1: (NOW FIXED) Find the first occurrence of magic and start from there
# TODO 2: Warn if we cannot parse a specific section and try to recover
# TODO 3: Remove error at end of file if we have only fragment of TLV
#

def tlvHeaderDecode(data):
    try:
        tlvType, tlvLength = struct.unpack('2I', data)
    except Exception as e:
        print("Error in tlvHeaderDecode: " + e.message)
        return 0, 0
    return tlvType, tlvLength

def parseDetectedObjects(data, tlvLength):
    numDetectedObj, xyzQFormat = struct.unpack('2H', data[:4])
    print("\tDetect Obj:\t%d "%(numDetectedObj))
    for i in range(numDetectedObj):
        print("\tObjId:\t%d "%(i))
        rangeIdx, dopplerIdx, peakVal, x, y, z = struct.unpack('3H3h', data[4+12*i:4+12*i+12])
        print("\t\tDopplerIdx:\t%d "%(dopplerIdx))
        print("\t\tRangeIdx:\t%d "%(rangeIdx))
        print("\t\tPeakVal:\t%d "%(peakVal))
        print("\t\tX:\t\t%07.3f "%(x*1.0/(1 << xyzQFormat)))
        print("\t\tY:\t\t%07.3f "%(y*1.0/(1 << xyzQFormat)))
        print("\t\tZ:\t\t%07.3f "%(z*1.0/(1 << xyzQFormat)))
        print("\t\tRange:\t\t%07.3fm"%(math.sqrt(pow((x*1.0/(1 << xyzQFormat)),2) + pow((y*1.0/(1 << xyzQFormat)),2) )))

def parseTrackedObjects(data, tlvLength):
    print("\tFOUND MMWDEMO_OUTPUT_MSG_TRACKED_OBJECTS !!!!")

def parseRangeProfile(data, tlvLength):
    for i in range(256):
        try:
            rangeProfile = struct.unpack('H', data[2*i:2*i+2])
            print("\tRangeProf[%d]:\t%07.3f "%(i, rangeProfile[0] * 1.0 * 6 / 8  / (1 << 8)))
        except Exception as e:
            print("parseRangeProfie error: " + e.message)
            pass
    print("\tTLVType:\t%d "%(2))

def parseStats(data, tlvLength):
    interProcess, transmitOut, frameMargin, chirpMargin, activeCPULoad, interCPULoad = struct.unpack('6I', data[:24])
    print("\tOutputMsgStats:\t%d "%(6))
    print("\t\tChirpMargin:\t%d "%(chirpMargin))
    print("\t\tFrameMargin:\t%d "%(frameMargin))
    print("\t\tInterCPULoad:\t%d "%(interCPULoad))
    print("\t\tActiveCPULoad:\t%d "%(activeCPULoad))
    print("\t\tTransmitOut:\t%d "%(transmitOut))
    print("\t\tInterprocess:\t%d "%(interProcess))

def tlvHeader(data):
    while data:
        headerLength = 36
        try:
            magic, version, length, platform, frameNum, cpuCycles, numObj, numTLVs = struct.unpack('Q7I', data[:headerLength])
        except:
            print "Improper TLV structure found: ", (data,)
            break
        print("Packet ID:\t%d "%(frameNum))
        print("Version:\t%x "%(version))
        print("TLV:\t\t%d "%(numTLVs))
        print("Detect Obj:\t%d "%(numObj))
        print("Platform:\t%X "%(platform))
	if version > 0x01000005:
	    subFrameNum = struct.unpack('I', data[36:40])[0]
	    headerLength = 40
	    print("Subframe:\t%d "%(subFrameNum))
        pendingBytes = length - headerLength
        data = data[headerLength:]
        for i in range(numTLVs):
            tlvType, tlvLength = tlvHeaderDecode(data[:8])
            data = data[8:]
            # MMWDEMO_OUTPUT_MSG_DETECTED_POINTS 1
            if (tlvType == 1):
                parseDetectedObjects(data, tlvLength)
            # MMWDEMO_OUTPUT_MSG_CLUSTERS 2
            elif (tlvType == 2):
                parseRangeProfile(data, tlvLength)
            # MMWDEMO_OUTPUT_MSG_TRACKED_OBJECTS 3
            elif (tlvType == 3):
                parseTrackedObjects(data, tlvLength)
            # MMWDEMO_OUTPUT_MSG_PARKING_ASSIST 4
            elif (tlvType == 4):
                print("\tFOUND MMWDEMO_OUTPUT_MSG_PARKING_ASSIST !!!!")
            elif (tlvType == 5):
                print("\tFOUND MMWDEMO_OUTPUT_MSG_RANGE_DOPPLER_HEAT_MAP !!!!")
            elif (tlvType == 6):
                parseStats(data, tlvLength)
            else:
                print("") #"Unidentified tlv type %d"%(tlvType)
            data = data[tlvLength:]
            pendingBytes -= (8+tlvLength)
        data = data[pendingBytes:]
        yield length, frameNum

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: parseTLV.py inputFile.bin")
        sys.exit()

    fileName = sys.argv[1]
    rawDataFile = open(fileName, "rb")
    rawData = rawDataFile.read()
    rawDataFile.close()
    magic = b'\x02\x01\x04\x03\x06\x05\x08\x07'
    offset = rawData.find(magic)
    rawData = rawData[offset:]
    for length, frameNum in tlvHeader(rawData):
        print
