SHELL := /bin/bash -o pipefail
all: webcorpus1 # webcorpus2

webcorpus1:
	make download_webcorpus1 extract_webcorpus1 filter count ballance venv sample \
        FILTER_FINAL_SUM?="e9a1c810bb7e652828a70be313079f2b3c271fe5453cb563575531be5e5feb48" \
        CONTS_FILTERED_SUM?="e75e1fe9c28a8d60a8356f77b7c9e0b71d609cf33438cebe279a771918d94b39" \
        BALLANCED_CONTS?="d2ccb4e29a4a3fc632f342f2f8662ef045f6dd4a18e33836adf4be29f99e163b"

webcorpus2:
	make download_webcorpus2 extract_webcorpus2 filter count ballance venv sample \
        FILTER_FINAL_SUM?="64b1c8db9990e776652ca2f0d05af478dbae0919ca3acd289595c9662584b5da" \
        CONTS_FILTERED_SUM?="f98bf6d47468326fc099e7fed8311acf6c219d71bbca2c0c981cc14437aedd6f" \
        BALLANCED_CONTS?="9995672be3260085f75d27b3972883b53d3d9bcb49aea21af8afce8054f64cf5"

prevcons:
	make download_prevcons process_prevcons

download_webcorpus1:
	@# About 32 minutes
	mkdir -p orig_webcorpus1 && cd orig_webcorpus1 && ../download_webcorpus1.sh && sha256sum -c ../sha256sum_webcorpus1

download_webcorpus2:
	@# About 26 minutes
	mkdir -p orig_webcorpus2 && cd orig_webcorpus2 && ../download_webcorpus2.sh && sha256sum -c sha256sums

extract_webcorpus1:
	@# Must write the full corpus to disk in on sentence per line (SPL) format
	@# to allow switching corpora in the following steps
	export LC_ALL="C.UTF-8" && python3 webcorpus1_to_spl.py | pigz -n > full_spl.txt.gz
	@echo "b8ae149c9ec07830c347e280d3b0b82444db6671f17f96ddfd1547065ccc0c39  full_spl.txt.gz" | \
         sha256sum -c - || exit 1
	@# About 51 minutes
	@# Words: 589 080 971
	@# Sentences: 42 482 107

extract_webcorpus2:
	@# Must write the full corpus to disk in on sentence per line (SPL) format
	@# to allow switching corpora in the following steps
	export LC_ALL="C.UTF-8" && pigz -cd orig_webcorpus2/*.gz | grep "^# text = " | sed 's/^# text = //' | \
        pigz -n > full_spl.txt.gz
	@echo "a98a7ed37a71205b47d528ad3c7557637850303a8c0d7a0eb7d87b38f9328c97  full_spl.txt.gz" | \
         sha256sum -c - || exit 1
	@# About 32 minutes
	@# Words: 9 217 857 283
	@# Sentences: 589 398 448

filter:
	@# Remove possible remaining multiple spaces and TABs:
	@# https://unix.stackexchange.com/questions/102008/how-do-i-trim-leading-and-trailing-whitespace-from-each-
	@# line-of-some-output/205854#205854
	@# Filter sentences which are at least 11 and maximum 50 words long
	@# Do not contain words longer than 25 character
	@# Do not contain three or more consecutive words starting with uppercase letter (proper names)
	@# Do not contain two at least four character long words fully uppercased in any position (shouting)
	@# Do not contain three consecutive non-alphanumeric words (single line pattern)
	@# Do not contain three consecutive one-letter word (typewriter style)
	@# Do not contain three or more backslash (\) character (bad escaping)
	@# Do not contain replacement character (�)
	@# Do not contain o with tilde (õ) instead ő and u with circumflex (û) instead of ű (encoding problem)
	@# Do not contain HTML escapes (&lt;,&gt;&#12345;)
	mkdir -p ~/tmp
	export LC_ALL="C.UTF-8" && pigz -cd full_spl.txt.gz | ./filter_corpus.sh | pigz -n > filter_final.txt.gz
	@echo "$(FILTER_FINAL_SUM) filter_final.txt.gz" | sha256sum -c - || exit 1
	@# Webcorpus 1.0:
	@# About 14 minutes
	@# Words: 272 544 786
	@# Sentences: 13 915 132
	@#
	@# Webcorpus 2.0:
	@# About 219 minutes
	@# Words: 4 036 428 613
	@# Sentences: 199 627 778

count: filter_final.txt.gz
	@# Count lines and filter rare (<=$5) words
	@# 1. Create contexts ($1 words long for left, $2 words long for left) for words in parallel
	@#     (only $3 <= long <= $4 words with lowercase alphabetic characters recognised by emMorph
	@#     i.e. not in the non_words.txt (one word per line))
	@# 2. sort entries
	@# 3. Uniq based on the 2nd and 3rd fields
	@# 4. Count lines (as uniq -c) based on the first field (TAB separated) and print only groups larger than
	@#	 the specified limit ($5)
	mkdir -p ~/tmp
	export LC_ALL="C.UTF-8" && pigz -cd filter_final.txt.gz | ./create_and_count_contexts.sh 5 5 4 50 30 | \
        pigz -n > conts_filtered.txt.gz
	@echo "$(CONTS_FILTERED_SUM) conts_filtered.txt.gz" | sha256sum -c - || exit 1
	@# Webcorpus 1.0:
	@# About 10 minutes
	@# Words (to be guessed): 127 350
	@# Contexts: 63 566 600
	@#
	@# Webcorpus 2.0:
	@# About 240 minutes
	@# Words (to be guessed): 653 813
	@# Contexts: 923 223 806

ballance: conts_filtered.txt.gz
	@# Select $1 random contexts for each word to ballance frequent and rare words
	export LC_ALL="C.UTF-8" && pigz -cd conts_filtered.txt.gz | python3 ballance_freqs.py -n 30 | \
        pigz -n > ballanced_conts.txt.gz
	echo "$(BALLANCED_CONTS) ballanced_conts.txt.gz" | sha256sum -c - || exit 1
	@# Webcorpus 1.0:
	@# About 3 minutes
	@# Words (to be guessed): 127 350
	@# Contexts: 3 820 500
	@#
	@# Webcorpus 2.0:
	@# About 42 minutes
	@# Words (to be guessed): 653 813
	@# Contexts: 19 614 390

venv:
	virtualenv -p python3 venv
	./venv/bin/pip install sqlalchemy

sample: ./venv/bin/pip ballanced_conts.txt.gz
	@# Sample from the ballanced dataset for portability (8000 words with 30 context each yield a 30 MB SQLite DB)
	export LC_ALL="C.UTF-8" && rm -rf webcorpus_conts.db && pigz -cd ballanced_conts.txt.gz | \
        python3 random_sampling_filter.py -k 8000 -c $$(pigz -cd ballanced_conts.txt.gz | cut -f1 | uniq | wc -l) | \
        ./venv/bin/python3 create_sqldb.py -f webcorpus_conts.db
	@# For both Webcorpus 1.0 and 2.0:
	@# About a few minutes
	@# Words (to be guessed): 8 000
	@# Contexts: 240 000
	@# DB size: about 30 MB

download_prevcons:
	wget https://github.com/kagnes/prevcons/raw/master/PrevCons.sqlite3

process_prevcons: download_prevcons venv
	@# Requires the database file (PrevCons.sqlite3) and the virtualenv (venv) to be created
	mkdir -p ~/tmp
	export LC_ALL="C.UTF-8" && ./venv/bin/python3 filter_prevcons.py | \
        sort --parallel=$$(nproc) -T ~/tmp -S10% --compress-program=pigz | \
        ./uniq_2nd_field.sh | ./uniq_3rd_field.sh | sed 's/^\(.*\)/\1\t1/' | \
        ./venv/bin/python3 create_sqldb.py -f prevcons_conts.db
	@echo 'Database succesfully created! (The errors above were not fatal.)'
	@# Less than a minute
	@# Words (to be guessed): 122
	@# Contexts: 15 816
	@# DB size: 1,4 MB

clean:
	rm -rf orig_* *.txt.gz *.db PrevCons.sqlite3
