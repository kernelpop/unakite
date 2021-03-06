from socket import *
import commands
import os
import sys

#Check for correct usage
if len(sys.argv) < 3:
	print "USAGE python " + sys.argv[0] + " <SERVER MACHINE>" + " <PORT NUMBER>"
else:
	serverName = sys.argv[1]
	serverPort = int(sys.argv[2])

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

def recvAll(sock, numBytes):

	# The buffer
	recvBuff = ""

	# The temporary buffer
	tmpBuff = ""

	# Keep receiving till all is received
	while len(recvBuff) < numBytes:

		# Attempt to receive bytes
		tmpBuff =  sock.recv(numBytes)

		# The other side has closed the socket
		if not tmpBuff:
			break

		# Add the received bytes to the buffer
		recvBuff += tmpBuff

	return recvBuff

def send_control(payload):
	data = payload
	bytesSent = 0
	while bytesSent != len(data):
			bytesSent += clientSocket.send(data[bytesSent:])
	print "Sent done!"
	print "payload:",payload
	return

while 1:
	arg = ""
	args_split = []
	try:
		arg = raw_input("ftp> ")
	except SyntaxError:
		arg = None
	args_split = arg.split()
	print "args_split:", args_split
	if (args_split[0] == 'ls'):
		send_control(arg)
		result = clientSocket.recv(40)
		print result
		continue
	elif (args_split[0] == 'put'):
		print "Server upload initiaded..."
		fileName = args_split[1]
		fileObj = open(fileName, "r")
		# Create a data socket
		dataSocket = socket(AF_INET, SOCK_STREAM)
		send_control(arg)
		result = clientSocket.recv(10)
		print "Assigned Ephemeral:", result
		dataSocket.connect((serverName, int(result)))
		numSent = 0
		fileData = None
		while True:
			# Read 65536 bytes of data
			fileData = fileObj.read(65536)
			# Make sure we did not hit EOF
			if fileData:
				dataSizeStr = str(len(fileData))
				while len(dataSizeStr) < 10:
					dataSizeStr = "0" + dataSizeStr
				fileData = dataSizeStr + fileData
				numSent = 0
				while len(fileData) > numSent:
					numSent += dataSocket.send(fileData[numSent:])
			else:
				break
		print "Sent", numSent, "bytes."
		dataSocket.close()
		fileObj.close()
	elif (args_split[0] == 'get'):
		print "Server download request..."
		# Create a data socket
		dataSocket = socket(AF_INET, SOCK_STREAM)
		send_control(arg)
		result = clientSocket.recv(10)
		print "Assigned Ephemeral:", result
		dataSocket.connect((serverName, int(result)))
		while True:
			fileData = ""
			recvBuff = ""
			fileSize = 0
			fileSizeBuff = ""
			#fileSizeBuff = recvAll(dataSocket, 10)
			fileSizeBuff = dataSocket.recv(10)
			fileSize = int(fileSizeBuff)
			print "The file size is ", fileSize
			fileData = recvAll(dataSocket, fileSize)
			print fileData
			filename = args_split[1]
			if os.path.exists(filename):
				append_write = 'a' #Append
			else:
				append_write = 'w' #Or make a new file
			file = open(filename,append_write)
			file.write(fileData)
			file.close()
	elif (arg == 'quit'):
		print "Disconnecting"
		break
	else:
		print "Unrecognized command"
		continue

incoming.close()
clientSocket.close()
