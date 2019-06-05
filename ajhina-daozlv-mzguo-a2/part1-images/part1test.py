file = open("output.txt","r")
lines = file.readlines()
totalwords = 0
TP = 0
TN = 0
groups = []
for line in lines:
   picGroup = line.split(" ")
   picGroup = picGroup[:-1]
   for i in range (len(picGroup)):
      for j in range (i, len(picGroup)):
         if picGroup[i][0:3] == picGroup[j][0:3]:
            TP += 1
   groups.append(picGroup)
   wordNumber = len(picGroup)
   totalwords += wordNumber
print(groups)
for group in groups:
   for i in range (len(group)):
      for j in range (i,len(groups)):
         for k in range (len(groups[j])):
            if groups[i][0:3] != groups[j][k][0:3] and group != groups[j]:
               TN +=1
totalPairs = (totalwords * (totalwords -1))/2
errorRate = (totalPairs - ((TP+TN)/2))/totalPairs
print(errorRate)
