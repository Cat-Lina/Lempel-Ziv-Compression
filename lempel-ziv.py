import datetime,time,re,sys
from bitstring import BitArray

def getByteArrayFromFile(filename):
    with open(filename, "rb") as f:
        allBytes=f.read()
    return allBytes

def getBytesFromFile(filename):
    chars=bytes()
    with open(filename, "rb") as f:
        chars = f.read()
    return chars

def mainPart(filename,searchBufferSize,lookAheadSize):
    text=getBytesFromFile(filename)
    #initialise the lookahead buffer
    #if the text to be encoded is less than the size of look ahead buffer, 
    # just store the entire text in the lookahead
    lookahead=bytes()
    search=bytes()
    lookahead = text[:lookAheadSize]
    encoded=[]
    x=1
    #main part-search process
    # i is the index of the start of the lookahead buffer
    i = 0
    while i < len(text):
        theBiggest = findMatch(search, lookahead)
        # theBiggest is a tuple that stores (index,length) of the longest match
        # within the window (search + lookahead)
        theBiggestIndex=theBiggest[0]
        theBiggestLength=theBiggest[1]
        if theBiggestLength == 0:
            howManyAgo = 0
        else:
            howManyAgo=len(search)-theBiggestIndex
        # Calculate the start index of the next lookahead buffer
        next_i = i + theBiggestLength + 1
        # Update the search and lookahead buffers for next pass
        search = text[max(0, next_i - searchBufferSize) : next_i]
        lookahead = text[next_i : min(len(text), next_i + lookAheadSize)]
        # Set the triplet symbol to the one directly after the match we found,
        if next_i > len(text):
            nextSymbol = b''
        # or to empty if we've reached the end of input
        else:
            nextSymbol = bytes([text[next_i-1]])
        encoded.append((howManyAgo,theBiggestLength,nextSymbol))
        i = next_i

    return encoded

# Takes the search buffer and lookahead buffer and returns a tuple
# (index, length) of the longest match.
def findMatch(search, lookahead):
    window = search + lookahead
    matchIndex = 0
    matchLength = 0
    while True:
        sequence = lookahead[:matchLength+1]
        # Search for the sequence in the window
        newMatchIndex = window.index(sequence, matchIndex)
        # Break if no match was found
        if newMatchIndex >= len(search):
            break
        matchIndex = newMatchIndex
        matchLength += 1
        # Break if we've reached the end of the lookahead
        if matchLength >= len(lookahead):
            break
    return (matchIndex, matchLength) 

def findBiggestMatchLength(encoded):
    biggest=0
    howLongAgo=0
    for i in range(len(encoded)):
        if encoded[i][1]>biggest:
            biggest=encoded[i][1]
            howLongAgo=encoded[i][0]
    return (biggest,howLongAgo)

def howManyBytes(size):
    if size<2**8:
        return 1
    elif size<2**16:
        return 2
    elif size<2**24:
        return 3
    else:
        return None

def writeToFile(encoded,searchBufferSize,lookAheadSize):
    numOfBytesForLastSeen=howManyBytes(searchBufferSize)
    numOfBytesForLength=howManyBytes(lookAheadSize)
    msg=b""
    for i in range (len(encoded)):
        msg+=(encoded[i][0]).to_bytes(numOfBytesForLastSeen, byteorder='big')
        msg+=(encoded[i][1]).to_bytes(numOfBytesForLength, byteorder='big')
        if len(encoded[i]) == 3:
            msg+=encoded[i][2]
    f = open('my_file', 'w+b')
    f.write(msg)
    f.close()
    return len(msg)

def convertCompressedFileToTriplets(searchBufferSize,lookAheadSize):
    numOfBytesForLastSeen=howManyBytes(searchBufferSize)
    numOfBytesForLength=howManyBytes(lookAheadSize)
    triplets=[]
    with open('my_file', "rb") as f:
        fileBytes = f.read()
    length=(len(fileBytes))//(numOfBytesForLastSeen+numOfBytesForLength+1)
    for i in range(length):
        lastSeen=b""
        for i in range (numOfBytesForLastSeen):
            lastSeen+=bytes([fileBytes[0]])
            fileBytes=fileBytes[1:]
        howLong=b""
        for i in range(numOfBytesForLength):
            howLong+=bytes([fileBytes[0]])
            fileBytes=fileBytes[1:]
        nextChar=bytes([fileBytes[0]])
        fileBytes=fileBytes[1:]
        triplets.append((int.from_bytes(lastSeen, byteorder='big'),int.from_bytes(howLong, byteorder='big'),nextChar))
    if (len(fileBytes))%(numOfBytesForLastSeen+numOfBytesForLength+1) !=0:
        lastSeen=b""
        for i in range (numOfBytesForLastSeen):
            lastSeen+=bytes([fileBytes[0]])
            fileBytes=fileBytes[1:]
        howLong=b""
        for i in range(numOfBytesForLength):
            howLong+=bytes([fileBytes[0]])
            fileBytes=fileBytes[1:]
        triplets.append((int.from_bytes(lastSeen, byteorder='big'),int.from_bytes(howLong, byteorder='big'),b''))
    return triplets 

def decompressFromTriplets(encoded):
    original=b""
    for i in range(len(encoded)):
        if encoded[i][0]==0 and encoded[i][1]==0:
            original+=encoded[i][2]
        else:
            lastSeen=encoded[i][0]
            length=encoded[i][1]
            substring=b""
            #check if the length of match is greater than how many ago
            if length>lastSeen:
                for k in range(lastSeen):
                        substring+=bytes([original[len(original)-lastSeen+k]])
                difference=length-lastSeen
                while difference>lastSeen:
                    for k in range(lastSeen):
                        substring+=bytes([original[len(original)-lastSeen+k]])
                    difference-=lastSeen
                for k in range(difference):
                        substring+=bytes([original[len(original)-lastSeen+k]])
            else:
                for j in range (length):
                    substring+=bytes([original[len(original)-lastSeen+j]])
            #check if it's not the end of file in which case a '-' is read
            if len(encoded[i]) < 3:
                substring+=b''
            else:
                substring+=encoded[i][2]
            #finally add the next token and 
            original+=substring
    return original    

def main():
    if len(sys.argv) == 1:
        filename="logo.bmp"
        searchBufferSize=65535
        lookAheadSize=255
    else:
        try:   
            filename=sys.argv[1]
            searchBufferSize=int(sys.argv[2])
            lookAheadSize=int(sys.argv[3])
        except IndexError:  
            print ("not enough parameters")
            sys.exit()
    start=time.time()
    encoded=mainPart(filename,searchBufferSize,lookAheadSize)
    end=time.time()
    print("Compression took ", end-start, " seconds")
    compressedSize=writeToFile(encoded,searchBufferSize,lookAheadSize)
    triplets=convertCompressedFileToTriplets(searchBufferSize,lookAheadSize)
    start=time.time()
    decompressed=decompressFromTriplets(triplets)
    end=time.time()
    print("Decompression took ", end-start, " seconds")
    originalFileBytes=getByteArrayFromFile(filename)
    print("Original file size is ",len(originalFileBytes),"bytes and compressed file size is ", compressedSize," bytes")
    print("compression ratio is ", len(originalFileBytes)/compressedSize)
    
if __name__== "__main__":
  main()
