import yadisk

from configuration import yadisk_token

y = yadisk.YaDisk(token=yadisk_token)

with open("readme.txt", "rb") as f:
    y.upload(f, "/destination.txt")




