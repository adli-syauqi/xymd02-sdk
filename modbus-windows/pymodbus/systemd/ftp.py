# Source - https://stackoverflow.com/a/12613970
# Posted by K Z, modified by community. See post 'Timeline' for change history
# Retrieved 2026-09-10, License - CC BY-SA 4.0

import ftplib
session = ftplib.FTP('server.address.com','USERNAME','PASSWORD')
file = open('kitten.jpg','rb')                  # file to send
session.storbinary('STOR kitten.jpg', file)     # send the file
file.close()                                    # close file and FTP
session.quit()
