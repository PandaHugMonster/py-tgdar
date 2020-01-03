# py-tgdar
Python 3 "ar" Archive library


## Code example

```
with ArFile.open('tgd-helpers_0.1-1_all.deb', 'r') as f:
    members = f.getmembers()
    print(members)

    member: ArInfo = f.getmember('debian-binary')
    if member:
        print(member.content)

    member: ArInfo = f.getmember('control.tar.gz')
    if member:
        tar = tarfile.open(fileobj=member.content_as_bytes_io)
        for member in tar.getmembers():
            if member.isfile():
                q: BufferedReader = tar.extractfile(member)
                for line in q.readlines():
                    print(line)
```