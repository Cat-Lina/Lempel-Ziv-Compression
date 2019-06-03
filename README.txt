INSTRUCTIONS FOR RUNNING lempel-ziv.py
FROM COMMAND LINE EXECUTE THE FOLLOWING
1) 'py lempel-ziv.py "filename" searchSize lookaheadSize'
recommended values for searchSize=65535 & lookaheadSize=255
e.g. 'py lempel-ziv.py "logo.bmp" 65535 255'
2) if no parameters are provided and you just run
'py lempel-ziv.py' 
default values are set for filename="logo.bmp"; searchSize=65535 
& lookaheadSize=255;

The sample file "logo.bmp" is included in the submission folder.

When running either of the commands you should get as output
somthing like this:

Compression took  0.009485244750976562  seconds
Decompression took  0.00550532341003418  seconds
Original file size is  10422 bytes and compressed file size is  2051  bytes
Compression ratio is  5.081423695758167

Also in the folder where your script is located another file will be
created called "my_file" which is a compressed version of the input file.