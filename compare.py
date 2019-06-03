import zlib,time,sys
def main():
    if len(sys.argv) == 1:
        filename="logo.bmp"
    else:
        try:   
            filename=sys.argv[1]
        except IndexError:  
            print ("filename not provided")
            sys.exit()
    original_data = open(filename, 'rb').read()  
    compressed_data = zlib.compress(original_data, zlib.Z_BEST_COMPRESSION)
    decompressed_data = zlib.decompress(compressed_data)
    compress_ratio = len(original_data) / len(compressed_data)
    print("Compression ratio is ",compress_ratio)
if __name__== "__main__":
  main()