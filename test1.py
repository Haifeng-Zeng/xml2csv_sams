import sys


num = [0]
k = 23

num1 = num[::-1]
num2 = list()
ans = list()
while k > 0 :
    num2.append(k % 10)
    k //= 10

addition = 0
i = 0
while i < len(num1) and i < len(num2) :
    ans.append((addition + num1[i] + num2[i]) % 10)
    addition = (addition + num1[i] + num2[i]) // 10
    i += 1

while i < len(num1) :
    ans.append((addition + num1[i]) % 10)
    addition = (addition + num1[i]) // 10
    i += 1

while i < len(num2) :
    ans.append((addition + num2[i]) % 10)
    addition = (addition + num2[i]) // 10
    i += 1
if addition == 1 :
     ans.append(1)

print(ans[::-1])
#return -1 if ans == 0 else -ans