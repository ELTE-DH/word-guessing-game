# Word Guessing Game

A [Cloze test-like](https://en.wikipedia.org/wiki/Cloze_test) game based on
 the idea of the "Nyelvi Játék" by [MorphoLogic Kft.](https://www.morphologic.hu/) on a new, different code base.

Multiple sample instances are running at:
- Webcorpus 1.0 (Hungarian): https://word-concordance-game.onrender.com/
- PrevCons (Hungarian): https://prev-guessing-game.onrender.com/
- OSCAR 2019 Polish deduplicated (Polish): https://polish-guessing-game.onrender.com/

# Installation

The required minimum Python version is 3.6.

1. Clone the repository
2. `pip install -r requirements.txt`
3. Setup the database and configuration ([see examples](example_databases)).
4. `python main.py`

# Recreating the database

- __NOTE__: One can use the previously created example databases in: [example_databases](example_databases) directory.
- __NOTE2__: The following scripts do reproducible processing of the corpora, see [ballance_freqs.py](create_database/ballance_freqs.py) to modify the fixed random seed if needed!

1. `cd create_database`
2. `make webcorpus1` XOR `make webcorpus2`
3. Setup the database in [`config.yaml`](config.yaml) (`database_name` key in `db_config`)

# License

This project is licensed under the terms of the GNU LGPL 3.0 license.

# Acknowledgement

The authors gratefully acknowledge the groundbreaking work of all pioneers who inspired this program. <br>
We wish to thank to the employees of _MorphoLogic Kft._ who created this program. <br>
We also thank to the publishers of both Webcorpus versions for making their corpus publicly available.

# References

If you use this program, please cite the following papers:

[Indig, B. and Lévai, D. (2022). __Okosabb vagy, mint egy XXXXXXXX? – egy nyelvi játéktól a nyelvmodellek összehasonlı́tásáig__. In Gábor Berend, et al., editors, _XVIII. Magyar Számı́tógépes Nyelvészeti Konferencia_, pages 31--44 Szeged, Hungary](https://rgai.inf.u-szeged.hu/sites/rgai.inf.u-szeged.hu/files/mszny2022.pdf)

```
@inproceedings{word-guessing-mszny2022,
    author = {Indig, Balázs and Lévai, Dániel},
    booktitle = {{XVIII}. {M}agyar {S}zámítógépes {N}yelvészeti {K}onferencia},
    title = {Okosabb vagy, mint egy {XXXXXXXX}? -- Egy nyelvi játéktól a nyelvmodellek összehasonlításáig},
    year = {2022},
    editor = {Gábor Berend and Gábor Gosztolya and Veronika Vincze},
    pages = {31--44},
    orcid-numbers = {Indig, Balázs/0000-0001-8090-3661}
}
```

[Balázs, I. and Dániel, L. (2023). __I’m Smarter than the Average BERT! – Testing Language Models Against Humans in a Word Guessing Game__. In Zygmunt Vetulani, et al., editors, _Human Language Technologies as a Challenge for Computer Science and Linguistics -- 2023_. pages 106–-110 Poznań, Poland](http://ltc.amu.edu.pl/)

```
@inproceedings{MTMT:33785196,
	author = {Indig, Balázs and Lévai, Dániel},
	booktitle = {Human Language Technologies as a Challenge for Computer Science and Linguistics -- 2023},
	title = {I’m Smarter than the Average BERT! – Testing Language Models Against Humans in a Word Guessing Game},
	year = {2023},
    editor = {Vetulani, Zygmunt and Paroubek, Patrick and Kubis, Marek},
	pages = {106-110},
	orcid-numbers = {Indig, Balázs/0000-0001-8090-3661}
}
```
