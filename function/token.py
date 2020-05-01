import os
from base64 import b64encode

# 256 bits of randomness
b = os.urandom(32)

# Convert to base-64
token = b64encode(b).decode('utf-8')

# Write the token file
with open('token.txt', 'w') as f:
    f.write(token)

