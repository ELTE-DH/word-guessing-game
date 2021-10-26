from glob import glob
from sys import stderr
from codecs import getreader
from tarfile import open as tarfile_open

for filename in glob('orig_webcorpus1/web2-4p-*.tar.gz'):
    fnames = set()
    with tarfile_open(filename, 'r:gz', encoding='latin2') as inp_tarfile:
        for member in inp_tarfile:
            if not member.isfile():
                print(f'ERROR: Not file {member.name} !', file=stderr)
                exit(1)
            elif member.name in fnames:
                print(f'ERROR: Duplicate filename {member.name} !', file=stderr)
                exit(1)
            else:
                fnames.add(member.name)
            for line in getreader('latin2')(inp_tarfile.extractfile(member)):
                if line.startswith('<s>'):
                    print(line[3:], end='')  # Untokenized sentences in SPL format
